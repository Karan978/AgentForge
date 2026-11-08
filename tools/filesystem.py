from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}


def list_files(repo_path: str) -> str:
    """
    Return a readable list of files in the repository.
    """

    root = Path(repo_path)

    if not root.exists():
        return f"Repository does not exist: {repo_path}"

    files = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        if any(
            ignored in path.parts
            for ignored in IGNORED_DIRECTORIES
        ):
            continue

        relative_path = path.relative_to(root)

        files.append(str(relative_path))

    files.sort()

    if not files:
        return "No files found."

    return "\n".join(files)


def read_file(
    repo_path: str,
    file_path: str,
) -> str:
    """
    Read a file inside the repository.
    """

    root = Path(repo_path).resolve()
    target = (root / file_path).resolve()

    # Prevent path traversal.
    if root not in target.parents and target != root:
        return "Error: file is outside repository."

    if not target.exists():
        return f"File does not exist: {file_path}"

    if not target.is_file():
        return f"Not a file: {file_path}"

    try:
        return target.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        return (
            f"Could not decode {file_path} as UTF-8."
        )


def write_file(
    repo_path: str,
    file_path: str,
    content: str,
) -> str:
    """
    Write content to a repository file.

    The developer agent uses this tool to modify code.
    """

    root = Path(repo_path).resolve()
    target = (root / file_path).resolve()

    # Prevent path traversal.
    if root not in target.parents and target != root:
        return "Error: file is outside repository."

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        content,
        encoding="utf-8",
    )

    return f"Successfully wrote {file_path}"