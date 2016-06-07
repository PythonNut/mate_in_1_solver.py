import chess
import random

board = chess.Board(None)

def verify_board(brd):
  if len(brd.pieces(chess.KING, chess.BLACK)) != 1:
      return False
  if len(brd.pieces(chess.KING, chess.WHITE)) != 1:
      return False
  if brd.is_game_over():
      return False
  return True

def get_random_square():
   return chess.square(random.randint(0, 7), random.randint(1, 7))

def get_random_piece(pieces):
    return chess.Piece.from_symbol(random.choice(pieces))

def generate_starting_board():
    brd = chess.Board(None)
    wking = get_random_square()
    bking = get_random_square()
    brd.set_piece_at(wking, chess.Piece.from_symbol("K"))
    brd.set_piece_at(bking, chess.Piece.from_symbol("k"))

    for i in range(random.randint(1,10)):
        square = get_random_square()
        piece = get_random_piece("PNBRQ")
        if not brd.piece_at(square):
          brd.set_piece_at(square, piece)

    return brd

def count_mates_in_1(brd):
    print(brd,"\n")
    count = 0
    for move in brd.legal_moves:
        cpy = brd.copy()
        cpy.push(move)
        print(cpy,"\n")
        if cpy.is_checkmate():
            count += 1
    return count

print(count_mates_in_1(generate_starting_board()))
