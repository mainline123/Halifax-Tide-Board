import json
import re
import urllib.request
from datetime import datetime, timezone
from html import unescape

URL = "https://www.tidetime.org/north-america/canada/nova-scotia.htm"
OUTPUT_FILE = "tides.json"


def download_page():
    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/131 Safari/537.36"
            )
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def html_to_text(html):
    # Remove scripts and styles
    text = re.sub(
        r"<script\b[^>]*>.*?</script>",
        "",
        html,
        flags=re.I | re.S
    )

    text = re.sub(
        r"<style\b[^>]*>.*?</style>",
        "",
        text,
        flags=re.I | re.S
    )

    # Put spaces between HTML elements
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"</[^>]+>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)

    text = unescape(text)

    # Collapse all whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_tides(html):
    text = html_to_text(html)

    # TideTime displays entries like:
    # Low 4:22am (0.43m)
    # High 9:56am (1.93m)

    pattern = re.compile(
        r"\b(High|Low)\s+"
        r"(\d{1,2}:\d{2}\s*(?:am|pm))"
        r"\s*\(\s*(-?\d+(?:\.\d+)?)\s*m\s*\)",
        re.I
    )

    matches = pattern.findall(text)

    tides = []

    for tide_type, tide_time, height in matches:

        tides.append({
            "type": tide_type.title(),
            "time": re.sub(
                r"\s+",
                "",
                tide_time
            ).lower(),
            "height_m": float(height)
        })

    return tides


def main():

    print("Downloading TideTime Nova Scotia tide data...")

    html = download_page()

    print(f"Downloaded {len(html):,} characters.")

    tides = extract_tides(html)

    print(f"Found {len(tides)} tide events.")

    if not tides:
        raise RuntimeError(
            "No tide entries were found in the TideTime page."
        )

    output = {
        "source": URL,
        "location": "Nova Scotia",
        "timezone": "America/Halifax",
        "updated_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "tides": tides
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2
        )

    print(f"Saved tide data to {OUTPUT_FILE}")

    for tide in tides[:8]:
        print(
            tide["type"],
            tide["time"],
            tide["height_m"],
            "m"
        )


if __name__ == "__main__":
    main()
