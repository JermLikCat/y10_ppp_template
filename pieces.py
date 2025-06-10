import board
# Use a bitboard for pieces!
class Piece():
    def __init__(self, board: board.Board, side: str, id: int):
        """Default initialization for a new piece. IDs: Pawn: 0, Bishop: 1, Rook: 2, Knight: 3, Queen: 4, King: 5, Empty: 6"""
        self.side = side # True = White, False = Black
        self.directions = []
        self.board = board
        # Type of piece, accessible by other functions
        self.id = id

    def encode_move(self, move: str) -> int:
        """Encodes move into an integer from algebraic notation. In the form of: piece_type - rank (as required) - location_y - location_x"""
        pass

        
class Pawn(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 0)
        

class Bishop(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 1)

class Rook(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 2)

class Knight(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 3)
        self.directions = [(1, 2), (2, 1), (2, -1), (-1, 2), (1, -2), (-2, 1), (-1, -2), (-2, -1)]

class Queen(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 4)

class King(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 5)

class EmptyPiece(Piece):
    def __init__(self, board: board.Board, side = None):
        # Side for empty piece does not matter
        super().__init__(board, side, 6)