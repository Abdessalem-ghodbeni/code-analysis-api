import os
import glob


def detect_framework(project_path):
    config_files = {
        "react": ["package.json", "src/App.js"],
        "angular": ["angular.json", "src/app"],
        "springboot": ["pom.xml", "src/main/java"],
        "laravel": ["composer.json", "routes/web.php"],
    }

    for framework, files in config_files.items():
        if all(os.path.exists(os.path.join(project_path, f)) for f in files):
            return framework
    return "unknown"
