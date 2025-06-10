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
    
    def is_multiple(self, raypos: tuple[int, int], direction: tuple[int, int], board_length: int, board_width: int) -> bool:
        if direction[0] == 0:
            if raypos[0] != 0:
                return False
        else:
            if raypos[0] % direction[0] != 0:
                return False
        
        if direction[1] == 0:
            if raypos[1] != 0:
                return False
        else:
            if raypos[1] % direction[1] != 0:
                return False
        
        return True
        

        
class Pawn(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 0)
        

class Bishop(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 1)

class Rook(Piece):
    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 2)

    def generate_rays(self, position: tuple[int, int], board_length: int, board_width: int):
        bitboard = ["0"] * board_length * board_width
        print(f"Position: {position}")
        
        # Get rays
        for y in range(board_length):
            for x in range(board_width):
                posdiff = (y - position[0], x - position[1])
                for direction in self.DIRECTIONS:
                    if self.is_multiple(posdiff, direction, board_length, board_width):
                        bitboard[y * board_length + x] = "1"
                        break
                  
        # Remove piece itself
        bitboard[position[0] * board_length + position[1]] = "0"
        
        bitboard = "".join(bitboard)
        
        bitboard = int(bitboard, 2)
        return bitboard

                        



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