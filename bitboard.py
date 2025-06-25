from gmpy2 import bit_scan1
import numpy


class Bitboard():
    def __init__(self, value: numpy.uint64, board_width: int, board_height: int):
        self.value = value
        self.board_width = board_width
        self.board_height = board_height
        self.board_area = board_width * board_height
    
    def display_bitboard(self):
        bbstring = self.format_bitboard(bin(self.value)[2:])
        x = 0
        y = 0
        for y in range(self.board_width):
            for x in range(self.board_height):
                print(bbstring[y * self.board_width + x], end=" ")
            print()
        print()
    
    def return_bitboard_coordinates(self, bitboard = None):
        """Return coordinates of least significant bit in a bitboard."""
        if bitboard == None:
            bitboard = self
        
        index = bit_scan1(bitboard.value)
        return self.convert_index_to_coordinates(index)
        
    def convert_index_to_coordinates(self, index: int):
        y_pos = index // self.board_width
        return (y_pos, index - (y_pos * self.board_width))
    
    def format_bitboard(self, bb: str) -> str:
        # Return bitboard string with empty 0s filled in at the back
        return (self.board_area - len(bb)) * "0" + bb

    def update(self, new_value: int):
        self.value = new_value
