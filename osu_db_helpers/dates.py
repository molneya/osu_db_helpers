
import os, gzip
from decoder import *

def run(osu_db_path, osu_songs_dir):
    '''
    Runs complete dates update process.
    '''
    with gzip.open("ranked_data.gz", 'rb') as fp:
        ranked_data = load_data(fp)

    with open(osu_db_path, 'rb+') as fp:
        update_last_modified(fp, ranked_data, osu_songs_dir)

def load_data(fp):
    '''
    Loads ranked date data into a dictionary.
    '''
    ranked_data = {}
    print(f"[update-dates] Loading ranked date data...")
    beatmapset_count = decode_int(fp)

    for _ in range(beatmapset_count):
        beatmapset_id = decode_int(fp)
        last_modified = decode_int(fp)
        ranked_data[beatmapset_id] = last_modified

    return ranked_data

def update_last_modified(fp, ranked_data, osu_songs_dir):
    '''
    Updates the last_modified parameter of each beatmap in our osu!.db and Songs folder to the date it was ranked.
    '''
    version = decode_int(fp)
    if version < 20191106:
        raise ValueError(f"Your osu!.db version ({version}) is too old! Please update osu! before running this program again.")

    fp.seek(13, os.SEEK_CUR)
    seek_ulebstring(fp)
    beatmap_count = decode_int(fp)

    print(f"[update-dates] Processing {beatmap_count} beatmaps...")
    total_leaderboards = 0
    total_updated = 0

    for _ in range(beatmap_count):
        for _ in range(8):
            seek_ulebstring(fp)
        osu_file = decode_ulebstring(fp)
        if decode_byte(fp) in (4, 5, 7):
            total_leaderboards += 1
        fp.seek(6, os.SEEK_CUR)
        last_modified_offset = fp.tell()
        fp.seek(32, os.SEEK_CUR)
        for _ in range(4):
            stars_pairs_count = decode_int(fp)
            fp.seek(14 * stars_pairs_count, os.SEEK_CUR)
        fp.seek(12, os.SEEK_CUR)
        fp.seek(17 * decode_int(fp), os.SEEK_CUR)
        fp.seek(4, os.SEEK_CUR)
        beatmapset_id = decode_int(fp)
        fp.seek(15, os.SEEK_CUR)
        for _ in range(2):
            seek_ulebstring(fp)
        fp.seek(2, os.SEEK_CUR)
        seek_ulebstring(fp)
        fp.seek(10, os.SEEK_CUR)
        osu_folder = decode_ulebstring(fp)
        fp.seek(18, os.SEEK_CUR)

        # Ignore beatmapsets where we don't have data for
        if beatmapset_id not in ranked_data:
            continue

        beatmap_end_offset = fp.tell()
        unix_time = ranked_data[beatmapset_id]

        # Go to where our last_modified is and update the value to windows ticks
        fp.seek(last_modified_offset, os.SEEK_SET)
        windows_ticks = (unix_time + 62135596800) * 10000000
        encode_long(windows_ticks, fp)

        # Update last access and modified times of the beatmap .osu file
        beatmap_path = os.path.join(osu_songs_dir, osu_folder, osu_file)
        os.utime(beatmap_path, (unix_time, unix_time))

        # Go back to the end of the beatmap to continue reading the file
        fp.seek(beatmap_end_offset, os.SEEK_SET)

        total_updated += 1

    print(f"[update-dates] Updated {total_updated}/{total_leaderboards} beatmaps from ranked/approved/loved beatmaps in database")
