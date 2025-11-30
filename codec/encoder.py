


import numpy as np
from config import *
from decoder import zigzagDecode

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
    rle_vals       = rleEncode(zigzag_vals)
    pixels_with_vle = variableLengthEncode(rle_vals)


    """ # Debugging information
    zig_zag_debug = zigzag_vals.reshape(total_frames, 128, 128)
    with open("output/zigzag.txt", "w") as f:
        for j, frame in enumerate(zig_zag_debug):
            f.write(f"# --- Frame {j} ---\n")
            np.savetxt(f, frame, fmt="%x")
            f.write("\n\n")

    rle_vals.tofile("output/rle.bin")

    with open('output/rle.txt', "w") as f:
        for i in range(0, len(rle_vals), 128):
            row = rle_vals[i:i+128]
            f.write(" ".join(hex(x) for x in row) + "\n") """


    """ decoded_zig = zigzagDecode(zigzag_vals).reshape(total_frames, 128, 128)
    with open("output/decoded_zig.txt", "w") as f:
        for j, frame in enumerate(decoded_zig):
            f.write(f"# --- Frame {j} ---\n")
            np.savetxt(f, frame, fmt="%x")
            f.write("\n\n") """


    print(f'Total number of bytes after RLE: {len(rle_vals)}')
    print(f'Total number of bytes if processed with VLE: {len(pixels_with_vle)}')


    #return pixels_with_vle
    return rle_vals # Seems applying VLE is unecessary now