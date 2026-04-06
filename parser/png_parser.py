import chess.pgn
import numpy as np
import os 


# https://python-chess.readthedocs.io/en/latest/core.html#colors

CHESS_PIECE_TYPES = {
    chess.PAWN: 1,
    chess.KNIGHT: 2,
    chess.BISHOP: 3,
    chess.ROOK: 4,
    chess.QUEEN: 5,
    chess.KING: 6
}

CHESS_COLORS = {
    chess.WHITE: True,
    chess.BLACK: False
}


# Configuration 

MAX_LEN = 100 # Max number of moves to process per game (to limit tensor size)
CHANNELS = 17 # 12 for pieces, 1 for side to move, 4 for castling rights
CHUNK_SIZE = 1000 # Number of games to process in one chunk (adjust based on memory constraints)

def parse_pgn_file(file_path):
    with open(file_path) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            yield game


def get_clean_ratings(headers):
  
    w_elo = headers.get("WhiteElo") or headers.get("WhiteRating")
    b_elo = headers.get("BlackElo") or headers.get("BlackRating")

    if w_elo and b_elo and w_elo != "?" and b_elo != "?":
        try:
            return [int(w_elo), int(b_elo)]
        except ValueError:
            return None
    return None

def process_game(game):

    # Get ranking of each player - fallback should be changed 
    ratings = get_clean_ratings(game.headers)
    if ratings is None:
        print("Skipping game due to missing or invalid ratings.")
        return None
    
    board = game.board()
    game_tensors = []

    for move in game.mainline_moves():
        if len(game_tensors) >= MAX_LEN:
            break
        game_tensors.append(board_to_tensor(board))
        board.push(move)

    if len(game_tensors) == 0:
        return None # Ignore games with no moves
    return np.array(game_tensors, dtype=np.int8), ratings


def board_to_tensor(board): 
    # 17 chanels for board state
    # 1 channels to signal the side to move
    # 2 channels each for castling rights ()
    # 6 channels each for the pieces (each piece has its own channel)
    tensor = np.zeros((CHANNELS, 8, 8), dtype=np.int8)

    # 1. Piece Placement (Channels 0-11)
    for color in [chess.WHITE, chess.BLACK]:
        # Base channel: 0 for white, 6 for black
        channel_offset = 0 if color == chess.WHITE else 6
        
        for piece_type in range(1, 7): # 1=Pawn, ..., 6=King
            # Get bitboard for the current piece type and color
            bb = board.pieces(piece_type, color)
            # Convert bitboard to square coordinates (list from 0 to 63)
            for sq in bb:
                row, col = divmod(sq, 8)
                tensor[channel_offset + piece_type - 1, row, col] = 1

    # 2. Side to Move (Channel 12)
    if board.turn == chess.WHITE:
        tensor[12, :, :] = 1 # Whole board to 1

    # 3. Castling Rights (Channels 13-16)
    # We use slicing [:, :], to fill the entire 8x8 matrices at once    
    if board.has_kingside_castling_rights(chess.WHITE):  tensor[13, :, :] = 1
    if board.has_queenside_castling_rights(chess.WHITE): tensor[14, :, :] = 1
    if board.has_kingside_castling_rights(chess.BLACK):  tensor[15, :, :] = 1
    if board.has_queenside_castling_rights(chess.BLACK): tensor[16, :, :] = 1

    return tensor

def add_padding(tensor):
    if tensor.ndim < 4: 
        return np.zeros((MAX_LEN, CHANNELS, 8, 8), dtype=np.int8)

    padded = np.zeros((MAX_LEN, CHANNELS, 8, 8), dtype=np.int8)
    length = min(tensor.shape[0], MAX_LEN)
    padded[:length] = tensor[:length]

    return padded




if __name__ == "__main__":
    output_dir = "processed_data"
    os.makedirs(output_dir, exist_ok=True)

    X_batch, Y_batch = [], []
    chunk_id = 0

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = "/home/playercoach/SEM I/SzUM/ficsgamesdb_202601_chess_nomovetimes_1366105.pgn"
    for game in parse_pgn_file(file_path):
        result = process_game(game)
        if result is not None:
            game_tensors, ratings = result
            game_tensors = add_padding(game_tensors)
            X_batch.append(game_tensors)
            Y_batch.append([int(ratings[0]), int(ratings[1])])

        # Save chunks 
        if len(X_batch) >= CHUNK_SIZE:
            out_path = os.path.join(output_dir, f"chunk_{chunk_id}.npz")
            np.savez_compressed(out_path, x=np.array(X_batch), y=np.array(Y_batch))
            print(f"Saved {out_path}")
            X_batch, Y_batch = [], []
            chunk_id += 1
    
