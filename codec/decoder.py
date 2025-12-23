
import numpy as np



def zigzagDecode(arr: np.ndarray) -> np.ndarray:
    return (arr.astype(np.int16) >> 1) ^ (-(arr.astype(np.int16)&1))


def rleDecode(stream: bytearray, width: int, height: int, position: int = 0) -> tuple[np.ndarray,  int]:


    out = []
    frame_pixels = width * height
    pixel_count = 0 
    i = position



    while pixel_count < frame_pixels and i < len(stream): 

        # parses the header byte
        run_len = stream[i] & 0x7F 
        is_run = stream[i] & 0x80 != 0

        i += 1 

        # Debug Asserts        
        if run_len == 0: 
            raise ValueError ("Invalid RLE length 0")
        
        if pixel_count + run_len > frame_pixels:
            raise ValueError("RLE token exceeds frame boundary, check encoder implementation")
        
        
        # Following sequence is a consecutive run 
        if is_run:

            # emit the value 
            run_value = stream[i] 

            for k in range(run_len):
               out.append(run_value)

            i += 1 

        else:

            # emit the following literal
            for k in range(run_len):
                out.append(stream[i])
                i += 1
        
        pixel_count += run_len

    return (np.array(out, dtype=np.uint8), i)



