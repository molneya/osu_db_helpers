
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

def update_db_stars(fp, new_fp, data):
    '''
    Updates star ratings of each beatmap in our osu!.db, copying data to a new osu!.db.
    '''
    version = decode_int(fp)
    assert version >= 20191106, f"Your osu!.db version ({version}) is too old! Please update osu! before running this program again."

    fp.seek(13, os.SEEK_CUR)
    seek_ulebstring(fp)
    beatmap_count = decode_int(fp)

    # Add osu!.db header to new file
    current_offset = fp.tell()
    fp.seek(0, os.SEEK_SET)
    new_fp.write(fp.read(current_offset))

    print(f"Processing {beatmap_count} beatmaps in osu!.db...")
    total_updated = 0

    for _ in range(beatmap_count):

        beatmap_start_offset = fp.tell()

        for _ in range(9):
            seek_ulebstring(fp)
        fp.seek(39, os.SEEK_CUR)

        stars_start_offset = fp.tell()

        # Seek past star rating int/double pairs for all modes
        for _ in range(4):
            stars_pairs_count = decode_int(fp)
            fp.seek(14 * stars_pairs_count, os.SEEK_CUR)

        stars_end_offset = fp.tell()

        fp.seek(12, os.SEEK_CUR)
        timing_points_count = decode_int(fp)
        fp.seek(17 * timing_points_count, os.SEEK_CUR)

        # Get beatmap_id to use later
        beatmap_id = decode_int(fp)

        fp.seek(19, os.SEEK_CUR)
        for _ in range(2):
            seek_ulebstring(fp)
        fp.seek(2, os.SEEK_CUR)
        seek_ulebstring(fp)
        fp.seek(10, os.SEEK_CUR)
        seek_ulebstring(fp)
        fp.seek(18, os.SEEK_CUR)

        beatmap_end_offset = fp.tell()

        # Write stuff before stars into new file
        fp.seek(beatmap_start_offset, os.SEEK_SET)
        new_fp.write(fp.read(stars_start_offset - beatmap_start_offset))

        # Write new stars info if we have it
        if beatmap_id in data:
            total_updated += 1

        # Else copy old stars data
        else:
            new_fp.write(fp.read(stars_end_offset - stars_start_offset))

        # Write stuff after stars into new file
        fp.seek(stars_end_offset, os.SEEK_SET)
        new_fp.write(fp.read(beatmap_end_offset - stars_end_offset))

    # Write osu!.db footer
    new_fp.write(fp.read(4))

    print(f"Updated {total_updated} beatmaps in osu!.db")
