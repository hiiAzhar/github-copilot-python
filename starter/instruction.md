# Flask Sudoku Project Instructions

These instructions apply to all refactoring and feature work in this Flask Sudoku application.

## Project Context

- The backend is a small Flask application in `app.py`.
- Sudoku rules, board generation, solving, and puzzle creation belong in `sudoku_logic.py`.
- Browser behavior belongs in `static/main.js`.
- Presentation and structure belong in `templates/index.html` and `static/styles.css`.
- Automated tests belong in `tests/` and use pytest.
- Keep game logic, HTTP routes, UI behavior, and data or persistence concerns separated where practical. Do not move responsibilities across these boundaries without a clear benefit.

## General Engineering Rules

1. Use clean, modular, maintainable Python code with small, reusable functions and clear names.
2. Follow PEP 8 and readable Python conventions. Preserve the existing style and public behavior unless a requirement explicitly calls for a change.
3. Inspect the existing implementation and relevant tests before making a significant change. Briefly explain the proposed approach, affected files, and any behavior or compatibility risks before implementing it.
4. Keep changes focused. Do not make unrelated edits, broad rewrites, speculative abstractions, or unnecessary dependency additions.
5. Add concise comments or docstrings only when they improve understanding of non-obvious behavior. Avoid comments that merely restate the code.
6. Handle expected errors consistently at the appropriate boundary. Return clear, user-appropriate responses and avoid exposing stack traces, internal state, or unnecessary implementation details.

## Flask and Data Boundaries

- Keep Flask route handlers thin: validate request data, call the appropriate application or game-logic function, and format the response.
- Keep Sudoku rules and generation independent from Flask so they can be tested directly.
- Validate request parameters and JSON payloads at the route boundary, including malformed, missing, or out-of-range values where relevant.
- Preserve existing route names, methods, response shapes, and status behavior unless the requirement explicitly changes the API.
- Treat in-memory state and any future persistence layer as separate concerns. Do not introduce a database or persistence dependency unless explicitly required.

## Sudoku Correctness

- Sudoku boards use the existing project constants and dimensions; do not duplicate magic values when a shared constant exists.
- A generated puzzle must have exactly one valid solution. Any change to generation, solving, clue removal, or validation must preserve this invariant and include tests that demonstrate uniqueness.
- Keep generated puzzles and solutions structurally valid: correct dimensions, valid values, preserved clues, and a solution consistent with the puzzle.
- Avoid relying on randomness alone for correctness. Seed or control randomness in tests when deterministic behavior is needed.

## Frontend and Accessibility

- Use semantic HTML elements and accessible labels, names, roles, and focus states.
- Keep controls keyboard-friendly wherever practical. Ensure the Sudoku grid and actions can be operated without a mouse.
- Preserve clear feedback for invalid input, loading, success, and error states without exposing implementation details.
- Keep CSS organized by component or responsibility, responsive across viewport sizes, and compatible with both light and dark color schemes.
- Preserve readable contrast, visible focus indicators, stable layout dimensions, and usable touch targets.
- Keep browser behavior in `static/main.js` and avoid duplicating game rules in client-side code unless the requirement explicitly needs client-side validation.

## Testing and Verification

- Use pytest for automated testing. Add or update focused tests for every new behavior, bug fix, route contract, or Sudoku rule change.
- Keep the full suite passing after every refactor or feature change. Run `pytest -q` from the project root before reporting completion.
- Test pure Sudoku logic directly and use Flask's test client for route behavior.
- Include boundary and error cases where they are part of the changed behavior.
- For changes to puzzle generation or solving, test exact-one-solution behavior rather than only checking board shape or one successful example.
- Do not weaken, delete, or skip a failing test to make the suite pass. Fix the implementation or clearly report a genuine test-environment issue.

## Change Discipline

- Before editing, identify the smallest owning module and the nearest relevant tests.
- Prefer the smallest change that satisfies the requirement and preserves existing functionality.
- After editing, run focused tests first when available, then run `pytest -q` from the project root.
- Review the final diff for accidental application changes, unrelated formatting, debug output, and new dependencies.
- Do not start feature implementation or refactoring beyond the requested scope.
