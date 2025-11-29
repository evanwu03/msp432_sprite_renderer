


import cv2 
import numpy as np
import time 
import os


from color_utils import Color_Resolution
from color_utils import bgr24_to_int


from quantizer import generate_palette
from quantizer import palette_bgr24_to_bgr565

from encoder import deltaEncode
from encoder import zigzagEncode
from encoder import rleEncode
from encoder import encodeUint16

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



     # Generate Color palette
    pixels = np.concatenate([frame.flatten() for frame in frame_list])

    color_palette = generate_palette(pixels, 256)
    color_palette = palette_bgr24_to_bgr565(color_palette)
    color_palette = list(dict.fromkeys(color_palette))



    print(f'length of color palette: {len(color_palette)}')
    for color in range(len(color_palette)):
        print(f'color_palette[{color}: {color_palette[color]:0X}]') 

 
    cap.open(PATH)
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