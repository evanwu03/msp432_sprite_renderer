

import numpy as np

def palette_bgr24_to_bgr565(palette24: list[int]) -> list[int]:
    palette565 = []
    for px in palette24:
        B = (px >> 16) & 0xFF
        G = (px >> 8)  & 0xFF
        R =  px        & 0xFF

        r5 = R >> 3
        g6 = G >> 2
        b5 = B >> 3

        rgb565 = (r5 << 11) | (g6 << 5) | b5
        palette565.append(rgb565)
    return palette565





def generate_palette(bucket, num_colors=256):

    target_depth = int(np.log2(num_colors)) 
    assert 2**target_depth == num_colors # "Num colors must be a power of 2!"

    return median_cut_recurse(bucket, 0, target_depth)


def median_cut_recurse(bucket, level, target_depth): 

    if level == target_depth:
        return [averageColor(bucket)]
    
    lower_palette, upper_palette = split_bucket(bucket)

    left_colors = median_cut_recurse(lower_palette, level+1, target_depth)
    right_colors = median_cut_recurse(upper_palette, level+1, target_depth)

    return left_colors + right_colors
def split_bucket(pixels): 

    b_min = min( (px >> 16) & 0xFF for px in pixels)
    b_max = max( (px >> 16) & 0xFF for px in pixels)
    g_min = min( (px >> 8)  & 0xFF for px in pixels)
    g_max = max( (px >> 8)  & 0xFF for px in pixels)
    r_min = min( (px & 0xFF) for px in pixels)
    r_max = max( (px & 0xFF) for px in pixels)

    b_range = b_max - b_min
    g_range = g_max - g_min
    r_range = r_max - r_min

    #print(f'min(B): {b_min}, max(B): {b_max}')
    #print(f'min(G): {g_min}, max(B): {g_max}')
    #print(f'min(B): {r_min}, max(B): {r_max}')


    if b_range >= g_range and b_range >= r_range: # Sort by blue 
        #pixels.sort(key=lambda px: (px >> 16) & 0xFF)
        pixels = sorted(pixels, key=lambda px: (px >> 16) & 0xFF)
    elif g_range >= r_range: # Sort by green 
        #pixels.sort(key=lambda px: (px >> 8) & 0xFF) 
        pixels = sorted(pixels, key=lambda px: (px >> 8) & 0xFF)
    elif r_range >= g_range: # Otherwise sort by red
        #pixels.sort(key=lambda px: (px & 0xFF))
        pixels = sorted(pixels, key=lambda px: (px & 0xFF))

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
