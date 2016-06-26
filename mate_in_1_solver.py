import chess
import math
import random
import time
import itertools
import decimal
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

def get_random_piece(pieces = "NBRQ"):
    return chess.Piece.from_symbol(random.choice(pieces))

def get_random_legal_piece(brd):
    promotions = 0
    pieces=set()
    n = len(brd.pieces(chess.KNIGHT, chess.WHITE))
    b = len(brd.pieces(chess.BISHOP, chess.WHITE))
    r = len(brd.pieces(chess.ROOK, chess.WHITE))
    q = len(brd.pieces(chess.QUEEN, chess.WHITE))

    promotions += max(n - 2, 0)
    promotions += max(b - 2, 0)
    promotions += max(r - 2, 0)
    promotions += max(q - 1, 0)

    if promotions < 8:
        pieces=set("NBRQ")
    else:
        if n < 2:
            pieces.add("N")
        if b < 2:
            pieces.add("B")
        if r < 2:
            pieces.add("R")
        if q < 1:
            pieces.add("Q")

    if pieces:
        return get_random_piece(list(pieces))

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
        square = random.choice(list(~get_occupied(brd)))
        piece = get_random_legal_piece(brd)
        if piece:
            res.set_piece_at(square, piece)

    else:
        # move a piece
        fr = random.choice(list(get_occupied(brd, "KPNBRQ")))
        to = random.choice(list(~get_occupied(brd, "kKPNBRQ")))
        piece = res.piece_at(fr)
        res.remove_piece_at(fr)
        res.set_piece_at(to, piece)

    return res
