
import argparse, os, pathlib, time
import dates, stars

def main():
    parser = argparse.ArgumentParser(prog="osu_db_helpers", description="Useful functions to manage your osu!.db")
    parser.add_argument("osu_dir", help="your base osu! directory", type=pathlib.Path)
    parser.add_argument("--update-dates", action="store_true", help="update dates to allow for sorting by ranked date")
    parser.add_argument("--update-stars", action="store_true", help="update stars to latest version")
    args = parser.parse_args()

    osu_db_path = os.path.join(args.osu_dir, "osu!.db")
    osu_songs_dir = os.path.join(args.osu_dir, "Songs")

    if not (args.update_dates or args.update_stars):
        raise ValueError("No options selected. Run command again with --update-dates and/or --update-stars to complete an action.")
    if not os.path.isfile(osu_db_path):
        raise ValueError("osu!.db not found. Did you supply the right directory?")
    if not os.path.isdir(osu_songs_dir):
        raise ValueError("Songs folder not found. Did you supply the right directory?")

    print("If you haven't made backups, press CTRL+C to terminate the program. Also, make sure osu! is closed. I do not claim responsibility for any corruptions that may occur.")
    print("Processing will automatically start in 10 seconds...")
    time.sleep(10)

    if args.update_dates:
        dates.run(osu_db_path, osu_songs_dir)

    if args.update_stars:
        stars.run(osu_db_path)

if __name__ == "__main__":
    exit(main())
