import os
import glob
import fnmatch
from app.config import settings


def get_code_files(project_path):
    files = []
    for file in glob.glob(f"{project_path}/**/*", recursive=True):
        if not os.path.isfile(file):
            continue

        # Exclusion stricte des assets et dépendances
        ignore_patterns = [
            "**/assets/**/*",
            "**/static/**/*",
            "**/vendor/**/*",
            "**/node_modules/**/*",
            "**/*.min.*",
            "**/*.html",  # Exclure les templates HTML
        ]

        if any(fnmatch.fnmatch(file, p) for p in ignore_patterns):
            continue

        ext = os.path.splitext(file)[1].lower()
        if ext in settings.VALID_EXTENSIONS:
            files.append(file)

    return files
