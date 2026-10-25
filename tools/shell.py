import subprocess


ALLOWED_COMMANDS = {
    "pytest",
    "python",
    "ruff",
}


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