

import numpy as np
from enum import Enum

class Color_Resolution(Enum):
    COLOR_BGR565 = 0
    COLOR_BGR444 = 1
    COLOR_BGR332 = 2


# Converts a frame in BGR888 -> BGR565
# first_frame: shape (H*W,), dtype uint32, format 0xBBGGRR

def bgr24_to_bgr565(pixels24: np.ndarray) -> np.ndarray:
    b = (pixels24 >> 16) & 0xFF
    g = (pixels24 >> 8)  & 0xFF
    r =  pixels24        & 0xFF

    b5 = (b >> 3)
    g6 = (g >> 2) 
    r5 = (r >> 3) 

    return ((b5 << 11) | (g6 << 5) | r5).astype(np.uint16)
