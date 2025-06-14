import bitboard
import magicnums

class Board():
    """ Piece IDs: Pawn: 0, Bishop: 1, Rook: 2, Knight: 3, Queen: 4, King: 5, Empty: 6"""
    PAWN_ID = 0
    BISHOP_ID = 1
    ROOK_ID = 2
    KNIGHT_ID = 3
    QUEEN_ID = 4
    KING_ID = 5
    EMPTY_ID = 6

    def __init__(self, game, side: str = "w"):
        self.game = game
        self.side = side
        self.wmaterial = []
        self.bmaterial = []
        
        # Setup pieces, and set board height, width and area
        self.setup_board()
        
        self.white_bitboard: bitboard.Bitboard = bitboard.Bitboard(0, self.board_width, self.board_height)
        self.black_bitboard: bitboard.Bitboard = bitboard.Bitboard(0, self.board_width, self.board_height)
        self.piece_bitboards: list[bitboard.Bitboard] = [bitboard.Bitboard(0, self.board_width, self.board_height)] * 6
        # self.board = board
        
        self.setup_bitboards(self.board)
        self.move((0, 2), (3, 2))
        self.check_move_legal((3, 2), (4, 4))
        self.piece_bitboards[self.ROOK_ID].display_bitboard()
        
    # SETUP
    
    def setup_board(self):
        """Initialize the original boards"""
        import pieces
        # Standard Board layout
        self.board: list[list[pieces.Piece]] = [
            [pieces.Rook(self, "b"), pieces.Knight(self, "b"), pieces.Bishop(self, "b"), pieces.Queen(self, "b"), pieces.King(self, "b"), pieces.Bishop(self, "b"), pieces.Knight(self, "b"), pieces.Rook(self, "b")],
            [pieces.Pawn(self, "b"), pieces.Pawn(self, "b"), pieces.Pawn(self, "b"), pieces.Pawn(self, "b"), pieces.Pawn(self, "b"), pieces.Pawn(self, "b"), pieces.Pawn(self, "b"), pieces.Pawn(self, "b")],
            [pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self)],
            [pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self)],
            [pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self)],
            [pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self), pieces.EmptyPiece(self)],
            [pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w")],
            [pieces.Rook(self, "w"), pieces.Knight(self, "w"), pieces.Bishop(self, "w"), pieces.Queen(self, "w"), pieces.King(self, "w"), pieces.Bishop(self, "w"), pieces.Knight(self, "w"), pieces.Rook(self, "w")]
        ]
        
        # Length: Y, Width: X
        self.board_height = len(self.board)
        self.board_width = len(self.board[0])
        self.board_area = self.board_height * self.board_width

    def setup_bitboards(self, board):
        
        # Initial generation of bitboards
        
        white_bitboard = ""
        black_bitboard = ""
        piece_bitboards = ["", "", "", "", "", ""]
        for row in board:
            for piece in row:
                # First recognize if piece is black or white
                if piece.side == "w":
                    white_bitboard += "1"
                    black_bitboard += "0"
                elif piece.side == "b":
                    black_bitboard += "1"
                    white_bitboard += "0"
                else:
                    white_bitboard += "0"
                    black_bitboard += "0"

                # Then check for pieces
                pieces = [0, 1, 2, 3, 4, 5]
                if piece.id in pieces:
                    piece_bitboards[piece.id] += "1"
                    pieces.remove(piece.id)
                for pid in pieces:
                    piece_bitboards[pid] += "0"

        self.white_bitboard.update(int(white_bitboard, 2))
        self.black_bitboard.update(int(black_bitboard, 2))
        for bitboard in range(len(piece_bitboards)):
            self.piece_bitboards[bitboard].update(int(piece_bitboards[bitboard], 2))
            
        # Generation of magic bitboards
        
        self.generate_magic_bitboards()
            
    def generate_magic_bitboards(self):
        self.ROOK_TABLE 
            
    def generate_rook_magic_table(self):
        table = [bitboard.Bitboard(0, self.board_width, self.board_height)] * magicnums.ROOK_SIZE
        
        for y in range(self.board_height):
            for x in range(self.board_width):
                index = y * self.board_width + x
                
                # Possible rays of the piece
                rays = magicnums.ROOK_MOVES[index].mask
                
                # Loop through all subsets
                
                pass
    
    def generate_bishop_magic_table():
        pass
    
    def generate_queen_magic_tables():
        pass
    
    def generate_magic_index(blockers: bitboard.Bitboard, magic_number: int, index_number: int) -> int:
        # Index bits are actually directly stored as 64 - their real value to decrease amount of operations needed
        return (blockers.value * magic_number) >> index_number
    
    def check_move_legal(self, p1: tuple[int, int], p2: tuple[int, int]):
        piece = self.board[p1[0]][p1[1]]
        
        # If piece is sliding
        if piece.id in [1, 2, 4]:
            self.check_sliding_move_legal(piece, p1, p2)
            
    def check_sliding_move_legal(self, piece, p1: tuple[int, int], p2: tuple[int, int]):
        # Magic bitboard method
        mask = piece.generate_sliding_mask((p1[0], p1[1]), piece.DIRECTIONS, self.board_height, self.board_width)
        lookup_table = "TODO"
        
    def generate_pseudolegal_moves(self):
        pass
    
    def move(self, p1: tuple[int, int], p2: tuple[int, int]):
        # TODO: represent boards in integers instead of strings - strings were used for debugging
        # Position in the form of (y, x)
        p1piece = self.board[p1[0]][p1[1]]
        p2piece = self.board[p2[0]][p2[1]]
        # Taking logic
        if p2piece.id != 6:
            if p2piece.side == "w":
                self.bmaterial.append(p2piece)
            else:
                self.wmaterial.append(p2piece)

        # Update bitboards
        # Make new bitboard to represent move
        movebb = ["0"] * self.board_area
        p1index = p1[0] * self.board_height + p1[1]
        p2index = p2[0] * self.board_height + p2[1]
        movebb[p1index] = "1"
        movebb[p2index] = "1"
        movebb = "".join(movebb)
        movebb = int(movebb, 2)

        takenbb = ["0"] * self.board_area
        takenbb[p2index] = "1"
        takenbb = "".join(takenbb)
        takenbb = int(takenbb, 2)

        # Update white and black bitboards of the attacked piece
        if p2piece.side == "w":
            self.white_bitboard.update(self.white_bitboard.value ^ takenbb)
        elif p2piece.side == "b":
            self.black_bitboard.update(self.black_bitboard.value ^ takenbb)
        
        # Update white and black bitboards of the moving piece
        if p1piece.side == "w":
            self.white_bitboard.update(self.white_bitboard.value ^ takenbb)
            self.white_bitboard.update(self.white_bitboard.value | takenbb)
        elif p1piece.side == "b":
            self.black_bitboard.update(self.black_bitboard.value ^ movebb)
            self.black_bitboard.update(self.black_bitboard.value | takenbb)
        
        # If piece is taken update bitboard of taken piece first
        if p2piece.id != 6:
            self.piece_bitboards[p2piece.id].update(self.piece_bitboards[p2piece.id].value ^ takenbb)
        # Then update bitboard of moved piece
        if p1piece.id != 6:
            self.piece_bitboards[p1piece.id].update(self.piece_bitboards[p1piece.id].value ^ movebb)

        # Move piece
        self.board[p2[0]][p2[1]] = self.board[p1[0]][p1[1]]
        import pieces
        self.board[p1[0]][p1[1]] = pieces.EmptyPiece(self)
        pass
    