

def zigzagDecode(x: int) -> int:
    return (x >> 1) ^ (-(x&1))


def decodeUint16(stream: bytearray, pos: int) -> tuple[int, int]: 

    val = int(0)
    shift = 0

    while True: 

        byte = stream[pos]
        pos += 1

        val |= (byte & 0x7F) << shift # Extract the least significant 7 bits   
        shift += 7

        if (byte & 0x80) == 0: # MSB = 0 -> end of integer
            break

    return val, pos






def rleDecode(values: list[int]) -> list[int]:

    result = []
    i = 0
    n = len(values)
    run_len = 0

    while i < n:

        cur = values[i]

        if cur == 0 :
            run_len = values[i+1]
            result.extend([0] * run_len)
            i += 2
        else:
            result.append(values[i])
            i += 1

    return result

