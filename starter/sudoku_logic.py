import copy
import random


SIZE = 9
EMPTY = 0
BOX_SIZE = 3
TOTAL_CELLS = SIZE * SIZE

DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 30,
}


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    for index in range(SIZE):
        if board[row][index] == num or board[index][col] == num:
            return False

    start_row = row - row % BOX_SIZE
    start_col = col - col % BOX_SIZE
    for box_row in range(start_row, start_row + BOX_SIZE):
        for box_col in range(start_col, start_col + BOX_SIZE):
            if board[box_row][box_col] == num:
                return False
    return True


def find_empty_cell(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def get_candidates(board, row, col):
    return [
        number
        for number in range(1, SIZE + 1)
        if is_safe(board, row, col, number)
    ]


def is_valid_board(board):
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return False

    if any(
        cell != EMPTY and not 1 <= cell <= SIZE
        for row in board
        for cell in row
    ):
        return False

    units = list(board)
    units.extend(
        [board[row][col] for row in range(SIZE)]
        for col in range(SIZE)
    )
    units.extend(
        [
            board[row][col]
            for row in range(box_row, box_row + BOX_SIZE)
            for col in range(box_col, box_col + BOX_SIZE)
        ]
        for box_row in range(0, SIZE, BOX_SIZE)
        for box_col in range(0, SIZE, BOX_SIZE)
    )
    return all(
        len(values := [value for value in unit if value != EMPTY])
        == len(set(values))
        for unit in units
    )


def find_most_constrained_cell(board):
    best_cell = None
    best_candidates = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue
            candidates = get_candidates(board, row, col)
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_cell = (row, col)
                best_candidates = candidates
                if not candidates:
                    return best_cell, best_candidates

    if best_cell is None:
        return None
    return best_cell, best_candidates


def fill_board(board):
    empty_cell = find_empty_cell(board)
    if empty_cell is None:
        return True

    row, col = empty_cell
    candidates = get_candidates(board, row, col)
    random.shuffle(candidates)
    for candidate in candidates:
        board[row][col] = candidate
        if fill_board(board):
            return True
        board[row][col] = EMPTY
    return False


def solve_board(board):
    selected = find_most_constrained_cell(board)
    if selected is None:
        return True

    (row, col), candidates = selected
    for candidate in candidates:
        board[row][col] = candidate
        if solve_board(board):
            return True
        board[row][col] = EMPTY
    return False


def count_solutions(board, limit=2):
    if limit < 1:
        raise ValueError('limit must be at least 1')
    if not is_valid_board(board):
        return 0

    working_board = deep_copy(board)

    def count_from_current_board():
        selected = find_most_constrained_cell(working_board)
        if selected is None:
            return 1

        (row, col), candidates = selected
        total = 0
        for candidate in candidates:
            working_board[row][col] = candidate
            total += count_from_current_board()
            working_board[row][col] = EMPTY
            if total >= limit:
                return total
        return total

    return count_from_current_board()


def remove_cells(board, clues):
    validate_clue_count(clues)
    removable_cells = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
        if board[row][col] != EMPTY
    ]
    cells_to_remove = len(removable_cells) - clues
    if cells_to_remove < 0:
        raise ValueError('board does not contain enough filled cells')

    random.shuffle(removable_cells)
    for row, col in removable_cells[:cells_to_remove]:
        board[row][col] = EMPTY


def validate_clue_count(clues):
    if not isinstance(clues, int) or not 0 <= clues <= TOTAL_CELLS:
        raise ValueError(f'clues must be between 0 and {TOTAL_CELLS}')


def get_prefilled_cells(puzzle):
    return [
        [cell != EMPTY for cell in row]
        for row in puzzle
    ]


def get_clues_for_difficulty(difficulty):
    try:
        return DIFFICULTY_CLUES[difficulty.lower()]
    except (AttributeError, KeyError) as error:
        available = ', '.join(DIFFICULTY_CLUES)
        raise ValueError(f'difficulty must be one of: {available}') from error


def _resolve_clues(clues, difficulty):
    if difficulty is not None:
        clues = get_clues_for_difficulty(difficulty)
    validate_clue_count(clues)
    return clues


def _remove_cells_preserving_uniqueness(solution, clues):
    puzzle = deep_copy(solution)
    removable_cells = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
    ]
    random.shuffle(removable_cells)

    for row, col in removable_cells:
        if sum(cell != EMPTY for row in puzzle for cell in row) <= clues:
            break
        original_value = puzzle[row][col]
        puzzle[row][col] = EMPTY
        if count_solutions(puzzle) != 1:
            puzzle[row][col] = original_value

    if sum(cell != EMPTY for row in puzzle for cell in row) == clues:
        return puzzle
    return None


def generate_puzzle(clues=35, difficulty=None):
    clues = _resolve_clues(clues, difficulty)
    for _ in range(10):
        solution = create_empty_board()
        fill_board(solution)
        puzzle = _remove_cells_preserving_uniqueness(solution, clues)
        if puzzle is not None:
            return puzzle, solution
    raise RuntimeError('unable to generate a puzzle with the requested clues')
