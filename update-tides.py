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


def visible_text(value):
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def extract_tides(html):
    tides = []

    marker_pattern = re.compile(
        r"(highTide|lowTide)",
        re.I
    )

    markers = list(marker_pattern.finditer(html))

    print(f"Found {len(markers)} tide markers.")

    for i, marker in enumerate(markers):

        start = marker.start()

        if i + 1 < len(markers):
            end = markers[i + 1].start()
        else:
            end = min(len(html), start + 1500)

        block = html[start:end]

        text = visible_text(block)

        tide_type = (
            "High"
            if marker.group(1).lower() == "hightide"
            else "Low"
        )

        time_match = re.search(
            r"\b(\d{1,2}:\d{2}\s*(?:am|pm))\b",
            text,
            re.I
        )

        height_match = re.search(
            r"(-?\d+(?:\.\d+)?)\s*m\b",
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
                "height_m": float(height_match.group(1))
            })

    return tides


def main():

    print("Downloading TideTime Nova Scotia tide data...")

    html = download_page()

    print(f"Downloaded {len(html):,} characters.")

    high_count = len(
        re.findall(r"highTide", html, re.I)
    )

    low_count = len(
        re.findall(r"lowTide", html, re.I)
    )

    print(f"highTide occurrences: {high_count}")
    print(f"lowTide occurrences: {low_count}")

    tides = extract_tides(html)

    print(f"Parsed {len(tides)} tide events.")

    if not tides:
        raise RuntimeError(
            "Tide markers were found, but no tide "
            "times/heights could be extracted."
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
        f"SUCCESS: Saved {len(tides)} tide events "
        f"to {OUTPUT_FILE}"
    )

    print("First tide events:")

    for tide in tides[:10]:
        print(
            tide["type"],
            tide["time"],
            tide["height_m"],
            "m"
        )


if __name__ == "__main__":
    main()
