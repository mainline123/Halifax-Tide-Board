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


def clean_text(value):
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def extract_tides(html):

    # TideTime uses highTide and lowTide elements.
    # Capture each complete element separately.
    block_pattern = re.compile(
        r'<[^>]*class=["\'][^"\']*\b(highTide|lowTide)\b[^"\']*["\'][^>]*>'
        r'(.*?)'
        r'</[^>]+>',
        re.I | re.S
    )

    blocks = block_pattern.findall(html)

    tides = []

    for tide_class, block in blocks:

        text = clean_text(block)

        tide_type = (
            "High"
            if tide_class.lower() == "hightide"
            else "Low"
        )

        time_match = re.search(
            r'(\d{1,2}:\d{2}\s*(?:am|pm))',
            text,
            re.I
        )

        height_match = re.search(
            r'\(\s*(-?\d+(?:\.\d+)?)\s*m\s*\)',
            text,
            re.I
        )

        if time_match and height_match:

            tide_time = re.sub(
                r"\s+",
                "",
                time_match.group(1)
            ).lower()

            tides.append({
                "type": tide_type,
                "time": tide_time,
                "height_m": float(
                    height_match.group(1)
                )
            })

    # Fallback:
    # If TideTime changes the surrounding HTML,
    # extract the visible tide sequence from the page.
    if not tides:

        text = html

        text = re.sub(
            r"<script\b[^>]*>.*?</script>",
            " ",
            text,
            flags=re.I | re.S
        )

        text = re.sub(
            r"<style\b[^>]*>.*?</style>",
            " ",
            text,
            flags=re.I | re.S
        )

        text = re.sub(
            r"<[^>]+>",
            " ",
            text
        )

        text = unescape(text)

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        pattern = re.compile(
            r'\b(High|Low)\s+'
            r'(\d{1,2}:\d{2}\s*(?:am|pm))'
            r'.{0,100}?'
            r'\(\s*(-?\d+(?:\.\d+)?)\s*m\s*\)',
            re.I | re.S
        )

        for tide_type, tide_time, height in pattern.findall(text):

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

    print(
        "Downloading TideTime Nova Scotia tide data..."
    )

    html = download_page()

    print(
        f"Downloaded {len(html):,} characters."
    )

    tides = extract_tides(html)

    print(
        f"Found {len(tides)} tide events."
    )

    if not tides:

        # Diagnostic information if the page changes again.
        print(
            "highTide occurrences:",
            len(
                re.findall(
                    r"highTide",
                    html,
                    re.I
                )
            )
        )

        print(
            "lowTide occurrences:",
            len(
                re.findall(
                    r"lowTide",
                    html,
                    re.I
                )
            )
        )

        raise RuntimeError(
            "TideTime downloaded successfully, "
            "but no tide events could be parsed."
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

    print(
        f"SUCCESS: Saved {len(tides)} "
        f"tide events to {OUTPUT_FILE}"
    )

    print("First tide events:")

    for tide in tides[:8]:

        print(
            tide["type"],
            tide["time"],
            tide["height_m"],
            "m"
        )


if __name__ == "__main__":
    main()
