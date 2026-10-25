import subprocess


def git_diff(repo_path: str) -> str:
    """
    Return the current git diff.
    """

    try:

        result = subprocess.run(
            ["git", "diff"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return (
                "Unable to obtain git diff:\n"
                + result.stderr
            )

        return result.stdout or "No changes."

    except Exception as exc:
        return f"Git diff failed: {exc}"


def git_status(repo_path: str) -> str:
    """
    Return git status.
    """

    try:

        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return result.stdout or "Working tree clean."

    except Exception as exc:
        return f"Git status failed: {exc}"