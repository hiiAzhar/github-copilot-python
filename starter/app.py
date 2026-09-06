from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'board': None,
    'locked': None,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    clues = int(request.args.get('clues', 35))
    difficulty = request.args.get('difficulty')
    puzzle, solution = sudoku_logic.generate_puzzle(clues, difficulty)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['board'] = sudoku_logic.deep_copy(puzzle)
    CURRENT['locked'] = sudoku_logic.get_prefilled_cells(puzzle)
    return jsonify({
        'puzzle': puzzle,
        'givens': sudoku_logic.get_prefilled_cells(puzzle),
    })


@app.route('/move', methods=['POST'])
def make_move():
    data = request.get_json(silent=True) or {}
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    board = CURRENT.get('board')
    row = data.get('row')
    col = data.get('col')
    value = data.get('value')

    if solution is None or puzzle is None or board is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not all(isinstance(index, int) for index in (row, col)):
        return jsonify({'error': 'Invalid cell coordinates'}), 400
    if not (0 <= row < sudoku_logic.SIZE and 0 <= col < sudoku_logic.SIZE):
        return jsonify({'error': 'Invalid cell coordinates'}), 400
    if puzzle[row][col] != sudoku_logic.EMPTY:
        return jsonify({'error': 'Prefilled cells cannot be changed'}), 400
    if CURRENT['locked'][row][col]:
        return jsonify({'error': 'This cell is locked'}), 400
    if not isinstance(value, int) or not 1 <= value <= sudoku_logic.SIZE:
        return jsonify({'error': 'Enter a number from 1 to 9'}), 400

    if value != solution[row][col]:
        board[row][col] = sudoku_logic.EMPTY
        return jsonify({'valid': False, 'completed': False})

    board[row][col] = value
    completed = board == solution
    return jsonify({'valid': True, 'completed': completed})


@app.route('/hint', methods=['POST'])
def get_hint():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    board = CURRENT.get('board')
    locked = CURRENT.get('locked')
    if puzzle is None or solution is None or board is None or locked is None:
        return jsonify({'error': 'No game in progress'}), 400

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] == sudoku_logic.EMPTY and board[row][col] == sudoku_logic.EMPTY:
                board[row][col] = solution[row][col]
                locked[row][col] = True
                return jsonify({
                    'row': row,
                    'col': col,
                    'value': solution[row][col],
                    'completed': board == solution,
                })

    return jsonify({'error': 'No empty cells available for a hint'}), 400

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return jsonify({'error': 'Invalid board'}), 400
    if any(
        not isinstance(row, list) or len(row) != sudoku_logic.SIZE
        for row in board
    ):
        return jsonify({'error': 'Invalid board'}), 400

    incorrect = []
    completed = True
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            value = board[i][j]
            if value == sudoku_logic.EMPTY:
                completed = False
            elif value != solution[i][j]:
                incorrect.append([i, j])
                completed = False
    return jsonify({'incorrect': incorrect, 'completed': completed})

if __name__ == '__main__':
    app.run(debug=True)