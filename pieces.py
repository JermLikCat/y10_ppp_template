import chess_game
import board

# Use a bitboard for pieces!

class Piece():
    def __init__(self, board: board.Board, side: bool):
        self.side = side
        self.directions = []
        self.board = board
        self.squares_attacking = []

    # TODO: update_squares_attacking
    def update_squares_attacking(self):
        pass

    def encode_move(self, move: str) -> int:
        """Encodes move into an integer from algebraic notation. In the form of: piece_type - rank (as required) - location_y - location_x"""
        pass

        
class Pawn(Piece):
    def __init__(self):
        pass

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
    def __init__(self):
        pass