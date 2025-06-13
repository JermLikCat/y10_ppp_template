class Bitboard():
    def __init__(self, value: int, board_width: int, board_height: int):
        self.value = value
        self.board_width = board_width
        self.board_height = board_height
        self.board_area = board_width * board_height
    
    def display_bitboard(self, bb: int):
        bbstring = self.format_bitboard(bin(bb)[2:])
        x = 0
        y = 0
        for y in range(self.board_width):
            for x in range(self.board_height):
                print(bbstring[y * self.board_width + x], end=" ")
            print()
        print()
        
    def format_bitboard(self, bb: str) -> str:
        # Return bitboard string with empty 0s filled in at the back
        return (self.board_area - len(bb)) * "0" + bb