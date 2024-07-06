
import os
from decoder import *

def load_data(fp):
    '''
    Loads beatmap stars data into a dictionary.
    '''
    data = {}
    print(f"Loading stars data...")
    beatmap_count = decode_int(fp)

    for _ in range(beatmap_count):
        beatmap_id = decode_int(fp)
        data[beatmap_id] = [{}, {}, {}, {}]

        for i in range(4):
            entries_count = decode_byte(fp)

            for _ in range(entries_count):
                mods = decode_int(fp)
                stars = decode_float(fp)
                data[beatmap_id][i][mods] = stars

    return data
