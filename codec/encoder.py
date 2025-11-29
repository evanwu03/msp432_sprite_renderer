


import cv2 
import numpy as np


from color_utils import Color_Resolution
from color_utils import bgr_to_bgr332_frame
from color_utils import bgr_to_bgr444_frame
from color_utils import bgr_to_bgr565_frame


from config import *


# Performs delta compression on a stream of frames and returns 
# a list of frames
def deltaEncode(cap: cv2.VideoCapture, color_resolution=Color_Resolution.COLOR_BGR565) -> np.ndarray:

    frames = []

    prev_frame = None

    while cap.isOpened():
        ret, current_frame = cap.read()

        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break


        # Convert from BGR to BGR565
        #current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2BGR565)
        #current_frame = bgr_to_bgr565(current_frame).astype(np.uint16)

        if color_resolution == Color_Resolution.COLOR_BGR565:
            current_frame = bgr_to_bgr565_frame(current_frame).astype(np.uint16)
        elif color_resolution == Color_Resolution.COLOR_BGR444:
            current_frame = bgr_to_bgr444_frame(current_frame).astype(np.uint16)
        elif color_resolution == Color_Resolution.COLOR_BGR332: 
            current_frame = bgr_to_bgr332_frame(current_frame).astype(np.uint16)
        
    
        if prev_frame is None: 
            #frames.append(current_frame)
            prev_frame = current_frame
            continue

        # Compute the delta frame as difference between current and previous frame
        # append it to list and update previous frame value
        delta_frame = np.subtract(current_frame, prev_frame)


        frames.append(delta_frame) 

        prev_frame = current_frame

    cap.release()
    return frames




def zigzagEncode(arr: np.ndarray) -> np.ndarray:
    return (arr << 1) ^ (arr >> 15)



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



def compress_video(cap: cv2.VideoCapture, filepath, color_resolution: Color_Resolution) -> bytearray:

    cap.open(filepath)


    #Delta Encoding
    delta_frames = deltaEncode(cap, Color_Resolution.COLOR_BGR332) # Need to edit so first frame is also returned
    delta_flatten = np.concatenate([frame.flatten() for frame in delta_frames])


    # Dumps delta frames in a txt file
    with open(FRAME_TXT_DUMP, "w") as f:
        for i, frame in enumerate(delta_frames):
            f.write(f"# --- Frame {i} ---\n")
            np.savetxt(f, frame, fmt="%x")
            f.write("\n\n")


    # ========================================================
    # Pixel Level RLE encoding scheme without tile compression 
    # ========================================================

    # Before encoding
    total_frames = len(delta_frames)
    print(f'Total number of frames: {total_frames}')
    print('Before variable length encoding')
    print(f'Total number of pixels: {len(delta_flatten)}')
    print(f'Total number of bytes: {len(delta_flatten)*2}\n')



    # flatten frames in 1D pixel array represented as uint16
    delta_pixels = np.concatenate([frame.flatten() for frame in delta_frames])
    delta_pixels = delta_pixels.astype(np.int16)
    delta_pixels.tofile(DELTA_BIN) 

    
     # Perform Zigzag -> RLE -> VLE chain
    zigzag_vals     = zigzagEncode(delta_pixels)
    rle_vals        = rleEncode(zigzag_vals)
    pixels_with_vle = variableLengthEncode(rle_vals)


    # Debugging information
    print('After variable length encoding')
    print(f'Total number of bytes: {len(pixels_with_vle)}')


    return pixels_with_vle