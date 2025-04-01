class ChessGame():
    def __init__(self):
        self.w_board = Board(self)
        self.b_board = Board(self, 'b')
        pass
    
class Board():
    def __init__(self, game: ChessGame, side: str = 'w'):
        self.game = game
        self.side = side
        self.current_board = [[Rook("b"), Knight("b"), Bishop("b"), Queen("b"), King("b"), Bishop("b"), Knight("b"), Rook("b")],
                            [Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b")],
                            ["", "", "", "", "", "", "", ""],
                            ["", "", "", "", "", "", "", ""],
                            ["", "", "", "", "", "", "", ""],
                            ["", "", "", "", "", "", "", ""],
                            [Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w")],
                            [Rook("w"), Knight("w"), Bishop("w"), Queen("w"), King("w"), Bishop("w"), Knight("w"), Rook("w")]]
        if self.side == 'b': # black
            self.current_board = [i[::-1] for i in self.current_board][::-1] # Reverse board
        
    # TODO: squares_attacked

class Piece():
    def __init__(self, game: ChessGame, board: Board, oppboard: Board, side: str):
        self.game = game
        self.board = board
        self.oppboard = oppboard
        self.side = side
        
        
class Pawn(Piece):
    def __init(self):
        pass

class Bishop(Piece):
    def __init(self):
        pass

class Queen(Piece):
    def __init(self):
        pass

class Rook(Piece):
    def __init(self):
        pass

class Knight(Piece):
    def __init(self):
        pass

class King(Piece):
    def __init(self):
        pass