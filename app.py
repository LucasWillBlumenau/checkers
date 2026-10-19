from dataclasses import dataclass


EMPTY = 0
BLACK = 1
WHITE = 2

ROW_SIZE = 8
COLUMN_SIZE = 8

MAX_SEARCH_DEPTH = 3

MIN_RATING = -8
MAX_RATING = 8


@dataclass(slots=True)
class Move:
    source: tuple[int, int]
    destination: tuple[int, int]
    taken_pieces: list[tuple[int, int]]


def get_symbol(color: int) -> str:
    if color == BLACK:
        return 'B'
    if color == WHITE:
        return 'W'
    return '#'


def create_board() -> list[list[int]]:
    return [
        [BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY],
        [EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK],
        [BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        [EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE],
        [WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY],
        [EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE],
    ]


def is_inbound(position: tuple[int, int]) -> bool:
    x, y = position
    return (
        x >= 0 and x < ROW_SIZE and
        y >= 0 and y < COLUMN_SIZE
    )


def switch_turn(turn: int) -> int:
    return WHITE if turn == BLACK else BLACK

def get_piece_in_position(board: list[list[int]], position: tuple[int, int]) -> int:
    x, y = position
    return board[y][x]

def evaluate_attacking_moves(board: list[list[int]], position: tuple[int, int], direction: int) -> list[Move]:
    x, y = position
    initial_position = position
    opposite_color = WHITE if board[y][x] == BLACK else BLACK

    def search_leaf_position(position: tuple[int, int], taken_pieces: list[tuple[int, int]]) -> list[Move]:
        moves = []

        position_x, position_y = position
        left_target = (position_x - 2, position_y + direction * 2)
        left_piece = (position_x - 1, position_y + direction)
        right_target = (position_x + 2, position_y + direction * 2)
        right_piece = (position_x + 1, position_y + direction)
        is_leaf = True

        if (
            is_inbound(left_target) and
            get_piece_in_position(board, left_target) == EMPTY and
            get_piece_in_position(board, left_piece) == opposite_color
        ):
            is_leaf = False
            left_moves = search_leaf_position(left_target, [*taken_pieces, left_piece])
            moves.extend(left_moves)

        if (
            is_inbound(right_target) and
            get_piece_in_position(board, right_target) == EMPTY and
            get_piece_in_position(board, right_piece) == opposite_color
        ):
            is_leaf = False
            right_moves = search_leaf_position(right_target, [*taken_pieces, right_piece])
            moves.extend(right_moves)

        if is_leaf and len(taken_pieces) > 0:
            return [Move(
                source=initial_position,
                destination=position,
                taken_pieces=taken_pieces
            )]
        return moves

    return search_leaf_position(position, [])


def evaluate_positional_moves(board: list[list[int]], position: tuple[int, int], direction: int) -> list[Move]:
    moves = []

    position_x, position_y = position
    move_targets = [
        (position_x - 1, position_y + direction),
        (position_x + 1, position_y + direction)
    ]

    for target in move_targets:
        x, y = target
        if is_inbound(target) and board[y][x] == EMPTY:
            moves.append(Move(
                source=position,
                destination=target,
                taken_pieces=[]
            ))

    return moves


def get_positions(board: list[list[int]], turn_piece: int) -> list[tuple[int, int]]:
    positions = []
    for i, row in enumerate(board):
        for j in range(len(row)):
            if board[i][j] != turn_piece:
                continue
            positions.append((j, i))
    return positions


def evaluate_board_moves(board: list[list[int]], turn_piece: int) -> None:
    direction = 1 if turn_piece == BLACK else -1
    positions = get_positions(board, turn_piece)

    moves = []

    for position in positions:
        moves.extend(evaluate_attacking_moves(board, position, direction))

    if len(moves) > 0:
       return moves

    for position in positions:
        moves.extend(evaluate_positional_moves(board, position, direction))
    return moves


def apply_move(board: list[list[int]], move: Move) -> None:
    src_x, src_y = move.source
    dest_x, dest_y = move.destination

    piece = board[src_y][src_x]
    board[src_y][src_x] = EMPTY
    board[dest_y][dest_x] = piece

    for taken_piece in move.taken_pieces:
        x, y = taken_piece
        board[y][x] = EMPTY


def undo_move(board: list[list[int]], move: Move) -> None:
    src_x, src_y = move.destination
    dest_x, dest_y = move.source

    piece = board[src_y][src_x]
    opposite_piece = switch_turn(piece)
    board[src_y][src_x] = EMPTY
    board[dest_y][dest_x] = piece

    for taken_piece in move.taken_pieces:
        x, y = taken_piece
        board[y][x] = opposite_piece


def is_game_over(board: list[int, int], turn: int) -> None:
    return False


def print_board(board: list[int, int]) -> None:
    for row in reversed(board):
        for element in row:
            print(get_symbol(element), end=' ')
        print()
    print()


def parse_input(value: str, max_value: int) -> int | None:
    if not value.isdigit():
        return None
    parsed = int(value)
    if parsed >= max_value:
        return None
    return parsed


def choose_move(moves: list[Move]) -> Move:
    for i, move in enumerate(moves, 1):
        print(f'{i}. {move.source} -> {move.destination}')
    print()

    option = parse_input(input('Escolha uma opção: '), len(moves))
    while option is None:
        print('Opção inválida. Tente novamente.')
        option = parse_input(input('Move: '), len(moves))

    return moves[option - 1]


def calculate_board_rating(board: list[list[int]]) -> int:
    rating = 0
    for row in reversed(board):
        for element in row:
            if element == EMPTY:
                continue
            rating += 1 if element == BLACK else -1
    return rating


def minmax(board: list[list[int]], turn: int) -> Move:
    evaluation_board = board.copy()

    def min(turn: int, depth: int) -> tuple[int, Move]:
        if depth == MAX_SEARCH_DEPTH:
            return calculate_board_rating(evaluation_board), None

        moves = evaluate_board_moves(board, turn)
        next_turn = switch_turn(turn)
        next_depth = depth + 1
        min_rating_value = MAX_RATING
        min_rating_move = None

        for move in moves:
            apply_move(evaluation_board, move)
            rating, _ = max(next_turn, next_depth)
            if min_rating_value > rating:
                min_rating_value = rating
                min_rating_move = move
            undo_move(evaluation_board, move)

        return min_rating_value, min_rating_move

    def max(turn: int, depth: int) -> None:
        if depth == MAX_SEARCH_DEPTH:
            return calculate_board_rating(evaluation_board), None

        moves = evaluate_board_moves(board, turn)
        next_turn = switch_turn(turn)
        next_depth = depth + 1
        max_rating_value = MIN_RATING
        max_rating_move = None

        for move in moves:
            apply_move(evaluation_board, move)
            rating, _ = min(next_turn, next_depth)
            if max_rating_value < rating:
                max_rating_value = rating
                max_rating_move = move
            undo_move(evaluation_board, move)

        return max_rating_value, max_rating_move

    _, move = max(turn, 0) if turn == BLACK else min(turn, 0)
    return move


def main() -> None:
    board = create_board()
    turn = BLACK
    while not is_game_over(board, turn):
        print_board(board)

        if turn == BLACK:
            moves = evaluate_board_moves(board, turn)
            move = choose_move(moves)
        else:
            move = minmax(board, turn)
            print(f'Computer played {move.source} -> {move.destination}')

        apply_move(board, move)
        turn = WHITE if turn == BLACK else BLACK


if __name__ == '__main__':
    main()
