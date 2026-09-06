# Flask Sudoku

A browser-based Sudoku game built with Flask and vanilla JavaScript. The application generates valid Sudoku puzzles, validates gameplay through Flask routes, and stores completed scores in the browser.

## Setup on Windows

Open PowerShell in the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks script activation, run the commands from Command Prompt instead:

```cmd
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run the Application

With the virtual environment activated:

```powershell
python app.py
```

Open the local Flask URL shown in the terminal, normally `http://127.0.0.1:5000/`.

## Run Tests

From the project root:

```powershell
pytest -q
```

The tests cover Sudoku board generation, unique solutions, difficulty levels, given cells, Flask routes, moves, hints, locking, and completion behavior.

## Implemented Features

- 9x9 Sudoku board with generated puzzles.
- Easy, Medium, and Hard difficulty levels with different clue counts.
- Puzzle generation that preserves exactly one valid solution.
- Explicit prefilled/given-cell data; given cells are locked.
- Immediate player move validation for values 1-9.
- Check action that highlights incorrect entries and recognizes completion.
- Hint action that fills and locks one empty cell using the solution.
- Elapsed game timer that stops on completion.
- Player name prompt and Top 10 leaderboard stored in browser `localStorage`.
- Light/dark mode toggle with persisted theme preference.
- Responsive board, controls, and leaderboard layout for desktop and mobile screens.
- Visual states for prefilled, hinted, correct, incorrect, and focused cells.

## Project Structure

```text
app.py                 Flask application and game routes
sudoku_logic.py        Sudoku board, solving, generation, and uniqueness logic
requirements.txt       Flask and pytest dependencies
instruction.md         Project guidance for future Copilot work
static/main.js         Board interaction, validation, timer, hints, theme, leaderboard
static/styles.css      Responsive light/dark UI styling
templates/index.html   Page structure and game controls
tests/conftest.py      Pytest import configuration
tests/test_sudoku.py   Sudoku and Flask route tests
```

## Flask Routes

- `GET /` renders the game page.
- `GET /new` creates a new puzzle. It accepts `difficulty=easy`, `medium`, or `hard`.
- `POST /move` validates a player move.
- `POST /hint` fills one available cell and locks it.
- `POST /check` checks the submitted board and returns incorrect cell coordinates and completion status.
