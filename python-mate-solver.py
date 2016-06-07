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

def get_random_piece(pieces = "PNBRQ"):
    return chess.Piece.from_symbol(random.choice(pieces))

def get_occupied(brd, pieces = "PNBRQ"):
    pieces_and_colors = []
    for piece in pieces:
        piece = chess.Piece.from_symbol(piece)
        pieces_and_colors.append((piece.piece_type, piece.color))
    res = chess.SquareSet()
    for piece, color in pieces_and_colors:
        try:
            for square in brd.pieces(piece, color):
                res.add(square)
        except UnboundLocalError:
            pass
    return res

def generate_starting_board():
    brd = chess.Board(None)
    wking = get_random_square()
    bking = get_random_square()
    brd.set_piece_at(wking, chess.Piece.from_symbol("K"))
    brd.set_piece_at(bking, chess.Piece.from_symbol("k"))

    for _ in range(random.randint(1, 10)):
        square = get_random_square()
        piece = get_random_piece()
        if not brd.piece_at(square):
          brd.set_piece_at(square, piece)

    return brd

def count_mates_in_1(brd):
    count = 0
    for move in brd.legal_moves:
        cpy = brd.copy()
        cpy.push(move)
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

def mutate_board(brd):
    res = brd.copy()
    mutate_type = random.randint(1, 4)
    if mutate_type == 1:
        return res
    elif mutate_type == 2:
        # Remove a piece
        try:
          square = random.choice(list(get_occupied(brd)))
        except IndexError:
            return res
        res.remove_piece_at(square)
    elif mutate_type == 3:
        # Add a piece
        square = get_random_square()
        piece = get_random_piece()
        if not brd.piece_at(square):
            res.set_piece_at(square, piece)
    else:
        fr = random.choice(list(get_occupied(brd, "kKPNBRQ")))
        to = random.choice(list(~get_occupied(brd, "kKPNBRQ")))
        piece = res.piece_at(fr)
        res.remove_piece_at(fr)
        res.set_piece_at(to, piece)
    return res

def create_initial_generation(n):
    gen = []
    count = 0
    while True:
        board = generate_starting_board()
        if verify_board(board):
            gen.append(board)
            count += 1
            if count == n:
                break
    return gen

def sort_generation_by_fitness(gen):
    return list(reversed(sorted(gen, key=count_mates_in_1)))

def create_new_generation(gen_sorted, n):
    newgen = []
    top = list(gen_sorted)[:n//10]
    count = 0
    while True:
        b1 = random.choice(top)
        b2 = random.choice(top)
        newb = mutate_board(blend_boards(b1, b2))
        if verify_board(newb):
          newgen.append(newb)
          count += 1
          if count == n:
              break
    return newgen

def main():
    n = 1000
    gen = create_initial_generation(n)
    while True:
        gen_sorted = sort_generation_by_fitness(gen)
        best = gen_sorted[0]
        print(best)
        print(count_mates_in_1(best))
        gen = create_new_generation(gen_sorted, n)

if __name__ == "__main__":
    main()
