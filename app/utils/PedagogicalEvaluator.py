from app.config import settings


class PedagogicalEvaluator:
    @staticmethod
    def generate_feedback(global_score, framework):
        feedback = {"validation_acquis": {}, "recommandations": []}

        # Évaluation frontend
        if framework in ["react", "angular"]:
            frontend_status = global_score >= 65
            feedback["validation_acquis"]["frontend"] = {
                "score": global_score,
                "valide": frontend_status,
                "commentaire": "Maîtrise des concepts frontend"
                if frontend_status
                else "Manque de maîtrise des composants et de l'état",
            }

        # Évaluation backend
        if framework in ["springboot", "laravel"]:
            backend_status = global_score >= 60
            feedback["validation_acquis"]["backend"] = {
                "score": global_score,
                "valide": backend_status,
                "commentaire": "Architecture backend solide"
                if backend_status
                else "Problèmes de structure API/BDD",
            }

        # Recommandations génériques
        if global_score < 50:
            feedback["recommandations"].append(
                "Revoir les fondamentaux du développement web"
            )
        elif global_score < 70:
            feedback["recommandations"].append("Améliorer l'architecture et les tests")

        return feedback
