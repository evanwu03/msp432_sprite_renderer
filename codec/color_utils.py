

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

    b5 = (b >> 3) & 0x1F
    g6 = (g >> 2) & 0x3F
    r5 = (r >> 3) & 0x1F

    return ((b5 << 11) | (g6 << 5) | r5).astype(np.uint16)



# Converts a frame in BGR888 -> BGR565
def bgr_to_bgr444_frame(bgr: np.ndarray) -> np.ndarray:

    blue  = (bgr[:, :, 0] >> 4)
    green = (bgr[:, :, 1] >> 4)
    red   = (bgr[:, :, 2] >> 4)

    #bgr444 = (red << 9) | (green << 5) | blue
    bgr444 = (blue << 9) | (green << 5) | red
    return bgr444


# 8 bit palette quantization using uniform scaling. Want to replace this with more optimized methods eventually
def bgr_to_bgr332_frame(bgr: np.ndarray) -> np.ndarray:

    blue  = (bgr[:, :, 0] >> 5)
    green = (bgr[:, :, 1] >> 5)
    red   = (bgr[:, :, 2] >> 6)

    #bgr444 = (red << 5) | (green << 2) | blue
    bgr444 = (blue << 5) | (green << 2) | red
    return bgr444


def bgr24_to_int(bgr: np.ndarray) -> np.ndarray:

    blue  = bgr[:, :, 0].astype(np.uint32)
    green = bgr[:, :, 1].astype(np.uint32)
    red   = bgr[:, :, 2].astype(np.uint32)

    #print(f'B: {blue}, G: {green}, R: {red}')
    bgr24 = (blue << 16) | (green << 8) | red 

    
    return bgr24.astype(np.uint32)


