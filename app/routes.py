from flask import request, jsonify
import logging
import os
from app.models.code_analyzer import CodeAnalyzer
from app.utils.project_detector import detect_framework
from app.utils.file_parser import get_code_files  # Nouveau module à créer

# Configure le logging
logger = logging.getLogger(__name__)


def init_routes(app):
    analyzer = CodeAnalyzer()

    @app.route("/analyze", methods=["POST"])
    def analyze_project():
        # Vérification basique des entrées
        if not request.json or "project_path" not in request.json:
            return jsonify({"error": "project_path est requis"}), 400

        project_path = request.json["project_path"]

        # Vérification de l'existence du chemin
        if not os.path.exists(project_path):
            return jsonify({"error": "Chemin du projet introuvable"}), 404

        # Détection du framework
        try:
            framework = detect_framework(project_path)
        except Exception as e:
            logger.error(f"Erreur détection framework: {str(e)}")
            return jsonify({"error": "Échec de la détection du framework"}), 500

        # Récupération des fichiers valides
        try:
            files = get_code_files(project_path)
        except Exception as e:
            logger.error(f"Erreur lecture fichiers: {str(e)}")
            return jsonify({"error": "Échec de l'analyse des fichiers"}), 500

        if not files:
            return jsonify({"error": "Aucun fichier source valide détecté"}), 400

        # Analyse des fichiers
        results = []
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    code = f.read()

                # Analyse du code
                analysis = analyzer.analyze_code(code, framework)
                results.append(
                    {"file": os.path.relpath(file, project_path), "analysis": analysis}
                )

            except UnicodeDecodeError:
                logger.warning(f"Fichier binaire ignoré: {file}")
                continue
            except Exception as e:
                logger.error(f"Erreur analyse {file}: {str(e)}")
                continue

        return jsonify(
            {"framework": framework, "files_analyzed": len(results), "results": results}
        )
