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
        # self.board = board
        self.setup_board()
        self.setup_bitboards(self.board)
        self.check_move_legal((0, 0), (7, 1))
        self.move((0, 0), (7, 1))
        self.print_bitboard(self.piece_bitboards[self.ROOK_ID])
        

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
        self.board_length = len(self.board[0])
        self.board_width = len(self.board)
        self.board_area = self.board_length * self.board_width

    def setup_bitboards(self, board):
        
        """Initializes all bitboards."""
        self.white_bitboard = ""
        self.black_bitboard = ""
        self.piece_bitboards = ["", "", "", "", "", ""]

        for row in board:
            for piece in row:
                # First recognize if piece is black or white
                if piece.side == "w":
                    self.white_bitboard += "1"
                    self.black_bitboard += "0"
                elif piece.side == "b":
                    self.black_bitboard += "1"
                    self.white_bitboard += "0"
                else:
                    self.white_bitboard += "0"
                    self.black_bitboard += "0"

                # Then check for pieces
                pieces = [0, 1, 2, 3, 4, 5]
                if piece.id in pieces:
                    self.piece_bitboards[piece.id] += "1"
                    pieces.remove(piece.id)
                for pid in pieces:
                    self.piece_bitboards[pid] += "0"

        self.white_bitboard = int(self.white_bitboard, 2)
        self.black_bitboard = int(self.black_bitboard, 2)
        for bitboard in range(len(self.piece_bitboards)):
            self.piece_bitboards[bitboard] = int(self.piece_bitboards[bitboard], 2)

    def check_move_legal(self, p1: tuple[int], p2: tuple[int]):
        self.board[0][0].generate_rays((0, 0), self.board_length, self.board_width)


    def generate_all_possible_moves(self):

        pass
    
    def move(self, p1: tuple[int], p2: tuple[int]):
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
        p1index = p1[0] * self.board_length + p1[1]
        p2index = p2[0] * self.board_length + p2[1]
        movebb[p1index] = "1"
        movebb[p2index] = "1"
        movebb = "".join(movebb)
        movebb = int(movebb, 2)

        takenbb = ["0"] * self.board_area
        takenbb[p2index] = "1"
        takenbb = "".join(takenbb)
        takenbb = int(takenbb, 2)

        # Update white and black bitboards
        if p2piece.side == "w":
            self.white_bitboard = self.white_bitboard ^ takenbb
        elif p2piece.side == "b":
            self.black_bitboard = self.black_bitboard ^ takenbb
        
        if p1piece.side == "w":
            self.white_bitboard = self.white_bitboard ^ movebb
            self.white_bitboard = self.white_bitboard | takenbb
        elif p1piece.side == "b":
            self.black_bitboard = self.black_bitboard ^ movebb
            self.black_bitboard = self.black_bitboard | takenbb
        
        # If piece is taken update bitboard of taken piece first
        if p2piece.id != 6:
            self.piece_bitboards[p2piece.id] = self.piece_bitboards[p2piece.id] ^ takenbb
        # Then update bitboard of moved piece
        if p1piece.id != 6:
            self.piece_bitboards[p1piece.id] = self.piece_bitboards[p1piece.id] ^ movebb

        # Move piece
        self.board[p2[0]][p2[1]] = self.board[p1[0]][p1[1]]
        import pieces
        self.board[p1[0]][p1[1]] = pieces.EmptyPiece(self)
        pass
    
    def format_bitboard(self, bb: str) -> str:
        # Return bitboard string with empty 0s filled in at the back
        return (self.board_area - len(bb)) * "0" + bb
    
    # TEMPORARY
    def print_bitboard(self, bb: int):
        bb = bin(bb)[2:]
        bb = self.format_bitboard(bb)
        x = 0
        y = 0
        for y in range(self.board_width):
            for x in range(self.board_length):
                print(bb[y * self.board_width + x], end=" ")
            print()
        print()