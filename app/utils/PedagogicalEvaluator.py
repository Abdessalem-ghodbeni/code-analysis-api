from app.config import settings
import os
import json
from collections import defaultdict


class PedagogicalEvaluator:
    # Liste des acquis pédagogiques à évaluer
    ACQUIS = {
        "frontend": {
            "structure_html": "Utilisation de balises sémantiques HTML5 pour structurer le contenu de manière logique.",
            "css": "Stylisation cohérente des interfaces en utilisant des règles CSS efficaces.",
            "css_responsive": "Mise en œuvre de media queries et conception mobile-first pour s'adapter à tous les écrans.",
            "accessibilite": "Respect des normes WCAG : contrastes, labels, navigation clavier, ARIA.",
            "interactivite": "Manipulation du DOM pour créer des interactions utilisateur (formulaires, menus, etc.).",
            "gestion_etat": "Gestion d'état efficace : transmission de données, gestion locale et globale.",
            "separation_concernes": "Organisation claire du code : séparation logique, structure, style.",
            "performance": "Optimisation de l'affichage (images, chargement différé, minimisation des scripts).",
            "tests_ui": "Réalisation de tests d'interface pour garantir le bon fonctionnement des composants visuels.",
        },
        "backend": {
            "architecture": "Structure claire basée sur des modèles comme MVC ou Hexagonale.",
            "gestion_donnees": "Lecture, écriture et manipulation de données via une base de données.",
            "api": "Création et documentation d'APIs RESTful pour le dialogue avec le frontend.",
            "validation": "Validation des données entrantes pour éviter les erreurs et failles de sécurité.",
            "securite": "Mise en œuvre de mécanismes d'authentification, autorisation, et chiffrement.",
            "gestion_erreurs": "Traitement propre des erreurs serveur et retour de messages explicites.",
            "performance": "Optimisation des requêtes, gestion de la charge, mise en cache.",
            "tests": "Rédaction de tests unitaires et d'intégration pour assurer la stabilité de l'application.",
        },
        "outil_dev": {
            "versioning": "Utilisation de Git pour gérer le code et collaborer efficacement.",
            "collaboration": "Travail en équipe avec des outils de suivi de tâches et de maquettes (Trello, Jira, Figma).",
            "ci_cd": "Compréhension des pipelines d'intégration et de déploiement continus.",
            "env_dev": "Configuration et utilisation d'un environnement local adapté au projet.",
            "documentation": "Rédaction d'une documentation claire pour les modules et les APIs.",
            "tests_automatises": "Utilisation d'outils de test pour automatiser les vérifications du code.",
            "debugging": "Analyse des erreurs avec console, logs, et outils de débogage.",
            "ux": "Sensibilité à l'expérience utilisateur : fluidité, clarté, ergonomie.",
        },
        "algorithmique": {
            "complexite": "Analyse de la complexité algorithmique pour optimiser les performances (Big O).",
            "structures_donnees": "Choix et usage pertinents des structures comme tableaux, listes, dictionnaires, piles, etc.",
            "paradigmes": "Compréhension et implémentation de design patterns (singleton, factory, observer, etc.).",
        },
    }

    # Critères spécifiques par framework
    FRAMEWORK_SPECIFIC_CRITERIA = {
        "react": {
            "composants": [
                "Utilisation de composants fonctionnels",
                "React.memo",
                "React.lazy",
            ],
            "hooks": ["useState", "useEffect", "useContext", "useCallback", "useMemo"],
            "routing": ["React Router", "gestion des paramètres d'URL"],
            "state_management": ["Redux", "Context API", "Recoil"],
            "performances": ["Memo", "virtualisation de listes", "lazy loading"],
        },
        "angular": {
            "composants": ["@Component", "cycles de vie", "directives personnalisées"],
            "services": ["@Injectable", "injection de dépendances", "singleton"],
            "routing": ["RouterModule", "Guards", "Resolvers"],
            "rxjs": ["Observables", "opérateurs", "gestion des souscriptions"],
            "forms": ["FormControl", "FormGroup", "Validators"],
        },
        "springboot": {
            "annotations": ["@RestController", "@Service", "@Repository", "@Autowired"],
            "api_rest": ["ResponseEntity", "gestion des exceptions", "versioning"],
            "security": ["Spring Security", "JWT", "OAuth2"],
            "data": ["JPA/Hibernate", "requêtes optimisées", "transactions"],
            "tests": ["JUnit", "Mockito", "Spring Test"],
        },
        "laravel": {
            "mvc": ["Models", "Controllers", "Blade Templates"],
            "eloquent": ["ORM", "relations", "migrations"],
            "middleware": ["authentification", "validation", "CSRF"],
            "services": ["Providers", "Facades", "Injection"],
            "tests": ["PHPUnit", "tests de fonctionnalités", "mocks"],
        },
    }

    # Patterns à rechercher dans le code pour détecter la présence de bonnes pratiques
    CODE_PATTERNS = {
        "frontend": {
            "structure_html": [
                "<header",
                "<nav",
                "<main",
                "<footer",
                "<section",
                "<article",
                "aria-",
            ],
            "css": ["@media", "display: flex", "display: grid", "rem", "vh", "vw"],
            "accessibilite": ["aria-", "alt=", "role=", "tabindex"],
            "tests_ui": ["test(", "describe(", "it(", "expect(", "render(", "screen."],
        },
        "backend": {
            "architecture": ["class", "interface", "abstract", "extends", "implements"],
            "api": [
                "@RestController",
                "@GetMapping",
                "@PostMapping",
                "app.get(",
                "app.post(",
                "router.get",
            ],
            "validation": ["validate", "Validator", "constraints", "required"],
            "tests": ["test", "assert", "mock", "@Test"],
        },
    }

    @classmethod
    def get_code_patterns(cls, framework):
        """Retourne les motifs de code adaptés au framework spécifique"""
        base_patterns = cls.CODE_PATTERNS.copy()

        # Ajouter motifs spécifiques au framework
        if framework == "react":
            base_patterns["frontend"]["composants"] = [
                "function",
                "=>",
                "React.memo",
                "React.lazy",
            ]
            base_patterns["frontend"]["hooks"] = [
                "useState",
                "useEffect",
                "useContext",
                "useReducer",
            ]
            base_patterns["frontend"]["state"] = [
                "useState",
                "useReducer",
                "createContext",
                "useContext",
            ]
        elif framework == "angular":
            base_patterns["frontend"]["composants"] = [
                "@Component",
                "implements OnInit",
                "ngOnInit",
            ]
            base_patterns["frontend"]["services"] = [
                "@Injectable",
                "providedIn: 'root'",
            ]
            base_patterns["frontend"]["rxjs"] = [
                "Observable",
                "Subject",
                "pipe",
                "subscribe",
            ]
        elif framework == "springboot":
            base_patterns["backend"]["api"] = [
                "@RestController",
                "@RequestMapping",
                "@GetMapping",
                "@PostMapping",
            ]
            base_patterns["backend"]["injection"] = [
                "@Autowired",
                "@Inject",
                "@Service",
                "@Repository",
            ]
            base_patterns["backend"]["data"] = [
                "@Entity",
                "@Repository",
                "JpaRepository",
            ]
        elif framework == "laravel":
            base_patterns["backend"]["api"] = [
                "Route::get",
                "Route::post",
                "Controller",
                "return response()->json",
            ]
            base_patterns["backend"]["models"] = [
                "extends Model",
                "protected $fillable",
                "function relations",
            ]

        return base_patterns

    @classmethod
    def analyze_file_content(cls, file_path, content, framework):
        """Analyse le contenu d'un fichier pour détecter les motifs de bonnes pratiques"""
        ext = os.path.splitext(file_path)[1].lower()
        patterns = cls.get_code_patterns(framework)

        results = defaultdict(dict)

        # Déterminer le domaine (frontend/backend) en fonction de l'extension
        domain = None
        if ext in [".html", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx"]:
            domain = "frontend"
        elif ext in [".java", ".py", ".php", ".rb", ".go", ".cs"]:
            domain = "backend"

        if not domain:
            return results

        # Chercher les patterns dans le contenu
        for category, pattern_list in patterns.get(domain, {}).items():
            matches = 0
            for pattern in pattern_list:
                if pattern in content:
                    matches += 1

            # Calcul d'un score proportionnel au nombre de patterns trouvés
            if pattern_list:  # Éviter division par zéro
                confidence = min(
                    1.0, matches / (len(pattern_list) * 0.7)
                )  # 70% des patterns = confiance max
                if confidence > 0.3:  # Seuil minimal de confiance
                    results[domain][category] = confidence

        return results

    @classmethod
    def evaluate_project(cls, files_analyses, framework, global_score):
        """Évalue les acquis pédagogiques basés sur l'analyse des fichiers"""
        acquis_evaluation = {}
        all_results = defaultdict(lambda: defaultdict(list))

        # Agréger les résultats de tous les fichiers
        for file_path, content in files_analyses:
            analysis = cls.analyze_file_content(file_path, content, framework)
            for domain, categories in analysis.items():
                for category, confidence in categories.items():
                    all_results[domain][category].append(confidence)

        # Calculer les scores par domaine et catégorie
        for domain, categories in all_results.items():
            if domain not in acquis_evaluation:
                acquis_evaluation[domain] = {}

            for category, confidences in categories.items():
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    acquis_evaluation[domain][category] = {
                        "score": round(avg_confidence * 100, 1),
                        "valide": avg_confidence >= 0.6,
                        "description": cls.ACQUIS.get(domain, {}).get(category, ""),
                    }

        # Ajouter évaluation framework-spécifique
        framework_domain = (
            "frontend" if framework in ["react", "angular"] else "backend"
        )
        framework_criteria = cls.FRAMEWORK_SPECIFIC_CRITERIA.get(framework, {})

        if framework_domain not in acquis_evaluation:
            acquis_evaluation[framework_domain] = {}

        for criteria, details in framework_criteria.items():
            # Score artificiel basé sur le score global pour le moment
            # (à remplacer par une analyse plus fine basée sur les patterns)
            score_factor = max(0.3, min(1.0, global_score / 100))
            criteria_score = round(score_factor * 100, 1)

            acquis_evaluation[framework_domain][criteria] = {
                "score": criteria_score,
                "valide": criteria_score >= 60,
                "description": f"Compétence {criteria} en {framework}",
                "details": details,
            }

        return acquis_evaluation

    @classmethod
    def generate_dynamic_recommendations(
        cls, acquis_evaluation, framework, global_score
    ):
        """Génère des recommandations personnalisées basées sur l'évaluation des acquis"""
        recommendations = []

        # Identifier les domaines les plus faibles
        domain_scores = {}
        for domain, categories in acquis_evaluation.items():
            valid_categories = 0
            total_categories = 0

            for _, details in categories.items():
                if details.get("valide", False):
                    valid_categories += 1
                total_categories += 1

            if total_categories > 0:
                domain_scores[domain] = valid_categories / total_categories
            else:
                domain_scores[domain] = 0

        # Recommandations générales basées sur le score global
        if global_score < 40:
            recommendations.append(
                {
                    "priorite": "haute",
                    "categorie": "fondamentaux",
                    "conseil": f"Revoyez les bases du développement {framework}. Essayez de suivre un tutoriel complet étape par étape.",
                }
            )
        elif global_score < 60:
            recommendations.append(
                {
                    "priorite": "moyenne",
                    "categorie": "progression",
                    "conseil": f"Votre compréhension des concepts de base est correcte, mais approfondissez les bonnes pratiques en {framework}.",
                }
            )

        # Recommandations spécifiques par domaine faible
        for domain, score in domain_scores.items():
            if score < 0.5:  # Moins de 50% des catégories validées
                if domain == "frontend":
                    if framework == "react":
                        recommendations.append(
                            {
                                "priorite": "haute",
                                "categorie": "frontend",
                                "conseil": "Améliorez votre compréhension des hooks React et du cycle de vie des composants.",
                            }
                        )
                    elif framework == "angular":
                        recommendations.append(
                            {
                                "priorite": "haute",
                                "categorie": "frontend",
                                "conseil": "Approfondissez l'architecture des composants Angular et la gestion des services.",
                            }
                        )
                elif domain == "backend":
                    if framework == "springboot":
                        recommendations.append(
                            {
                                "priorite": "haute",
                                "categorie": "backend",
                                "conseil": "Travaillez sur l'architecture en couches et l'injection de dépendances.",
                            }
                        )
                    elif framework == "laravel":
                        recommendations.append(
                            {
                                "priorite": "haute",
                                "categorie": "backend",
                                "conseil": "Renforcez votre maîtrise du modèle MVC et de l'ORM Eloquent.",
                            }
                        )
                elif domain == "algorithmique":
                    recommendations.append(
                        {
                            "priorite": "moyenne",
                            "categorie": "algorithmique",
                            "conseil": "Revoyez les structures de données et les algorithmes de base pour optimiser votre code.",
                        }
                    )

        # Recommandations spécifiques par acquis faibles
        for domain, categories in acquis_evaluation.items():
            for category, details in categories.items():
                if not details.get("valide", True) and details.get("score", 0) < 50:
                    specific_rec = cls.get_specific_recommendation(
                        domain, category, framework
                    )
                    if specific_rec:
                        recommendations.append(specific_rec)

        # Limiter à 5 recommandations max
        return recommendations[:5]

    @classmethod
    def get_specific_recommendation(cls, domain, category, framework):
        """Génère une recommandation spécifique basée sur un domaine et une catégorie"""
        recs = {
            "frontend": {
                "structure_html": {
                    "priorite": "moyenne",
                    "categorie": "html",
                    "conseil": "Utilisez davantage de balises sémantiques HTML5 pour améliorer l'accessibilité et le SEO.",
                },
                "css_responsive": {
                    "priorite": "moyenne",
                    "categorie": "css",
                    "conseil": "Adoptez une approche mobile-first avec des media queries pour un design responsive.",
                },
                "accessibilite": {
                    "priorite": "haute",
                    "categorie": "a11y",
                    "conseil": "Intégrez les attributs ARIA et respectez les normes WCAG pour l'accessibilité.",
                },
                "gestion_etat": {
                    "priorite": "haute",
                    "categorie": "architecture",
                    "conseil": f"Améliorez la gestion d'état dans votre application {framework} en centralisant la logique.",
                },
                "performance": {
                    "priorite": "moyenne",
                    "categorie": "optimisation",
                    "conseil": "Optimisez le chargement avec du code splitting et du lazy loading.",
                },
                "tests_ui": {
                    "priorite": "moyenne",
                    "categorie": "qualité",
                    "conseil": "Ajoutez des tests unitaires pour vos composants principaux.",
                },
                "composants": {
                    "priorite": "haute",
                    "categorie": "architecture",
                    "conseil": f"Refactorisez votre code en composants {framework} plus petits et réutilisables.",
                },
                "hooks": {
                    "priorite": "haute",
                    "categorie": "react",
                    "conseil": "Utilisez les hooks personnalisés pour factoriser la logique commune entre composants.",
                },
                "services": {
                    "priorite": "haute",
                    "categorie": "angular",
                    "conseil": "Utilisez l'injection de dépendances pour découpler les services des composants.",
                },
            },
            "backend": {
                "architecture": {
                    "priorite": "haute",
                    "categorie": "structure",
                    "conseil": f"Adoptez une architecture en couches plus claire pour votre application {framework}.",
                },
                "gestion_donnees": {
                    "priorite": "haute",
                    "categorie": "base de données",
                    "conseil": "Optimisez vos requêtes de base de données et utilisez des transactions.",
                },
                "api": {
                    "priorite": "moyenne",
                    "categorie": "interface",
                    "conseil": "Documentez votre API avec Swagger/OpenAPI et suivez les principes RESTful.",
                },
                "validation": {
                    "priorite": "haute",
                    "categorie": "sécurité",
                    "conseil": "Renforcez la validation des données entrantes côté serveur.",
                },
                "securite": {
                    "priorite": "haute",
                    "categorie": "sécurité",
                    "conseil": "Implémentez une authentification robuste et sécurisez vos endpoints.",
                },
                "tests": {
                    "priorite": "moyenne",
                    "categorie": "qualité",
                    "conseil": "Augmentez la couverture de tests unitaires pour vos services critiques.",
                },
            },
            "outil_dev": {
                "versioning": {
                    "priorite": "basse",
                    "categorie": "collaboration",
                    "conseil": "Améliorez la qualité de vos messages de commit et utilisez des branches fonctionnelles.",
                },
                "documentation": {
                    "priorite": "moyenne",
                    "categorie": "maintenabilité",
                    "conseil": "Documentez les fonctions et classes principales pour faciliter la maintenance.",
                },
                "tests_automatises": {
                    "priorite": "moyenne",
                    "categorie": "qualité",
                    "conseil": "Mettez en place des tests automatisés dans votre pipeline CI/CD.",
                },
            },
            "algorithmique": {
                "complexite": {
                    "priorite": "moyenne",
                    "categorie": "performance",
                    "conseil": "Revoyez la complexité de vos algorithmes pour améliorer les performances.",
                },
                "structures_donnees": {
                    "priorite": "moyenne",
                    "categorie": "performance",
                    "conseil": "Choisissez des structures de données plus adaptées à vos cas d'usage.",
                },
            },
        }

        return recs.get(domain, {}).get(category, None)

    @classmethod
    def classify_student(cls, global_score, acquis_evaluation):
        """Classifie l'étudiant en fonction de son score global et de ses acquis validés"""
        # Calculer le pourcentage d'acquis validés
        total_acquis = 0
        validated_acquis = 0

        for domain, categories in acquis_evaluation.items():
            for _, details in categories.items():
                total_acquis += 1
                if details.get("valide", False):
                    validated_acquis += 1

        acquis_percentage = (
            (validated_acquis / total_acquis) * 100 if total_acquis > 0 else 0
        )

        # Classification basée sur une combinaison du score global et des acquis validés
        final_score = (global_score * 0.6) + (acquis_percentage * 0.4)

        if final_score >= 80:
            return {
                "niveau": "excellent",
                "commentaire": "Maîtrise avancée du développement et des bonnes pratiques.",
            }
        elif final_score >= 65:
            return {
                "niveau": "bon",
                "commentaire": "Bonne compréhension des concepts et application correcte des pratiques.",
            }
        elif final_score >= 50:
            return {
                "niveau": "moyen",
                "commentaire": "Compréhension basique du développement avec des points à améliorer.",
            }
        else:
            return {
                "niveau": "faible",
                "commentaire": "Des lacunes importantes nécessitant un accompagnement renforcé.",
            }

    @classmethod
    def generate_note_range(cls, global_score, classification):
        """Génère une fourchette de note sur 20 en fonction du score global et de la classification"""
        base_note = global_score / 5  # Conversion du score sur 100 en note sur 20

        # Ajustement selon la classification
        if classification["niveau"] == "excellent":
            min_note = max(16, base_note - 1)
            max_note = min(20, base_note + 1)
        elif classification["niveau"] == "bon":
            min_note = max(12, base_note - 1)
            max_note = min(16, base_note + 1)
        elif classification["niveau"] == "moyen":
            min_note = max(8, base_note - 1)
            max_note = min(12, base_note + 1)
        else:
            min_note = max(0, base_note - 1)
            max_note = min(8, base_note + 1)

        return {"min": round(min_note, 1), "max": round(max_note, 1)}

    @classmethod
    def generate_feedback(cls, files_analyses, global_score, framework):
        """Génère un feedback pédagogique complet et dynamique"""
        # Évaluer les acquis
        acquis_evaluation = cls.evaluate_project(
            files_analyses, framework, global_score
        )

        # Générer des recommandations
        recommendations = cls.generate_dynamic_recommendations(
            acquis_evaluation, framework, global_score
        )

        # Classifier l'étudiant
        classification = cls.classify_student(global_score, acquis_evaluation)

        # Générer une fourchette de note
        note_range = cls.generate_note_range(global_score, classification)

        # Construire le rapport complet
        feedback = {
            "validation_acquis": acquis_evaluation,
            "recommandations": recommendations,
            "classification": classification,
            "note_suggeree": note_range,
            "conclusion": f"L'étudiant a {'validé' if classification['niveau'] in ['excellent', 'bon'] else 'partiellement validé' if classification['niveau'] == 'moyen' else 'non validé'} les acquis pédagogiques.",
        }

        return feedback
