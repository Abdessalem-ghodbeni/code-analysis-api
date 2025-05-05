from flask import request, jsonify
import logging
import os
from app.models.code_analyzer import CodeAnalyzer
from app.utils.project_detector import detect_framework
from app.utils.file_parser import get_code_files
from app.config import settings

logger = logging.getLogger(__name__)


class PedagogicalEvaluator:
    @staticmethod
    def generate_feedback(global_score, framework):
        """Génère un feedback structuré basé sur le score global et le framework"""
        feedback = {"competences": {}, "recommandations": []}

        # Évaluation générique
        feedback["global"] = {
            "score": global_score,
            "niveau": "Acquis validés"
            if global_score >= 70
            else "Acquis partiellement validés"
            if global_score >= 50
            else "Acquis non validés",
        }

        # Évaluation framework-spécifique
        if framework == "angular":
            feedback["competences"]["frontend"] = {
                "commentaire": "Maîtrise des composants Angular"
                if global_score >= 65
                else "Problèmes de structure des composants",
                "elements_verifies": [
                    "Utilisation des décorateurs @Component",
                    "Gestion des services injectables",
                    "Routing Angular",
                ],
            }
        elif framework == "react":
            feedback["competences"]["frontend"] = {
                "commentaire": "Bon usage des hooks React"
                if global_score >= 65
                else "Gestion d'état améliorable",
                "elements_verifies": [
                    "Utilisation de useState/useEffect",
                    "Structure des composants",
                    "Gestion des props",
                ],
            }

        # Recommandations pédagogiques
        if global_score < 50:
            feedback["recommandations"].append(
                "Revoyez les fondamentaux de la programmation web"
            )
            feedback["recommandations"].append(
                "Pratiquez les exercices de validation sur les hooks/componentes"
            )
        elif global_score < 70:
            feedback["recommandations"].append(
                "Améliorez l'architecture globale de l'application"
            )
            feedback["recommandations"].append("Ajoutez des tests unitaires de base")

        return feedback


def init_routes(app):
    analyzer = CodeAnalyzer()

    @app.route("/analyze", methods=["POST"])
    def analyze_project():
        try:
            # Validation de la requête
            if not request.json or "project_path" not in request.json:
                return jsonify(
                    {
                        "error": "Paramètre manquant",
                        "message": "Le chemin 'project_path' est requis",
                    }
                ), 400

            project_path = request.json["project_path"]
            logger.info(f"Début analyse pour : {project_path}")

            # Vérification du projet
            if not os.path.exists(project_path):
                return jsonify(
                    {
                        "error": "Projet introuvable",
                        "conseil": "Vérifiez le chemin et les permissions",
                    }
                ), 404

            # Détection du framework
            try:
                framework = detect_framework(project_path)
                if framework == "unknown":
                    return jsonify(
                        {
                            "error": "Framework non reconnu",
                            "conseil": "Structure du projet non conforme aux standards",
                        }
                    ), 400
            except Exception as e:
                logger.error(f"Erreur détection framework : {str(e)}")
                return jsonify({"error": "Échec détection framework"}), 500

            # Récupération fichiers pertinents
            try:
                files = get_code_files(project_path)
                if not files:
                    return jsonify(
                        {
                            "error": "Aucun code source analysable",
                            "conseil": "Vérifiez les exclusions dans file_parser.py",
                        }
                    ), 400
            except Exception as e:
                logger.error(f"Erreur lecture fichiers : {str(e)}")
                return jsonify({"error": "Échec lecture fichiers"}), 500

            # Analyse des fichiers
            total_score = 0
            problem_files = []
            results = []

            for index, file in enumerate(files, 1):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        code = f.read()

                    analysis = analyzer.analyze_code(code, framework)
                    file_score = analysis["quality_score"]
                    total_score += file_score

                    # Enregistrement fichiers problématiques
                    if file_score < settings.MODEL_CONFIG["thresholds"]["good"]:
                        problem_files.append(
                            {
                                "file": os.path.relpath(file, project_path),
                                "score": round(file_score * 100, 1),
                                "details": analysis.get("framework_analysis", {}),
                            }
                        )

                    results.append(analysis)

                    # Log de progression
                    if index % 10 == 0:
                        logger.info(
                            f"Analyse en cours : {index}/{len(files)} fichiers traités"
                        )

                except Exception as e:
                    logger.error(f"Erreur analyse {file} : {str(e)}")
                    continue

            # Calcul score global
            global_score = round((total_score / len(files)) * 100, 1) if files else 0

            # Génération feedback pédagogique
            feedback = PedagogicalEvaluator.generate_feedback(global_score, framework)

            # Construction réponse finale
            response = {
                "framework": framework,
                "statistiques": {
                    "fichiers_analyses": len(files),
                    "fichiers_problematiques": len(problem_files),
                    "score_global": global_score,
                },
                "evaluation_pedagogique": feedback,
                "fichiers_critiques": sorted(problem_files, key=lambda x: x["score"])[
                    :5
                ],
            }

            logger.info("Analyse terminée avec succès")
            return jsonify(response)

        except Exception as e:
            logger.error(f"ERREUR GLOBALE : {str(e)}", exc_info=True)
            return jsonify(
                {
                    "error": "Erreur interne",
                    "message": "Échec du traitement de la requête",
                }
            ), 500
