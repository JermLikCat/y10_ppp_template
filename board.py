class Board():
    def __init__(self, game, side: str = "w"):
        self.game = game
        self.side = side
        self.wmaterial = []
        self.bmaterial = []
        # self.board = board
        self.setup_board()
        self.setup_bitboards(self.board)
        self.move((0, 0), (7, 0))
        self.print_bitboard(self.white_bitboard)
        self.print_bitboard(self.black_bitboard)
        self.print_bitboard(self.piece_bitboards[2])

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

        takenbb = ["0"] * self.board_area
        takenbb[p2index] = "1"
        takenbb = "".join(takenbb)

        

        # Update white and black bitboards
        if p2piece.side == "w":
            print(self.white_bitboard)
            print(takenbb)
            self.white_bitboard = bin(int(self.white_bitboard, 2) ^ int(takenbb, 2))[2:]
        elif p2piece.side == "b":
            self.black_bitboard = bin(int(self.black_bitboard, 2) ^ int(takenbb, 2))[2:]
        print(self.white_bitboard)
        if p1piece.side == "w":
            self.white_bitboard = bin(int(self.white_bitboard, 2) ^ int(movebb, 2))[2:]
            self.white_bitboard = bin(int(self.white_bitboard, 2) | int(takenbb, 2))[2:]
        elif p1piece.side == "b":
            self.black_bitboard = bin(int(self.black_bitboard, 2) ^ int(movebb, 2))[2:]
            self.black_bitboard = bin(int(self.black_bitboard, 2) | int(takenbb, 2))[2:]
        

        print("P1 & P2")
        self.print_bitboard(self.piece_bitboards[p2piece.id])
        self.print_bitboard(self.piece_bitboards[p1piece.id])
        # If piece is taken update bitboard of taken piece first
        if p2piece.id != 6:
            self.piece_bitboards[p2piece.id] = bin(int(self.piece_bitboards[p2piece.id], 2) ^ int(takenbb, 2))[2:]
        
        # Then update bitboard of moved piece
        if p1piece.id != 6:
            self.piece_bitboards[p1piece.id] = bin(int(self.piece_bitboards[p1piece.id], 2) | int(movebb, 2))[2:]

        # Reformat bitboards
        self.white_bitboard = self.format_bitboard(self.white_bitboard)
        self.black_bitboard = self.format_bitboard(self.black_bitboard)
        if p1piece.id != 6:
            self.piece_bitboards[p1piece.id] = self.format_bitboard(self.piece_bitboards[p1piece.id])

        # Move piece
        self.board[p2[0]][p2[1]] = self.board[p1[0]][p1[1]]
        import pieces
        self.board[p1[0]][p1[1]] = pieces.EmptyPiece(self)

        

        pass
    
    def format_bitboard(self, bb: str) -> str:
        # Return bitboard string with empty 0s filled in at the back
        return (self.board_area - len(bb)) * "0" + bb
    
    # TEMPORARY
    def print_bitboard(self, bb):
        x = 0
        y = 0
        for y in range(self.board_width):
            for x in range(self.board_length):
                print(bb[y * self.board_width + x], end=" ")
            print()
        print()