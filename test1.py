class Piece:
    def __init__(self, value, piece):
        self.value = value
        self.piece = piece
        
    def doublevalue(self):
        self.value *= 2
        
board = [
    [Piece(1, 'A'), Piece(1, 'B'), Piece(1, 'C')],
    [Piece(2,"F")],
    [Piece(3,"G")]
]

board[0][1].doublevalue()
print(board[0][1].value)
class BoardClass:
    def __init__(self,board):
        self.board = board
        self.tile = "Skibidi"
    def display_board(self):
        for row in self.board:
            for item in row:
                print(item.piece,end = " ")
            print("")
            
    def calculate_total_value(self):
        total = 0
        for row in self.board:
            for item in row:
                total += item.value
                
        return total
john = BoardClass(board)
john.display_board()
john.board[0][1].piece = "Z"
john.board[0][1].value = 10

 
john.display_board()
print(john.calculate_total_value())