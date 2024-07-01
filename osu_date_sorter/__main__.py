
import argparse
import gzip
import pathlib
import time
from sorter import load_data, update_db_last_modified, update_file_last_modified

def main():
    parser = argparse.ArgumentParser(prog="osu_date_sorter", description="Overwrites last_modified in osu!.db to allow sorting by date ranked")
    parser.add_argument("osu_db", help="osu!.db file", type=argparse.FileType("rb+"))
    parser.add_argument("osu_songs", help="osu! Songs folder", type=pathlib.Path)
    args = parser.parse_args()

    print("If you haven't made backups, press CTRL+C to terminate the program. Also, make sure osu! is closed. I do not claim responsibility for any corruptions that may occur.")
    print("Processing will automatically start in 10 seconds...")
    time.sleep(10)

    with gzip.open("ranked_data.gz", 'rb') as f:
        ranked_data = load_data(f)

    update_db_last_modified(args.osu_db, ranked_data)
    update_file_last_modified(args.osu_songs, ranked_data)

if __name__ == "__main__":
    exit(main())
