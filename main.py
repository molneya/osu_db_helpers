
import argparse
import gzip
import os
import time
from decoder import *
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(prog="osu_db_helpers", description="Orders beatmaps by ranked date using the date added sort option.")
    parser.add_argument("directory", help="your base osu! directory", type=Path)
    args = parser.parse_args()

    osu_db_path = args.directory / "osu!.db"
    osu_songs_path = args.directory / "Songs"

    if not osu_db_path.is_file():
        raise ValueError("osu!.db not found. Did you supply the right directory?")
    if not osu_songs_path.is_dir():
        raise ValueError("Songs folder not found. Did you supply the right directory?")

    print("If you haven't made backups, press CTRL+C to terminate the program. Also, make sure osu! is closed. I do not claim responsibility for any corruptions that may occur.")
    print("Processing will automatically start in 10 seconds...")
    time.sleep(10)

    ranked_data = load()

    with osu_db_path.open('rb+') as fp:
        update(fp, osu_songs_path, ranked_data)

def load():
    '''
    Loads ranked date data from file.
    '''
    ranked_data = {}
    base_path = Path(__file__).parent

    # Try loading ranked_data.csv in case anyone decides to use their own (up-to-date) data
    data_path = base_path / "ranked_data.csv"

    if data_path.is_file():
        print("Loading data from ranked_data.csv")

        with data_path.open('r') as fp:
            for line in fp:
                beatmapset_id, last_modified = line.strip().split(',')
                ranked_data[int(beatmapset_id)] = int(last_modified)

        return ranked_data

    # Otherwise use my compressed data
    data_path = base_path / "ranked_data.gz"

    with gzip.open(data_path, 'rb') as fp:
        for line in fp:
            beatmapset_id, last_modified = line.decode().strip().split(',')
            ranked_data[int(beatmapset_id)] = int(last_modified)

    return ranked_data

def update(fp, osu_songs_path, ranked_data):
    '''
    Updates the last_modified parameter of each ranked beatmap in the osu!.db and Songs folder to the date it was ranked.
    '''
    version = decode_int(fp)
    if version < 20250107:
        raise ValueError(f"Your osu!.db version ({version}) is too old! Please update osu! before running this program again.")

    fp.seek(13, os.SEEK_CUR)
    seek_ulebstring(fp)
    beatmap_count = decode_int(fp)

    print(f"Processing {beatmap_count} beatmaps...")
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
            fp.seek(10 * decode_int(fp), os.SEEK_CUR)
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
        beatmap_path = osu_songs_path / osu_folder / osu_file
        os.utime(beatmap_path, (unix_time, unix_time))

        # Go back to the end of the beatmap to continue reading the file
        fp.seek(beatmap_end_offset, os.SEEK_SET)

        total_updated += 1

    print(f"Updated {total_updated}/{total_leaderboards} beatmaps from ranked/approved/loved beatmaps in database")

if __name__ == "__main__":
    exit(main())
