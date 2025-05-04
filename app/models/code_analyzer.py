from transformers import pipeline, AutoTokenizer
from app.config import settings


class CodeAnalyzer:
    def __init__(self):
        self.codebert = pipeline(
            "text-classification", model=settings.MODEL_CONFIG["codebert"]
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            settings.MODEL_CONFIG["codellama"]
        )

    def analyze_code(self, code, framework):
        # Analyse avec CodeBERT
        codebert_result = self.codebert(code[: settings.MODEL_CONFIG["max_length"]])[0]

        # Analyse framework-spécifique
        prompt = self._generate_prompt(code, framework)
        analysis = self._codellama_analysis(prompt)

        return {
            "quality_score": codebert_result["score"],
            "framework_analysis": analysis,
        }

    def _generate_prompt(self, code, framework):
        return f"""
		[Étudiant] Analyse ce code {framework} :
		{code[: settings.MODEL_CONFIG["max_length"]]}
		
		Critères :
		{", ".join(settings.FRAMEWORK_RULES[framework])}
		"""

    def _codellama_analysis(self, prompt):
        # Implémentation simplifiée (à adapter)
        return {"score": 0.75, "details": "..."}
