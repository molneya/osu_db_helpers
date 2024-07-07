# osu! db helpers

Useful functions to manage your osu!.db.

## Usage

To download and view command usage:

```bash
git clone https://github.com/molneya/osu_db_helpers
cd osu_db_helpers
python osu_db_helpers --help
```

To update the `osu!.db` to sort by date added in game, you need to supply your osu! directory and the `--update-dates` flag, for example:

```bash
python osu_db_helpers "E:\osu!" --update-dates
```

To update all star ratings in your `osu!.db`, you need to supply your osu! directory and the `--update-stars` flag, for example:

```bash
python osu_db_helpers "E:\osu!" --update-stars
```

You can also supply both flags to do both operations at once.

## Warning

Make sure you close osu! before running any commands or else osu! will overwrite it.
I would also recommend backing up your `osu!.db` before doing this. I am not responsible for any database corruption or data loss you may experience.

## Data

`ranked_data.gz` is up to date as of 2024-07-01.
`stars_data.gz` is up to date as of 2024-06-05.
