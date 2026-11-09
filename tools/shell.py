from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass


ALLOWED_COMMANDS = {
    "pytest",
    "python",
    "ruff",
}

# pytest exit codes: https://docs.pytest.org/en/stable/reference/exit-codes.html
PYTEST_EXIT_MESSAGES = {
    0: "All tests passed.",
    1: "Some tests failed.",
    2: "Test execution was interrupted.",
    3: "pytest hit an internal error.",
    4: "pytest was invoked incorrectly.",
    5: "No tests were collected.",
}


@dataclass
class TestRun:
    """
    Structured result of a test run.

    `exit_code` is None when the run timed out or could not start.
    """

    exit_code: int | None
    output: str

    @property
    def passed(self) -> bool:
        return self.exit_code == 0

    @property
    def no_tests(self) -> bool:
        return self.exit_code == 5

    def describe(self) -> str:
        if self.exit_code is None:
            return "Tests did not complete."
        return PYTEST_EXIT_MESSAGES.get(
            self.exit_code,
            f"pytest exited with code {self.exit_code}.",
        )

    def __str__(self) -> str:
        return (
            f"Exit code: {self.exit_code}\n"
            f"{self.describe()}\n\n"
            f"{self.output}"
        )


def run_command(
    command: str,
    repo_path: str,
    timeout: int = 60,
) -> str:
    """
    Execute a limited command inside the repository.
    """

    command_name = command.split()[0]

    if command_name not in ALLOWED_COMMANDS:
        return (
            f"Command '{command_name}' is not allowed."
        )

    try:

        result = subprocess.run(
            command,
            cwd=repo_path,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        return (
            f"Exit code: {result.returncode}\n\n"
            f"{output}"
        )

    except subprocess.TimeoutExpired:
        return (
            f"Command timed out after {timeout} seconds."
        )

    except Exception as exc:
        return f"Command failed: {exc}"


def run_tests(
    repo_path: str,
    timeout: int = 300,
) -> TestRun:
    """
    Run the repository's pytest suite and return a structured result.

    Pass/fail is decided by pytest's exit code, never by searching the
    output text. The cache provider and bytecode writing are disabled so
    the run does not leave `.pytest_cache/` or `__pycache__/` in the repo.
    """

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

    except subprocess.TimeoutExpired:
        return TestRun(
            None,
            f"Tests timed out after {timeout} seconds.",
        )

    except Exception as exc:
        return TestRun(None, f"Could not run tests: {exc}")

    return TestRun(
        result.returncode,
        result.stdout + "\n" + result.stderr,
    )
