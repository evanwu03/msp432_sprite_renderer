

import numpy as np
import cv2

# Example: img is a 2D numpy array of dtype np.uint16
# representing a 128x128 frame of RGB565 or delta values

PATH='videos/apple.jpeg'
img = cv2.imread(PATH, cv2.IMREAD_COLOR_BGR) # your 16-bit frame here as np.uint16


def get_bit_planes(frame) -> list: 
    bitplanes = []

    for k in range(0,16):
        mask = np.uint16(1 << k)
        plane = (frame & mask) >> k     # isolate kth bit plane
        visual = np.uint8(plane * 255)  # scale 0/1 → 0/255 for visualization
        bitplanes.append(visual)
    
    return bitplanes

bitplanes = get_bit_planes(img)
cv2.imshow("bitplane", np.hstack(bitplanes))
cv2.waitKey()
cv2.destroyAllWindows()