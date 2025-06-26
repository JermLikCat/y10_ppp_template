from board import Board

class ChessGame():
    def __init__(self, side: str):
        self.side = side
        self.board = Board(self, side)
        # self.game_loop()
        
    """def game_loop(self):
        while True:
            self.board.display_board()
            self.board.display_bitboard(self.board.piece_bitboards[0])
            
            print("Please choose your move.")
            print("From: (Please input in the form of: xy)")
            from_square = input()
            print("To: (Please input in the form of xy)")
            to_square = input()
            
            from_pos = int(from_square[1]) * self.board.BOARD_WIDTH + int(from_square[0])
            to_pos = int(to_square[1]) * self.board.BOARD_WIDTH + int(to_square[0])
            
            print("(Debug): Enter type of move")
            move_id = int(input())
            
            possible_moves = self.board.generate_legal_moves()
            
            move = self.board.encode_move(move_id, from_pos, to_pos)
            if move in possible_moves:
                self.board.move(move)
            else:
                print("Illegal move!")
            """
            