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

    for _ in range(random.randint(1, 32)):
        square = get_random_square()
        piece = get_random_piece()
        if not brd.piece_at(square):
          brd.set_piece_at(square, piece)

    return brd

def count_mates_in_1(brd):
    count = 0
    for move in brd.legal_moves:
        brd.push(move)
        if brd.is_checkmate():
            count += 1
        brd.pop()
    return count

def fitness(brd):
    return count_mates_in_1(brd) + 1 - len(get_occupied(brd))/64

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
            progress = str(count).rjust(9, " ")
            print("{}/{} Creating generation".format(progress, n), end="\r")
            if count == n:
                break
    return gen

def score_generation(gen):
    gen_scores = []
    for board in gen:
        gen_scores.append(fitness(board))
        progress = str(len(gen_scores)).rjust(9, ' ')
        print("{}/{} Scoring generation".format(progress, len(gen)), end="\r")
    # gen_sorted = list(zip(gen, gen_scores))
    # gen_sorted.sort(key=lambda x: -x[1])
    return gen_scores

def create_new_generation(gen, gen_scores, n, velocity):
    tournament_size = 4
    newgen = []
    count = 0
    gen_combined = list(zip(gen, gen_scores))
    while True:
        tournament1 = random.sample(range(len(gen_combined)), tournament_size)
        tournament2 = random.sample(range(len(gen_combined)), tournament_size)
        b1 = gen[max(tournament1, key=lambda i: gen_scores[i])]
        b2 = gen[max(tournament2, key=lambda i: gen_scores[i])]
        newb = blend_boards(b1, b2)

        for _ in range(round(random.expovariate(velocity))):
            newb = mutate_board(newb)
        if verify_board(newb):
            newgen.append(newb)
            count += 1
            progress = str(count).rjust(9, " ")
            print("{}/{} Creating generation".format(progress, n), end="\r")
            if count == n:
                break
    return newgen

def main():
    gen_size = 1000
    velocity = 1
    gens_to_keep = 5
    gen = create_initial_generation(gen_size)
    gen_number = 1
    while True:
        gen_scores = score_generation(gen)
        best = max(gen_scores)
        print(gen[gen_scores.index(best)])
        print("Gen {}: {} Mates/{} Mean".format(gen_number, best, sum(gen_scores)/gen_size))
        gen = create_new_generation(gen, gen_scores, gen_size, velocity)
        gen_number += 1

if __name__ == "__main__":
    main()
