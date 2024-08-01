
import os, gzip
from decoder import *

def run(osu_db_path, osu_songs_dir, purge_modes):
    '''
    Runs complete purge process.
    '''
    new_osu_db_path = osu_db_path + "_new"

    with open(osu_db_path, 'rb') as fp:
        with open(new_osu_db_path, 'wb') as new_fp:
            purge_beatmaps(fp, new_fp, osu_songs_dir, purge_modes)

    # Cleanup files
    os.remove(osu_db_path)
    os.rename(new_osu_db_path, osu_db_path)
    purge_folders(osu_songs_dir)

def purge_beatmaps(fp, new_fp, osu_songs_dir, purge_modes):
    '''
    Deletes beatmaps from our osu database according to some criteria, copying data to a new osu!.db.
    '''
    version = decode_int(fp)
    if version < 20191106:
        raise ValueError(f"Your osu!.db version ({version}) is too old! Please update osu! before running this program again.")

    fp.seek(13, os.SEEK_CUR)
    seek_ulebstring(fp)
    beatmap_count = decode_int(fp)

    # Add osu!.db header to new file
    header_end_offset = fp.tell()
    fp.seek(0, os.SEEK_SET)
    new_fp.write(fp.read(header_end_offset))

    print(f"[purge-beatmaps] Processing {beatmap_count} beatmaps...")
    total_purged = 0

    for _ in range(beatmap_count):
        beatmap_start_offset = fp.tell()
        for _ in range(8):
            seek_ulebstring(fp)
        osu_file = decode_ulebstring(fp)
        fp.seek(39, os.SEEK_CUR)
        for _ in range(4):
            stars_pairs_count = decode_int(fp)
            fp.seek(14 * stars_pairs_count, os.SEEK_CUR)
        fp.seek(12, os.SEEK_CUR)
        fp.seek(17 * decode_int(fp), os.SEEK_CUR)
        fp.seek(22, os.SEEK_CUR)
        mode = decode_byte(fp)
        for _ in range(2):
            seek_ulebstring(fp)
        fp.seek(2, os.SEEK_CUR)
        seek_ulebstring(fp)
        fp.seek(10, os.SEEK_CUR)
        osu_folder = decode_ulebstring(fp)
        fp.seek(18, os.SEEK_CUR)
        beatmap_end_offset = fp.tell()

        if mode in purge_modes:
            # Delete existing .osu
            beatmap_path = os.path.join(osu_songs_dir, osu_folder, osu_file)
            os.remove(beatmap_path)
            total_purged += 1

            # Skip writing data to the new osu!.db
            continue

        # Write current beatmap to new file
        fp.seek(beatmap_start_offset, os.SEEK_SET)
        new_fp.write(fp.read(beatmap_end_offset - beatmap_start_offset))

    # Write osu!.db footer to new file
    new_fp.write(fp.read(4))

    # Update the new osu!.db beatmap count to reflect new beatmap count
    new_fp.seek(header_end_offset - 4, os.SEEK_SET)
    encode_int(beatmap_count - total_purged, new_fp)

    print(f"[purge-beatmaps] Purged {total_purged}/{beatmap_count} beatmaps from database")

def purge_folders(osu_songs_dir):
    '''
    Deletes folders containing no .osu files.
    '''
    songs_listing = os.listdir(osu_songs_dir)
    beatmapset_count = len(songs_listing)
    print(f"[purge-beatmaps] Processing {beatmapset_count} beatmapsets...")
    total_purged = 0

    for osu_folder in os.listdir(osu_songs_dir):
        folder_path = os.path.join(osu_songs_dir, osu_folder)
        osu_folder_contents = os.listdir(folder_path)

        # If there are any .osu files, ignore
        if any(file.endswith(".osu") for file in osu_folder_contents):
            continue

        # Otherwise, delete this folder
        shutil.rmtree(folder_path)
        total_purged += 1

    print(f"[purge-beatmaps] Purged {total_purged}/{beatmapset_count} beatmapsets without difficulties")
