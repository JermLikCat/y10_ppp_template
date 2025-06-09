import chess_game
from board import Board

# Use a bitboard for pieces!

class Piece():
    def __init__(self, board: Board, side: bool):
        self.side = side # True = White, False = Black
        self.directions = []
        self.board = board

    def encode_move(self, move: str) -> int:
        """Encodes move into an integer from algebraic notation. In the form of: piece_type - rank (as required) - location_y - location_x"""
        pass

        
class Pawn(Piece):
    def __init__(self):
        print(self.side)

class Bishop(Piece):
    def __init__(self):
        pass

class Queen(Piece):
    def __init__(self):
        pass

class Rook(Piece):
    def __init__(self):
        pass

class Knight(Piece):
    def __init__(self):
        self.directions = [(1, 2), (2, 1), (2, -1), (-1, 2), (1, -2), (-2, 1), (-1, -2), (-2, -1)]

class King(Piece):
    def __init__(self):
        pass

class EmptyPiece(Piece):
    def __init__(self, side = True):
        # Side for empty piece does not matter
        pass