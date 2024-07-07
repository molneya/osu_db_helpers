
import argparse
import gzip
import os
import pathlib
import time

import dates
import stars

def main():
    parser = argparse.ArgumentParser(prog="osu_date_sorter", description="Useful functions to manage your osu!.db")
    parser.add_argument("osu_dir", help="your base osu! directory", type=pathlib.Path)
    parser.add_argument("--update-dates", action="store_true", help="update dates to allow for sorting by ranked date")
    parser.add_argument("--update-stars", action="store_true", help="update stars to latest version")
    args = parser.parse_args()

    assert args.update_dates or args.update_stars, "No options selected. Run command again with --update-dates and/or --update-stars to complete an action."
    osu_db_path = os.path.join(args.osu_dir, "osu!.db")
    assert os.path.isfile(osu_db_path), "osu!.db not found. Did you supply the right directory?"
    osu_song_dir = os.path.join(args.osu_dir, "Songs")
    assert os.path.isdir(osu_song_dir), "Songs folder not found. Did you supply the right directory?"

    print("If you haven't made backups, press CTRL+C to terminate the program. Also, make sure osu! is closed. I do not claim responsibility for any corruptions that may occur.")
    print("Processing will automatically start in 10 seconds...")
    time.sleep(10)

    if args.update_dates:
        # Load ranked data
        with gzip.open("ranked_data.gz", 'rb') as fp:
            ranked_data = dates.load_data(fp)
        # Update osu!.db entries
        with open(osu_db_path, 'rb+') as fp:
            dates.update_db_last_modified(fp, ranked_data)
        # Update file last modified entries
        dates.update_file_last_modified(osu_song_dir, ranked_data)

    if args.update_stars:
        # Load stars data
        #with gzip.open("stars_data.gz", 'rb') as fp:
            #stars_data = stars.load_data(fp)
        with open(osu_db_path, 'rb') as fp:
            with open(osu_db_path + "_new", 'wb') as fp_new:
                stars.update_db_stars(fp, fp_new, {})

if __name__ == "__main__":
    exit(main())
