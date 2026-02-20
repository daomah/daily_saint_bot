# daily_saint_bot

Fetches the top saint of the day from the OCA (Orthodox Church in America) website and formats it as a markdown file, ready for social media or personal notes.

## What it does

For each day, the bot:

1. Pulls the saint listing from the OCA website for that date
2. Takes the first (top) saint listed, or a random lesser-commemorated saint with `--random`
3. Fetches the saint's large icon image URL
4. Fetches the troparion and kontakion from the troparia page
5. Outputs a markdown file with a linked title, icon image, troparion, kontakion, and a standard hashtag footer

## Usage

```bash
python3 bot.py                     # top saint, today's date
python3 bot.py 2026-01-18          # top saint, specific date (YYYY-MM-DD)
python3 bot.py --random            # random non-top saint for today
python3 bot.py --random 2026-01-18 # random non-top saint, specific date
python3 bot.py -o 18.md            # save to file instead of stdout
```

`--random` picks randomly from all saints commemorated that day except the top saint. If only one saint is listed for the day, that saint is used regardless.

Output goes to stdout by default. Redirect to save:

```bash
python3 bot.py 2026-01-18 > 18.md
```

## Setup

Requires Python 3.9+ and the packages in `requirements.txt`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# or on Arch Linux:
sudo pacman -S python-requests python-beautifulsoup4
```

Run with the venv python:

```bash
.venv/bin/python bot.py
.venv/bin/python bot.py 2026-01-18
```

## Output format

```markdown
## [The Circumcision of our Lord and Savior Jesus Christ - 01 January](https://www.oca.org/saints/lives/2026/01/01/100001-the-circumcision-of-our-lord-and-savior-jesus-christ)

![The Circumcision of our Lord and Savior Jesus Christ](https://images.oca.org/icons/lg/january/0101circumcision.jpg)

🎶troparion🎶

Enthroned on high with the Eternal Father and Your divine Spirit,
O Jesus, You willed to be born on earth of the unwedded handmaid, your Mother.
...

🎶kontakion🎶

The Lord of all accepts to be circumcised,
thus, as He is good, excises the sins of mortal men.
...

#Christian #OrthodoxChristian #Orthodox #Orthostr #Saint
```

## How it works

The bot scrapes two pages on oca.org for each date:

### Saints listing page
`/saints/lives/YYYY/MM/DD` — the bot collects all `<article class="saint">` elements on the page. In default mode the first is used; in `--random` mode one is chosen at random from the rest. From each article it extracts:
- The saint's name from `<h2 class="name">`
- The slug URL for the life and troparia pages
- The icon image URL (upgraded from thumbnail to large size)

### Troparia page
`/saints/troparia/YYYY/MM/DD/SAINT_SLUG` — the bot extracts the first troparion and first kontakion from the `<article>` elements on the page. Chant line-break markers (`/`) are converted to newlines.

## Resources

| Resource | URL |
|---|---|
| OCA Lives of the Saints | https://www.oca.org/saints/lives |
| OCA Icon Images | https://images.oca.org/icons/lg/ |

## License

The **code** in this repository is released under the [MIT License](LICENSE).

The **output** produced by the bot contains liturgical texts (troparia and kontakia) sourced from the OCA website. These texts are the property of their respective copyright holders. The output is intended for personal devotional use.
