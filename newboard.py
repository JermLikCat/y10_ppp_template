import magicnums
import lookuptables
import numpy as np
import numpy.typing as npt
import queue
from gmpy2 import bit_scan1

# NOTE:
# LEAST SIGNIFICANT BIT IS BOTTOM RIGHT, MOST SIGNIFICANT ON TOP LEFT.
# BITBOARD IS INDEXED ASCENDINGLY FROM RIGHT TO LEFT, BOTTOM TO TOP
# POSITION IN THE FORM OF (x, y)
# << MOVES TOWARDS THE LEFT
# >> MOVES TOWARDS THE RIGHT
# << self.board_width MOVES ONE ROW UP
# >> self.board_width MOVES ONE ROW DOWN
# MOVE ENCODING - FLAG, FIRST POSITION, SECOND POSITION

class Board:
    PAWN_ID = 0
    BISHOP_ID = 1
    ROOK_ID = 2
    KNIGHT_ID = 3
    QUEEN_ID = 4
    KING_ID = 5
    EMPTY_ID = 6
    
    SIDE_BITBOARDS = 0
    PIECE_BITBOARDS = 1
    SPECIAL_BITBOARDS = 2
    
    WHITE_SIDE = 0
    BLACK_SIDE = 1
    
    BOARD_AREA = 64
    BOARD_WIDTH = 8
    BOARD_HEIGHT = 8
    
    FIRST_RANK = 0x00000000000000FF
    SECOND_RANK = 0x000000000000FF00
    THIRD_RANK = 0x0000000000FF0000
    FOURTH_RANK = 0x00000000FF000000
    FIFTH_RANK = 0x000000FF00000000
    SIXTH_RANK = 0x0000FF0000000000
    SEVENTH_RANK = 0x00FF000000000000
    EIGTH_RANK = 0xFF00000000000000
    
    LEFT_BORDER = 0x8080808080808080
    RIGHT_BORDER = 0x101010101010101
    
    # Kings/Rooks moved detection constants for castling
    CASTLE_BLACK_SHORT_ROOK = 0
    CASTLE_BLACK_LONG_ROOK = 1
    CASTLE_BLACK_KING = 2
    CASTLE_WHITE_SHORT_ROOK = 3
    CASTLE_WHITE_LONG_ROOK = 4
    CASTLE_WHITE_KING = 5
    
    # Move encoding ids
    QUIET_MOVE = 0
    DOUBLE_PAWN_PUSH = 1
    KING_CASTLE = 2
    QUEEN_CASTLE = 3
    CAPTURE = 4
    EP_CAPTURE = 5
    KNIGHT_PROMOTION = 8
    BISHOP_PROMOTION = 9
    ROOK_PROMOTION = 10
    QUEEN_PROMOTION = 11
    KNIGHT_PROMOTION_CAPTURE = 12
    BISHOP_PROMOTION_CAPTURE = 13
    ROOK_PROMOTION_CAPTURE = 14
    QUEEN_PROMOTION_CAPTURE = 15
    
    NULL_POSITION = 65
    
    WHITE_ICONS = [u'♟', u'♝', u'♜', u'♞', u'♛', u'♚']
    BLACK_ICONS = [u'♙', u'♗', u'♖', u'♘', u'♕', u'♔']
    EMPTY_ICON = u'.'
    
    def __init__(self, game, side):
        self.game = game
        self.side = side
        
        self.ROOK_TABLE: npt.NDArray
        self.BISHOP_TABLE: npt.NDArray
        self.ROOK_TABLE, self.BISHOP_TABLE = self.setup_magic_tables()
        
        self.side_bitboards: npt.NDArray
        self.piece_bitboards: npt.NDArray
        
        self.side_bitboards, self.piece_bitboards = self.setup_bitboards()
        
        self.castle_bools_queue = queue.LifoQueue()
        self.castle_bools_queue.put(np.full(6, True))
        
        self.move_history = []
    
    
    # SETUP
    
    def setup_magic_tables(self):
        rook_table = self.generate_magic_table([(1, 0), (0, 1), (-1, 0), (0, -1)], magicnums.ROOK_SIZE, magicnums.ROOK_MOVES)
        bishop_table = self.generate_magic_table([(1, 1), (-1, 1), (1, -1), (-1, -1)], magicnums.BISHOP_SIZE, magicnums.BISHOP_MOVES)
        return rook_table, bishop_table
    
    def setup_bitboards(self):
        side_bitboards = np.array([np.uint64(0)] * 2)
        side_bitboards[self.WHITE_SIDE] = 0b0000000000000000000000000000000000000000000000001111111111111111
        side_bitboards[self.BLACK_SIDE] = 0b1111111111111111000000000000000000000000000000000000000000000000
        piece_bitboards = np.array([np.uint64(0)] * 6)
        piece_bitboards[self.BISHOP_ID] = 0b0010010000000000000000000000000000000000000000000000000000100100
        piece_bitboards[self.KNIGHT_ID] = 0b0100001000000000000000000000000000000000000000000000000001000010
        piece_bitboards[self.ROOK_ID] = 0b1000000100000000000000000000000000000000000000000000000010000001
        piece_bitboards[self.KING_ID] = 0b0000100000000000000000000000000000000000000000000000000000001000
        piece_bitboards[self.QUEEN_ID] = 0b0001000000000000000000000000000000000000000000000000000000010000
        piece_bitboards[self.PAWN_ID] = 0b0000000011111111000000000000000000000000000000001111111100000000
        return side_bitboards, piece_bitboards
    
    # WIN CONDITIONS
    
    def in_check(self, side: int) -> bool:
        white_bitboard = self.side_bitboards[self.WHITE_SIDE]
        black_bitboard = self.side_bitboards[self.BLACK_SIDE]
        if side == self.WHITE_SIDE:
            kingBB = self.piece_bitboards[self.KING_ID] & white_bitboard

            # Go through all black pieces
            ROOK_ATTACKERS = self.generate_sliding_moves(kingBB, white_bitboard, black_bitboard, self.ROOK_ID, True)
            BISHOP_ATTACKERS = self.generate_sliding_moves(kingBB, white_bitboard, black_bitboard, self.BISHOP_ID, True)
            # We do not need to generate queen - just do a bitwise OR
            PAWN_ATTACKERS = self.generate_pawn_moves(kingBB, white_bitboard, black_bitboard, self.move_history, True)
            KNIGHT_ATTACKERS = self.generate_knight_moves(kingBB, white_bitboard, black_bitboard, True)
            KING_ATTACKERS = self.generate_king_moves(kingBB, white_bitboard, black_bitboard, True)
            
            if ((ROOK_ATTACKERS & (black_bitboard & self.piece_bitboards[self.ROOK_ID])) | (BISHOP_ATTACKERS & (black_bitboard & self.piece_bitboards[self.BISHOP_ID])) | (PAWN_ATTACKERS & (black_bitboard & self.piece_bitboards[self.PAWN_ID])) | (KNIGHT_ATTACKERS & (black_bitboard & self.piece_bitboards[self.KNIGHT_ID])) | (KING_ATTACKERS & (black_bitboard & self.piece_bitboards[self.KING_ID]))):
                return True
            return False
        elif side == self.BLACK_SIDE:
            kingBB = self.piece_bitboards[self.KING_ID] & black_bitboard
            
            # Go through all white pieces
            ROOK_ATTACKERS = self.generate_sliding_moves(kingBB, white_bitboard, black_bitboard, self.ROOK_ID, True)
            BISHOP_ATTACKERS = self.generate_sliding_moves(kingBB, white_bitboard, black_bitboard, self.BISHOP_ID, True)
            # We do not need to generate queen - just do a bitwise OR
            PAWN_ATTACKERS = self.generate_pawn_moves(kingBB, white_bitboard, black_bitboard, self.move_history, True)
            KNIGHT_ATTACKERS = self.generate_knight_moves(kingBB, white_bitboard, black_bitboard, True)
            KING_ATTACKERS = self.generate_king_moves(kingBB, white_bitboard, black_bitboard, True)
            
            if ((ROOK_ATTACKERS & (white_bitboard & self.piece_bitboards[self.ROOK_ID])) | (BISHOP_ATTACKERS & (white_bitboard & self.piece_bitboards[self.BISHOP_ID])) | (PAWN_ATTACKERS & (white_bitboard & self.piece_bitboards[self.PAWN_ID])) | (KNIGHT_ATTACKERS & (white_bitboard & self.piece_bitboards[self.KNIGHT_ID])) | (KING_ATTACKERS & (white_bitboard & self.piece_bitboards[self.KING_ID]))):
                return True
            return False
        else:
            raise Exception("Invalid side!")
            
    def check_condition(self, side: int) -> str:
        if len(self.generate_legal_moves()[side]) == 0:
            if self.in_check(side):
                return "c"
            else:
                return "s"
        
        return False

    
    # MOVE GENERATION
    
    def generate_legal_moves(self):
        white_moves = []
        black_moves = []
        # Make a bitboard of the current board to loop through
        white_bitboard = self.side_bitboards[self.WHITE_SIDE]
        black_bitboard = self.side_bitboards[self.BLACK_SIDE]
        current_board = white_bitboard | black_bitboard
        while current_board != 0:
            current_position = np.uint64(1) << self.return_lsb_position(current_board)
            if (self.piece_bitboards[self.ROOK_ID] & (current_position)):
                possible_moves = self.generate_sliding_moves(current_position, white_bitboard, black_bitboard, self.ROOK_ID)
            elif (self.piece_bitboards[self.BISHOP_ID] & (current_position)):
                possible_moves = self.generate_sliding_moves(current_position, white_bitboard, black_bitboard, self.BISHOP_ID)
            elif (self.piece_bitboards[self.QUEEN_ID] & (current_position)):
                possible_moves = self.generate_sliding_moves(current_position, white_bitboard, black_bitboard, self.QUEEN_ID)
            elif (self.piece_bitboards[self.PAWN_ID] & (current_position)):
                possible_moves = self.generate_pawn_moves(current_position, white_bitboard, black_bitboard, self.move_history)
            elif (self.piece_bitboards[self.KNIGHT_ID] & (current_position)):
                possible_moves = self.generate_knight_moves(current_position, white_bitboard, black_bitboard)
            elif (self.piece_bitboards[self.KING_ID] & (current_position)):
                possible_moves = self.generate_king_moves(current_position, white_bitboard, black_bitboard)
            
            side = self.WHITE_SIDE if current_position & white_bitboard else self.BLACK_SIDE
            for move in possible_moves:
                self.make_move(move)
                if not self.in_check(side):
                    if side == self.WHITE_SIDE:
                        white_moves.append(move)
                    elif side == self.BLACK_SIDE:
                        black_moves.append(move)
                self.unmake_move(self.move_history)
            
            current_board ^= current_position
        return white_moves, black_moves
    
    def generate_pawn_moves(self, current_position: np.uint64, white_bitboard: np.uint64, black_bitboard: np.uint64, move_history: list, return_bb = False):
        moves = []
        bb = np.uint64(0)
        if (current_position & white_bitboard):
            # Normal pushes & promotions
            pushed = ((current_position << self.BOARD_WIDTH) | self.FIRST_RANK) ^ self.FIRST_RANK
            if not (pushed & white_bitboard) and not (pushed & black_bitboard):
                if not (pushed & self.EIGTH_RANK):
                    moves.append(self.encode_move(self.QUIET_MOVE, current_position, pushed))
                else:
                    moves.append(self.encode_move(self.ROOK_PROMOTION, current_position, pushed))
                    moves.append(self.encode_move(self.BISHOP_PROMOTION, current_position, pushed))
                    moves.append(self.encode_move(self.KNIGHT_PROMOTION, current_position, pushed))
                    moves.append(self.encode_move(self.QUEEN_PROMOTION, current_position, pushed))
                bb |= pushed
            # Double pushes
            if current_position & self.SECOND_RANK:
                pushed = current_position << (self.BOARD_WIDTH * 2)
                if not (pushed & white_bitboard):
                    moves.append(self.encode_move(self.DOUBLE_PAWN_PUSH, current_position, pushed))
                    bb |= pushed
            
            # Make a mask for takes
            mask = ((current_position << self.BOARD_WIDTH) | self.FIRST_RANK) ^ self.FIRST_RANK
            mask_left = ((mask << np.uint64(1)) | self.RIGHT_BORDER) ^ self.RIGHT_BORDER
            mask_right = ((mask >> np.uint64(1)) | self.LEFT_BORDER) ^ self.LEFT_BORDER
            take_mask = mask_left | mask_right
            
            takes = take_mask & black_bitboard
            
            # Pawn takes & promotion-takes
            if not (takes & self.EIGTH_RANK):
                while takes != 0:
                    pos = self.return_lsb_position(takes)
                    moves.append(self.encode_move(self.CAPTURE, current_position, (np.uint64(1) << pos)))
                    bb |= np.uint64(1) << pos
                    takes ^= (np.uint64(1) << pos)
            else:
                while takes != 0:
                    pos = self.return_lsb_position(takes)
                    posBB = (np.uint64(1) << pos)
                    moves.append(self.encode_move(self.ROOK_PROMOTION, current_position, posBB))
                    moves.append(self.encode_move(self.BISHOP_PROMOTION, current_position, posBB))
                    moves.append(self.encode_move(self.KNIGHT_PROMOTION, current_position, posBB))
                    moves.append(self.encode_move(self.QUEEN_PROMOTION, current_position, posBB))
                    bb |= posBB
                    takes ^= (np.uint64(1) << pos)
            
            # En passant
            mask_left = ((current_position << np.uint64(1)) | self.RIGHT_BORDER) ^ self.RIGHT_BORDER
            mask_right = ((current_position >> np.uint64(1)) | self.LEFT_BORDER) ^ self.LEFT_BORDER
            ep_mask = mask_left | mask_right
            
            en_passantable = ep_mask & black_bitboard
            
            if en_passantable and len(move_history) >= 1:
                # Find last move
                flag, _, to_pos = self.decode_move(move_history[-1])
                if flag == self.DOUBLE_PAWN_PUSH and (np.uint64(1) << to_pos) & en_passantable and not (en_passantable & white_bitboard):
                    moves.append(self.encode_move(self.EP_CAPTURE, current_position, take_mask & (np.uint64(1) << (to_pos + self.BOARD_WIDTH))))
                    bb |= take_mask & (np.uint64(1) << (to_pos + self.BOARD_WIDTH))
            
            
        elif (current_position & black_bitboard):
            # Normal pushes and promotions
            pushed = (current_position >> self.BOARD_WIDTH)
            if not (pushed & white_bitboard) and not (pushed & black_bitboard) and pushed > 0:
                if not (pushed & self.FIRST_RANK):
                    moves.append(self.encode_move(self.QUIET_MOVE, current_position, pushed))
                else:
                    moves.append(self.encode_move(self.ROOK_PROMOTION, current_position, pushed))
                    moves.append(self.encode_move(self.BISHOP_PROMOTION, current_position, pushed))
                    moves.append(self.encode_move(self.KNIGHT_PROMOTION, current_position, pushed))
                    moves.append(self.encode_move(self.QUEEN_PROMOTION, current_position, pushed))
                bb |= pushed
                
            # Double pushes
            if current_position & self.SEVENTH_RANK:
                pushed = current_position >> (self.BOARD_WIDTH * 2)
                if not (pushed & black_bitboard):
                    moves.append(self.encode_move(self.DOUBLE_PAWN_PUSH, current_position, pushed))
                    bb |= pushed
            
            # Make a mask for takes
            
            mask = (current_position >> self.BOARD_WIDTH)
            mask_left = ((mask << np.uint64(1)) | self.RIGHT_BORDER) ^ self.RIGHT_BORDER
            mask_right = ((mask >> np.uint64(1)) | self.LEFT_BORDER) ^ self.LEFT_BORDER
            take_mask = mask_left | mask_right
            
            takes = take_mask & white_bitboard
            
            # Pawn takes and promotion-takes
            if not (takes & self.FIRST_RANK):
                while takes != 0:
                    pos = self.return_lsb_position(takes)
                    moves.append(self.encode_move(self.CAPTURE, current_position, (np.uint64(1) << pos)))
                    bb |= np.uint64(1) << pos
                    takes ^= (np.uint64(1) << pos)
            else:
                while takes != 0:
                    pos = self.return_lsb_position(takes)
                    posBB = (np.uint64(1) << pos)
                    moves.append(self.encode_move(self.ROOK_PROMOTION, current_position, posBB))
                    moves.append(self.encode_move(self.BISHOP_PROMOTION, current_position, posBB))
                    moves.append(self.encode_move(self.KNIGHT_PROMOTION, current_position, posBB))
                    moves.append(self.encode_move(self.QUEEN_PROMOTION, current_position, posBB))
                    bb |= posBB
                    takes ^= (np.uint64(1) << pos)
            
            # En passant
            mask_left = ((current_position << np.uint64(1)) | self.RIGHT_BORDER) ^ self.RIGHT_BORDER
            mask_right = ((current_position >> np.uint64(1)) | self.LEFT_BORDER) ^ self.LEFT_BORDER
            ep_mask = mask_left | mask_right
            
            en_passantable = ep_mask & white_bitboard
            
            if en_passantable and len(move_history) >= 1:
                # Find last move
                flag, _, to_pos = self.decode_move(move_history[-1])
                if flag == self.DOUBLE_PAWN_PUSH and (np.uint64(1) << to_pos) & en_passantable and not en_passantable & white_bitboard:
                    moves.append(self.encode_move(self.EP_CAPTURE, current_position, take_mask & (np.uint64(1) << (to_pos + self.BOARD_WIDTH))))
                    bb |= take_mask & (np.uint64(1) << (to_pos + self.BOARD_WIDTH))
                
        return moves if not return_bb else bb
    
    def generate_knight_moves(self, current_position: np.uint64, white_bitboard: np.uint64, black_bitboard: np.uint64, return_bb = False):
        moves = []
        bb = np.uint64(0)
        index = self.return_lsb_position(current_position)
        
        possible_moves = np.uint64(lookuptables.KNIGHT_TABLE[index])
        
        if current_position & white_bitboard:
            possible_moves = (possible_moves & white_bitboard) ^ white_bitboard
            while possible_moves != 0:
                current = self.return_lsb_position(possible_moves)
                move_flag = self.CAPTURE if (np.uint64(1) << current) & black_bitboard else self.QUIET_MOVE
                moves.append(self.encode_move(move_flag, index, current))
                bb |= np.uint64(1) << current
                possible_moves ^= (np.uint64(1) << current)
        elif current_position & black_bitboard:
            possible_moves = (possible_moves & black_bitboard) ^ black_bitboard
            while possible_moves != 0:
                current = self.return_lsb_position(possible_moves)
                move_flag = self.CAPTURE if (np.uint64(1) << current) & white_bitboard else self.QUIET_MOVE
                moves.append(self.encode_move(move_flag, index, current))
                bb |= np.uint64(1) << current
                possible_moves ^= (np.uint64(1) << current)
        
        return moves if not return_bb else bb
    
    def generate_king_moves(self, current_position: np.uint64, white_bitboard: np.uint64, black_bitboard: np.uint64, return_bb = False):
        
        # Standard moves & castling
        moves = []
        bb = np.uint64(0)
        index = self.return_lsb_position(current_position)
        
        possible_moves = np.uint64(lookuptables.KING_TABLE[index])
        castle_bools = self.castle_bools_queue.get()
        self.castle_bools_queue.put(castle_bools)
        
        if current_position & white_bitboard:
            # Standard moves
            possible_moves = (possible_moves & white_bitboard) ^ white_bitboard
            while possible_moves != 0:
                current = self.return_lsb_position(possible_moves)
                move_flag = self.CAPTURE if (np.uint64(1) << current) & black_bitboard else self.QUIET_MOVE
                moves.append(self.encode_move(move_flag, index, current))
                bb |= np.uint64(1) << current
                possible_moves ^= (np.uint64(1) << current)
            
            # Castling
            
            if castle_bools[self.CASTLE_WHITE_KING]:
                # Rays of sight
                sight = self.generate_sliding_moves(current_position, white_bitboard, black_bitboard, self.ROOK_ID)
                
                # Short castle
                if castle_bools[self.CASTLE_WHITE_SHORT_ROOK] and np.uint16(0b0000000011000001) in sight:
                    moves.append(self.encode_move(self.KING_CASTLE, current_position, 0))
                    bb |= 0b0000000011000001
                
                # Long castle
                if castle_bools[self.CASTLE_WHITE_LONG_ROOK] and np.uint16(0b0000000011000111) in sight:
                    moves.append(self.encode_move(self.KING_CASTLE, current_position, 7))
                    bb |= 0b0000000011000111
                    

        elif current_position & black_bitboard:
            possible_moves = (possible_moves & black_bitboard) ^ black_bitboard
            while possible_moves != 0:
                current = self.return_lsb_position(possible_moves)
                move_flag = self.CAPTURE if (np.uint64(1) << current) & white_bitboard else self.QUIET_MOVE
                moves.append(self.encode_move(move_flag, index, current))
                bb |= np.uint64(1) << current
                possible_moves ^= (np.uint64(1) << current)
                
            if castle_bools[self.CASTLE_BLACK_KING]:
                # Rays of sight
                sight = self.generate_sliding_moves(current_position, white_bitboard, black_bitboard, self.ROOK_ID)
                
                # Short castle
                if castle_bools[self.CASTLE_BLACK_SHORT_ROOK] and np.uint16(0b0000111011111000) in sight:
                    moves.append(self.encode_move(self.KING_CASTLE, current_position, 56))
                    bb |= 0b0000111011111000
                
                # Long castle
                if castle_bools[self.CASTLE_BLACK_LONG_ROOK] and np.uint16(0b0000111011111111) in sight:
                    moves.append(self.encode_move(self.KING_CASTLE, current_position, 63))
                    bb |= 0b0000111011111111

        return moves if not return_bb else bb
        
    def generate_sliding_moves(self, current_position: np.uint64, white_bitboard: np.uint64, black_bitboard: np.uint64, piece_id, return_bb = False):
        moves = []
        bb = np.uint64(0)
        index = self.return_lsb_position(current_position)
        
        if piece_id == self.ROOK_ID:
            index_number = magicnums.ROOK_MOVES[index].index_number
            magic_number = magicnums.ROOK_MOVES[index].magic
            offset = magicnums.ROOK_MOVES[index].offset
            mask = magicnums.ROOK_MOVES[index].mask
            
            blockers = (white_bitboard | black_bitboard) & mask
            possible_moves = np.uint64(self.ROOK_TABLE[self.generate_magic_index(blockers, magic_number, index_number, offset)])
        elif piece_id == self.BISHOP_ID:
            index_number = magicnums.BISHOP_MOVES[index].index_number
            magic_number = magicnums.BISHOP_MOVES[index].magic
            offset = magicnums.BISHOP_MOVES[index].offset
            mask = magicnums.BISHOP_MOVES[index].mask
            
            blockers = (white_bitboard | black_bitboard) & mask
            possible_moves = np.uint64(self.BISHOP_TABLE[self.generate_magic_index(blockers, magic_number, index_number, offset)])
        elif piece_id == self.QUEEN_ID:
            if not return_bb:
                return self.generate_sliding_moves(current_position, white_bitboard, black_bitboard, self.ROOK_ID) + self.generate_sliding_moves(current_position, white_bitboard, black_bitboard, self.BISHOP_ID)
            else:
                return self.generate_sliding_moves(current_position, white_bitboard, black_bitboard, self.ROOK_ID, True) | self.generate_sliding_moves(current_position, white_bitboard, black_bitboard, self.BISHOP_ID, True)
        if current_position & white_bitboard:
            possible_moves = (possible_moves & white_bitboard) ^ white_bitboard
            while possible_moves != 0:
                current = self.return_lsb_position(possible_moves)
                move_flag = self.CAPTURE if (np.uint64(1) << current) & black_bitboard else self.QUIET_MOVE
                moves.append(self.encode_move(move_flag, index, current))
                bb |= np.uint64(1) << current
                possible_moves ^= (np.uint64(1) << current)
        elif current_position & black_bitboard:
            possible_moves = (possible_moves & black_bitboard) ^ black_bitboard
            while possible_moves != 0:
                current = self.return_lsb_position(possible_moves)
                move_flag = self.CAPTURE if (np.uint64(1) << current) & white_bitboard else self.QUIET_MOVE
                moves.append(self.encode_move(move_flag, index, current))
                bb |= np.uint64(1) << current
                possible_moves ^= (np.uint64(1) << current)
            
        return moves if not return_bb else bb
    
    # MOVE EXECUTION
    def make_move(self, move: np.uint16):

        flag, from_pos, to_pos = self.decode_move(move)
        
        fromBB = np.uint64(1) << from_pos
        toBB = np.uint64(1) << to_pos
        fromToBB = fromBB ^ toBB
        
        # First, find the piece_id and color
        piece_id = -1
        for id, bb in enumerate(self.piece_bitboards):
            if fromBB & bb:
                piece_id = id
                break
        
        side = -1
        for id, color in enumerate(self.side_bitboards):
            if fromBB & color:
                side = id
        
        castle_bools = self.castle_bools_queue.get()
        self.castle_bools_queue.put(castle_bools)
        
        # Update castling parameters depending on position of original position
        if piece_id in [self.ROOK_ID, self.KING_ID]:
            if from_pos == 0:
                castle_bools[self.CASTLE_WHITE_SHORT_ROOK] = False
            elif from_pos == 3:
                castle_bools[self.CASTLE_WHITE_KING] = False
            elif from_pos == 3:
                castle_bools[self.CASTLE_WHITE_LONG_ROOK] = False
            elif from_pos == 56:
                castle_bools[self.CASTLE_BLACK_SHORT_ROOK] = False
            elif from_pos == 59:
                castle_bools[self.CASTLE_BLACK_KING] = False
            elif from_pos == 63:
                castle_bools[self.CASTLE_BLACK_LONG_ROOK] = False
            
        # Update quiet moves first
        self.piece_bitboards[piece_id] ^= fromToBB
        self.side_bitboards[side] ^= fromToBB
        
        # Then update captures
        if flag in [self.CAPTURE, self.BISHOP_PROMOTION_CAPTURE, self.KNIGHT_PROMOTION_CAPTURE, self.QUEEN_PROMOTION_CAPTURE, self.ROOK_PROMOTION_CAPTURE]:
            # Find id and color of captured piece
            captured_piece_id = -1
            for id, bb in enumerate(self.piece_bitboards):
                if toBB & bb:
                    captured_piece_id = id
                    break
            
            # Captured side is opposite of taking side
            captured_side = 1 - side
            
            self.piece_bitboards[captured_piece_id] ^= toBB
            self.side_bitboards[captured_side] ^= toBB
        
        elif flag in [self.EP_CAPTURE]:
            if side == self.WHITE_SIDE:
                capturedBB = np.uint64(1) << (to_pos - self.BOARD_WIDTH)
            elif side == self.BLACK_SIDE:
                capturedBB = np.uint64(1) << (to_pos + self.BOARD_WIDTH)
                
            captured_side = 1 - side
            # We know that the captured piece must be a pawn
            self.piece_bitboards[self.PAWN_ID] ^= capturedBB
            self.side_bitboards[captured_side] ^= capturedBB
        
        # Promotions
        if flag in [self.BISHOP_PROMOTION, self.BISHOP_PROMOTION_CAPTURE, self.KNIGHT_PROMOTION, self.KNIGHT_PROMOTION_CAPTURE, self.QUEEN_PROMOTION, self.QUEEN_PROMOTION_CAPTURE, self.ROOK_PROMOTION, self.BISHOP_PROMOTION_CAPTURE]:
            self.piece_bitboards[piece_id] ^= toBB
            if flag in [self.BISHOP_PROMOTION, self.BISHOP_PROMOTION_CAPTURE]:
                self.piece_bitboards[self.BISHOP_ID] ^= toBB
            elif flag in [self.KNIGHT_PROMOTION, self.KNIGHT_PROMOTION_CAPTURE]:
                self.piece_bitboards[self.KNIGHT_ID] ^= toBB
            elif flag in [self.QUEEN_PROMOTION, self.QUEEN_PROMOTION_CAPTURE]:
                self.piece_bitboards[self.QUEEN_ID] ^= toBB
            elif flag in [self.ROOK_PROMOTION, self.ROOK_PROMOTION_CAPTURE]:
                self.piece_bitboards[self.ROOK_ID] ^= toBB
        
        self.move_history.append(move)
        self.castle_bools_queue.put(castle_bools)
        
        
    def unmake_move(self, history: list):
        last_move = history[-1]
        flag, from_pos, to_pos = self.decode_move(last_move)
        
        fromBB = np.uint64(1) << from_pos
        toBB = np.uint64(1) << to_pos
        fromToBB = fromBB ^ toBB
        
        # First, find the piece_id and color
        piece_id = -1
        for id, bb in enumerate(self.piece_bitboards):
            if fromBB & bb:
                piece_id = id
                break
        
        side = -1
        for id, color in enumerate(self.side_bitboards):
            if fromBB & color:
                side = id
        
        # Reset castle bools queue to previous state
        self.castle_bools_queue.get()
        self.move_history = self.move_history[:-1]
        
        # Undo promotions
        if flag in [self.BISHOP_PROMOTION, self.BISHOP_PROMOTION_CAPTURE, self.KNIGHT_PROMOTION, self.KNIGHT_PROMOTION_CAPTURE, self.QUEEN_PROMOTION, self.QUEEN_PROMOTION_CAPTURE, self.ROOK_PROMOTION, self.BISHOP_PROMOTION_CAPTURE]:
            self.piece_bitboards[piece_id] ^= toBB
            if flag in [self.BISHOP_PROMOTION, self.BISHOP_PROMOTION_CAPTURE]:
                self.piece_bitboards[self.BISHOP_ID] ^= toBB
            elif flag in [self.KNIGHT_PROMOTION, self.KNIGHT_PROMOTION_CAPTURE]:
                self.piece_bitboards[self.KNIGHT_ID] ^= toBB
            elif flag in [self.QUEEN_PROMOTION, self.QUEEN_PROMOTION_CAPTURE]:
                self.piece_bitboards[self.QUEEN_ID] ^= toBB
            elif flag in [self.ROOK_PROMOTION, self.ROOK_PROMOTION_CAPTURE]:
                self.piece_bitboards[self.ROOK_ID] ^= toBB
                
        # Then undo captures
        if flag in [self.CAPTURE, self.BISHOP_PROMOTION_CAPTURE, self.KNIGHT_PROMOTION_CAPTURE, self.QUEEN_PROMOTION_CAPTURE, self.ROOK_PROMOTION_CAPTURE]:
            # Find id and color of captured piece
            captured_piece_id = -1
            for id, bb in enumerate(self.piece_bitboards):
                if toBB & bb:
                    captured_piece_id = id
                    break
            
            # Captured side is opposite of taking side
            captured_side = 1 - side
            
            self.piece_bitboards[captured_piece_id] ^= toBB
            self.side_bitboards[captured_side] ^= toBB
        
        elif flag in [self.EP_CAPTURE]:
            if side == self.WHITE_SIDE:
                capturedBB = np.uint64(1) << (to_pos - self.BOARD_WIDTH)
            elif side == self.BLACK_SIDE:
                capturedBB = np.uint64(1) << (to_pos + self.BOARD_WIDTH)
                
            captured_side = 1 - side
            # We know that the captured piece must be a pawn
            self.piece_bitboards[self.PAWN_ID] ^= capturedBB
            self.side_bitboards[captured_side] ^= capturedBB
                
        # Reset quiet moves
        self.piece_bitboards[piece_id] ^= fromToBB
        self.side_bitboards[side] ^= fromToBB

    
    # HELPER FUNCTIONS
    def generate_magic_index(self, blockers: np.uint64, magic_number: np.uint64, index_number: np.uint64, offset: np.uint64) -> np.uint64:
        return (blockers * magic_number) >> (index_number) + offset
    
    def generate_magic_table(self, deltas, size, data: npt.NDArray):
        table = np.empty(size)
        
        for position in range(self.BOARD_AREA):
            magic_data = data[position]
            rays = magic_data.mask
            
            blockers = np.uint64(0)
            
            # Loop through all subsets
            while True:
                possible_rays = self.generate_piece_rays(deltas, blockers, position)
                table[self.generate_magic_index(blockers, magic_data.magic, magic_data.index_number, magic_data.offset)] = possible_rays
                blockers = (blockers - rays) & rays
                
                if blockers == 0:
                    break
        
        return table

    def generate_piece_rays(self, deltas: tuple[int, int], blockers: np.uint64, position: int) -> np.uint64:
        final = np.uint64(0)
        for delta in deltas:
            ray = np.uint64(1) << np.uint64(position)
            while not (ray & blockers):
                if self.is_bit_colliding_with_border(ray, delta):
                    break
                    
                if ray & blockers:
                    break
                if delta[0] > 0:
                    ray <<= delta[0]
                elif delta[0] < 0:
                    ray >>= abs(delta[0])
                
                if delta[1] > 0:
                    ray <<= (self.BOARD_WIDTH * delta[1])
                elif delta[1] < 0:
                    ray >>= abs(self.BOARD_WIDTH * delta[1])
                
                final |= ray
        
        return final
    
    def display_bitboard(self, val):
        bbstring = self.format_bitboard(bin(val)[2:])
        x = 0
        y = 0
        for y in range(self.BOARD_WIDTH):
            for x in range(self.BOARD_HEIGHT):
                print(bbstring[y * self.BOARD_WIDTH + x], end=" ")
            print()
        print()
        
    def format_bitboard(self, bb: str) -> str:
        # Return bitboard string with empty 0s filled in at the back
        return (self.BOARD_AREA - len(bb)) * "0" + bb

    def is_bit_colliding_with_border(self, ray, delta):
        # Check borders
        if delta[0] < 0:
            if ray & self.RIGHT_BORDER:
                return True
        elif delta[0] > 0:
            if ray & self.LEFT_BORDER:
                return True
            
        if delta[1] < 0:
            if ray & self.FIRST_RANK:
                return True
        elif delta[1] > 0:
            if ray & self.EIGTH_RANK:
                return True
        
        return False
        
    
    def encode_move(self, flag: int, from_pos: int | np.uint64, to_pos: int | np.uint64) -> np.uint16:
        if type(from_pos) == np.uint64:
            from_pos = self.return_lsb_position(from_pos)
        if type(to_pos) == np.uint64:
            to_pos = self.return_lsb_position(to_pos)
        
        return np.uint16((flag << 12) + (from_pos << 6) + to_pos)
    
    def decode_move(self, encoded_move: np.uint16):
        from_pos = encoded_move >> 12
        to_pos = (encoded_move << 4) >> 10
        flag = (encoded_move << 10) >> 10
        return flag, from_pos, to_pos
    
    def return_lsb_position(self, bitboard):
        """Return position of least significant bit in a bitboard."""
        
        index = bit_scan1(int(bitboard))
        
        if index != None: 
            return np.uint64(index)
        else:
            return np.uint64(self.NULL_POSITION)
    
    def display_board(self):
        for row in range(self.BOARD_HEIGHT):
            for piece in range(self.BOARD_WIDTH):
                piece_BB = np.uint64(1) << piece
                if piece_BB & self.side_bitboards[self.WHITE_SIDE]:
                    for id, bb in enumerate(self.piece_bitboards):
                        if piece_BB & bb:
                            print(self.WHITE_ICONS[id], end = " ")
                            break
                elif piece_BB & self.side_bitboards[self.BLACK_SIDE]:
                    for id, bb in enumerate(self.piece_bitboards):
                        if piece_BB & bb:
                            print(self.WHITE_ICONS[id], end = " ")
                            break
                else:
                    print(self.EMPTY_ICON, end = " ")
            
            print()
        
class ChessAI:
    def __init__(self, board):
        self.board = board
    
    def evaluate(self):
        pass
