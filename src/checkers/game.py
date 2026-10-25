from dataclasses import dataclass

# Board Setup
EMPTY = 0
BLACK_PIECE = 1
WHITE_PIECE = 2
ROW_SIZE = 8
COLUMN_SIZE = 8

# Minimax + Evaluation
MAX_SEARCH_DEPTH = 8
MIN_RATING = -37
MAX_RATING = 37

# Game State
BLACK_WON = 0
WHITE_WON = 1
DRAW = 2
LIMIT_OF_POSITION_REPETION = 3


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


@dataclass(slots=True)
class BoardState:
    black_piece: int
    black_king: int
    black_regular: int
    white_piece: int
    white_king: int
    white_regular: int


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


def get_offset_by_piece(piece: Piece | None) -> int:
    if piece is None:
        return 0
    if piece.color == BLACK_PIECE:
        return 64
    return 128


def get_board_id(board: list[list[Piece | None]]) -> int:
    board_id = 0
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            offset = get_offset_by_piece(piece)
            shift_size = offset + i * ROW_SIZE + j
            board_id |= 1 << shift_size
    return board_id


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
                    promote=y in (0, 7)
                    and not get_position_is_king(board, initial_position),
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
                    promote=y in (0, 7) and not get_position_is_king(board, position),
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


def get_board_state(board: list[list[Piece | None]]) -> BoardState:
    black_regular = 0
    white_regular = 0
    black_king = 0
    white_king = 0
    for row in board:
        for piece in row:
            if piece is None:
                continue
            elif piece.color == BLACK_PIECE and piece.is_king:
                black_king += 1
            elif piece.color == BLACK_PIECE:
                black_regular += 1
            elif piece.color == WHITE_PIECE and piece.is_king:
                white_king += 1
            else:
                white_regular += 1

    return BoardState(
        white_king=white_king,
        white_regular=white_regular,
        white_piece=white_king + white_regular,
        black_king=black_king,
        black_regular=black_regular,
        black_piece=black_king + black_regular,
    )


def increment_position_count(positions_count: dict[int, int], board_id: int) -> None:
    if positions_count.get(board_id) is None:
        positions_count[board_id] = 1
    else:
        positions_count[board_id] += 1


def check_winner(
    board: list[list[Piece | None]],
    turn: int,
    positions_count: dict[int, int],
    moves: list[Move] | None = None,
) -> int | None:
    board_id = get_board_id(board)
    increment_position_count(positions_count, board_id)
    board_state = get_board_state(board)
    if board_state.black_piece == 0:
        return WHITE_PIECE
    if board_state.white_piece == 0:
        return BLACK_PIECE

    if moves is None:
        moves = evaluate_board_moves(board, turn)

    if len(moves) == 0:
        if turn == BLACK_PIECE:
            return WHITE_WON
        return BLACK_WON

    no_regular = board_state.black_regular == 0 and board_state.white_regular == 0
    insufficient_kings = board_state.black_king <= 2 and board_state.white_king <= 2
    if (no_regular and insufficient_kings) or positions_count[
        board_id
    ] >= LIMIT_OF_POSITION_REPETION:
        return DRAW

    return None


def print_board(board: list[list[Piece | None]]) -> None:
    for row in reversed(board):
        for piece in row:
            print(get_symbol(piece.color if piece is not None else EMPTY), end=" ")
        print()
    print()


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


def get_rating_by_state(state: int) -> int:
    if state == BLACK_WON:
        return MAX_RATING
    if state == WHITE_WON:
        return MIN_RATING
    return 0


def minimax(
    board: list[list[Piece | None]], turn: int, positions_count: dict[int, int]
) -> Move:
    evaluation_board = copy_board(board)
    evaluation_positions_count = positions_count.copy()

    def min_value(
        turn: int, alpha: int, beta: int, depth: int
    ) -> tuple[int, Move | None]:
        if depth == MAX_SEARCH_DEPTH:
            return calculate_board_rating(evaluation_board), None

        moves = evaluate_board_moves(evaluation_board, turn)
        next_turn = switch_turn(turn)
        next_depth = depth + 1
        min_rating_value = MAX_RATING
        min_rating_move = moves[0] if moves else None

        state = check_winner(evaluation_board, turn, evaluation_positions_count, moves)
        if state is not None:
            return get_rating_by_state(state), None

        for move in moves:
            apply_move(evaluation_board, move)
            rating, _ = max_value(next_turn, alpha, beta, next_depth)
            undo_move(evaluation_board, move)

            beta = min(beta, rating)
            if alpha >= beta:
                return rating, move

            if min_rating_value > rating:
                min_rating_value = rating
                min_rating_move = move

        return min_rating_value, min_rating_move

    def max_value(
        turn: int, alpha: int, beta: int, depth: int
    ) -> tuple[int, Move | None]:
        if depth == MAX_SEARCH_DEPTH:
            return calculate_board_rating(evaluation_board), None

        moves = evaluate_board_moves(evaluation_board, turn)
        next_turn = switch_turn(turn)
        next_depth = depth + 1
        max_rating_value = MIN_RATING
        max_rating_move = moves[0] if moves else None

        state = check_winner(evaluation_board, turn, evaluation_positions_count, moves)
        if state is not None:
            return get_rating_by_state(state), None

        for move in moves:
            apply_move(evaluation_board, move)
            rating, _ = min_value(next_turn, alpha, beta, next_depth)
            undo_move(evaluation_board, move)

            alpha = max(alpha, rating)
            if alpha >= beta:
                return rating, move

            if max_rating_value < rating:
                max_rating_value = rating
                max_rating_move = move

        return max_rating_value, max_rating_move

    _, move = (
        max_value(turn, MIN_RATING, MAX_RATING, 0)
        if turn == BLACK_PIECE
        else min_value(turn, MIN_RATING, MAX_RATING, 0)
    )
    if move is None:
        raise Exception("cannot calculate move sequence")

    return move
