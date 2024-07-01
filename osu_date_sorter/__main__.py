
import argparse
import gzip
import os
import pathlib
import time
from sorter import load_data, update_db_last_modified, update_file_last_modified

def main():
    parser = argparse.ArgumentParser(prog="osu_date_sorter", description="Updates your osu!.db and Songs directory to allow sorting by Ranked Date using the Date Added sort in game.")
    parser.add_argument("osu_dir", help="your base osu! directory", type=pathlib.Path)
    args = parser.parse_args()

    osu_db_path = os.path.join(args.osu_dir, "osu!.db")
    assert os.path.isfile(osu_db_path), "osu!.db not found. Did you supply the right directory?"
    osu_song_dir = os.path.join(args.osu_dir, "Songs")
    assert os.path.isdir(osu_db_path), "Songs folder not found. Did you supply the right directory?"

    print("If you haven't made backups, press CTRL+C to terminate the program. Also, make sure osu! is closed. I do not claim responsibility for any corruptions that may occur.")
    print("Processing will automatically start in 10 seconds...")
    time.sleep(10)

    with gzip.open("ranked_data.gz", 'rb') as f:
        ranked_data = load_data(f)

    with open(osu_db_path, 'rb+') as f:
        update_db_last_modified(f, ranked_data)

    update_file_last_modified(osu_song_dir, ranked_data)

if __name__ == "__main__":
    exit(main())
