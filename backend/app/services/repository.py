from pathlib import Path
from git import Repo


def clone_repository(repository_url: str, destination: str) -> dict:
    destination_path = Path(destination)

    if destination_path.exists() and any(destination_path.iterdir()):
        raise ValueError("Destination directory is not empty.")

    destination_path.mkdir(parents=True, exist_ok=True)

    Repo.clone_from(repository_url, destination_path)

    return {
        "repository_url": repository_url,
        "local_path": str(destination_path),
        "status": "cloned",
    }