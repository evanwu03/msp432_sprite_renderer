

import cv2
import numpy as np
from enum import Enum

class Color_Resolution(Enum):
    COLOR_BGR565 = 0
    COLOR_BGR444 = 1
    COLOR_BGR332 = 2


# Converts a frame in BGR888 -> BGR565
def bgr_to_bgr565_frame(bgr: cv2.typing.MatLike) -> cv2.typing.MatLike:

    blue  = (bgr[:, :, 0] >> 3)
    green = (bgr[:, :, 1] >> 2)
    red   = (bgr[:, :, 2] >> 3)

    #bgr565 = (red << 11) | (green << 5) | blue
    bgr565  = (blue << 11) | (green << 5) | red
    return bgr565


# Converts a frame in BGR888 -> BGR565
def bgr_to_bgr444_frame(bgr: cv2.typing.MatLike) -> cv2.typing.MatLike:

    blue  = (bgr[:, :, 0] >> 4)
    green = (bgr[:, :, 1] >> 4)
    red   = (bgr[:, :, 2] >> 4)

    #bgr444 = (red << 9) | (green << 5) | blue
    bgr444 = (blue << 9) | (green << 5) | red
    return bgr444


# 8 bit palette quantization using uniform scaling. Want to replace this with more optimized methods eventually
def bgr_to_bgr332_frame(bgr: cv2.typing.MatLike) -> cv2.typing.MatLike:

    blue  = (bgr[:, :, 0] >> 5)
    green = (bgr[:, :, 1] >> 5)
    red   = (bgr[:, :, 2] >> 6)

    #bgr444 = (red << 5) | (green << 2) | blue
    bgr444 = (blue << 5) | (green << 2) | red
    return bgr444


def bgr24_to_int(bgr: cv2.typing.MatLike) -> cv2.typing.MatLike:

    blue  = bgr[:, :, 0].astype(np.uint32)
    green = bgr[:, :, 1].astype(np.uint32)
    red   = bgr[:, :, 2].astype(np.uint32)

    #print(f'B: {blue}, G: {green}, R: {red}')
    bgr24 = (blue << 16) | (green << 8) | red 

    
    return bgr24.astype(np.uint32)


