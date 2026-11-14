# AgentForge

**An experimental multi-agent AI system for software engineering workflows.**

AgentForge is a Python project exploring how specialized AI agents can collaborate to support software development tasks, from code analysis and implementation to quality assurance.

The project aims to organize these responsibilities into a modular, coordinated workflow rather than relying on a single component to handle every stage.

> **Project status:** Work in progress. Features and integrations are being developed incrementally.

## Objectives

- **Code analysis:** Identify potential issues and understand existing code.
- **Code development:** Assist with implementing features and modifying existing code.
- **Quality assurance:** Run tests and review code changes for potential defects.
- **Workflow orchestration:** Coordinate tasks and pass relevant information between components.
- **Modular design:** Keep agent logic, workflow state, tools, and prompts separate and maintainable.

These are project objectives; individual capabilities will be documented as they become implemented and tested.


### Components

| Component | Responsibility |
|---|---|
| `agents/analyst.py` | Code analysis and issue identification |
| `agents/developer.py` | Code implementation and modification |
| `agents/qa.py` | Quality checks and test-oriented review |
| `graph/state.py` | Shared state for workflow execution |
| `graph/workflow.py` | Coordination and orchestration of workflow steps |
| `requirements.txt` | Python project dependencies |

The architecture may evolve as the system grows.

## Technology Stack

- **Language:** Python
- **AI integrations and orchestration:** Under development

Frameworks, model providers, and additional tools will be documented as they are integrated into the project.

## Getting Started

### Prerequisites

- Python version compatible with the project's dependencies
- API credentials for any external model providers used by the implementation

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/AgentForge.git
cd AgentForge
```

Create a virtual environment.

**Windows (Git Bash):**

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

### Configuration

AgentForge needs an OpenAI API key. Put it in the `.env` file in the project folder:

```
OPENAI_API_KEY=sk-...
```

If `.env` is missing, create it by copying the template:

```bash
cp .env.example .env
```

On Windows Command Prompt or Anaconda Prompt, use `copy .env.example .env`.

- `.env` is listed in `.gitignore`, so it is never committed. `.env.example` is committed and must never contain a real key.
- An `OPENAI_API_KEY` environment variable, if set, takes precedence over `.env`.
- The key is not passed to the target repository's tests when they run.

Never commit API keys, passwords, or other secrets to version control.

### Running the Project

AgentForge works on a **local folder** that is a git repository. It does not accept a git URL and does not clone, download, or copy anything. To work on a remote repository, clone it first and pass the local path.

#### Requirements for the target repository

- **It is a git repository** with at least one commit. Pass its top-level folder, the one that contains `.git`.
- **Its working tree is clean.** Commit or stash your changes first. AgentForge refuses to start otherwise, so that the final diff contains only the agents' changes and can be reverted.
- **Its dependencies are installed in the same Python environment as AgentForge.** Tests run with `python -m pytest` using AgentForge's interpreter.
- **Git is installed and on your `PATH`.**

#### Usage

```bash
python main.py --repo "<path-to-local-repository>" --task "<engineering task>"
```

Example:

```bash
python main.py --repo "C:/Users/me/projects/calculator" --task "Make add() raise TypeError for non-numeric input, with tests"
```

#### What happens

1. **Analyst:** reads the relevant files and writes an implementation plan. It does not modify anything.
2. **Developer:** edits and creates files in the repository, writes tests, and runs them.
3. **QA:** runs the test suite, reviews the full diff, and returns `APPROVED` or `CHANGES_REQUESTED`.
4. If tests fail or QA requests changes, the Developer tries again with QA's feedback, up to 3 attempts.

At the end, AgentForge prints the analysis, developer summary, changed files, diff, test results, code review, and a final status (`SUCCESS` or `FAILED`, with the reason).

#### Reviewing the result

AgentForge **edits files directly in the folder you pass**. It **never commits, pushes, or switches branches**. All changes are left uncommitted for you to review:

```bash
cd "<path-to-local-repository>"
git status
git diff
```

- **To keep the changes:** commit them yourself.
- **To discard them:** run the commands printed at the end of a failed run:

  ```bash
  git -C "<path-to-local-repository>" restore --staged --worktree .
  git -C "<path-to-local-repository>" clean -fd
  ```

  `git clean -fd` deletes untracked files. This is safe only because the tree was clean before the run.

#### Important notes

- **Code is sent to OpenAI.** File names, the contents of files the agents read, the diff, and the test output are sent to the OpenAI API. Do not run AgentForge on code you are not permitted to share.
- **Only run it on repositories you trust.** Running the test suite executes the repository's code on your machine, with your environment variables.
- **Do not point `--repo` at the AgentForge folder itself.**
- **Try it on a small throwaway repository first,** or on a separate clone (`git clone <original> <copy>`), so your original folder is never touched.

## Development Roadmap

- [ ] Define the shared workflow state.
- [ ] Implement the analysis, development, and QA components.
- [ ] Connect the components into a coordinated workflow.
- [ ] Integrate model providers and configuration management.
- [ ] Add automated tests and error handling.
- [ ] Validate the workflow with sample software engineering tasks.
- [ ] Document setup, execution, and evaluation results.

## Testing

Automated testing and workflow validation are planned as part of development. Test instructions and results will be documented as they become available.


## License

No license has been selected yet. Licensing and reuse terms will be added when a license is chosen.
