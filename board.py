import chess_game
import pieces
class Board():
    def __init__(self, game: chess_game.ChessGame, board: list[list[pieces.Piece]], side: bool = True):
        self.game = game
        self.side = side
        # self.board = board
        self.board = [
            [pieces.Rook(self, False), pieces.Knight(self, False), pieces.Bishop(self, False), pieces.Queen(self, False), pieces.King(self, False), pieces.Bishop(self, False), pieces.Knight(self, False), pieces.Rook(self, False)],
            [pieces.Pawn(self, False), pieces.Pawn(self, False), pieces.Pawn(self, False), pieces.Pawn(self, False), pieces.Pawn(self, False), pieces.Pawn(self, False), pieces.Pawn(self, False), pieces.Pawn(self, False)],
            [pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self)],
            []
            ]
        self.attacked_sqaures = self.update_attacked_squares(self.board)
        self.board_length = len(self.board[0])
        self.board_width = len(self.board)

    def generate_all_possible_moves(self):
        pass
