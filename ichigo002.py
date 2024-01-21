from typing import List, Union
import numpy as np
from IPython.display import clear_output
import time
import os
import random

BLACK = -1  # 黒
WHITE = 1   # 白
EMPTY = 0   # 空

def init_board(N:int=8):
    """
    ボードを初期化する
    N: ボードの大きさ　(N=8がデフォルト値）
    """
    board = np.zeros((N, N), dtype=int)
    C0 = N//2
    C1 = C0-1
    board[C1, C1], board[C0, C0] = WHITE, WHITE  # White
    board[C1, C0], board[C0, C1] = BLACK, BLACK  # Black
    return board

def count_board(board, piece=EMPTY):
    return np.sum(board == piece)

# Emoji representations for the pieces
BG_EMPTY = "\x1b[42m"
BG_RESET = "\x1b[0m"

stone_codes = [
    f'{BG_EMPTY}⚫️{BG_RESET}',
    f'{BG_EMPTY}🟩{BG_RESET}',
    f'{BG_EMPTY}⚪️{BG_RESET}',
]

# stone_codes = [
#     f'黒',
#     f'・',
#     f'白',
# ]

def stone(piece):
    return stone_codes[piece+1]

def display_clear():
    os.system('clear')
    clear_output(wait=True)

BLACK_NAME=''
WHITE_NAME=''

def display_board(board, clear=True, sleep=0, black=None, white=None):
    """
    オセロ盤を表示する
    """
    global BLACK_NAME, WHITE_NAME
    if clear:
        clear_output(wait=True)
    if black:
        BLACK_NAME=black
    if white:
        WHITE_NAME=white
    for i, row in enumerate(board):
        for piece in row:
            print(stone(piece), end='')
        if i == 1:
            print(f'  {BLACK_NAME}')
        elif i == 2:
            print(f'   {stone(BLACK)}: {count_board(board, BLACK):2d}')
        elif i == 3:
            print(f'  {WHITE_NAME}')
        elif i == 4:
            print(f'   {stone(WHITE)}: {count_board(board, WHITE):2d}')
        else:
            print()  # New line after each row
    if sleep > 0:
        time.sleep(sleep)

def all_positions(board):
    N = len(board)
    return [(r, c) for r in range(N) for c in range(N)]

# Directions to check (vertical, horizontal)
directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)]

def is_valid_move(board, row, col, player):
    # Check if the position is within the board and empty
    N = len(board)
    if row < 0 or row >= N or col < 0 or col >= N or board[row, col] != 0:
        return False

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < N and 0 <= c < N and board[r, c] == -player:
            while 0 <= r < N and 0 <= c < N and board[r, c] == -player:
                r, c = r + dr, c + dc
            if 0 <= r < N and 0 <= c < N and board[r, c] == player:
                return True
    return False

def get_valid_moves(board, player):
    return [(r, c) for r, c in all_positions(board) if is_valid_move(board, r, c, player)]

def flip_stones(board, row, col, player):
    N = len(board)
    stones_to_flip = []
    for dr, dc in directions:
        directional_stones_to_flip = []
        r, c = row + dr, col + dc
        while 0 <= r < N and 0 <= c < N and board[r, c] == -player:
            directional_stones_to_flip.append((r, c))
            r, c = r + dr, c + dc
        if 0 <= r < N and 0 <= c < N and board[r, c] == player:
            stones_to_flip.extend(directional_stones_to_flip)
    return stones_to_flip

def display_move(board, row, col, player):
    stones_to_flip = flip_stones(board, row, col, player)
    board[row, col] = player
    display_board(board, sleep=0.3)
    for r, c in stones_to_flip:
        board[r, c] = player
        display_board(board, sleep=0.1)
    display_board(board, sleep=0.6)

def find_eagar_move(board, player):
    valid_moves = get_valid_moves(board, player)
    max_flips = 0
    best_result = None
    for r, c in valid_moves:
        stones_to_flip = flip_stones(board, r, c, player)
        if max_flips < len(stones_to_flip):
            best_result = (r, c)
            max_flips = len(stones_to_flip)
    return best_result

class OthelloAI(object):
    def __init__(self, face, name):
        self.face = face
        self.name = name

    def __repr__(self):
        return f"{self.face}{self.name}"

    def move(self, board: np.array, piece: int)->tuple[int, int]:
        valid_moves = get_valid_moves(board, piece)
        return valid_moves[0]

    def say(self, board: np.array, piece: int)->str:
        if count_board(board, piece) >= count_board(board, -piece):
            return 'やったー'
        else:
            return 'がーん'

class OchibiAI(OthelloAI):
    def __init__(self, face, name):
        self.face = face
        self.name = name

    def move(self, board: np.array, piece: int)->tuple[int, int]:
        valid_moves = get_valid_moves(board, piece)
        return valid_moves[0]

import traceback

def board_play(player: OthelloAI, board, piece: int):
    display_board(board, sleep=0)
    if len(get_valid_moves(board, piece)) == 0:
        print(f"{player}は、置けるところがありません。スキップします。")
        return True
    try:
        start_time = time.time()
        r, c = player.move(board.copy(), piece)
        end_time = time.time()
    except:
        print(f"{player.face}{player.name}は、エラーを発生させました。反則まけ")
        traceback.print_exc()
        return False
    if not is_valid_move(board, r, c, piece):
        print(f"{player}が返した({r},{c})には、置けません。反則負け。")
        return False
    display_move(board, r, c, piece)
    return True

def comment(player1: OthelloAI, player2: OthelloAI, board):
    try:
        print(f"{player1}: {player1.say(board, BLACK)}")
    except:
        pass
    try:
        print(f"{player2}: {player2.say(board, WHITE)}")
    except:
        pass

def game(player1: OthelloAI, player2: OthelloAI,N=6):
    board = init_board(N)
    display_board(board, black=f'{player1}', white=f'{player2}')
    while count_board(board, EMPTY) > 0:
        if not board_play(player1, board, BLACK):
            break
        if not board_play(player2, board, WHITE):
            break
    comment(player1, player2, board)

class RandomAI(OthelloAI):
    def __init__(self, face, name):
        self.face = face
        self.name = name

    def move(self, board, color: int)->tuple[int, int]:
        """
        ボードが与えられたとき、どこに置くか(row,col)を返す
        """
        valid_moves = get_valid_moves(board, color)
        # ランダムに選ぶ
        selected_move = random.choice(valid_moves)
        return selected_move

class IchigoAI(OthelloAI):
    def __init__(self, face, name, depth=3, exploration_weight=1.41, early_game_weight=2.0, mid_game_weight=1.5, end_game_weight=1.0):
        super().__init__(face, name, depth)
        self.exploration_weight = exploration_weight
        self.early_game_weight = early_game_weight
        self.mid_game_weight = mid_game_weight
        self.end_game_weight = end_game_weight

    def evaluate(self, board, color):
        piece_diff = count_board(board, color) - count_board(board, -color)
        mobility_diff = len(get_valid_moves(board, color)) - len(get_valid_moves(board, -color))
        stability_diff = self.stability_score(board, color) - self.stability_score(board, -color)
        corner_diff = self.corner_score(board, color) - self.corner_score(board, -color)

        game_phase = self.determine_game_phase(board)
        if game_phase == "early":
            return self.early_game_weight * (piece_diff + 2 * mobility_diff + 3 * stability_diff + 5 * corner_diff)
        elif game_phase == "mid":
            return self.mid_game_weight * (piece_diff + 2 * mobility_diff + 3 * stability_diff + 5 * corner_diff)
        else:
            return self.end_game_weight * (piece_diff + 2 * mobility_diff + 3 * stability_diff + 5 * corner_diff)

    def determine_game_phase(self, board):
        empty_squares = count_board(board, EMPTY)
        if empty_squares > len(board) * len(board) * 0.6:
            return "early"
        elif empty_squares > len(board) * len(board) * 0.2:
            return "mid"
        else:
            return "end"

    def stability_score(self, board, color):
        stable_score = 0
        for r in range(len(board)):
            for c in range(len(board[r])):
                if board[r, c] == color:
                    stable_score += self.get_stability_at_position(board, r, c)
        return stable_score

    def get_stability_at_position(self, board, row, col):
        stability = 0
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r, c] == 0:
                r, c = r + dr, c + dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r, c] == board[row, col]:
                stability += 1
        return stability

    def corner_score(self, board, color):
        corners = [(0, 0), (0, len(board) - 1), (len(board) - 1, 0), (len(board) - 1, len(board) - 1)]
        corner_count = 0
        for corner in corners:
            if board[corner[0], corner[1]] == color:
                corner_count += 1
                corner_count += self.get_mobility_around_corner(board, corner[0], corner[1], color)
        return corner_count

    def get_mobility_around_corner(self, board, row, col, color):
        mobility = 0
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r, c] == 0:
                r, c = r + dr, c + dc
                mobility += 1
        return mobility
