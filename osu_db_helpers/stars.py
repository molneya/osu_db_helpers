
import os, gzip
from decoder import *

def run(osu_db_path):
    '''
    Runs complete stars update process.
    '''
    new_osu_db_path = osu_db_path + "_new"

    with gzip.open("stars_data.gz", 'rb') as fp:
        stars_data = load_data(fp)

    with open(osu_db_path, 'rb') as fp:
        with open(new_osu_db_path, 'wb') as new_fp:
            update_stars(fp, new_fp, stars_data)

    # Cleanup files
    os.remove(osu_db_path)
    os.rename(new_osu_db_path, osu_db_path)

def load_data(fp):
    '''
    Loads beatmap stars data into a dictionary.
    '''
    stars_data = {}
    print(f"[update-stars] Loading stars data...")
    beatmap_count = decode_int(fp)

    for _ in range(beatmap_count):
        beatmap_id = decode_int(fp)
        stars_data[beatmap_id] = [{}, {}, {}, {}]

        for i in range(4):
            entries_count = decode_byte(fp)

            for _ in range(entries_count):
                mods = decode_int(fp)
                stars = decode_float(fp)
                stars_data[beatmap_id][i][mods] = stars

    return stars_data

def update_stars(fp, new_fp, stars_data):
    '''
    Updates star ratings of each beatmap in our osu!.db, copying data to a new osu!.db.
    '''
    version = decode_int(fp)
    if version < 20191106:
        raise ValueError(f"Your osu!.db version ({version}) is too old! Please update osu! before running this program again.")

    fp.seek(13, os.SEEK_CUR)
    seek_ulebstring(fp)
    beatmap_count = decode_int(fp)

    # Add osu!.db header to new file
    current_offset = fp.tell()
    fp.seek(0, os.SEEK_SET)
    new_fp.write(fp.read(current_offset))

    print(f"[update-stars] Processing {beatmap_count} beatmaps...")
    total_leaderboards = 0
    total_updated = 0

    for _ in range(beatmap_count):
        beatmap_start_offset = fp.tell()

        for _ in range(9):
            seek_ulebstring(fp)

        if decode_byte(fp) in (4, 5, 7):
            total_leaderboards += 1

        fp.seek(38, os.SEEK_CUR)

        stars_start_offset = fp.tell()

        for _ in range(4):
            stars_pairs_count = decode_int(fp)
            fp.seek(14 * stars_pairs_count, os.SEEK_CUR)

        stars_end_offset = fp.tell()

        fp.seek(12, os.SEEK_CUR)
        fp.seek(17 * decode_int(fp), os.SEEK_CUR)

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
        if beatmap_id in stars_data:

            for mode in range(4):
                mode_stars_data = stars_data[beatmap_id][mode]
                stars_pairs_count = len(mode_stars_data)

                # Add EZ and HR to mania mode
                if mode == 3:
                    stars_pairs_count *= 3

                encode_int(stars_pairs_count, new_fp)

                for mods, stars in mode_stars_data.items():
                    new_fp.write(b'\x08')
                    encode_int(mods, new_fp)
                    new_fp.write(b'\x0D')
                    encode_double(stars, new_fp)

                    # Add EZ and HR to mania mode
                    if mode == 3:
                        new_fp.write(b'\x08')
                        encode_int(mods + 2, new_fp)
                        new_fp.write(b'\x0D')
                        encode_double(stars, new_fp)
                        new_fp.write(b'\x08')
                        encode_int(mods + 16, new_fp)
                        new_fp.write(b'\x0D')
                        encode_double(stars, new_fp)

            total_updated += 1

        # Otherwise, copy old stars data
        else:
            new_fp.write(fp.read(stars_end_offset - stars_start_offset))

        # Write stuff after stars into new file
        fp.seek(stars_end_offset, os.SEEK_SET)
        new_fp.write(fp.read(beatmap_end_offset - stars_end_offset))

    # Write osu!.db footer
    new_fp.write(fp.read(4))

    print(f"[update-stars] Updated {total_updated}/{total_leaderboards} beatmaps from ranked/approved/loved beatmapsets")
