class ChessGame():
    def __init__(self):
        self.w_board = Board(self)
        self.b_board = Board(self, 'b')
        pass
    
class Board():
    def __init__(self, game: ChessGame, side: str = 'w'):
        self.game = game
        self.side = side
        self.current_board = [[Rook("b", self), Knight("b", self), Bishop("b", self), Queen("b", self), King("b", self), Bishop("b", self), Knight("b", self), Rook("b", self)],
                            [Pawn("b", self), Pawn("b", self), Pawn("b", self), Pawn("b", self), Pawn("b", self), Pawn("b", self), Pawn("b", self), Pawn("b", self)],
                            ["", "", "", "", "", "", "", ""],
                            ["", "", "", "", "", "", "", ""],
                            ["", "", "", "", "", "", "", ""],
                            ["", "", "", "", "", "", "", ""],
                            [Pawn("w", self), Pawn("w", self), Pawn("w", self), Pawn("w", self), Pawn("w", self), Pawn("w", self), Pawn("w", self), Pawn("w", self)],
                            [Rook("w", self), Knight("w", self), Bishop("w", self), Queen("w", self), King("w", self), Bishop("w", self), Knight("w", self), Rook("w", self)]]
        self.attacked_sqaures = self.update_attacked_squares(self.current_board)
        self.board_length = len(self.current_board[0])
        self.board_width = len(self.current_board)
        if self.side == 'b': # black
            self.current_board = [i[::-1] for i in self.current_board][::-1] # Reverse board
        
    # TODO: update_attacked_squares
    def update_attacked_squares(current_board) -> list:
        return []


class Piece(Board):
    def __init__(self, side: str, board: Board):
        self.side = side
        self.directions = []
        self.board = board
        self.squares_attacking = []

    # TODO: update_squares_attacking
    def update_squares_attacking(self):
        pass

    def encode_move(self, move: str) -> int:
        """Encodes move into an integer from algebraic notation. In the form of: id - piece_type - location_y - location_x"""
        

    def check_in_bounds(self, end: int, board: Board):
        pass

    def check_validity(self, start: int, end: int, directions: list, board: Board):
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