from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
import re
from app.config import settings
from collections import defaultdict


class CodeAnalyzer:
    def __init__(self):
        self.codebert = pipeline(
            "text-classification", model=settings.MODEL_CONFIG["codebert"]
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            settings.MODEL_CONFIG["codellama"]
        )

        # Patterns de code courants par langage pour une analyse plus précise
        self.language_patterns = {
            "javascript": {
                "quality": [
                    "const",
                    "let",
                    "async/await",
                    "try/catch",
                    "destructuring",
                ],
                "bad_practices": ["var ", "eval(", "==", "with("],
                "tests": ["describe(", "it(", "test(", "expect(", "assert"],
                "frameworks": {
                    "react": ["useState", "useEffect", "jsx", "<Component", "props"],
                    "angular": ["@Component", "@Injectable", "ngOnInit"],
                },
            },
            "typescript": {
                "quality": ["interface", "type", "readonly", "private", "public"],
                "bad_practices": ["any", "as any", "// @ts-ignore"],
                "tests": ["describe(", "it(", "test(", "expect(", "assert"],
            },
            "java": {
                "quality": ["@Override", "final", "private", "try/catch", "interface"],
                "bad_practices": ["catch(Exception", "public static void main"],
                "tests": ["@Test", "assertEquals", "assertTrue", "assertFalse"],
                "frameworks": {
                    "springboot": [
                        "@RestController",
                        "@Service",
                        "@Autowired",
                        "@Repository",
                    ]
                },
            },
            "python": {
                "quality": ["def", "class", "try/except", "with open", "if __name__"],
                "bad_practices": ["except:", "global ", "exec("],
                "tests": ["def test_", "assert", "unittest", "pytest"],
                "frameworks": {
                    "flask": ["@app.route", "request.", "jsonify", "Blueprint"],
                    "django": ["models.", "views.", "@login_required"],
                },
            },
            "html": {
                "quality": [
                    "<!DOCTYPE html>",
                    "<html lang=",
                    "meta name=",
                    "semantic tags",
                ],
                "bad_practices": ["<font>", "<center>", "style='", "onclick="],
                "accessibility": ["aria-", "role=", "alt=", "tabindex="],
            },
            "css": {
                "quality": ["@media", "rem", "em", "display: flex", "display: grid"],
                "bad_practices": ["!important", "*{", "position: absolute"],
            },
        }

        # Métriques de code à analyser
        self.code_metrics = {
            "complexity": {
                "patterns": ["for", "while", "if", "else", "switch", "case", "?"],
                "threshold": 15,  # Nombre max de structures de contrôle par fonction
            },
            "function_length": {
                "max_lines": 30  # Nombre max de lignes par fonction
            },
            "naming": {
                "camelCase": r"[a-z][a-zA-Z0-9]*",
                "snake_case": r"[a-z][a-z0-9_]*",
                "PascalCase": r"[A-Z][a-zA-Z0-9]*",
            },
        }

        # Critères d'évaluation par framework
        self.framework_criteria = {
            "react": {
                "component_structure": ["function", "props", "return", "jsx"],
                "state_management": ["useState", "useReducer", "useContext"],
                "effects": ["useEffect", "useLayoutEffect", "useMemo", "useCallback"],
                "routing": ["useNavigate", "useParams", "Routes", "Route"],
                "props_validation": ["PropTypes", "defaultProps", "isRequired"],
                "tests": ["render", "screen", "fireEvent", "waitFor"],
            },
            "angular": {
                "component_structure": ["@Component", "selector", "template", "styles"],
                "state_management": ["@Input", "@Output", "EventEmitter", "ngOnInit"],
                "services": [
                    "@Injectable",
                    "providedIn",
                    "constructor",
                    "dependency injection",
                ],
                "directives": ["@Directive", "*ngIf", "*ngFor", "[ngClass]"],
                "rxjs": ["Observable", "Subject", "pipe", "subscribe", "unsubscribe"],
                "tests": ["TestBed", "ComponentFixture", "inject", "compileComponents"],
            },
            "springboot": {
                "rest_api": [
                    "@RestController",
                    "@GetMapping",
                    "@PostMapping",
                    "@PutMapping",
                ],
                "data_layer": ["@Repository", "JpaRepository", "CrudRepository"],
                "service_layer": ["@Service", "@Autowired", "dependency injection"],
                "configuration": [
                    "@Configuration",
                    "@Bean",
                    "application.properties",
                    "application.yml",
                ],
                "security": ["@PreAuthorize", "SecurityContext", "Authentication"],
                "tests": ["@Test", "MockMvc", "when", "thenReturn"],
            },
            "laravel": {
                "mvc": ["extends Controller", "Model", "Blade", "view("],
                "routing": ["Route::get", "Route::post", "Route::resource"],
                "orm": ["Eloquent", "migrations", "relationships", "$fillable"],
                "auth": ["Auth::", "middleware", "guards", "policies"],
                "validation": ["Validator::", "$request->validate", "FormRequest"],
                "tests": ["PHPUnit", "Feature", "Unit", "assertStatus"],
            },
        }

    def detect_language(self, file_path, code):
        """Détecte le langage de programmation basé sur l'extension et le contenu"""
        ext = os.path.splitext(file_path)[1].lower() if file_path else ""

        language_map = {
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".py": "python",
            ".html": "html",
            ".css": "css",
            ".scss": "css",
        }

        # Détection par extension
        if ext in language_map:
            return language_map[ext]

        # Détection par contenu si extension non reconnue
        if "import React" in code or "useState" in code:
            return "javascript"
        if "def " in code and ":" in code:
            return "python"
        if "class " in code and "{" in code and "}" in code:
            return "java"
        if "<!DOCTYPE html>" in code or "<html" in code:
            return "html"

        # Par défaut
        return "unknown"

    def analyze_code_metrics(self, code, language):
        """Analyse les métriques de qualité de code"""
        metrics = {}

        # Analyse de la longueur des fonctions
        if language in ["javascript", "typescript", "java", "python"]:
            # Extraction des fonctions basée sur le langage
            if language in ["javascript", "typescript"]:
                # Regex simplifiée pour JS/TS
                functions = re.findall(
                    r"(function\s+\w+\s*\(.*?\)\s*\{[\s\S]*?\})", code
                )
                # Ajouter les fonctions fléchées et méthodes de classe
                functions += re.findall(
                    r"(const\s+\w+\s*=\s*(?:\(.*?\)|\w+)\s*=>\s*\{[\s\S]*?\})", code
                )
                functions += re.findall(r"(\w+\s*\(.*?\)\s*\{[\s\S]*?\})", code)
            elif language == "python":
                # Extraction simplifiée des fonctions Python
                functions = re.findall(
                    r"(def\s+\w+\s*\(.*?\):\s*(?:[\s\S]*?)(?:\n\S|\Z))", code
                )
            elif language == "java":
                # Extraction simplifiée des méthodes Java
                functions = re.findall(
                    r"(\w+(?:\s+\w+)*\s+\w+\s*\(.*?\)\s*\{[\s\S]*?\})", code
                )

            # Analyse des fonctions trouvées
            if functions:
                long_functions = 0
                complex_functions = 0

                for func in functions:
                    lines = func.count("\n") + 1
                    if lines > self.code_metrics["function_length"]["max_lines"]:
                        long_functions += 1

                    complexity = 0
                    for pattern in self.code_metrics["complexity"]["patterns"]:
                        complexity += len(re.findall(r"\b" + pattern + r"\b", func))

                    if complexity > self.code_metrics["complexity"]["threshold"]:
                        complex_functions += 1

                total_functions = len(functions)
                metrics["function_metrics"] = {
                    "total_functions": total_functions,
                    "long_functions": long_functions,
                    "complex_functions": complex_functions,
                    "long_functions_percent": round(
                        (long_functions / total_functions) * 100, 1
                    )
                    if total_functions > 0
                    else 0,
                    "complex_functions_percent": round(
                        (complex_functions / total_functions) * 100, 1
                    )
                    if total_functions > 0
                    else 0,
                }

        # Analyse des conventions de nommage
        if language in ["javascript", "typescript", "java", "python"]:
            # Analyse des variables/fonctions selon les conventions du langage
            if language in ["javascript", "typescript"]:
                # Variables et fonctions en camelCase
                variables = re.findall(r"\b(let|const|var)\s+(\w+)", code)
                functions = re.findall(r"\bfunction\s+(\w+)", code) + re.findall(
                    r"\bconst\s+(\w+)\s*=\s*(?:function|\()", code
                )
                camel_case_pattern = re.compile(
                    self.code_metrics["naming"]["camelCase"]
                )

                valid_vars = sum(
                    1
                    for _, var_name in variables
                    if camel_case_pattern.fullmatch(var_name)
                )
                valid_funcs = sum(
                    1
                    for func_name in functions
                    if camel_case_pattern.fullmatch(func_name)
                )

                total_vars = len(variables)
                total_funcs = len(functions)

                metrics["naming_conventions"] = {
                    "valid_variables_percent": round((valid_vars / total_vars) * 100, 1)
                    if total_vars > 0
                    else 100,
                    "valid_functions_percent": round(
                        (valid_funcs / total_funcs) * 100, 1
                    )
                    if total_funcs > 0
                    else 100,
                }
            elif language == "python":
                # Variables et fonctions en snake_case
                variables = re.findall(r"\b(\w+)\s*=", code)
                functions = re.findall(r"\bdef\s+(\w+)", code)
                snake_case_pattern = re.compile(
                    self.code_metrics["naming"]["snake_case"]
                )

                valid_vars = sum(
                    1
                    for var_name in variables
                    if snake_case_pattern.fullmatch(var_name)
                )
                valid_funcs = sum(
                    1
                    for func_name in functions
                    if snake_case_pattern.fullmatch(func_name)
                )

                total_vars = len(variables)
                total_funcs = len(functions)

                metrics["naming_conventions"] = {
                    "valid_variables_percent": round((valid_vars / total_vars) * 100, 1)
                    if total_vars > 0
                    else 100,
                    "valid_functions_percent": round(
                        (valid_funcs / total_funcs) * 100, 1
                    )
                    if total_funcs > 0
                    else 100,
                }

        # Analyse des patterns de qualité spécifiques au langage
        if language in self.language_patterns:
            quality_score = 0
            bad_practices_score = 0
            patterns_found = []
            bad_practices_found = []

            # Recherche de bonnes pratiques
            for pattern in self.language_patterns[language].get("quality", []):
                if pattern in code:
                    quality_score += 1
                    patterns_found.append(pattern)

            # Recherche de mauvaises pratiques
            for pattern in self.language_patterns[language].get("bad_practices", []):
                if pattern in code:
                    bad_practices_score += 1
                    bad_practices_found.append(pattern)

            total_quality = len(self.language_patterns[language].get("quality", []))
            total_bad = len(self.language_patterns[language].get("bad_practices", []))

            if total_quality > 0:
                metrics["quality_patterns"] = {
                    "score": round((quality_score / total_quality) * 100, 1),
                    "patterns_found": patterns_found,
                }

            if total_bad > 0:
                metrics["bad_practices"] = {
                    "score": round(
                        ((total_bad - bad_practices_score) / total_bad) * 100, 1
                    ),
                    "patterns_found": bad_practices_found,
                }

        return metrics

    def analyze_framework_specific(self, code, framework, language):
        """Analyse le code selon les critères spécifiques au framework"""
        if framework not in self.framework_criteria:
            return {}

        results = {}

        # Pour chaque critère spécifique au framework
        for criterion, patterns in self.framework_criteria[framework].items():
            matches = 0
            patterns_found = []

            for pattern in patterns:
                if pattern in code:
                    matches += 1
                    patterns_found.append(pattern)

            # Calcul d'un score proportionnel au nombre de patterns trouvés
            if patterns:  # Éviter division par zéro
                confidence = min(
                    1.0, matches / (len(patterns) * 0.7)
                )  # 70% des patterns = confiance max
                results[criterion] = {
                    "score": round(confidence * 100, 1),
                    "patterns_found": patterns_found,
                    "evaluation": "Good"
                    if confidence > 0.7
                    else "Average"
                    if confidence > 0.4
                    else "Needs improvement",
                }

        # Ajouter un score global de conformité au framework
        total_score = sum(item["score"] for item in results.values())
        if results:
            results["framework_conformity"] = round(total_score / len(results), 1)

        return results

    def analyze_code(self, code, framework, file_path=None):
        """Analyse complète du code avec plusieurs métriques et spécificités framework"""
        # Limiter la taille du code à analyser
        truncated_code = code[: settings.MODEL_CONFIG["max_length"]]

        # Détecter le langage
        language = self.detect_language(file_path, truncated_code)

        # Analyse avec CodeBERT pour une évaluation générale de la qualité
        codebert_result = self.codebert(truncated_code)[0]

        # Analyse des métriques de code
        metrics = self.analyze_code_metrics(truncated_code, language)

        # Analyse spécifique au framework
        framework_analysis = self.analyze_framework_specific(
            truncated_code, framework, language
        )

        # Calcul du score global basé sur plusieurs facteurs
        global_score = codebert_result["score"]

        # Ajuster le score en fonction des métriques de code
        if "function_metrics" in metrics:
            # Pénaliser les fonctions trop longues et complexes
            long_func_penalty = (
                metrics["function_metrics"]["long_functions_percent"] / 200
            )  # Max 0.5 de pénalité
            complex_func_penalty = (
                metrics["function_metrics"]["complex_functions_percent"] / 200
            )  # Max 0.5 de pénalité
            global_score = max(
                0.1, global_score - long_func_penalty - complex_func_penalty
            )

        if "naming_conventions" in metrics:
            # Pénaliser le non-respect des conventions de nommage
            naming_penalty = (
                200
                - metrics["naming_conventions"]["valid_variables_percent"]
                - metrics["naming_conventions"]["valid_functions_percent"]
            ) / 400  # Max 0.5 de pénalité
            global_score = max(0.1, global_score - naming_penalty)

        # Ajuster le score en fonction des bonnes/mauvaises pratiques
        if "quality_patterns" in metrics:
            quality_bonus = (
                metrics["quality_patterns"]["score"] / 100
            ) * 0.2  # Max 0.2 de bonus
            global_score = min(1.0, global_score + quality_bonus)

        if "bad_practices" in metrics:
            bad_practices_penalty = (
                (100 - metrics["bad_practices"]["score"]) / 100 * 0.3
            )  # Max 0.3 de pénalité
            global_score = max(0.1, global_score - bad_practices_penalty)

        # Compiler les résultats
        result = {
            "language": language,
            "quality_score": global_score,
            "quality_label": self.get_quality_label(global_score),
            "metrics": metrics,
            "framework_analysis": framework_analysis,
        }

        # Générer des suggestions d'amélioration
        result["suggestions"] = self.generate_suggestions(result)

        return result

    def get_quality_label(self, score):
        """Convertit le score en une étiquette descriptive"""
        thresholds = settings.MODEL_CONFIG["thresholds"]

        if score >= thresholds["excellent"]:
            return "excellent"
        elif score >= thresholds["good"]:
            return "good"
        elif score >= thresholds["poor"]:
            return "average"
        else:
            return "poor"

    def generate_suggestions(self, analysis_result):
        """Génère des suggestions d'amélioration basées sur l'analyse"""
        suggestions = []

        # Suggestions basées sur les métriques de fonction
        if (
            "metrics" in analysis_result
            and "function_metrics" in analysis_result["metrics"]
        ):
            func_metrics = analysis_result["metrics"]["function_metrics"]

            if func_metrics["long_functions_percent"] > 20:
                suggestions.append(
                    {
                        "category": "structure",
                        "severity": "medium",
                        "message": f"Réduisez la taille de vos fonctions en les décomposant. {func_metrics['long_functions_percent']}% de vos fonctions sont trop longues.",
                    }
                )

            if func_metrics["complex_functions_percent"] > 20:
                suggestions.append(
                    {
                        "category": "complexity",
                        "severity": "high",
                        "message": f"Simplifiez la logique de vos fonctions complexes. {func_metrics['complex_functions_percent']}% de vos fonctions ont une complexité excessive.",
                    }
                )

        # Suggestions basées sur les conventions de nommage
        if (
            "metrics" in analysis_result
            and "naming_conventions" in analysis_result["metrics"]
        ):
            naming = analysis_result["metrics"]["naming_conventions"]

            if naming["valid_variables_percent"] < 80:
                suggestions.append(
                    {
                        "category": "convention",
                        "severity": "low",
                        "message": f"Suivez les conventions de nommage pour les variables. Seulement {naming['valid_variables_percent']}% de vos variables respectent les conventions.",
                    }
                )

            if naming["valid_functions_percent"] < 80:
                suggestions.append(
                    {
                        "category": "convention",
                        "severity": "low",
                        "message": f"Suivez les conventions de nommage pour les fonctions. Seulement {naming['valid_functions_percent']}% de vos fonctions respectent les conventions.",
                    }
                )

        # Suggestions basées sur les bonnes pratiques
        if (
            "metrics" in analysis_result
            and "quality_patterns" in analysis_result["metrics"]
        ):
            quality = analysis_result["metrics"]["quality_patterns"]

            if quality["score"] < 60:
                suggestions.append(
                    {
                        "category": "best_practices",
                        "severity": "medium",
                        "message": f"Améliorez l'utilisation des bonnes pratiques pour {analysis_result['language']}. Score actuel: {quality['score']}%.",
                    }
                )

        # Suggestions basées sur les mauvaises pratiques
        if (
            "metrics" in analysis_result
            and "bad_practices" in analysis_result["metrics"]
        ):
            bad = analysis_result["metrics"]["bad_practices"]

            if bad["score"] < 70:
                suggestions.append(
                    {
                        "category": "bad_practices",
                        "severity": "high",
                        "message": f"Éliminez les mauvaises pratiques détectées: {', '.join(bad['patterns_found'][:3])}",
                    }
                )

        # Suggestions basées sur l'analyse du framework
        if (
            "framework_analysis" in analysis_result
            and "framework_conformity" in analysis_result["framework_analysis"]
        ):
            framework_score = analysis_result["framework_analysis"][
                "framework_conformity"
            ]

            if framework_score < 50:
                suggestions.append(
                    {
                        "category": "framework",
                        "severity": "high",
                        "message": f"Améliorez votre utilisation du framework {analysis_result.get('framework', 'détecté')}. Score de conformité: {framework_score}%.",
                    }
                )

            # Suggestions pour des critères spécifiques du framework
            for criterion, details in analysis_result["framework_analysis"].items():
                if (
                    criterion != "framework_conformity"
                    and isinstance(details, dict)
                    and details.get("score", 100) < 40
                ):
                    suggestions.append(
                        {
                            "category": "framework_specific",
                            "severity": "medium",
                            "message": f"Améliorez l'utilisation de '{criterion}' dans votre code {analysis_result.get('framework', 'détecté')}.",
                        }
                    )

        # Limiter le nombre de suggestions
        return suggestions[:5]

    def _generate_prompt(self, code, framework):
        """Génère un prompt pour l'analyse avec CodeLlama"""
        return f"""
		[Analyse de Code] Évaluez ce code {framework} :
		{code[:1000]}...
		
		Critères d'évaluation :
		- Structure et organisation du code
		- Utilisation des bonnes pratiques {framework}
		- Qualité et lisibilité
		- Points forts et axes d'amélioration
		"""

    def _codellama_analysis(self, prompt):
        """Analyse le code avec CodeLlama"""
        # Cette implémentation est simplifiée
        # Dans une version réelle, il faudrait intégrer l'API de CodeLlama ou un modèle local

        # Pour l'instant, retournons une évaluation fictive
        return {
            "score": 0.75,
            "strengths": ["Structure claire", "Bonnes pratiques"],
            "weaknesses": ["Complexité élevée", "Tests manquants"],
            "recommendations": [
                "Ajouter des tests unitaires",
                "Refactoriser les fonctions complexes",
            ],
        }
