
import numpy as np
from encoder import rleEncode

test_data = np.zeros(1000, dtype=np.uint16)      
out = rleEncode(test_data)

print(f'Test1:')
for v in out:
    #print(hex(v), end=" ")
    print(v, end=" ")

print('\n')

test_data = np.array([0,0,0,5,6,0,0,0], dtype=np.uint16)
out = rleEncode(test_data)

print(f'Test2:')
for v in out:
    print(v, end=" ")

print('\n')


test_data = np.array([0,0,0,128,6,128,0], dtype=np.uint16)
out = rleEncode(test_data)

print(f'Test3:')
for v in out:
    print(v, end=" ")

print('\n')
