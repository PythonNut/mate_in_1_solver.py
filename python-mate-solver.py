import chess
import random
import itertools

def verify_board(brd):
  if len(brd.pieces(chess.KING, chess.BLACK)) != 1:
      return False
  if len(brd.pieces(chess.KING, chess.WHITE)) != 1:
      return False
  if brd.is_game_over():
      return False
  if brd.was_into_check():
      return False
  if brd.is_check():
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

    for _ in range(random.randint(1, 10)):
        square = get_random_square()
        piece = get_random_piece("PNBRQ")
        if not brd.piece_at(square):
          brd.set_piece_at(square, piece)

    return brd

def count_mates_in_1(brd):
    print(brd, "\n")
    count = 0
    for move in brd.legal_moves:
        cpy = brd.copy()
        cpy.push(move)
        print(cpy, "\n")
        if cpy.is_checkmate():
            count += 1
    return count

def blend_boards(brd1, brd2):
    res = chess.Board(None)
    for r, f in itertools.product(*[range(8)]*2):
        square = chess.square(r, f)
        if random.getrandbits(1):
          res.set_piece_at(square, brd1.piece_at(square))
        else:
          res.set_piece_at(square, brd2.piece_at(square))

    wkings = res.pieces(chess.KING, chess.WHITE)
    bkings = res.pieces(chess.KING, chess.BLACK)
    if len(wkings) == 0:
        if random.getrandbits(1):
            wking = brd1.pieces(chess.KING, chess.WHITE)
        else:
            wking = brd2.pieces(chess.KING, chess.WHITE)
        for square in wking:
          res.set_piece_at(square, chess.Piece.from_symbol("K"))

    elif len(wkings) > 1:
        kept = random.choice(list(wkings))
        for square in wkings:
            if square != kept:
                res.remove_piece_at(square)

    if len(bkings) == 0:
        if random.getrandbits(1):
            bking = brd1.pieces(chess.KING, chess.BLACK)
        else:
            bking = brd2.pieces(chess.KING, chess.BLACK)
        for square in bking:
            res.set_piece_at(square, chess.Piece.from_symbol("k"))

    elif len(bkings) > 1:
        kept = random.choice(list(bkings))
        for square in bkings:
            if square != kept:
                res.remove_piece_at(square)

    return res

b1 = generate_starting_board()
b2 = generate_starting_board()
print(b1,"\n")
print(b2,"\n")
res = blend_boards(b1, b2)
print(res, verify_board(res))
