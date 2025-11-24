


import cv2 
import numpy as np
import time 

PATH = 'videos/ordinary.mp4'
FRAME_TXT_DUMP = 'output/ordinary.txt'
RAW_BIN  = 'output/ordinary.bin'


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
def delta_encode(cap: cv2.VideoCapture) -> list:

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
        current_frame = bgr_to_bgr565(current_frame)

    
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


def bgr_to_bgr565(rgb: cv2.typing.MatLike) -> cv2.typing.MatLike:

    blue  = (rgb[:, :, 0] >> 3)
    green = (rgb[:, :, 1] >> 2)
    red   = (rgb[:, :, 2] >> 3)

    rgb565 = (red << 11) | (green << 5) | blue
    return rgb565



def main(): 

    cap = cv2.VideoCapture(PATH)

    print(f'FPS: {cap.get(cv2.CAP_PROP_FPS)}')      
    #video_playback(cap)
    
    
    #cap.open(PATH)
    delta_frames = delta_encode(cap)
    print(f'Total number of frames: {len(delta_frames)}')
    

    #prints frames in hex format
    for i, frame in enumerate(delta_frames): 
        np.savetxt(FRAME_TXT_DUMP, frame, fmt='%x')
    

    all_pixels = np.concatenate([frame.flatten() for frame in delta_frames])
    all_pixels = all_pixels.astype(np.uint16)
    all_pixels.tofile(RAW_BIN)
    print(f'Total number of pixels: {len(all_pixels)}')
    print(f'Total number of bytes: {len(all_pixels)*2}')

if __name__ == "__main__":
    main()