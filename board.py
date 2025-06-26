import bitboard
import magicnums
import ctypes
import lookuptables
import copy
# NOTE:
# TOP-LEFT is INDEX 0, GOING FROM LEFT TO RIGHT IN A BITBOARD
# << MOVES TOWARDS THE LEFT
# >> MOVES TOWARDS THE RIGHT
# << self.board_width MOVES ONE ROW UP
# >> self.board_width MOVES ONE ROW DOWN


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
        
        self.en_passantable = []
        
        # index 0 = white king pos, index 1 = black king pos
        self.king_positions = [(0, 0), (0, 0)]
        
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
        self.en_passantboard = bitboard.Bitboard(0, self.board_width, self.board_height)
        self.castleboard = bitboard.Bitboard(0, self.board_width, self.board_height)
        
        self.setup_bitboards(self.board)
        self.game_loop()
        
    def game_loop(self):
        UNICODE_PIECES = {
            'r': u'♜', 'n': u'♞', 'b': u'♝', 'q': u'♛',
            'k': u'♚', 'p': u'♟', 'R': u'♖', 'N': u'♘',
            'B': u'♗', 'Q': u'♕', 'K': u'♔', 'P': u'♙',
            '.': '.'
        }
        icons = ['p', 'b', 'r', 'n', 'q', 'k', '.']
        bicons = ['P', 'B', 'R', 'N', 'Q', 'K', '.']
        currentside = "w"
        while True:
            print(f"It's {currentside}'s turn!")
            print(f"Current evaluation: {self.evaluate("w")}")
            y = 0
            x = 0
            for row in self.board:
                
                print (y, end = " ")
                for piece in row:
                    if piece.side == "w":
                        print(UNICODE_PIECES[icons[piece.id]], end = " ")
                    else:
                        print(UNICODE_PIECES[bicons[piece.id]], end = " ")
                y += 1
                print()
                
            print("  0 1 2 3 4 5 6 7")
            
            print("Enter the positions in the form of yx.")
            
            print("> ", end = "")
            
            print("Position 1:")
            p1 = input().strip()
            while not p1.isnumeric() or len(p1) != 2:
                print("Invalid input!")
                p1 = input()
            print("> ", end = "")
            print("Position 2:")
            p2 = input()
            while not p2.isnumeric() or len(p2) != 2:
                print("Invalid input!")
                p2 = input()
            p1 = (int(p1[0]), int(p1[1]))
            p2 = (int(p2[0]), int(p2[1]))

            moves = self.return_legal_moves(currentside)
            
            if (p1, p2) in moves:
                
                # move piece
                material, self.white_bitboard, self.black_bitboard, self.piece_bitboards, self.king_positions = self.move((int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), True)
                # Clear en passant list
                self.en_passantboard.value = 0
                self.en_passantable = []
                if currentside == "b":
                    currentside = "w"
                else:
                    currentside = "b"
            else:
                print("Illegal move!")
            
            # Checkmate logic
                
            moves = self.return_legal_moves(currentside)
            if len(moves) == 0:
                if currentside == "w":
                    if self.check_check(self.board[self.king_positions[0][0]][self.king_positions[0][1]], self.king_positions[0]):
                        print("Checkmate! Black wins")
                    else:
                        print("Stalemate")
                elif currentside == "b":
                    if self.check_check(self.board[self.king_positions[1][0]][self.king_positions[1][1]], self.king_positions[1]):
                        print("Checkmate! White wins")
                    else:
                        print("Stalemate")
                break
                
                
    # MOVE GENERATION
    
    def return_legal_moves(self, side: str) -> list:
        """Returns all legal moves in a list, in the form of a tuple (a, b)"""
        
        legal_moves = []
        
        # Loop through board
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece.side == side:
                    position = (y, x)
                    index = position[0] * self.board_width + position[1]
                    
                    if piece.id in [self.BISHOP_ID, self.ROOK_ID, self.QUEEN_ID]:
                        possible_moves = self.get_possible_sliding_moves(piece, piece.id, position, index)
                    elif piece.id in [self.PAWN_ID]:
                        possible_moves = self.get_possible_pawn_moves(piece, piece.id, position, index)
                    elif piece.id in [self.KNIGHT_ID]:
                        possible_moves = self.get_possible_knight_moves(piece, piece.id, position, index)
                    elif piece.id in [self.KING_ID]:
                        pass # We will check for possible king moves later
                    else:
                        continue
                    
                    # Remove own piece from possible moves
                    if side == "w":
                        possible_moves.value = (possible_moves.value & self.white_bitboard.value) ^ possible_moves.value
                    else:
                        possible_moves.value = (possible_moves.value & self.black_bitboard.value) ^ possible_moves.value
                    
                    if piece.id in [self.KING_ID]:
                        possible_moves = self.get_possible_king_moves(piece, piece.id, position, index)
                    
                    from gmpy2 import bit_scan1
                    while bit_scan1(possible_moves.value) != None:
                        newpos_bit = bit_scan1(possible_moves.value)
                        newpos_bit_adjusted = self.board_area - (newpos_bit + 1)
                        y_pos = newpos_bit_adjusted // self.board_width
                        newpos = (y_pos, newpos_bit_adjusted - (y_pos * self.board_width))
                        if self.check_move_legal(position, newpos):
                            legal_moves.append((position, newpos))
                        possible_moves.value ^= 1 << newpos_bit

        return legal_moves

    
    
    def evaluate(self, side_to_move = "w") -> float:
        mg = [0, 0]
        eg = [0, 0]
        game_phase = 0
        
        WHITE = 0
        BLACK = 1
        
        
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece.id != 6:
                    if piece.side == "w":
                        mg[WHITE] += lookuptables.WHITE_MG_TABLE[piece.id][y][x]
                        eg[WHITE] += lookuptables.WHITE_EG_TABLE[piece.id][y][x]
                    elif piece.side == "b":
                        mg[BLACK] += lookuptables.BLACK_MG_TABLE[piece.id][y][x]
                        eg[BLACK] += lookuptables.BLACK_EG_TABLE[piece.id][y][x]
                    game_phase += lookuptables.GAMEPHASE_INC[piece.id]
        
        side_to_move = WHITE if side_to_move == "w" else BLACK
        mg_score = mg[side_to_move] - mg[abs(side_to_move - 1)]
        eg_score = eg[side_to_move] - eg[abs(side_to_move - 1)]
        
        mg_phase = game_phase
        if (mg_phase > 24):
            mg_phase = 24
            
        eg_phase = 24 - mg_phase
        return ((mg_score * mg_phase + eg_score * eg_phase) / 24) / 100 # remove 100 later
    
    def perft_test(self, depth, side = "b"):
        if side == "b":
            side = "w"
        else:
            side = "b"
        moves = self.return_legal_moves(side)
        length = len(moves)
        nodes = 0
        if depth == 0:
            return 1
        for i in range(length):
            self.move(moves[i][0], moves[i][1])
            nodes += self.perft_test(depth - 1, side)
            self.move(moves[i][1], moves[i][0])
        return nodes

    def copy_bitboard(self, bb: bitboard.Bitboard):
        return bitboard.Bitboard(bb.value, self.board_width, self.board_height)
    
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
        
        # Update King positions
        self.king_positions[0] = (7, 4)
        self.king_positions[1] = (0, 4)
        
        
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
        print("Loading magic bitboards...")
        self.generate_magic_bitboards()
        print("Done!")
            
    def generate_magic_bitboards(self):
        self.ROOK_TABLE = self.generate_magic_table([(1, 0), (0, 1), (-1, 0), (0, -1)], magicnums.ROOK_SIZE, magicnums.ROOK_MOVES)
        self.BISHOP_TABLE = self.generate_magic_table([(1, 1), (-1, 1), (1, -1), (-1, -1)], magicnums.BISHOP_SIZE, magicnums.BISHOP_MOVES)
    
    def generate_magic_table(self, deltas, table_size, magic_data):
        
        # Generate empty table
        table = [bitboard.Bitboard(0, self.board_width, self.board_height)] * table_size

        for y in range(self.board_height):
            for x in range(self.board_width):
                index = y * self.board_width + x
                magic_data_current = magic_data[index]

                rays = magic_data_current.mask
                
                # Loop through all subsets
                
                # Emulate do while loop
                blockers = bitboard.Bitboard(0, self.board_width, self.board_height)

                while True:
                    possible = self.generate_possible_moves(deltas, blockers, index)
                    
                    table[self.generate_magic_index(blockers, magic_data_current.magic, magic_data_current.index_number, magic_data_current.offset)] = possible
                    blockers.value = (blockers.value - rays) & rays;
                    
                    if blockers.value == 0:
                        break
        return table
    
    def generate_possible_moves(self, deltas, blockers, index):
        final_bb = bitboard.Bitboard(0, self.board_width, self.board_height)
        for delta in deltas:
            ray = 1 << (self.board_area - index - 1)
            while not (ray & blockers.value):
                    
                # Initial border check:
                if self.border_colliding(ray, delta):
                    break
                
                # Apply operations
                
                # Y-delta
                
                if delta[0] > 0:
                    ray = ray >> self.board_width * delta[0]
                elif delta[0] < 0:
                    ray = ray << -(self.board_width * delta[0])
                   
                # X-delta
                if delta[1] > 0:
                    ray = ray >> delta[1]
                elif delta[1] < 0:
                    ray = ray << -delta[1]

                
                # Boundary check
                if ray <= 0 or ray >= (1 << 64):
                    break
                
                # Update result
                final_bb.value |= ray
                
                # break if touching a blocker
                if ray & blockers.value:
                    break

        return final_bb     
    
    def border_colliding(self, ray, delta):
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
                return True
        elif delta[0] < 0:
            if ray & TOP_BORDER:
                return True
            
        if delta[1] > 0:
            if ray & RIGHT_BORDER:
                return True
        elif delta[1] < 0:
            if ray & LEFT_BORDER:
                return True
        return False
    
    def generate_magic_index(self, blockers: bitboard.Bitboard, magic_number: int, index_number: int, offset: int) -> int:
        # Index bits are actually directly stored as (64 - their real value) to decrease amount of operations needed
        # TODO: Change to wrapping multiplication
        
        return (ctypes.c_uint64((blockers.value * magic_number)).value >> (index_number)) + offset
    
    def check_move_legal(self, p1: tuple[int, int], p2: tuple[int, int]):
        """Make sure move is legal - that is, make sure it accounts for checks"""
        
        # Boundary checks - cant be negative or over the width/height of the board
        if p1[0] >= self.board_height or p1[0] < 0 or p2[0] >= self.board_height or p2[0] < 0:
            return False
        if p1[1] >= self.board_width or p1[1] < 0 or p2[1] >= self.board_width or p2[1] < 0:
            return False
        
        piece = self.board[p1[0]][p1[1]]
        
        # Account for checks - this only checks for pseudo-legal moves
        # We do this by seeing if the king is in check after testing out the move
        material, white_bitboard, black_bitboard, piece_bitboards, king_positions = self.move(p1, p2, False)
        
        if piece.side == "w":
            if self.check_check(piece, king_positions[0], None, white_bitboard, black_bitboard, piece_bitboards):
                return False
        elif piece.side == "b":
            if self.check_check(piece, king_positions[1], None, white_bitboard, black_bitboard, piece_bitboards):
                return False
        
        return True
    
    def check_check(self, piece, position: tuple[int, int], index = None, white_bitboard = None, black_bitboard = None, piece_bitboards = None) -> bool:
        """Check for if a king is in check. Take in the King piece and position as parameters. If in check return True. Otherwise, return False."""
        if index == None:
            index = (position[0] * self.board_width + position[1])

        if white_bitboard == None:
            white_bitboard = self.white_bitboard
        if black_bitboard == None:
            black_bitboard = self.black_bitboard
        if piece_bitboards == None:
            piece_bitboards = self.piece_bitboards
        
        ROOK_ATTACKERS = self.get_possible_sliding_moves(piece, self.ROOK_ID, position, index, white_bitboard, black_bitboard).value & (piece_bitboards[self.ROOK_ID].value | piece_bitboards[self.QUEEN_ID].value)
        BISHOP_ATTACKERS = self.get_possible_sliding_moves(piece, self.BISHOP_ID, position, index, white_bitboard, black_bitboard).value & (piece_bitboards[self.BISHOP_ID].value | piece_bitboards[self.QUEEN_ID].value)
        # Don't need queen attacks as we can check if queen is in either rook or bishop attacks
        PAWN_ATTACKERS = self.get_possible_pawn_moves(piece, self.PAWN_ID, position, index).value & piece_bitboards[self.PAWN_ID].value
        KNIGHT_ATTACKERS = self.get_possible_knight_moves(piece, self.KNIGHT_ID, position, index).value & piece_bitboards[self.KNIGHT_ID].value

        if piece.side == "w":
            if ((ROOK_ATTACKERS & black_bitboard.value) | (BISHOP_ATTACKERS & black_bitboard.value) | (PAWN_ATTACKERS & black_bitboard.value) | (KNIGHT_ATTACKERS & black_bitboard.value)):
                return True
        elif piece.side == "b":
            if ((ROOK_ATTACKERS & white_bitboard.value) | (BISHOP_ATTACKERS & white_bitboard.value) | (PAWN_ATTACKERS & white_bitboard.value) | (KNIGHT_ATTACKERS & white_bitboard.value)):
                return True
        return False
    
    def get_possible_pawn_moves(self, piece, piece_id, position: tuple[int, int], index = None, white_bitboard = None, black_bitboard = None):
        # TODO: EN PASSANT
        THIRD_RANK = 0xff0000
        SIXTH_RANK = 0xff0000000000
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
        if index == None:
            index = (position[0] * self.board_width + position[1])
        
        if white_bitboard == None:
            white_bitboard = self.white_bitboard
        if black_bitboard == None:
            black_bitboard = self.black_bitboard
        initial_bit_shift = 1 << 64 - (index + 1)
        
        # Initialize possible moves
        possible_moves = bitboard.Bitboard(initial_bit_shift, self.board_width, self.board_height)
        
        # Shift possible moves forward/backward depending on side
        # Don't need to boundary check for above 1 >> 64 or below 0 as pawn promotes on back rank
        if piece.side == "w":
            possible_moves.value <<= self.board_width
            # Add double pushes, unless it is blocked by another piece or is not in the second rank
            # THIRD_RANK is used because we already pushed the pawn up
            if possible_moves.value & THIRD_RANK and (((possible_moves.value << self.board_width) & white_bitboard.value) ^ possible_moves.value):
                possible_moves.value |= (possible_moves.value << self.board_width)
            # Remove any opposing piece from front of pawn possible moves as pawn can't take forwards
            possible_moves.value ^= (black_bitboard.value & possible_moves.value)
            # Account for takes
            # Make a mask
            mask = (1 << (64 - (index + 1))) << self.board_width
            mask |= (((mask << 1) | RIGHT_BORDER) ^ RIGHT_BORDER | ((mask >> 1) | LEFT_BORDER) ^ LEFT_BORDER)
            
            # Add mask to possible moves
            possible_moves.value |= (mask & black_bitboard.value)
            
            # Account for en passant
            # We dont need to check for y boundaries as it never is a problem in en passant
            if position[1] - 1 >= 0 and position[1] - 1 < self.board_width:
                if self.board[position[0]][position[1] - 1] in self.en_passantable:
                    possible_moves.value |= 1 << (64 - (((position[0] - 1) * self.board_width + position[1] - 1) + 1))
                    self.en_passantboard.value |= 1 << (64 - (((position[0] - 1) * self.board_width + position[1] - 1) + 1))
            if position[1] + 1 >= 0 and position[1] + 1 < self.board_width:
                if self.board[position[0]][position[1] + 1] in self.en_passantable:
                    possible_moves.value |= 1 << (64 - (((position[0] - 1) * self.board_width + position[1] + 1) + 1))
                    self.en_passantboard.value |= 1 << (64 - (((position[0] - 1) * self.board_width + position[1] + 1) + 1))
        else:
            possible_moves.value >>= self.board_width
            
            # Add double pushes, unless it is blocked by another piece or is not in the second rank
            # THIRD_RANK is used because we already pushed the pawn up
            if possible_moves.value & SIXTH_RANK and (((possible_moves.value << self.board_width) & black_bitboard.value) ^ possible_moves.value):
                possible_moves.value |= (possible_moves.value >> self.board_width)
            # Remove any opposing piece from front of pawn possible moves as pawn can't take forwards
            possible_moves.value ^= (white_bitboard.value & possible_moves.value)
            # Account for takes
            # Make a mask
            mask = (1 << (64 - (index + 1))) >> self.board_width
            mask |= (((mask << 1) | RIGHT_BORDER) ^ RIGHT_BORDER | ((mask >> 1) | LEFT_BORDER) ^ LEFT_BORDER)
            
            # Add mask to possible moves
            possible_moves.value |= (mask & white_bitboard.value)
            
            # Account for en passant
            # We dont need to check for y boundaries as it never is a problem in en passant
            if position[1] - 1 >= 0 and position[1] - 1 < self.board_width:
                if self.board[position[0]][position[1] - 1] in self.en_passantable:
                    possible_moves.value |= 1 << (64 - (((position[0] + 1) * self.board_width + position[1] - 1) + 1))
                    self.en_passantboard.value |= 1 << (64 - (((position[0] + 1) * self.board_width + position[1] - 1) + 1))
            if position[1] + 1 >= 0 and position[1] + 1 < self.board_width:
                if self.board[position[0]][position[1] + 1] in self.en_passantable:
                    possible_moves.value |= 1 << (64 - (((position[0] + 1) * self.board_width + position[1] + 1) + 1))
                    self.en_passantboard.value |= 1 << (64 - (((position[0] + 1) * self.board_width + position[1] + 1) + 1))
        return possible_moves
    
    def get_possible_sliding_moves(self, piece, piece_id, position: tuple[int, int], index = None, white_bitboard = None, black_bitboard = None):
        if index == None:
            index = (position[0] * self.board_width + position[1])

        if white_bitboard == None:
            white_bitboard = self.white_bitboard
        if black_bitboard == None:
            black_bitboard = self.black_bitboard
        # Magic bitboard method

        if piece_id == self.ROOK_ID:
            index_number = magicnums.ROOK_MOVES[index].index_number
            magic_number = magicnums.ROOK_MOVES[index].magic
            offset = magicnums.ROOK_MOVES[index].offset
            mask = magicnums.ROOK_MOVES[index].mask
            blockers = bitboard.Bitboard((white_bitboard.value | black_bitboard.value) & mask, self.board_width, self.board_height)

            possible_moves = self.ROOK_TABLE[self.generate_magic_index(blockers, magic_number, index_number, offset)]

        elif piece_id == self.BISHOP_ID:
            index_number = magicnums.BISHOP_MOVES[index].index_number
            magic_number = magicnums.BISHOP_MOVES[index].magic
            offset = magicnums.BISHOP_MOVES[index].offset
            mask = magicnums.BISHOP_MOVES[index].mask
            blockers = bitboard.Bitboard((white_bitboard.value | black_bitboard.value) & mask, self.board_width, self.board_height)

            possible_moves = self.BISHOP_TABLE[self.generate_magic_index(blockers, magic_number, index_number, offset)]
            
        elif piece_id == self.QUEEN_ID:
            # Queen travels in direction of both rook and bishop
            possible_moves = bitboard.Bitboard(self.get_possible_sliding_moves(piece, self.ROOK_ID, position, index, white_bitboard, black_bitboard).value | self.get_possible_sliding_moves(piece, self.BISHOP_ID, position, index, white_bitboard, black_bitboard).value, self.board_width, self.board_height)

        possible_moves = self.copy_bitboard(possible_moves)
        return possible_moves
        
    def get_possible_knight_moves(self, piece, piece_id, position: tuple[int, int], index = None):
        if index == None:
            index = (position[0] * self.board_width + position[1])
        possible_moves = bitboard.Bitboard(lookuptables.KNIGHT_TABLE[index], self.board_width, self.board_height)
        return possible_moves

    def get_possible_king_moves(self, piece, piece_id, position: tuple[int, int], index = None):
        if index == None:
            index = (position[0] * self.board_width + position[1])
        possible_moves = bitboard.Bitboard(lookuptables.KING_TABLE[index], self.board_width, self.board_height)
        if piece.side == "w":
            possible_moves.value = (possible_moves.value & self.white_bitboard.value) ^ possible_moves.value
        else:
            possible_moves.value = (possible_moves.value & self.black_bitboard.value) ^ possible_moves.value
        
        # Account for castling
        # Only make it a viable option if the piece is not moved
        if not piece.has_moved and not self.check_check(piece, position, index):
            if not self.board[position[0]][0].has_moved and self.board[position[0]][0].id == self.ROOK_ID and self.board[position[0]][0].side == piece.side:
                value = (1 << (64 - (position[0] * self.board_width + 1)))
                possible_moves.value |= value
                self.castleboard.value |= value
            if not self.board[position[0]][self.board_width - 1].has_moved and self.board[position[0]][self.board_width - 1].id == self.ROOK_ID and self.board[position[0]][self.board_width - 1].side == piece.side:
                value = (1 << (64 - (position[0] * self.board_width + (self.board_width - 1) + 1)))
                possible_moves.value |= value
                self.castleboard.value |= value
        
        return possible_moves
        
    
    
    def move(self, p1: tuple[int, int], p2: tuple[int, int], change_board = False):
        """Returns new board with move completed, along with material, and new bitboards."""
        
        king_positions = self.king_positions.copy()
        
        # En passant

        # If en passant then take piece
        en_passant = (1 << (64 - ((p2[0]) * self.board_width + p2[1] + 1))) & self.en_passantboard.value
        if en_passant:
            # If moving to right
            if p2[1] > p1[1]:
                self.remove_piece((p1[0], p1[1] + 1))
            elif p2[1] < p1[1]:
                self.remove_piece((p1[0], p1[1] - 1))
        # Clear en passant list
        self.en_passantboard.value = 0
        self.en_passantable = []
        
        material = []
       
        # Position in the form of (y, x)
        p1piece = self.board[p1[0]][p1[1]]
        p2piece = self.board[p2[0]][p2[1]]
        # Adding to material
        if p2piece.id != 6:
            if p2piece.side == "w":
                material = self.bmaterial.copy()
                material.append(p2piece)
            else:
                material = self.wmaterial.copy()
                material.append(p2piece)

        # Update bitboards
        # Set indices
        p1index = p1[0] * self.board_height + p1[1]
        p2index = p2[0] * self.board_height + p2[1]
        
        # Update white and black bitboards
        p1move = 1 << (64 - (p1index + 1))
        p2move = 1 << (64 - (p2index + 1))
        white_bitboard = bitboard.Bitboard(0, self.board_width, self.board_height)
        black_bitboard = bitboard.Bitboard(0, self.board_width, self.board_height)
        
        import copy
        piece_bitboards = copy.deepcopy(self.piece_bitboards)
        if not (p2move & self.castleboard.value and p2piece.id == self.ROOK_ID and p2piece.side == p1piece.side):
            if p1piece.side == "w":
                white_bitboard.value = (p1move ^ self.white_bitboard.value) | p2move
                black_bitboard.value = (self.black_bitboard.value | white_bitboard.value) ^ white_bitboard.value
            else:
                black_bitboard.value = (p1move ^ self.black_bitboard.value) | p2move
                white_bitboard.value = (black_bitboard.value | self.white_bitboard.value) ^ black_bitboard.value
            
            
            # Update piece bitboards
            bothmoves = p1move | p2move
            if p1piece.id != 6:
                piece_bitboards[p1piece.id].value = self.piece_bitboards[p1piece.id].value ^ bothmoves
            if p2piece.id != 6:
                piece_bitboards[p2piece.id].value = self.piece_bitboards[p2piece.id].value ^ p2move
            # Update King positions
            if p1piece.id == self.KING_ID:
                if p1piece.side == "w":
                    king_positions[0] = p2
                else:
                    king_positions[1] = p2
            if change_board:
                # Move piece on list
                self.board[p2[0]][p2[1]] = self.board[p1[0]][p1[1]]
                import pieces
                self.board[p1[0]][p1[1]] = pieces.EmptyPiece(self)

                        
                # Update en-passantable pieces
                if p1piece.id == self.PAWN_ID:
                    # Double push
                    if abs(p1[0] - p2[0]) == 2:
                        self.en_passantable.append(p1piece)
                p1piece.has_moved = True
                
                # Update promotions
                if p1piece.id == self.PAWN_ID:
                    BACK_RANK = 0xff00000000000000
                    FRONT_RANK = 0xff
                    if p1piece.side == "w":
                        if p2move & BACK_RANK:
                            self.promote(p2, "w", True)
                    elif p1piece.side == "b":
                        if p2move & FRONT_RANK:
                            self.promote(p2, "b", True)
        else:
            if change_board:
                material, white_bitboard, black_bitboard, piece_bitboards = self.castle(p1, p2)
                p1piece.has_moved = True
                self.castleboard.value = 0
        return material, white_bitboard, black_bitboard, piece_bitboards, king_positions

    def promote(self, position, side, prompt = True):
        new_piece = "q"
        if prompt:
            new_piece = input("What piece would you like to promote to? ('q', 'r', 'b', 'n')")
            
        index = 1 << 63 - (position[0] * self.board_width + position[1])
        self.piece_bitboards[self.PAWN_ID].value ^= index
        import pieces
        match new_piece:
            case 'q':
                self.board[position[0]][position[1]] = pieces.Queen(self, side)
                self.piece_bitboards[self.QUEEN_ID].value |= index
            case 'r':
                self.board[position[0]][position[1]] = pieces.Rook(self, side)
                self.piece_bitboards[self.ROOK_ID].value |= index
            case 'b':
                self.board[position[0]][position[1]] = pieces.Bishop(self, side)
                self.piece_bitboards[self.BISHOP_ID].value |= index
            case 'n':
                self.board[position[0]][position[1]] = pieces.Knight(self, side)
                self.piece_bitboards[self.KNIGHT_ID].value |= index
                
    
    def remove_piece(self, position):
        pos_bb = 1 << (64 - (position[0] * self.board_width + position[1] + 1))
        
        if self.board[position[0]][position[1]].side == "w":
            self.white_bitboard.value ^= pos_bb
            self.bmaterial.append(self.board[position[0]][position[1]])
        else:
            self.black_bitboard.value ^= pos_bb
            self.wmaterial.append(self.board[position[0]][position[1]])
        
        if self.board[position[0]][position[1]].id != 6:
            self.piece_bitboards[self.board[position[0]][position[1]].id].value ^= pos_bb
        
        import pieces
        self.board[position[0]][position[1]] = pieces.EmptyPiece(self)
    
    def castle(self, king_position: tuple[int, int], rook_position: tuple[int, int]):
        """Castle type: True = long, False = short"""
        if abs(rook_position[1] - king_position[1]) == 4:
            material, self.white_bitboard, self.black_bitboard, self.piece_bitboards, self.king_positions = self.move(king_position, (king_position[0], king_position[1] - 2), True)
            material, self.white_bitboard, self.black_bitboard, self.piece_bitboards, self.king_positions = self.move(rook_position, (rook_position[0], rook_position[1] + 3), True)
        elif abs(rook_position[1] - king_position[1]) == 3:
            material, self.white_bitboard, self.black_bitboard, self.piece_bitboards, self.king_positions = self.move(king_position, (king_position[0], king_position[1] + 2), True)
            material, self.white_bitboard, self.black_bitboard, self.piece_bitboards, self.king_positions = self.move(rook_position, (rook_position[0], rook_position[1] - 2), True)
        return material, self.white_bitboard, self.black_bitboard, self.piece_bitboards, king_position
    