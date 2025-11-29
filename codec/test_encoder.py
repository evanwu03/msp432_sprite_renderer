
import numpy as np
from encoder import rleEncode
from encoder import zigzagEncode

test = np.zeros(1000, dtype=np.uint16)
print(rleEncode(test))


test = np.array([0,0,0,5,6,0,0], dtype=np.uint16)
print(rleEncode(test))


