

import numpy as np

def palette_bgr24_to_bgr565(palette24: np.ndarray) -> np.ndarray:

    B = (palette24 >> 16) & 0xFF
    G = (palette24 >> 8)  & 0xFF
    R =  palette24         & 0xff
    
    B5 = B >> 3
    G6 = G >> 2
    R5 = R >> 3
   
    bgr565 = (B5 << 11) | (G6 << 5) | R5
    return bgr565
    


def generate_palette(bucket: np.ndarray, num_colors=256)  -> np.ndarray:
 
    target_depth = int(np.log2(num_colors)) 
    assert 2**target_depth == num_colors # "Num colors must be a power of 2!"
    palette = median_cut_recurse(bucket, 0, target_depth)
    return np.array(palette)



def median_cut_recurse(bucket: np.ndarray, level: int, target_depth: int) -> np.ndarray:

    if level == target_depth:
        return [averageColor(bucket)]
    
    lower_palette, upper_palette = split_bucket(bucket)

    left_colors = median_cut_recurse(lower_palette, level+1, target_depth)
    right_colors = median_cut_recurse(upper_palette, level+1, target_depth)

    return left_colors + right_colors



def split_bucket(pixels: np.ndarray) -> np.ndarray: 

    key = None

    B = (pixels >> 16) & 0xFF
    G = (pixels >> 8)  & 0xFF
    R = pixels         & 0xff

    b_range = B.max() - B.min()
    g_range = G.max() - G.min()
    r_range = R.max() - R.min()

    if b_range >= g_range and b_range >= r_range:
        key = (pixels >> 16) & 0xFF     # blue
    elif g_range >= r_range:
        key = (pixels >> 8) & 0xFF      # green
    else:
        key = pixels & 0xFF             # red

    # NumPy sort using a key
    pixels = pixels[np.argsort(key, kind='stable')]

    lower, upper = np.array_split(pixels, 2)

    """ print("\n--- DEBUG SORT CHECK ---")
    print("Showing first 20 sorted pixels AND extracted channels:")

    for px in pixels[:20]:
        B = (px >> 16) & 0xFF
        G = (px >> 8)  & 0xFF
        R =  px        & 0xFF
        print(f"{px:06X}   B={B:3}  G={G:3}  R={R:3}")
    print("-------------------------\n") """ 
    #print(f'len(lower): {len(lower)}')
    #print(f'len(upper): {len(upper)}')

    return (lower, upper)


def averageColor(pixel: np.ndarray) -> np.ndarray:
     
     if len(pixel) == 0:
         print("Did not find any pixels to average")
         return 0
     
     B = int(((pixel >> 16) & 0xFF).mean())
     G = int(((pixel >> 8)  & 0xFF).mean())
     R = int(( pixel        & 0xFF).mean())

     return (B << 16) | (G << 8) | R
