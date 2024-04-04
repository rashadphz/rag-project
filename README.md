## Setup

The project is using Poetry for dependency management.

1. **Install Poetry**: Instructions [official Poetry documentation](https://python-poetry.org/docs/#installing-with-the-official-installer).

2. **Install Dependencies**: run `poetry install` to install the project dependencies.

### Running Python Scripts
- To run a python script, you can use the command `poetry run python <script>.py`,
- Easier alternative: use `poetry shell` to enter the virtual environment and run the script directly with `python <script>.py`.

### Managing Dependencies
- Adding dependencies: `poetry add <package-name>`.
- Updating dependencies: `poetry update`.
- Removing dependencies: `poetry remove <package-name>`.
