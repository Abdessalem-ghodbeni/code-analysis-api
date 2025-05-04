MODEL_CONFIG = {
    "codebert": "microsoft/codebert-base",
    "codellama": "codellama/CodeLlama-7b-hf",
    "max_length": 512,
    "thresholds": {"excellent": 0.8, "good": 0.6, "poor": 0.4},
}

FRAMEWORK_RULES = {
    "react": ["useState", "useEffect", "props", "components"],
    "springboot": ["@RestController", "@Service", "@Repository"],
    "angular": ["@Component", "@Injectable", "RxJS"],
}
BLACKLISTED_FILES = [
    # Fichiers images
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.ico",
    "*.svg",
    # Fichiers binaires
    "*.pdf",
    "*.docx",
    "*.exe",
    "*.dll",
    "*.bin",
    # Archives
    "*.zip",
    "*.tar.gz",
    "*.rar",
    # Dépendances
    "package-lock.json",
    "yarn.lock",
    "*.min.js",
]

VALID_EXTENSIONS = [
    ".js",
    ".jsx",
    ".ts",
    ".tsx",  # JavaScript/TypeScript
    ".java",
    ".kt",
    ".scala",  # JVM
    ".py",  # Python
    ".php",  # PHP
    ".html",
    ".css",
    ".scss",  # Web
]
