# Example file showing a basic pygame "game loop"
import time
from threading import Thread

import pygame
from pygame.surface import Surface

from checkers.game import (
    BLACK_PIECE,
    WHITE_PIECE,
    Move,
    Piece,
    apply_move,
    check_winner,
    create_board,
    evaluate_board_moves,
    minimax,
)

WIDTH = 800
HEIGHT = 800
ROWS = 8
COLUMNS = 8
PIECE_SIZE = WIDTH // ROWS
PIECE_CENTER_DISTANCE = PIECE_SIZE // 2
PIECE_RADIUS = 45
TARGET_RADIUS = 10

FPS = 60

DARK_SQUARE_COLOR = (118, 150, 86)
LIGHT_SQUARE_COLOR = (238, 238, 210)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


def get_piece_color(piece: int) -> tuple[int, int, int]:
    if piece == BLACK_PIECE:
        return BLACK
    return WHITE


def draw_pieces(surface: Surface, board: list[list[Piece | None]]) -> None:
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece is None:
                continue
            color = get_piece_color(piece.color)
            _ = pygame.draw.circle(
                surface,
                color,
                (
                    j * PIECE_SIZE + PIECE_CENTER_DISTANCE,
                    HEIGHT - (i * PIECE_SIZE + PIECE_CENTER_DISTANCE) - 1,
                ),
                PIECE_RADIUS,
            )

            if piece.is_king:
                _ = pygame.draw.circle(
                    surface,
                    YELLOW,
                    (
                        j * PIECE_SIZE + PIECE_CENTER_DISTANCE,
                        HEIGHT - (i * PIECE_SIZE + PIECE_CENTER_DISTANCE) - 1,
                    ),
                    TARGET_RADIUS,
                )


def draw_targets(surface: Surface, targets: list[tuple[int, int]]) -> None:
    for target in targets:
        x, y = target
        _ = pygame.draw.circle(
            surface,
            RED,
            (
                x * PIECE_SIZE + PIECE_CENTER_DISTANCE,
                HEIGHT - (y * PIECE_SIZE + PIECE_CENTER_DISTANCE) - 1,
            ),
            TARGET_RADIUS,
        )


def draw_board(
    surface: Surface, board: list[list[Piece | None]], targets: list[tuple[int, int]]
) -> None:
    _ = surface.fill(LIGHT_SQUARE_COLOR)
    for i in range(ROWS):
        for j in range(i % 2, COLUMNS, 2):
            _ = pygame.draw.rect(
                surface,
                DARK_SQUARE_COLOR,
                (i * PIECE_SIZE, j * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE),
            )
    draw_pieces(surface, board)
    draw_targets(surface, targets)


def get_square(position: tuple[int, int]) -> tuple[int, int]:
    x, y = position
    column = x // PIECE_SIZE
    row = y // PIECE_SIZE

    return column, ROWS - row - 1


def key_moves_by_position(moves: list[Move]) -> dict[tuple[int, int], list[Move]]:
    moves_by_position: dict[tuple[int, int], list[Move]] = {}
    for move in moves:
        if moves_by_position.get(move.source) is None:
            moves_by_position[move.source] = [move]
        else:
            moves_by_position[move.source].append(move)
    return moves_by_position


def key_moves_by_destination(
    moves: list[Move],
) -> dict[tuple[int, int], Move]:
    moves_by_target: dict[tuple[int, int], Move] = {}
    for move in moves:
        moves_by_target[move.destination] = move
    return moves_by_target


def run_game(
    board: list[list[Piece | None]], is_running: list[bool], winner: list[int | None]
) -> None:
    turn = BLACK_PIECE
    while is_running[0] and winner[0] is None:
        if turn == WHITE_PIECE:
            time.sleep(0.5)
            print("Computer 1 is thinking")

            move = minimax(board, turn)
            apply_move(board, move)

            turn = BLACK_PIECE

            print(f"Computer 1 played {move.source} -> {move.destination}")
        else:
            time.sleep(0.25)
            print("Computer 2 is thinking")

            move = minimax(board, turn)
            apply_move(board, move)

            turn = WHITE_PIECE

            print(f"Computer 2 played {move.source} -> {move.destination}")

        winner[0] = check_winner(board, turn)


def main() -> None:
    _ = pygame.init()
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True

    board = create_board()
    turn = BLACK_PIECE
    moves_by_position = key_moves_by_position(evaluate_board_moves(board, turn))
    available_targets: dict[tuple[int, int], Move] = {}

    is_running = [True]
    winner: list[int | None] = [None]
    thread = Thread(target=run_game, args=(board, is_running, winner))
    thread.start()

    while is_running[0] or winner[0]:
        draw_board(surface, board, [target for target in available_targets])
        pygame.display.flip()
        _ = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running[0] = False
        #     if event.type == pygame.MOUSEBUTTONUP:
        #         square = get_square(event.pos)
        #         move = available_targets.get(square)
        #         if move is not None:
        #             apply_move(board, move)
        #             turn = WHITE_PIECE

        #             moves_by_position = {}
        #             available_targets = {}

        #             draw_board(surface, board, [target for target in available_targets])
        #             pygame.display.flip()
        #             clock.tick(FPS)

        #             continue

        #         available_moves = moves_by_position.get(square)
        #         if available_moves is None:
        #             available_targets = {}
        #         else:
        #             available_targets = key_moves_by_destination(available_moves)

        # draw_board(surface, board, [target for target in available_targets])
        # pygame.display.flip()
        # clock.tick(FPS)

    thread.join()
    pygame.quit()

    if winner[0] == BLACK_PIECE:
        print("Black won")
    elif winner[0] == WHITE_PIECE:
        print("White won")


if __name__ == "__main__":
    main()
