import pytest

import sudoku_logic
from app import CURRENT, app


def test_create_empty_board_has_expected_shape():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_count_solutions_rejects_invalid_prefilled_board():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 1

    assert sudoku_logic.count_solutions(board) == 0


def test_generate_puzzle_returns_valid_solution_and_requested_clues():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(
        len(row) == sudoku_logic.SIZE
        for row in puzzle + solution
    )
    expected_values = list(range(1, sudoku_logic.SIZE + 1))
    assert all(sorted(row) == expected_values for row in solution)
    assert all(
        sorted(solution[row][col] for row in range(sudoku_logic.SIZE))
        == expected_values
        for col in range(sudoku_logic.SIZE)
    )
    assert all(
        sorted(
            solution[row][col]
            for row in range(box_row, box_row + 3)
            for col in range(box_col, box_col + 3)
        ) == expected_values
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_col in range(0, sudoku_logic.SIZE, 3)
    )
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    assert sudoku_logic.count_solutions(puzzle) == 1
    assert all(
        puzzle[row][col] == solution[row][col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] != sudoku_logic.EMPTY
    )


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_difficulty_generates_unique_puzzle_with_expected_clues(difficulty):
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == (
        sudoku_logic.DIFFICULTY_CLUES[difficulty]
    )
    assert sudoku_logic.count_solutions(puzzle) == 1
    assert all(
        puzzle[row][col] in (sudoku_logic.EMPTY, solution[row][col])
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )


def test_prefilled_cells_are_explicit_and_match_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty='easy')
    givens = sudoku_logic.get_prefilled_cells(puzzle)

    assert all(len(row) == sudoku_logic.SIZE for row in givens)
    assert all(
        givens[row][col] == (puzzle[row][col] != sudoku_logic.EMPTY)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )
    assert all(
        not givens[row][col] or puzzle[row][col] == solution[row][col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )


def test_new_game_returns_a_puzzle():
    client = app.test_client()

    response = client.get('/new?clues=40')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    givens = response.get_json()['givens']
    assert len(puzzle) == sudoku_logic.SIZE
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 40
    assert givens == sudoku_logic.get_prefilled_cells(puzzle)


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_new_game_accepts_all_difficulties(difficulty):
    client = app.test_client()

    response = client.get(f'/new?difficulty={difficulty}')
    data = response.get_json()

    assert response.status_code == 200
    assert sum(
        cell
        for row in data['givens']
        for cell in row
    ) == sudoku_logic.DIFFICULTY_CLUES[difficulty]
    assert data['givens'] == sudoku_logic.get_prefilled_cells(data['puzzle'])
    assert sudoku_logic.count_solutions(data['puzzle']) == 1


def test_check_solution_accepts_current_solution():
    client = app.test_client()
    client.get('/new')
    solution = CURRENT['solution']

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'completed': True}


def test_check_solution_highlights_only_incorrect_entered_cells():
    client = app.test_client()
    client.get('/new?difficulty=easy')
    board = sudoku_logic.deep_copy(CURRENT['solution'])
    editable_cell = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if CURRENT['puzzle'][row][col] == sudoku_logic.EMPTY
    )
    row, col = editable_cell
    incorrect_value = next(
        value for value in range(1, sudoku_logic.SIZE + 1)
        if value != CURRENT['solution'][row][col]
    )
    board[row][col] = incorrect_value

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {
        'incorrect': [[row, col]],
        'completed': False,
    }


def test_move_rejects_incorrect_value_and_clears_player_cell():
    client = app.test_client()
    response = client.get('/new?difficulty=easy')
    data = response.get_json()
    row, col = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if not data['givens'][row][col]
    )
    solution_value = CURRENT['solution'][row][col]
    incorrect_value = next(
        value for value in range(1, sudoku_logic.SIZE + 1)
        if value != solution_value
    )

    move = client.post('/move', json={
        'row': row,
        'col': col,
        'value': incorrect_value,
    })

    assert move.status_code == 200
    assert move.get_json() == {'valid': False, 'completed': False}
    assert CURRENT['board'][row][col] == sudoku_logic.EMPTY


def test_move_rejects_changes_to_prefilled_cell():
    client = app.test_client()
    response = client.get('/new?difficulty=easy')
    data = response.get_json()
    row, col = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if data['givens'][row][col]
    )

    move = client.post('/move', json={
        'row': row,
        'col': col,
        'value': data['puzzle'][row][col],
    })

    assert move.status_code == 400
    assert 'cannot be changed' in move.get_json()['error']


def test_hint_fills_and_locks_exactly_one_empty_cell():
    client = app.test_client()
    response = client.get('/new?difficulty=hard')
    data = response.get_json()
    empty_before = sum(
        cell == sudoku_logic.EMPTY
        for row in CURRENT['board']
        for cell in row
    )

    hint = client.post('/hint')
    result = hint.get_json()
    row, col = result['row'], result['col']

    assert hint.status_code == 200
    assert result['value'] == CURRENT['solution'][row][col]
    assert data['givens'][row][col] is False
    assert CURRENT['board'][row][col] == result['value']
    assert CURRENT['locked'][row][col] is True
    assert sum(
        cell == sudoku_logic.EMPTY
        for row in CURRENT['board']
        for cell in row
    ) == empty_before - 1

    move = client.post('/move', json={
        'row': row,
        'col': col,
        'value': result['value'],
    })
    assert move.status_code == 400
    assert 'locked' in move.get_json()['error']


def test_hint_does_not_overwrite_player_entries():
    client = app.test_client()
    client.get('/new?difficulty=hard')
    player_cell = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if CURRENT['puzzle'][row][col] == sudoku_logic.EMPTY
    )
    row, col = player_cell
    move = client.post('/move', json={
        'row': row,
        'col': col,
        'value': CURRENT['solution'][row][col],
    })
    assert move.get_json()['valid'] is True

    hint = client.post('/hint')

    assert hint.status_code == 200
    assert (hint.get_json()['row'], hint.get_json()['col']) != player_cell
    assert CURRENT['locked'][row][col] is False


def test_correct_moves_complete_the_current_puzzle():
    client = app.test_client()
    response = client.get('/new?difficulty=hard')
    data = response.get_json()
    editable_cells = [
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if not data['givens'][row][col]
    ]

    for row, col in editable_cells[:-1]:
        move = client.post('/move', json={
            'row': row,
            'col': col,
            'value': CURRENT['solution'][row][col],
        })
        assert move.get_json() == {'valid': True, 'completed': False}

    row, col = editable_cells[-1]
    move = client.post('/move', json={
        'row': row,
        'col': col,
        'value': CURRENT['solution'][row][col],
    })

    assert move.status_code == 200
    assert move.get_json() == {'valid': True, 'completed': True}