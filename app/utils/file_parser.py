import os
import glob
import fnmatch
from app.config import settings


def get_code_files(project_path):
    files = []
    for file in glob.glob(f"{project_path}/**/*", recursive=True):
        if not os.path.isfile(file):
            continue

        # Vérifier la liste noire
        if any(
            fnmatch.fnmatch(file, pattern) for pattern in settings.BLACKLISTED_FILES
        ):
            continue

        # Vérifier les extensions valides
        ext = os.path.splitext(file)[1].lower()
        if ext in settings.VALID_EXTENSIONS:
            files.append(file)

    return files
