#!/usr/bin/env python3
"""
daily_saint_bot - Fetches the top saint of the day from oca.org
and formats it for social media posting.
"""

import argparse
import random
import re
import sys
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.oca.org"
TAGS = "#Christian #OrthodoxChristian #Orthodox #Orthostr #Saint"


def fetch_page(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_saint_article(article) -> tuple[str, str, str]:
    """Extract (saint_name, slug_path, icon_url) from a saint <article> element."""
    name_tag = article.find("h2", class_="name")
    saint_name = re.sub(r"\s+", " ", name_tag.get_text(strip=True)) if name_tag else ""
    saint_name = re.sub(r"<!--.*?-->", "", saint_name).strip()

    life_link = article.find("a", href=re.compile(r"/saints/lives/\d{4}/\d{2}/\d{2}/\d+-.+"))
    slug_path = life_link["href"] if life_link else ""

    img = article.find("figure", class_="thumbnail")
    img_tag = img.find("img") if img else None
    icon_url = ""
    if img_tag and img_tag.get("src"):
        icon_url = re.sub(r"/icons/(xsm|sm|md)/", "/icons/lg/", img_tag["src"])
        if not icon_url.startswith("http"):
            icon_url = f"https:{icon_url}" if icon_url.startswith("//") else f"https://images.oca.org{icon_url}"

    return saint_name, slug_path, icon_url


def get_all_saints(day: date) -> list[tuple[str, str, str]]:
    """Return a list of (saint_name, slug_path, icon_url) for all saints on the given day."""
    url = f"{BASE_URL}/saints/lives/{day.year}/{day.month:02d}/{day.day:02d}"
    soup = fetch_page(url)

    articles = soup.find_all("article", class_=re.compile(r"\bsaint\b"))
    if not articles:
        print(f"ERROR: Could not find any saint on {url}", file=sys.stderr)
        sys.exit(1)

    return [parse_saint_article(a) for a in articles]


def clean_chant_text(text: str) -> str:
    """Replace chant line-break markers (/) with actual newlines."""
    # " / " marks a line break in OCA chant notation
    text = re.sub(r"\s*/\s*", "\n", text)
    # Strip trailing whitespace from each line
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


def get_troparia(slug_path: str) -> tuple[str, str]:
    """Return (troparion_text, kontakion_text) from the troparia page."""
    troparia_path = slug_path.replace("/saints/lives/", "/saints/troparia/")
    url = f"{BASE_URL}{troparia_path}"
    soup = fetch_page(url)

    troparion = ""
    kontakion = ""

    # Each troparion/kontakion is in its own <article> with an <h2> heading and <p> body
    for article in soup.find_all("article"):
        h2 = article.find("h2")
        if not h2:
            continue
        label = h2.get_text(strip=True).lower()
        p = article.find("p")
        text = clean_chant_text(p.get_text(strip=True)) if p else ""

        if "troparion" in label and not troparion:
            troparion = text
        elif "kontakion" in label and not kontakion:
            kontakion = text

    return troparion, kontakion


def format_output(saint_name: str, slug_path: str, icon_url: str, troparion: str, kontakion: str, day: date) -> str:
    life_url = f"{BASE_URL}{slug_path}"
    day_str = f"{day.day:02d} {day.strftime('%B')}"

    lines = [
        f"## [{saint_name} - {day_str}]({life_url})",
        "",
    ]

    if icon_url:
        lines += [f"![{saint_name}]({icon_url})", ""]

    if troparion:
        lines += ["🎶troparion🎶", "", troparion, ""]

    if kontakion:
        lines += ["🎶kontakion🎶", "", kontakion, ""]

    lines.append(TAGS)

    return "\n".join(lines)


def parse_date(date_str: str) -> date:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    print(f"ERROR: Could not parse date '{date_str}'. Use YYYY-MM-DD format.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Fetch the top saint of the day from oca.org")
    parser.add_argument(
        "date",
        nargs="?",
        help="Date to fetch (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "-o", "--output",
        help="Save output to this file instead of printing to stdout.",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Pick a random non-top saint for the day. Falls back to the top saint if only one is listed.",
    )
    args = parser.parse_args()

    day = parse_date(args.date) if args.date else date.today()

    print(f"Fetching saint for {day.strftime('%B %d, %Y')}...", file=sys.stderr)

    saints = get_all_saints(day)

    if args.random and len(saints) > 1:
        saint_name, slug_path, icon_url = random.choice(saints[1:])
        print(f"Random saint: {saint_name}", file=sys.stderr)
    else:
        saint_name, slug_path, icon_url = saints[0]
        if args.random:
            print(f"Only one saint today, using: {saint_name}", file=sys.stderr)
        else:
            print(f"Top saint: {saint_name}", file=sys.stderr)

    troparion, kontakion = get_troparia(slug_path)

    output = format_output(saint_name, slug_path, icon_url, troparion, kontakion, day)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output + "\n")
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
