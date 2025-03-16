from displayio import Palette

# Helper method to create a 1-bit palette with a black background and the specified color as the foreground.
def make_palette(color):
    p = Palette(2)
    p[0] = 0x000000
    p[1] = color
    return p

# Do not remove these. They may be referenced by name elsewhere.
# Feel free to change the actual color value, however.
WHITE = 0xFFFFFF
ORANGE = 0xFF9000
AMBER = 0xFFBF00
YELLOW = 0xFFFF00
GREEN = 0x41FF00
CYAN = 0x00FFFF
BLUE = 0x0000FF
PURPLE = 0xA000FF
MAGENTA = 0xFF00FF
RED = 0xFF0000

# Feel free to add new colors here

# You can add or remove any colors to this list that you want, as long as there is at least one.
ALL = [
    WHITE,
    ORANGE, 
    AMBER,
    YELLOW,
    GREEN,
    CYAN,
    BLUE,
    PURPLE,
    MAGENTA,
    RED,    
]