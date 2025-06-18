import bitboard
import magicnums
import ctypes

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
        self.board: list
        self.board_area: int
        self.board_width: int
        self.board_height: int
        self.ROOK_TABLE: list
        self.BISHOP_TABLE: list
        
        # Setup pieces, and set board height, width and area
        self.setup_board()
        
        self.white_bitboard: bitboard.Bitboard = bitboard.Bitboard(0, self.board_width, self.board_height)
        self.black_bitboard: bitboard.Bitboard = bitboard.Bitboard(0, self.board_width, self.board_height)
        self.piece_bitboards: list[bitboard.Bitboard] = [bitboard.Bitboard(0, self.board_width, self.board_height),
                                                         bitboard.Bitboard(0, self.board_width, self.board_height),
                                                         bitboard.Bitboard(0, self.board_width, self.board_height),
                                                         bitboard.Bitboard(0, self.board_width, self.board_height),
                                                         bitboard.Bitboard(0, self.board_width, self.board_height),
                                                         bitboard.Bitboard(0, self.board_width, self.board_height)]
        
        
        self.setup_bitboards(self.board)
        
        self.check_move_legal((7, 0), (3, 0))
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
            [pieces.EmptyPiece(self), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w"), pieces.Pawn(self, "w")],
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
                    pieces.pop(piece.id)
                for pid in pieces:
                    piece_bitboards[pid] += "0"
                    
        self.white_bitboard.update(int(white_bitboard, 2))
        self.black_bitboard.update(int(black_bitboard, 2))
        for i, bitboard in enumerate(piece_bitboards):
            self.piece_bitboards[i].update(int(bitboard, 2))
            
        # Generation of magic bitboards
        print("Loading...")
        self.generate_magic_bitboards()
        print("Done!")
            
    def generate_magic_bitboards(self):
        self.ROOK_TABLE = self.generate_magic_table([(1, 0), (0, 1), (-1, 0), (0, -1)], magicnums.ROOK_SIZE, magicnums.ROOK_MOVES)
        self.BISHOP_TABLE = self.generate_magic_table([(1, 1), (-1, 1), (1, -1), (-1, -1)], magicnums.BISHOP_SIZE, magicnums.BISHOP_MOVES)
    
    def generate_magic_table(self, deltas, table_size, magic_data):
        table = [bitboard.Bitboard(0, self.board_width, self.board_height)] * table_size
        for y in range(self.board_height):
            for x in range(self.board_width):
                index = y * self.board_width + x
                magic_data_current = magic_data[(index)]

                rays = magic_data_current.mask
                
                # Loop through all subsets
                
                # Emulate do while loop
                blockers = bitboard.Bitboard(0, self.board_width, self.board_height)

                while True:

                    possible = self.generate_possible_moves(deltas, blockers, index)
                    
                    table[self.generate_magic_index(blockers, magic_data_current.magic, magic_data_current.index_number)] = bitboard.Bitboard(possible, self.board_width, self.board_height)
                    
                    blockers.value = (blockers.value - rays) & rays;
                    
                    if blockers.value == 0:
                        break
    
    def generate_possible_moves(self, deltas, blockers, index):
        final_bb = bitboard.Bitboard(0, self.board_width, self.board_height)
        for delta in deltas:
            ray = 1 << index

            while not (ray & blockers.value):
                
                # Apply operations
                
                # Y-delta
                
                if delta[0] > 0:
                    ray = ray << self.board_width * delta[0]
                elif delta[0] < 0:
                    ray = ray >> -(self.board_width * delta[0])
                   
                # X-delta
                if delta[1] > 0:
                    ray = ray << delta[1]
                elif delta[1] < 0:
                    ray = ray >> -delta[1]
                    
                # Number represents:
                # 10000000
                # 10000000
                # 10000000
                # 10000000
                # 10000000
                # 10000000
                # 10000000
                # 10000000
                LEFT_BORDER = 0x8080808080808080
                
                # Number represents:
                # 00000001
                # 00000001
                # 00000001
                # 00000001
                # 00000001
                # 00000001
                # 00000001
                # 00000001
                RIGHT_BORDER = 0x101010101010101
                
                # Number represents:
                # 11111111
                # 00000000
                # 00000000
                # 00000000
                # 00000000
                # 00000000
                # 00000000
                # 00000000
                TOP_BORDER = 0xFF00000000000000
                
                # Number represents:
                # 00000000
                # 00000000
                # 00000000
                # 00000000
                # 00000000
                # 00000000
                # 00000000
                # 11111111
                BOTTOM_BORDER = 0xFF
                
                # Check borders
                if delta[0] > 0:
                    if ray & BOTTOM_BORDER:
                        break
                elif delta[0] < 0:
                    if ray & TOP_BORDER:
                        break
                    
                if delta[1] > 0:
                    if ray & RIGHT_BORDER:
                        break
                elif delta[1] < 0:
                    if ray & LEFT_BORDER:
                        break
                
                # Boundary check
                if ray <= 0 or ray >= (1 << 64):
                    break
                
                # break if touching a blocker
                if ray & blockers.value:
                    break
                
                # Update result
                final_bb.value |= ray

        return final_bb     
    
    def generate_magic_index(self, blockers: bitboard.Bitboard, magic_number: int, index_number: int) -> int:
        # Index bits are actually directly stored as (64 - their real value) to decrease amount of operations needed
        # TODO: Change to wrapping multiplication
        
        return ctypes.c_uint64((blockers.value * magic_number)).value >> (index_number)
    
    def check_move_legal(self, p1: tuple[int, int], p2: tuple[int, int]):
        piece = self.board[p1[0]][p1[1]]
        
        # If piece is sliding
        if piece.id in [1, 2, 4]:
            self.check_sliding_move_legal(piece, p1, p2)
            
    def check_sliding_move_legal(self, piece, p1: tuple[int, int], p2: tuple[int, int]):
        # Magic bitboard method
        mask = piece.generate_sliding_mask((p1[0], p1[1]), piece.DIRECTIONS, self.board_height, self.board_width)
        index = p1[0] * self.board_width + p1[1]
        
        if piece.id == self.ROOK_ID:
            index_number = magicnums.ROOK_MOVES[index].index_number
            magic_number = magicnums.ROOK_MOVES[index].magic
            blockers = bitboard.Bitboard((self.white_bitboard.value & self.black_bitboard.value) & mask.value, self.board_width, self.board_height)
            print(index_number, magic_number)
            possible_moves = self.ROOK_TABLE[self.generate_magic_index(blockers, magic_number, index_number)]
            possible_moves.display_bitboard()
            # Check if move is possible using bitwise AND
            # Check for if take is possible
        
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
    