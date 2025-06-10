class ChessGame():
    def __init__(self, side: str):
        self.side = side
        from board import Board
        self.board = Board(self, side)
