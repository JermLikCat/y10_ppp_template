import board
import bitboard
# Use a bitboard for pieces!
class Piece():
    def __init__(self, board: board.Board, side: str, id: int):
        """Default initialization for a new piece. IDs: Pawn: 0, Bishop: 1, Rook: 2, Knight: 3, Queen: 4, King: 5, Empty: 6"""
        self.side = side # "w" for white, "b" for black
        self.directions = []
        self.board = board
        # Type of piece, accessible by other functions
        self.id = id
        self.has_moved = False

    def encode_move(self, move: str) -> int:
        """Encodes move into an integer from algebraic notation. In the form of: piece_type - rank (as required) - location_y - location_x"""
        pass
    
    def is_multiple(self, currentpos: tuple[int, int], raypos: tuple[int, int], direction: tuple[int, int], board_height: int, board_width: int) -> bool:
        
        if direction[0] == 0:
            if raypos[0] != 0:
                return False
        else:
            if raypos[0] % direction[0] != 0:
                return False
            if currentpos[0] == 0 or currentpos[0] == board_height - 1:
                return False
        
        if direction[1] == 0:
            if raypos[1] != 0:
                return False
        else:
            if raypos[1] % direction[1] != 0:
                return False
            if currentpos[1] == 0 or currentpos[1] == board_width - 1:
                return False
            
        if direction[0] != 0 and direction[1] != 0:
            if raypos[0] // direction[0] != raypos[1] // direction[1]:
                return False
        
        return True
    
    def generate_sliding_mask(self, position: tuple[int, int], deltas: list[tuple[int, int]], board_height: int, board_width: int):
        bb = ["0"] * board_height * board_width
        
        """
        Generate rays for a sliding piece for use in magic bbs:
        e.g. for rook in (3, 3):
        . . . . . . . .
        . . # . . . . .
        . # . # # # # .
        . . # . . . . .
        . . # . . . . .
        . . # . . . . .
        . . # . . . . .
        . . . . . . . .
        """
        
        for y in range(board_height):
            for x in range(board_width):
                posdiff = (y - position[0], x - position[1])
                currentpos = (y, x)
                for direction in deltas:
                    if self.is_multiple(currentpos, posdiff, direction, board_height, board_width):
                        bb[y * board_height + x] = "1"
                        break
                  
        # Remove piece itself
        bb[position[0] * board_height + position[1]] = "0"
        
        bb = "".join(bb)
        
        bb = int(bb, 2)
        return bitboard.Bitboard(bb, board_width, board_height)

        
class Pawn(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 0)
        

class Bishop(Piece):
    DIRECTIONS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 1)

class Rook(Piece):
    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 2)


class Knight(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 3)
        self.directions = [(1, 2), (2, 1), (2, -1), (-1, 2), (1, -2), (-2, 1), (-1, -2), (-2, -1)]

class Queen(Piece):
    DIRECTIONS = [(1, 1), (1, -1), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (-1, 0)]
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 4)

class King(Piece):
    def __init__(self, board: board.Board, side: str):
        super().__init__(board, side, 5)

class EmptyPiece(Piece):
    def __init__(self, board: board.Board, side = None):
        # Side for empty piece does not matter
        super().__init__(board, side, 6)