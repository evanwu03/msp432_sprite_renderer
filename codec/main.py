


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

    # Optional: play back video you plan to compress
    video_playback(FILEPATH)


    video = extract_video_frames(FILEPATH)
    print(f'Video Resolution: {video.shape}')

    # Video Resolution specs
    height = video.shape[1]
    width = video.shape[2]
    num_frames = len(video)

    # Flatten to 1D list of pixels
    pixels = np.concatenate([frame.ravel() for frame in video])
    raw_size_bytes = len(pixels)*4


    print(f'Raw file size in RGB24: {raw_size_bytes}')


    # Generate Color palette
    color_palette = generate_palette(pixels, 256)
    color_palette = palette_bgr24_to_bgr565(color_palette)


    #color_palette = np.array(list(dict.fromkeys(color_palette)), dtype=np.uint16)
    ##color_palette = color_palette[np.argsort(color_palette, kind='quicksort')] # Naive sorting of colors
    
    """ perm = np.random.permutation(len(color_palette)) # Scrambling color list to see effect on file size
    color_palette = color_palette[perm]  """

    quantization_start_time = time.time()
    quantized = quantize_pixels(pixels, color_palette) 
    quantized_frame = quantized.reshape(num_frames, height, width)
    quantization_finish_time = time.time()
    print(f'Total quantization time: {(quantization_finish_time-quantization_start_time):.2f}')

    #print(f'Quantized Video Resolution: {quantized_frame.shape}')


    """ print(f'Dimensions of quantized frames: {quantized_frame.shape}')
    print(f'length of color palette: {len(color_palette)}')
    for color in range(len(color_palette)):
        print(f'color_palette[{color}: {color_palette[color]:0X}]')   """
    

    # Compress video
    encoded_frames = bytearray()

    # append global header to byte array. format of final C stream will be as follows 
    # [HEADER] 
    # Byte 0–1 : Magic            (e.g. 0x56 0x43 = "VC")
    # Byte 2   : Width            (e.g. 128 pixels)
    # Byte 3   : Height           (e.g. 128 pixels )
    # Byte 4   : Num colors       (palette size: e.g. 256)
    # Byte 5   : Flags            (delta, zigzag, etc.)
    # [PALETTE] 
    # [FRAME STREAM]

    encoded_frames = compress_video(quantized_frame)


    print(f'Total Compression Ratio: {raw_size_bytes/len(encoded_frames):.2f}')
    
    with open(ENCODED_BIN, "wb") as f:
        f.write(b"\x56\x43")         # decoder expects this to identify video format
        f.write(bytes([width, height]))    # Width and Height of frames
        f.write((256).to_bytes(2, "big"))                 # number of colors in palette
        f.write(bytes([0xFF]))       # Dummy byte for flags to be defined later

        f.write(color_palette.tobytes())       # color palette 


        f.write(encoded_frames)     # compressed frames


    with open(ENCODED_BIN, "rb") as f:
        data = f.read()

    with open("output/video_data.inc", "w") as f:
        for i, b in enumerate(data):
            if i % 12 == 0:
                f.write("\n")
            f.write(f"0x{b:02X}, ")


    

    end_time = time.time()
    print(f'Total time elapsed: {end_time-start_time:.2f}')

if __name__ == "__main__":
    main()