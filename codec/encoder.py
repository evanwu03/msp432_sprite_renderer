


import cv2 
import numpy as np


from color_utils import Color_Resolution
from color_utils import bgr_to_bgr332_frame
from color_utils import bgr_to_bgr444_frame
from color_utils import bgr_to_bgr565_frame

# Performs delta compression on a stream of frames and returns 
# a list of frames
def deltaEncode(cap: cv2.VideoCapture, color_resolution=Color_Resolution.COLOR_BGR565) -> list:

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


# Variable length encoding
# 1. Break number into 7 bit groups
# 2. Set top bit = 0 for last byte
# 3. Set top bit = 1 for continuation
def encodeUint16(x: int) -> bytearray:

    buf = bytearray()

    while True: 

        byte = x & 0x7F
        x >>= 7
        
        if x != 0:
            byte |= 0x80 
    
        buf.append(byte)

        if x == 0:
            break

    return buf # Return byte array 


def zigzagEncode(x: int) -> int:
    return int((x << 1) ^ (x >> 15))



def rleEncode(values: list[int]) -> list[int]:

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

