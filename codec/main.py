


import numpy as np
import time 


from quantizer import generate_palette
from quantizer import palette_bgr24_to_bgr565
from quantizer import quantize_pixels


from encoder import compress_video

from video import video_playback
from video import extract_video_frames

from config import *

def main(): 

    start_time = time.time()

    video_playback(FILEPATH)

    video = extract_video_frames(FILEPATH)
    print(f'Video Resolution: {video.shape}')

    height = video.shape[1]
    weight = video.shape[2]
    num_frames = len(video)

    # Generate Color palette
    pixels = np.concatenate([frame.flatten() for frame in video])

    print(f'Raw file size in RGB24: {len(pixels)*4}')

    color_palette = generate_palette(pixels, 256)
    color_palette = palette_bgr24_to_bgr565(color_palette)
    
    #color_palette = np.array(list(dict.fromkeys(color_palette)), dtype=np.uint16)
    #color_palette = color_palette[np.argsort(color_palette, kind='quicksort')] # Naive sorting of colors
    
    """ perm = np.random.permutation(len(color_palette)) # Scrambling color list to see effect on file size
    color_palette = color_palette[perm] """

    quantized = quantize_pixels(pixels, color_palette) 
    quantized_frame = quantized.reshape(num_frames, height, weight)

    #print(f'Quantized Video Resolution: {quantized_frame.shape}')


    """ print(f'Dimensions of quantized frames: {quantized_frame.shape}')
    print(f'length of color palette: {len(color_palette)}')
    for color in range(len(color_palette)):
        print(f'color_palette[{color}: {color_palette[color]:0X}]')   """
    

    #print(quantized_frame)


    # Compress video
    encoded_frames = compress_video(quantized_frame)

    
    with open(ENCODED_BIN, "wb") as f:
        f.write(encoded_frames)



    end_time = time.time()
    print(f'Total time elapsed: {end_time-start_time:.2f}')

if __name__ == "__main__":
    main()