


import cv2 
import numpy as np
import time 
import os
from enum import Enum 



# Filepaths
FILENAME = 'ordinary.mp4'
#FILENAME = 'ordinary_12fps.mp4'
#FILENAME = 'ordinary_96x96_12fps.mp4'
#FILENAME = 'kanade_128x128.mp4'
#FILENAME = 'ryo_yamada_128x128.mp4'
#FILENAME = 'ryo_yamada_128x128_12fps.mp4'
#FILENAME = 'kikuri.mp4'

BASE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE, 'videos', FILENAME)
FRAME_TXT_DUMP = os.path.join(BASE, 'output', 'delta.txt')
DELTA_BIN = os.path.join(BASE, 'output', 'delta.bin')
ENCODED_TXT_DUMP = os.path.join(BASE, 'output', 'post_vle.txt')
ENCODED_BIN  = os.path.join(BASE, 'output', 'post_vle.bin')
DECODED_TXT_DUMP = os.path.join(BASE, 'output', 'decoded_pixels.txt')
DECODED_BIN = os.path.join(BASE, 'output', 'decoded_pixels.bin')



# Tile Specifications
TILE_WIDTH  = 16 # Pixels
TILE_HEIGHT = 16
NUM_TILES = 256
FRAME_WIDTH = 128
FRAME_HEIGHT = 128


class Color_Resolution(Enum):
    COLOR_BGR565 = 0
    COLOR_BGR444 = 1
    COLOR_BGR332 = 2



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



# Converts a frame in BGR888 -> BGR565
def bgr_to_bgr565_frame(bgr: cv2.typing.MatLike) -> cv2.typing.MatLike:

    blue  = (bgr[:, :, 0] >> 3)
    green = (bgr[:, :, 1] >> 2)
    red   = (bgr[:, :, 2] >> 3)

    #bgr565 = (red << 11) | (green << 5) | blue
    bgr565  = (blue << 11) | (green << 5) | red
    return bgr565

def palette_bgr24_to_bgr565(palette24: list[int]) -> list[int]:
    palette565 = []
    for px in palette24:
        B = (px >> 16) & 0xFF
        G = (px >> 8)  & 0xFF
        R =  px        & 0xFF

        r5 = R >> 3
        g6 = G >> 2
        b5 = B >> 3

        rgb565 = (r5 << 11) | (g6 << 5) | b5
        palette565.append(rgb565)
    return palette565



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
    #run_len1 = 0


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

        # If we decide to RLE on consecutive 1s
        """ if cur == 1:
            run_len1 = 1
            while (i+run_len1 < n) and (values[i+run_len1] == 0):
                run_len1 += 1

            # Append (val, count)
            result.append(cur)
            result.append(run_len1)
            i += run_len1    """      


        
        


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



def generate_palette(bucket, num_colors=256):

    target_depth = int(np.log2(num_colors)) 
    assert 2**target_depth == num_colors # "Num colors must be a power of 2!"

    return median_cut_recurse(bucket, 0, target_depth)


def median_cut_recurse(bucket, level, target_depth): 

    if level == target_depth:
        return [averageColor(bucket)]
    
    lower_palette, upper_palette = split_bucket(bucket)

    left_colors = median_cut_recurse(lower_palette, level+1, target_depth)
    right_colors = median_cut_recurse(upper_palette, level+1, target_depth)

    return left_colors + right_colors
def split_bucket(pixels): 

    b_min = min( (px >> 16) & 0xFF for px in pixels)
    b_max = max( (px >> 16) & 0xFF for px in pixels)
    g_min = min( (px >> 8)  & 0xFF for px in pixels)
    g_max = max( (px >> 8)  & 0xFF for px in pixels)
    r_min = min( (px & 0xFF) for px in pixels)
    r_max = max( (px & 0xFF) for px in pixels)

    b_range = b_max - b_min
    g_range = g_max - g_min
    r_range = r_max - r_min

    #print(f'min(B): {b_min}, max(B): {b_max}')
    #print(f'min(G): {g_min}, max(B): {g_max}')
    #print(f'min(B): {r_min}, max(B): {r_max}')


    if b_range >= g_range and b_range >= r_range: # Sort by blue 
        #pixels.sort(key=lambda px: (px >> 16) & 0xFF)
        pixels = sorted(pixels, key=lambda px: (px >> 16) & 0xFF)
    elif g_range >= r_range: # Sort by green 
        #pixels.sort(key=lambda px: (px >> 8) & 0xFF) 
        pixels = sorted(pixels, key=lambda px: (px >> 8) & 0xFF)
    elif r_range >= g_range: # Otherwise sort by red
        #pixels.sort(key=lambda px: (px & 0xFF))
        pixels = sorted(pixels, key=lambda px: (px & 0xFF))

    lower, upper = np.array_split(pixels, 2)

    """ print("\n--- DEBUG SORT CHECK ---")
    print("Showing first 20 sorted pixels AND extracted channels:")

    for px in pixels[:20]:
        B = (px >> 16) & 0xFF
        G = (px >> 8)  & 0xFF
        R =  px        & 0xFF
        print(f"{px:06X}   B={B:3}  G={G:3}  R={R:3}")
    print("-------------------------\n") """ 
    #print(f'len(lower): {len(lower)}')
    #print(f'len(upper): {len(upper)}')

    return (lower, upper)


def averageColor(pixel: np.ndarray) -> np.ndarray:
     
     if len(pixel) == 0:
         return 0
     
     B = int(((pixel >> 16) & 0xFF).mean())
     G = int(((pixel >> 8)  & 0xFF).mean())
     R = int(( pixel        & 0xFF).mean())

     return (B << 16) | (G << 8) | R

def main(): 

    start_time = time.time()


    cap = cv2.VideoCapture(PATH)

    print(f'FPS: {cap.get(cv2.CAP_PROP_FPS)}')      
    #video_playback(cap)
    

    # Open video
    cap.open(PATH)




    frame_list = []
    while cap.isOpened(): 

        ret, current = cap.read()
        if not ret: 
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        #print(current.shape)
        packed = bgr24_to_int(current)
        
        frame_list.append(packed)


    
    cap.release()
    cv2.destroyAllWindows()

    """ total = 0
    for i, f in enumerate(frame_list):
        print(i, f.shape, f.size)
        total += f.size

    print("expected total:", total)
    """

    pixels = np.concatenate([frame.flatten() for frame in frame_list])
    color_palette = generate_palette(pixels, 256)
    color_palette = palette_bgr24_to_bgr565(color_palette)
    
    print(f'length of color palette: {len(color_palette)}')
    for color in range(len(color_palette)):
        print(f'color_palette[{color}: {color_palette[color]:0X}]') 

    cap.open(PATH)
    #Delta Encoding
    #delta_frames = deltaEncode(cap, Color_Resolution.COLOR_BGR444) # np.ndarray of frames from mp4
    #delta_frames = deltaEncode(cap, Color_Resolution.COLOR_BGR565) # 
    delta_frames = deltaEncode(cap, Color_Resolution.COLOR_BGR332) # Need to edit so first frame is also returned
    delta_flatten = np.concatenate([frame.flatten() for frame in delta_frames])

        # Dumps delta frames in a txt file
    with open(FRAME_TXT_DUMP, "w") as f:
        for i, frame in enumerate(delta_frames):
            f.write(f"# --- Frame {i} ---\n")
            np.savetxt(f, frame, fmt="%x")
            f.write("\n\n")




    # ========================================================
    # Pixel Level RLE encoding scheme with tile compression 
    # ========================================================

    # tiles = []

    # Construct tiles
    """ for frame in delta_frames:
        for row in range(0, FRAME_WIDTH, TILE_WIDTH): 
            for col in range(0, FRAME_HEIGHT, TILE_HEIGHT): # Scan across columns first then
                tile = np.array(frame[row:row+TILE_HEIGHT, col:col+TILE_WIDTH])
                tiles.append(tile) """


    """ # Print total number of zero tiles
    total_tiles = len(tiles)
    zero_tiles = sum(1 for t in tiles if not np.any(t))
    zero_tile_ratio = zero_tiles/total_tiles
    print(f'Zero tile ratio {zero_tile_ratio:0.2f}') """


    """ prev = None
    repeat_count = 0

    for idx, tile in enumerate(tiles):
        if prev is not None and np.array_equal(tile, prev):
            repeat_count += 1
        prev = tile

    repeat_ratio = repeat_count / len(tiles)
    print(f'Tile repeat ratio: {repeat_ratio:.2f}\n') """
   
    


    """  # run tile compression algorithm
    output = bytearray()
    
    for tile in tiles:


        if not np.any(tile): 
            # Skip tile
            output.append(TILE_SKIP)
            continue

        flat_tile = tile.flatten()    
        # Run Zigzag, and RLE
        zz = [zigzagEncode(px) for px in flat_tile]   

        rle = rleEncode(zz)


        # Write length of RLE so we can decode tile boundary later
        output.extend(encodeUint16(len(rle)))

        for px in rle:
            output.extend(encodeUint16(px))  """
    

    # After encoding
    """ print('After variable length encoding')
    print(f'Total number of bytes: {len(output)}') """

    #print(f'Compression Ratio: {len(delta_flatten)*2/len(output):.2f}')

    """ # Dump encoded data to binary
    with open(ENCODED_BIN, "wb") as f:
        f.write(output)   """
    


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
    zigzag_vals = [zigzagEncode(px) for px in delta_pixels]

    rle_vals    = rleEncode(zigzag_vals)
    pixels_with_vle = bytearray().join(
        encodeUint16(px) for px in rle_vals
    )



    # Debugging information
    print('After variable length encoding')
    print(f'Total number of bytes: {len(pixels_with_vle)}')

    with open(ENCODED_BIN, "wb") as f:
        f.write(pixels_with_vle)   


    """ arr = np.array(zigzag_vals).reshape(total_frames, 96, 96).astype(np.uint16)
    with open('output/zigzag_encoded.txt', 'w') as f:
        for frame_num in range(total_frames):
            f.write(f"# --- Frame {frame_num} ---\n")
            np.savetxt(f, arr[frame_num], fmt="%04X")
            f.write("\n\n") """




    """  # Decoding back to BGR656 delta frames
    zigzag_vals_rle_encoded = []
    pos = 0
    while pos < len(pixels_with_vle): 
        val, pos = decodeUint16(pixels_with_vle, pos)
        zigzag_vals_rle_encoded.append(val)

    decoded_zigzag_vals = rleDecode(zigzag_vals_rle_encoded)

    decoded_to_deltas = np.array([zigzagDecode(px) for px in decoded_zigzag_vals], dtype=np.int16)
    decoded_to_deltas.tofile(DECODED_BIN)   """


    


    end_time = time.time()
    print(f'Total time elapsed: {end_time-start_time:.2f}')

if __name__ == "__main__":
    main()