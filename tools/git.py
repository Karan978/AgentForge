from __future__ import annotations

import difflib
import subprocess
from pathlib import Path

from tools.filesystem import IGNORED_DIRECTORIES


def _git(repo_path: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _is_ignored(relative_path: str) -> bool:
    return any(
        part in IGNORED_DIRECTORIES
        for part in Path(relative_path).parts
    )


def _untracked_files(repo_path: str) -> list[str]:
    """
    Untracked files that are not excluded by .gitignore or by
    IGNORED_DIRECTORIES.
    """

    result = _git(
        repo_path,
        "ls-files",
        "--others",
        "--exclude-standard",
    )

    if result.returncode != 0:
        return []

    return [
        line
        for line in result.stdout.splitlines()
        if line and not _is_ignored(line)
    ]


def _new_file_diff(repo_path: str, relative_path: str) -> str:
    path = Path(repo_path) / relative_path

    try:
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    except (UnicodeDecodeError, OSError):
        return f"Binary or unreadable new file: {relative_path}\n"

    return "".join(
        difflib.unified_diff(
            [],
            lines,
            fromfile="/dev/null",
            tofile=f"b/{relative_path}",
        )
    )


def git_diff(repo_path: str) -> str:
    """
    Return all changes in the working tree relative to HEAD:
    unstaged, staged, and new (untracked) files.

    The git index is not modified.
    """

    try:

        has_head = _git(
            repo_path, "rev-parse", "--verify", "HEAD"
        ).returncode == 0

        # `git diff HEAD` covers staged and unstaged changes together.
        # A repository with no commits has no HEAD, so fall back to the
        # staged diff against the empty tree.
        result = (
            _git(repo_path, "diff", "HEAD")
            if has_head
            else _git(repo_path, "diff", "--cached")
        )

        if result.returncode != 0:
            return (
                "Unable to obtain git diff:\n"
                + result.stderr
            )

        parts = [result.stdout] if result.stdout else []

        for relative_path in _untracked_files(repo_path):
            parts.append(_new_file_diff(repo_path, relative_path))

        return "\n".join(parts) or "No changes."

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


def working_tree_problem(repo_path: str) -> str | None:
    """
    Return a reason the repository cannot be used safely, or None if it
    is a git repository with a clean working tree.

    A clean starting point guarantees that every change in the final
    diff was made by the agents, and that it can be reverted.
    """

    try:
        result = _git(repo_path, "status", "--porcelain")
    except Exception as exc:
        return f"Could not run git: {exc}"

    if result.returncode != 0:
        return (
            f"{repo_path} is not a git repository "
            f"({result.stderr.strip()})."
        )

    dirty = [
        line
        for line in result.stdout.splitlines()
        if line and not _is_ignored(line[3:])
    ]

    if dirty:
        return (
            "The working tree has uncommitted changes. Commit or stash "
            "them first so the agents' changes are not mixed with yours:\n"
            + "\n".join(dirty)
        )

    return None
