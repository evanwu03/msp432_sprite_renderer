


import cv2 
import numpy as np


from color_utils import Color_Resolution
from color_utils import bgr_to_bgr332_frame
from color_utils import bgr_to_bgr444_frame
from color_utils import bgr_to_bgr565_frame


from config import *


# Performs delta compression on a stream of frames and returns 
# a list of frames
def deltaEncode(palette_indices: np.ndarray) -> np.ndarray:


    deltas = []

    prev = None

    for idx_frame in palette_indices: 

        if prev is None:
            deltas.append(idx_frame)
            prev = idx_frame
            continue

        # Compute the delta frame as difference between current and previous frame
        # append it to list and update previous frame value
        delta_frame = idx_frame.astype(np.int16) - prev.astype(np.int16)

        deltas.append(delta_frame) 

        prev = idx_frame


    return deltas

    
def zigzagEncode(arr: np.ndarray) -> np.ndarray:
    return ((arr << 1) ^ (arr >> 15)).astype(np.uint8)


""" def zigzagEncode(arr: np.ndarray) -> np.ndarray: 

    zigzag = []
    for i in range(len(arr)):
        zigzag.append(zigzagEncodeSingle(arr[i]))
        
    return np.array(zigzag, dtype=np.uint16)

def zigzagEncodeSingle(val) :
    if val < 0:
        return - 2 * val  - 1
    return 2 * val  """


def rleEncode(values: np.ndarray) -> np.ndarray:

    result = []
    i = 0 
    n = len(values)
    run_len = 0

    while i < n:

        cur = values[i]

        if cur == 0:
            run_len = 1
            while (i+run_len < n) and (values[i+run_len] == 0):
                run_len += 1

            # Append (val, count)
            result.append(cur)
            result.append(run_len)
            i += run_len

        else: 
            result.append(cur)
            i+=1


    return result 


# Variable length encoding
# 1. Break number into 7 bit groups
# 2. Set top bit = 0 for last byte
# 3. Set top bit = 1 for continuation

def variableLengthEncode(arr: np.ndarray) -> bytearray:
    out = bytearray()
    for v in arr:
        out.extend(encodeUint16(int(v)))
    return out


def encodeUint16(arr: int) -> bytearray:

    buf = bytearray()

    while True: 

        byte = arr & 0x7F
        arr >>= 7
        
        if arr != 0:
            byte |= 0x80 
    
        buf.append(byte)

        if arr == 0:
            break

    return buf # Return byte array 



def compress_video(frames: np.ndarray) -> bytearray:


    #Delta Encoding
    delta_frames = deltaEncode(frames) # Need to edit so first frame is also returned

    # Dumps delta frames in a txt file
    with open(FRAME_TXT_DUMP, "w") as f:
        for i, frame in enumerate(delta_frames):
            f.write(f"# --- Frame {i} ---\n")
            np.savetxt(f, frame, fmt="%x")
            f.write("\n\n")


    # ========================================================
    # Pixel Level RLE encoding scheme without tile compression 
    # ========================================================


    # flatten frames in 1D pixel array represented as uint16
    delta_pixels = np.concatenate([frame.flatten() for frame in delta_frames])
    delta_pixels = delta_pixels.astype(np.int16)
    delta_pixels.tofile(DELTA_BIN) 

    # Before encoding
    total_frames = len(delta_frames)
    print(f'Total number of frames: {total_frames}')
    print('Before variable length encoding')
    print(f'Total number of pixels: {len(delta_pixels)}')
    print(f'Total number of bytes: {len(delta_pixels)*2}\n')


     # Perform Zigzag -> RLE -> VLE chain
    zigzag_vals     = zigzagEncode(delta_pixels)
    rle_vals        = rleEncode(zigzag_vals)
    pixels_with_vle = variableLengthEncode(rle_vals)


    # Debugging information
    print('After variable length encoding')
    print(f'Total number of bytes: {len(pixels_with_vle)}')


    return pixels_with_vle