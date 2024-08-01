# osu! db helpers

Useful functions to manage your osu!.db.

## Usage

To download and view command usage:

```bash
git clone https://github.com/molneya/osu_db_helpers
cd osu_db_helpers
python osu_db_helpers --help
```

This program comes with the following flags:

- `--update-dates` updates the date_added attribute of all beatmaps to the time it was ranked so you can sort by ranked date using "Date Added" in game.
- `--update-stars` updates star ratings of all beatmaps to the latest version.
- `--purge-mode MODE` deletes all beatmaps from a specified mode.

For example, if you want to update all star ratings whilst removing all catch and mania beatmaps, you can run the following command:

```bash
python osu_db_helpers "E:\osu!" --update-stars --purge-mode 2 --purge-mode 3
```

## Warning

Make sure you close osu! before running any commands or else osu! will overwrite it.
I would also recommend backing up your `osu!.db` before doing this. I am not responsible for any database corruption or data loss you may experience.

## Data

`ranked_data.gz` is up to date as of 2024-07-01.
`stars_data.gz` is up to date as of 2024-06-05.

If you require more recent data, make an issue or something.
