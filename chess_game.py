import board

class ChessGame():
    def __init__(self, side: bool):
        # Side = true -> White, Side = false -> Black
        self.side = side
        self.board  = board.Board()
