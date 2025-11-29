


import cv2 
import numpy as np
import time 


from color_utils import Color_Resolution
from color_utils import bgr24_to_int


from quantizer import generate_palette
from quantizer import palette_bgr24_to_bgr565

from encoder import compress_video

from video import video_playback


from config import *

def main(): 

    start_time = time.time()


    cap = cv2.VideoCapture(PATH)

    print(f'FPS: {cap.get(cv2.CAP_PROP_FPS)}')      
    #video_playback(cap)
    

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


    """ # Generate Color palette
    pixels = np.concatenate([frame.flatten() for frame in frame_list])

    color_palette = generate_palette(pixels, 256)
    color_palette = palette_bgr24_to_bgr565(color_palette)
    color_palette = list(dict.fromkeys(color_palette))
 
    print(f'length of color palette: {len(color_palette)}')
    for color in range(len(color_palette)):
        print(f'color_palette[{color}: {color_palette[color]:0X}]')  """

 
    # Compress video
    encoded_frames = compress_video(cap, PATH, Color_Resolution.COLOR_BGR444)


    with open(ENCODED_BIN, "wb") as f:
        f.write(encoded_frames)



    end_time = time.time()
    print(f'Total time elapsed: {end_time-start_time:.2f}')

if __name__ == "__main__":
    main()