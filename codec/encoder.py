


import numpy as np
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
        
    return np.array(zigzag, dtype=np.uint8)

def zigzagEncodeSingle(val) :
    if val < 0:
        return - 2 * val  - 1
    return 2 * val 
 """


def rleEncode(values: np.ndarray) -> np.ndarray:
    result = []
    n = len(values)
    i = 0

    RUN_HEADER = 0x80
    LITERAL_HEADER = 0x00


    while i < n:
        # =============================================================
        # Check for encoded run (repetition of same value)
        # =============================================================
        run_val = int(values[i])
        run_len = 1


        while((i + run_len < n) and (run_len < 127) and (values[i+run_len] == run_val)):
            run_len += 1
    

        if run_len >= 2: 

            header = RUN_HEADER | run_len
            result.append(header)
            result.append(run_val)
            i += run_len
            continue

        # =============================================================
        # Otherwise: LITERAL RUN (collect until next repeated run)
        # =============================================================

        literal_count = 1
        lit_start = i

        while i + literal_count < n and literal_count < 127: 

  
            next_idx = lit_start + literal_count

            if  (next_idx < n - 1) and (int(values[next_idx]) == values[next_idx+1]):
                break

            literal_count += 1
       
        header = LITERAL_HEADER | literal_count 
        result.append(header)

        for j in range(0, literal_count):
            result.append(values[i+j])


        i += literal_count

    return np.array(result, dtype=np.uint8)


""" def rle_vertical_replication(values: np.ndarray) -> np.ndarray:

    result = []
    i = int(0) 
    n = len(values)
    run_len = np.uint8(0)

    while i < n: 

    
    return 
 """



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

    compressed_frames = bytearray()

    #Delta Encoding
    delta_frames = deltaEncode(frames) # Need to edit so first frame is also returned

    # Dumps delta frames in a txt file
    with open(FRAME_TXT_DUMP, "w") as f:
        for i, frame in enumerate(delta_frames):
            f.write(f"# --- Frame {i} ---\n")
            np.savetxt(f, frame, fmt="%x")
            f.write("\n\n")


    # ==============================
    # Byte Level RLE encoding scheme
    # ==============================

    # Before encoding
    #total_frames = len(delta_frames)
    #print(f'Total number of frames: {total_frames}')

    # Perform Zigzag -> RLE 
    for frame in delta_frames: 

        flat_frame = frame.ravel()
        assert len(flat_frame) == 128*128 
        zigzag_frame = zigzagEncode(flat_frame)
        assert zigzag_frame.ndim == 1
        assert len(zigzag_frame) == 128*128  
        rle_frame = rleEncode(zigzag_frame)

        compressed_frames.extend(rle_frame)

    # Debugging information
    print(f'Total number of bytes after RLE: {len(compressed_frames)}')

    return compressed_frames