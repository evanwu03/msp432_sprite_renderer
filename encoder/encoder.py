


import cv2 
import numpy as np
import time 
import os


# Filepaths
FILENAME = 'ordinary.mp4'
#FILENAME = 'ryo_yamada_128x128.mp4'
BASE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE, 'videos', FILENAME)
FRAME_TXT_DUMP = os.path.join(BASE, 'output', 'delta.txt')
DELTA_BIN = os.path.join(BASE, 'output', 'delta.bin')
ENCODED_TXT_DUMP = os.path.join(BASE, 'output', 'post_vle.txt')
ENCODED_BIN  = os.path.join(BASE, 'output', 'post_vle.bin')
DECODED_TXT_DUMP = os.path.join(BASE, 'output', 'decoded_pixels.txt')
DECODED_BIN = os.path.join(BASE, 'output', 'decoded_pixels.bin')



# Tile Specifications
TILE_WIDTH  = 8 # Pixels
TILE_HEIGHT = 8
NUM_TILES = 256
FRAME_WIDTH = 128
FRAME_HEIGHT = 128

# Tile OPCODe
TILE_SKIP = 0xFF 
TILE_DATA = 0xFE



# Plays back video on screen
def video_playback(cap: cv2.VideoCapture) -> None:
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = 1/fps

    while cap.isOpened():
        ret, frame = cap.read()
        
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            print('Ending playback...')
            break

        time.sleep(delay)

    cap.release()
    cv2.destroyAllWindows()





# Performs delta compression on a stream of frames and returns 
# a list of frames
def deltaEncode(cap: cv2.VideoCapture) -> list:

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
        current_frame = bgr_to_bgr565(current_frame).astype(np.uint16)

    
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


"""
Undo delta compression.
deltas: list of delta frames (each int16 or int32 2D array)
first_frame: the original BGR565 frame (uint16)
Returns list of full frames in uint16.
"""
""" def delta_decode(deltas: np.ndarray, first_frame: np.ndarray) -> np.ndarray:
    print('Hello World')
 """

# Converts a frame in BGR888 -> BGR565
def bgr_to_bgr565(bgr: cv2.typing.MatLike) -> cv2.typing.MatLike:

    blue  = (bgr[:, :, 0] >> 3)
    green = (bgr[:, :, 1] >> 2)
    red   = (bgr[:, :, 2] >> 3)

    bgr565 = (red << 11) | (green << 5) | blue
    return bgr565



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



def zigzagDecode(x: int) -> int:
    return (x >> 1) ^ (-(x&1))




def decodeUint16(stream: bytearray, pos: int) -> tuple[int, int]: 

    val = int(0)
    shift = 0

    while True: 

        byte = stream[pos]
        pos += 1

        val |= (byte & 0x7F) << shift # Extract the least significant 7 bits   
        shift += 7

        if (byte & 0x80) == 0: # MSB = 0 -> end of integer
            break

    return val, pos




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


def rleDecode(values: list[int]) -> list[int]:

    result = []
    i = 0
    n = len(values)
    run_len = 0

    while i < n:

        cur = values[i]

        if cur == 0 :
            run_len = values[i+1]
            result.extend([0] * run_len)
            i += 2
        else:
            result.append(values[i])
            i += 1

    return result



def main(): 

    start_time = time.time()


    cap = cv2.VideoCapture(PATH)

    print(f'FPS: {cap.get(cv2.CAP_PROP_FPS)}')      
    video_playback(cap)
    

    # Open video
    cap.open(PATH)

    #Delta Encoding
    delta_frames = deltaEncode(cap) # np.ndarray of frames from mp4
    delta_flatten = np.concatenate([frame.flatten() for frame in delta_frames])

    # Perform Tile compression/skipping here
    # 
    # 
    tiles = []

    # Construct tiles
    for frame in delta_frames:
        for row in range(0, FRAME_WIDTH, TILE_WIDTH): 
            for col in range(0, FRAME_HEIGHT, TILE_HEIGHT): # Scan across columns first then
                tile = np.array(frame[row:row+TILE_HEIGHT, col:col+TILE_WIDTH])
                tiles.append(tile)


    output = bytearray()

    # run tile compression algorithm
    for tile in tiles:

        tile_all_zeros = not np.any(tile)

        if not np.any(tile): 
            #output.extend(encodeUint16(TILE_SKIP))
            output.append(TILE_SKIP)

        else: 
            flat_tile = tile.flatten()    
            # Run Zigzag, and RLE
            zz = [zigzagEncode(px) for px in flat_tile]   

            rle = rleEncode(zz)


            # Write length of RLE so we can decode tile boundary later
            output.extend(encodeUint16(len(rle)))

            for px in rle:
                output.extend(encodeUint16(px)) 


    # Debugging information
    print(f'Total number of frames: {len(delta_frames)}')
    print('Before variable length encoding')
    print(f'Total number of pixels: {len(delta_flatten)}')
    print(f'Total number of bytes: {len(delta_flatten)*2}\n')

    print('After variable length encoding')
    print(f'Total number of bytes: {len(output)}')
        
    # flatten frames in 1D pixel array represented as uint16
    delta_pixels = np.concatenate([frame.flatten() for frame in delta_frames])
    delta_pixels = delta_pixels.astype(np.int16)
    delta_pixels.tofile(DELTA_BIN)


    # Decoding back to BGR656 delta frames
    """ zigzag_vals_rle_encoded = []
    pos = 0
    while pos < len(output): 
        val, pos = decodeUint16(output, pos)
        zigzag_vals_rle_encoded.append(val)

    decoded_zigzag_vals = rleDecode(zigzag_vals_rle_encoded)

    decoded_to_deltas = np.array([zigzagDecode(px) for px in decoded_zigzag_vals], dtype=np.int16)
    decoded_to_deltas.tofile(DECODED_BIN)  """
    
    """

    # Debugging information
    print('Before variable length encoding')
    print(f'Total number of pixels: {len(delta_pixels)}')
    print(f'Total number of bytes: {len(delta_pixels)*2}\n')

    
    # Perform Zigzag -> RLE -> VLE chain
    zigzag_vals = [zigzagEncode(px) for px in delta_pixels]
    rle_vals    = rleEncode(zigzag_vals)
    pixels_with_vle = bytearray().join(
        encodeUint16(px) for px in rle_vals
    )
    
    # Debugging information
    print('After variable length encoding')
    print(f'Total number of bytes: {len(pixels_with_vle)}')




    # Decoding back to BGR656 delta frames
    zigzag_vals_rle_encoded = []
    pos = 0
    while pos < len(pixels_with_vle): 
        val, pos = decodeUint16(pixels_with_vle, pos)
        zigzag_vals_rle_encoded.append(val)

    decoded_zigzag_vals = rleDecode(zigzag_vals_rle_encoded)

    decoded_to_deltas = np.array([zigzagDecode(px) for px in decoded_zigzag_vals], dtype=np.int16)
    decoded_to_deltas.tofile(DECODED_BIN) """


    # Dumps delta frames in a txt file
    with open(FRAME_TXT_DUMP, "w") as f:
        for i, frame in enumerate(delta_frames):
            f.write(f"# --- Frame {i} ---\n")
            np.savetxt(f, frame, fmt="%x")
            f.write("\n\n")


    # Dump to binary and txt file
    with open(ENCODED_BIN, "wb") as f:
        f.write(output) 

    
    end_time = time.time()
    print(f'Total time elapsed: {end_time-start_time:.2f}')

if __name__ == "__main__":
    main()