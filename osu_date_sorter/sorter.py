
import os
from decoder import *

def load_data(fp):
    '''
    Loads ranked date data into a dictionary.
    '''
    print(f"Loading ranked date data...")
    last_modified_dict = {}
    beatmapset_count = decode_int(fp)

    for _ in range(beatmapset_count):
        beatmapset_id = decode_int(fp)
        last_modified = decode_int(fp)
        last_modified_dict[beatmapset_id] = last_modified

    return last_modified_dict

def update_db_last_modified(fp, last_modified_dict):
    '''
    Updates the last_modified parameter of each beatmap in our osu!.db to a custom one.
    '''
    # Version check: if we have a osu!.db that is too old we probably can't decode it correctly
    version = decode_int(fp)
    assert version >= 20191106, f"Your osu!.db version ({version}) is too old! Please update osu! before running this program again."
    # Seek past folder_count (4), account_unlocked (1), account_unlocked_date (8)
    fp.seek(13, 1)
    # Seek past player_name
    seek_ulebstring(fp)
    
    beatmap_count = decode_int(fp)
    print(f"Processing {beatmap_count} beatmaps in osu!.db...")
    total_leaderboards = 0
    total_updated = 0

    for _ in range(beatmap_count):
        # Seek past artist, artist_unicode, title, title_uncode, creator, version, audio_filename, beatmap_hash, beatmap_filename
        for _ in range(9):
            seek_ulebstring(fp)
        # Tally maps with leaderboards
        status = decode_byte(fp)
        if status in (4, 5, 7):
            total_leaderboards += 1
        # Seek past count_circles (2), count_sliders (2), count_spinners (2)
        fp.seek(6, os.SEEK_CUR)
        # Get the offset of last_modified to modify it later
        last_modified_offset = fp.tell()
        # Seek past last_modified (8), approach_rate (4), circle_size (4), hp_drain (4), overall_difficulty (4), slider_velocity (8)
        fp.seek(32, os.SEEK_CUR)
        # Seek past star rating int/double pairs for all modes
        for _ in range(4):
            stars_pairs_count = decode_int(fp)
            fp.seek(14 * stars_pairs_count, os.SEEK_CUR)
        # Seek past drain_time (4), total_time (4), preview_time (4)
        fp.seek(12, os.SEEK_CUR)
        # Seek past timing points
        timing_points_count = decode_int(fp)
        fp.seek(17 * timing_points_count, os.SEEK_CUR)
        # Seek past beatmap_id (4)
        fp.seek(4, os.SEEK_CUR)
        # Get beatmapset_id for use later
        beatmapset_id = decode_int(fp)
        # Seek past thread_id (4), osu_grade (1), taiko_grade (1), catch_grade (1), mania_grade (1),
        # local_offset (2), stack_leniency (4), mode (1)
        fp.seek(15, os.SEEK_CUR)
        # Seek past source, tags
        for _ in range(2):
            seek_ulebstring(fp)
        # Seek past online_offset (2)
        fp.seek(2, os.SEEK_CUR)
        # Seek past title_font
        seek_ulebstring(fp)
        # Seek past unplayed (1), last_played (8), osz2 (1)
        fp.seek(10, os.SEEK_CUR)
        # Seek past beatmap_folder
        seek_ulebstring(fp)
        # Seek past last_checked (8), ignore_sound (1), ignore_skin (1), disable_storyboard (1), disable_video (1), visual_override (1),
        # last_modified? (4), scroll_speed (1)
        fp.seek(18, os.SEEK_CUR)

        # Ignore beatmapsets where we don't have an entry in our dict
        if beatmapset_id not in last_modified_dict:
            continue

        # Get the offset of the end of the beatmap to go back to it later
        end_offset = fp.tell()
        # Go to where our last_modified is and update the value to windows ticks
        fp.seek(last_modified_offset, os.SEEK_SET)
        windows_ticks = (last_modified_dict[beatmapset_id] + 62135596800) * 10000000
        encode_long(windows_ticks, fp)
        # Go back to the end of the beatmap to continue reading the file
        fp.seek(end_offset, os.SEEK_SET)
        total_updated += 1

    print(f"Updated {total_updated}/{total_leaderboards} beatmaps from ranked/approved/loved beatmapsets in osu!.db")

def update_file_last_modified(dir, last_modified_dict):
    '''
    Updates the access and modified times of each beatmap in our Songs folder to a custom one.
    '''
    beatmapsets = os.listdir(dir)
    print(f"Processing {len(beatmapsets)} beatmapsets in Songs...")
    total_updated = 0

    for beatmapset in beatmapsets:
        # Try to get the beatmapset_id from the folder name
        try:
            beatmapset_id = int(beatmapset.split()[0])
        except ValueError:
            continue

        # Ignore beatmapsets where we don't have an entry in our dict
        if beatmapset_id not in last_modified_dict:
            continue

        beatmapset_path = os.path.join(dir, beatmapset)

        # Iterate over all difficulty files
        for beatmap in os.listdir(beatmapset_path):
            if not beatmap.endswith(".osu"):
                continue

            # Update last access and modified times of the beatmap
            beatmap_path = os.path.join(beatmapset_path, beatmap)
            unix_time = last_modified_dict[beatmapset_id]
            os.utime(beatmap_path, (unix_time, unix_time))

            # Tally updated maps
            total_updated += 1

    print(f"Updated {total_updated} beatmaps from ranked/approved/loved beatmapsets in Songs")
