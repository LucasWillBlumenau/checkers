from dataclasses import dataclass

EMPTY = 0
BLACK_PIECE = 1
WHITE_PIECE = 2

ROW_SIZE = 8
COLUMN_SIZE = 8

MAX_SEARCH_DEPTH = 6

MIN_RATING = -12
MAX_RATING = 12


@dataclass(slots=True)
class Move:
    source: tuple[int, int]
    destination: tuple[int, int]
    taken_pieces: list[tuple[int, int, bool]]
    promote: bool


@dataclass(slots=True)
class Piece:
    color: int
    is_king: bool

    @staticmethod
    def black(is_king: bool = False) -> "Piece":
        return Piece(BLACK_PIECE, is_king)

    @staticmethod
    def white(is_king: bool = False) -> "Piece":
        return Piece(WHITE_PIECE, is_king)

    def copy(self) -> "Piece":
        return Piece(self.color, self.is_king)


def get_symbol(color: int) -> str:
    if color == BLACK_PIECE:
        return "B"
    if color == WHITE_PIECE:
        return "W"
    return "#"


def create_board() -> list[list[Piece | None]]:
    return [
        [
            Piece.black(),
            None,
            Piece.black(),
            None,
            Piece.black(),
            None,
            Piece.black(),
            None,
        ],
        [
            None,
            Piece.black(),
            None,
            Piece.black(),
            None,
            Piece.black(),
            None,
            Piece.black(),
        ],
        [
            Piece.black(),
            None,
            Piece.black(),
            None,
            Piece.black(),
            None,
            Piece.black(),
            None,
        ],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [
            None,
            Piece.white(),
            None,
            Piece.white(),
            None,
            Piece.white(),
            None,
            Piece.white(),
        ],
        [
            Piece.white(),
            None,
            Piece.white(),
            None,
            Piece.white(),
            None,
            Piece.white(),
            None,
        ],
        [
            None,
            Piece.white(),
            None,
            Piece.white(),
            None,
            Piece.white(),
            None,
            Piece.white(),
        ],
    ]


def is_inbound(position: tuple[int, int]) -> bool:
    x, y = position
    return x >= 0 and x < ROW_SIZE and y >= 0 and y < COLUMN_SIZE


def switch_turn(turn: int) -> int:
    return WHITE_PIECE if turn == BLACK_PIECE else BLACK_PIECE


def get_piece_in_position(
    board: list[list[Piece | None]], position: tuple[int, int]
) -> Piece | None:
    x, y = position
    return board[y][x]


def get_position_color(
    board: list[list[Piece | None]], position: tuple[int, int]
) -> int:
    x, y = position
    piece = board[y][x]
    if piece is None:
        return EMPTY
    return piece.color


def get_position_is_king(
    board: list[list[Piece | None]], position: tuple[int, int]
) -> bool:
    x, y = position
    piece = board[y][x]
    if piece is None:
        return False
    return piece.is_king


def evaluate_attacking_moves(
    board: list[list[Piece | None]], position: tuple[int, int], direction: int
) -> list[Move]:
    initial_position = position

    color = get_position_color(board, position)
    opposite_color = WHITE_PIECE if color == BLACK_PIECE else BLACK_PIECE

    def search_leaf_position(
        position: tuple[int, int], taken_pieces: list[tuple[int, int, bool]]
    ) -> list[Move]:
        moves: list[Move] = []

        position_x, position_y = position
        left_target = (position_x - 2, position_y + direction * 2)
        left_piece = (position_x - 1, position_y + direction)
        right_target = (position_x + 2, position_y + direction * 2)
        right_piece = (position_x + 1, position_y + direction)
        is_leaf = True

        if (
            is_inbound(left_target)
            and get_position_color(board, left_target) == EMPTY
            and get_position_color(board, left_piece) == opposite_color
        ):
            is_leaf = False
            left_moves = search_leaf_position(
                left_target,
                [*taken_pieces, (*left_piece, get_position_is_king(board, left_piece))],
            )
            moves.extend(left_moves)

        if (
            is_inbound(right_target)
            and get_position_color(board, right_target) == EMPTY
            and get_position_color(board, right_piece) == opposite_color
        ):
            is_leaf = False
            right_moves = search_leaf_position(
                right_target,
                [
                    *taken_pieces,
                    (*right_piece, get_position_is_king(board, right_piece)),
                ],
            )
            moves.extend(right_moves)

        if is_leaf and len(taken_pieces) > 0:
            _, y = position
            return [
                Move(
                    source=initial_position,
                    destination=position,
                    taken_pieces=taken_pieces,
                    promote=y in (0, 7) and not get_position_is_king(board, position),
                )
            ]
        return moves

    return search_leaf_position(position, [])


def evaluate_positional_moves(
    board: list[list[Piece | None]], position: tuple[int, int], direction: int
) -> list[Move]:
    moves: list[Move] = []

    position_x, position_y = position
    move_targets = [
        (position_x - 1, position_y + direction),
        (position_x + 1, position_y + direction),
    ]

    for target in move_targets:
        x, y = target
        if is_inbound(target) and board[y][x] is None:
            moves.append(
                Move(
                    source=position,
                    destination=target,
                    taken_pieces=[],
                    promote=y in (0, 7) and not get_position_is_king(board, target),
                )
            )

    return moves


def get_positions(
    board: list[list[Piece | None]], turn_piece: int
) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece is not None and piece.color == turn_piece:
                positions.append((j, i))
    return positions


def evaluate_board_moves(
    board: list[list[Piece | None]], turn_piece: int
) -> list[Move]:
    direction = 1 if turn_piece == BLACK_PIECE else -1
    positions = get_positions(board, turn_piece)

    moves: list[Move] = []

    for position in positions:
        if get_position_is_king(board, position):
            moves.extend(evaluate_attacking_moves(board, position, -direction))
        moves.extend(evaluate_attacking_moves(board, position, direction))

    if len(moves) > 0:
        return moves

    for position in positions:
        if get_position_is_king(board, position):
            moves.extend(evaluate_positional_moves(board, position, -direction))
        moves.extend(evaluate_positional_moves(board, position, direction))
    return moves


def apply_move(board: list[list[Piece | None]], move: Move) -> None:
    src_x, src_y = move.source
    dest_x, dest_y = move.destination

    piece = board[src_y][src_x]
    if piece is None:
        for row in reversed(board):
            for piece in row:
                print(piece.color if piece is not None else 0, end=" ")
            print()

        raise Exception(f"invalid board state: cannot apply move {move}")

    board[src_y][src_x] = None
    board[dest_y][dest_x] = Piece(piece.color, piece.is_king or move.promote)

    for taken_piece in move.taken_pieces:
        x, y, _ = taken_piece
        board[y][x] = None


def undo_move(board: list[list[Piece | None]], move: Move) -> None:
    src_x, src_y = move.destination
    dest_x, dest_y = move.source

    piece = board[src_y][src_x]
    if piece is None:
        raise Exception(f"invalid board state: cannot undo move {move}")

    opposite_piece = switch_turn(piece.color)
    board[src_y][src_x] = None
    board[dest_y][dest_x] = Piece(piece.color, piece.is_king and not move.promote)

    for taken_piece in move.taken_pieces:
        x, y, is_king = taken_piece
        board[y][x] = Piece(opposite_piece, is_king)


def is_game_over(board: list[list[Piece | None]], turn: int) -> bool:
    return False


def print_board(board: list[list[Piece | None]]) -> None:
    for row in reversed(board):
        for piece in row:
            print(get_symbol(piece.color if piece is not None else EMPTY), end=" ")
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
        print(f"{i}. {move.source} -> {move.destination}")
    print()

    option = parse_input(input("Escolha uma opção: "), len(moves))
    while option is None:
        print("Opção inválida. Tente novamente.")
        option = parse_input(input("Move: "), len(moves))

    return moves[option - 1]


def calculate_board_rating(board: list[list[Piece | None]]) -> int:
    rating = 0
    for row in reversed(board):
        for element in row:
            if element is None:
                continue
            weight = 3 if element.is_king else 1
            rating += weight * (1 if element.color == BLACK_PIECE else -1)
    return rating


def copy_board(board: list[list[Piece | None]]) -> list[list[Piece | None]]:
    new_board: list[list[Piece | None]] = []
    for row in board:
        new_row: list[Piece | None] = []
        for piece in row:
            new_row.append(piece.copy() if piece is not None else None)
        new_board.append(new_row)
    return new_board


def minmax(board: list[list[Piece | None]], turn: int) -> Move:
    evaluation_board = copy_board(board)

    def min(turn: int, depth: int) -> tuple[int, Move | None]:
        if depth == MAX_SEARCH_DEPTH:
            return calculate_board_rating(evaluation_board), None

        moves = evaluate_board_moves(evaluation_board, turn)
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

    def max(turn: int, depth: int) -> tuple[int, Move | None]:
        if depth == MAX_SEARCH_DEPTH:
            return calculate_board_rating(evaluation_board), None

        moves = evaluate_board_moves(evaluation_board, turn)
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

    _, move = max(turn, 0) if turn == BLACK_PIECE else min(turn, 0)
    if move is None:
        raise Exception("cannot calculate move sequence")

    return move


def main() -> None:
    board = create_board()
    turn = BLACK_PIECE
    while not is_game_over(board, turn):
        print_board(board)

        if turn == BLACK_PIECE:
            moves = evaluate_board_moves(board, turn)
            move = choose_move(moves)
        else:
            move = minmax(board, turn)
            print(f"Computer played {move.source} -> {move.destination}")

        apply_move(board, move)
        turn = WHITE_PIECE if turn == BLACK_PIECE else BLACK_PIECE


if __name__ == "__main__":
    main()
