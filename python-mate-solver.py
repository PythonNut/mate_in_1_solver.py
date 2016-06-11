import chess
import math
import random
import time
import itertools
import multiprocessing as mp
try:
    import numpy as np
    import matplotlib.pyplot as plt
    PLOTTING = True
except:
    PLOTTING = False

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

    promotions = 0
    p = len(brd.pieces(chess.PAWN, chess.WHITE))
    n = len(brd.pieces(chess.KNIGHT, chess.WHITE))
    b = len(brd.pieces(chess.BISHOP, chess.WHITE))
    r = len(brd.pieces(chess.ROOK, chess.WHITE))
    q = len(brd.pieces(chess.QUEEN, chess.WHITE))

    promotions += max(n - 2, 0)
    promotions += max(b - 2, 0)
    promotions += max(r - 2, 0)
    promotions += max(q - 1, 0)

    if p + promotions > 8:
        return False

    return True

def get_random_square():
   return chess.square(random.randint(0, 7), random.randint(0, 7))

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

def generate_starting_board(_=None):
    while True:
        brd = chess.Board(None)
        wking = get_random_square()
        bking = chess.square(4, 4)
        brd.set_piece_at(wking, chess.Piece.from_symbol("K"))
        brd.set_piece_at(bking, chess.Piece.from_symbol("k"))

        for _ in range(random.randint(1, 16)):
            square = get_random_square()
            piece = get_random_piece()
            if not brd.piece_at(square):
              brd.set_piece_at(square, piece)

        if verify_board(brd):
            return brd


def count_mates_in_1(brd):
    count = 0
    moves = brd.legal_moves
    for move in moves:
        brd.push(move)
        if brd.is_checkmate():
            count += 1
        brd.pop()
    return count, len(moves)

def fitness(brd):
    return count_mates_in_1(brd)

def blend_boards(brd1, brd2, p=0.5):
    res = chess.Board(None)
    for r, f in itertools.product(*[range(8)]*2):
        square = chess.square(r, f)
        if random.random() > p:
          res.set_piece_at(square, brd1.piece_at(square))
        else:
          res.set_piece_at(square, brd2.piece_at(square))

    wkings = res.pieces(chess.KING, chess.WHITE)
    bkings = res.pieces(chess.KING, chess.BLACK)
    if len(wkings) == 0:
        if random.random() > p:
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
        if random.random() > p:
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
        # Substitute a piece
        try:
            square = random.choice(list(get_occupied(brd)))
        except IndexError:
            return res
        piece = get_random_piece()
        res.set_piece_at(square, piece)

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
        # move a piece
        fr = random.choice(list(get_occupied(brd, "KPNBRQ")))
        to = random.choice(list(~get_occupied(brd, "kKPNBRQ")))
        piece = res.piece_at(fr)
        res.remove_piece_at(fr)
        res.set_piece_at(to, piece)

    return res

def create_initial_generation(n, thread_pool):
    gen = [None] * n

    new_boards = thread_pool.imap(generate_starting_board, range(n), 10)
    start_time = time.perf_counter()
    for i, brd in enumerate(new_boards):
        gen[i] = brd
        if i%10 == 0:
            progress = str(i).rjust(9, " ")
            velocity = round(i/(time.perf_counter() - start_time))
            print("{}/{} Creating generation {}B/s".format(progress, n, velocity), end="\r")

    return gen

def score_generation(gen, thread_pool):
    gen_scores = np.zeros(len(gen))
    total_positions = 0
    velocity = 0

    start_time = time.time()
    fitnesses = thread_pool.imap(fitness, gen, 10)
    last_status = 0
    for i, (fit, moves) in enumerate(fitnesses):
        gen_scores[i] = fit
        total_positions += moves
        if total_positions - last_status > 1000:
            last_status = total_positions
            velocity = round(total_positions/(time.time() - start_time))
            progress = str(i).rjust(9, ' ')
            print("{}/{} Scoring generation {}N/s".format(progress, len(gen), velocity), end="\r")
    print(" "*80, end="\r")
    return gen_scores

def select_from_current_generation(gen, gen_scores, n):
    select_rate = 0.85

    k = round(n * select_rate)
    total_fitness = np.sum(gen_scores)
    p = total_fitness/k
    start = np.random.random() * p
    keep = []
    i = 0
    cum_fit = 0
    fits = np.arange(start, total_fitness, p)
    for floor_cum_fit in fits:
        while cum_fit + gen_scores[i] < floor_cum_fit:
            cum_fit += gen_scores[i]
            i += 1
        keep.append(gen[i])

    assert len(keep) == k
    return keep

def create_new_generation(parents, n):
    crossover_rate = 0.85
    mutation_rate = 0.05

    newgen = [None] * n
    total_tries = 0

    count = 0
    while True:
        b1, b2 = random.sample(parents, 2)
        if random.random() < crossover_rate:
            newb = blend_boards(b1, b2)
        else:
            newb = random.choice([b1, b2])

        if random.random() < mutation_rate:
            newb = mutate_board(newb)

        total_tries += 1
        if verify_board(newb):
            newgen[count] = newb
            count += 1
            progress = str(count).rjust(9, " ")
            print("{}/{} Creating generation".format(progress, n), end="\r")

        if count == n:
            break

    return newgen

def main():
    if PLOTTING:
        plt.ion()
        plt.show()
    gen_size = 1000
    gens_to_keep = 5
    p = mp.Pool()

    gen = create_initial_generation(gen_size, p)
    gen_number = 1
    prev_gens = []
    while True:
        gen_scores = score_generation(gen, p)
        if PLOTTING:
            prev_gens.append(gen_scores)
            if len(prev_gens) > gens_to_keep:
                prev_gens = prev_gens[-gens_to_keep:]
            hists = []
            plt.figure(1)
            plt.clf()
            plot_curves_count = 10
            for i, g in enumerate(prev_gens[-plot_curves_count:]):
                opacity = 0.2
                if i == plot_curves_count - 1:
                    opacity = 1
                X = np.sort(g)
                Y = np.linspace(0, 1, len(g), endpoint=False)
                hists.append(plt.plot(X, Y, alpha=opacity, label="Gen {}".format(gen_number-len(prev_gens)+i+1)))
            plt.figure(2)
            plt.clf()
            for pct in [0, 25, 75, 100]:
                pct_fun = lambda arr: np.percentile(arr, pct)
                plt.plot(range(len(prev_gens)), list(map(pct_fun, prev_gens)))
            plt.plot(range(len(prev_gens)), list(map(np.mean, prev_gens)))
            plt.draw()
            plt.pause(0.001)

        best = max(gen_scores)
        print(gen[np.nonzero(gen_scores == best)[0][0]])
        print("Gen {}: {} Mates/{} Mean".format(gen_number, best, sum(gen_scores)/gen_size))
        parents = select_from_current_generation(gen, gen_scores, gen_size)
        gen = create_new_generation(parents, gen_size)
        gen_number += 1

if __name__ == "__main__":
    main()
