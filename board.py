import chess_game
import pieces
ssssss = True
#test
class Board():
    def __init__(self, game: chess_game.ChessGame, board: list[list[pieces.Piece]], side: str = 'w'):
        self.game = game
        self.side = side
        self.current_board = [[Rook("b", True), Knight("b", 1), Bishop("b", 1), Queen("b", self), King("b", self), Bishop("b", self), Knight("b", self), Rook("b", self)],
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