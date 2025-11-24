


import cv2 
import numpy as np
import time 

PATH = 'videos/ordinary.mp4'
FRAME_TXT_DUMP = 'output/ordinary_delta.txt'
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

# Converts a frame in BGR888 -> BGR565
def bgr_to_bgr565(bgr: cv2.typing.MatLike) -> cv2.typing.MatLike:

    blue  = (bgr[:, :, 0] >> 3)
    green = (bgr[:, :, 1] >> 2)
    red   = (bgr[:, :, 2] >> 3)

    bgr565 = (red << 11) | (green << 5) | blue
    return bgr565



# BIT mask returns least significant N bits
BITMASK  = [ 
    0b00000000,
    0b00000001,
    0b00000011,
    0b00000111,
    0b00001111,
    0b00011111,
    0b00111111,
    0b01111111,
    0b11111111,
]

# For uint16 we can have 2 groups of 7 bits
BITSHIFTS = [7, 7, 1]


def getLSB(x: np.uint8, n: np.uint8) -> np.uint8: 

    # Guard clause here    
    return x & BITMASK[n-1]

# Variable length encoding
# 1. Break number into 7 bit groups
# 2. Set top bit = 0 for last byte
# 3. Set top bit = 1 for continuation
def encodeUint16(x: np.uint16) -> bytearray:

    buf = bytearray()

    for i in range(len(BITSHIFTS)): 

        lsb = getLSB(x, BITSHIFTS[i]) | 0b10000000 # get the LSB and mark continuation bit 
        buf.append(lsb)        

        x = x >> BITSHIFTS[i] ## move on to next group of 7 bits
        
        if x == 0:
            break
    buf[-1] &= 0b01111111
    return buf # Return byte array 


def main(): 

    start_time = time.time()


    cap = cv2.VideoCapture(PATH)

    print(f'FPS: {cap.get(cv2.CAP_PROP_FPS)}')      
    #video_playback(cap)
    
    
    #cap.open(PATH)
    delta_frames = delta_encode(cap)


    print(f'Total number of frames: {len(delta_frames)}')


    # Dumps delta frames in a txt file
    with open(FRAME_TXT_DUMP, "w") as f:
        for i, frame in enumerate(delta_frames):
            f.write(f"# --- Frame {i} ---\n")
            np.savetxt(f, frame, fmt="%x")
            f.write("\n\n")


        
    # flatten frames in 1D pixel array represented as uint16
    raw_pixels = np.concatenate([frame.flatten() for frame in delta_frames])
    raw_pixels = raw_pixels.astype(np.uint16)
    raw_pixels.tofile(RAW_BIN)


    # Debugging information
    print('Before variable length encoding')
    print(f'Total number of pixels: {len(raw_pixels)}')
    print(f'Total number of bytes: {len(raw_pixels)*2}\n')

    
    # Perform VLE
    
    pixels_with_vle = bytearray().join(encodeUint16(pixel) for pixel in raw_pixels)


    # Dump to binary and txt file
    with open('output/video_vle.bin', "wb") as f:
        f.write(pixels_with_vle)

    with open('output/video_vle.txt', "w") as f:
        f.write(pixels_with_vle.hex(" "))


    # Debugging information
    print('After variable length encoding')
    print(f'Total number of bytes: {len(pixels_with_vle)}')


    end_time = time.time()
    print(f'Total time elapsed: {end_time-start_time:.2f}')

if __name__ == "__main__":
    main()