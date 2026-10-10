from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
}


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rs",
}


def discover_source_files(repository_path: str) -> list[dict]:
    root = Path(repository_path)

    if not root.exists():
        raise FileNotFoundError("Repository does not exist.")

    files = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        files.append(
            {
                "path": str(path.relative_to(root)),
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
            }
        )

    return files