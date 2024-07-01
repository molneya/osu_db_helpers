# osu! date sorter

Updates your osu!.db and Songs directory to allow sorting by Ranked Date using the Date Added sort in game.

## Usage

To download and run the help command:

```bash
git clone https://github.com/molneya/osu_date_sorter
cd osu_date_sorter
python osu_date_sorter --help
```

To make the program update your stuff, you need to supply your osu! directory, for example:

```bash
python osu_date_sorter "E:\osu!"
```

Make sure you close osu! before running this command or else osu! will overwrite it.
I would also recommend backing up your osu!.db before doing this. I am not responsible for any database corruption or data loss you may experience.
