import json
import re
import urllib.request
from datetime import datetime, timezone

URL = "https://www.tidetime.org/north-america/canada/nova-scotia.htm"
OUTPUT_FILE = "tides.json"


def download_page():
    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; Halifax-Tide-Board/1.0)"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_tides(html):
    # Remove script/style content so we only parse the visible tide table.
    cleaned = re.sub(
        r"<script\b[^>]*>.*?</script>",
        "",
        html,
        flags=re.I | re.S
    )

    cleaned = re.sub(
        r"<style\b[^>]*>.*?</style>",
        "",
        cleaned,
        flags=re.I | re.S
    )

    # Convert HTML into simple readable text.
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.I)
    cleaned = re.sub(r"</(?:li|div|td|tr|p|span|h\d)>", "\n", cleaned, flags=re.I)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)

    cleaned = (
        cleaned
        .replace("&nbsp;", " ")
        .replace("&amp;", "&")
    )

    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n+", "\n", cleaned)

    # Find visible entries such as:
    # Low 4:22am (0.43m)
    # High 9:56am (1.93m)
    pattern = re.compile(
        r"\b(High|Low)\s+"
        r"(\d{1,2}:\d{2}\s*(?:am|pm))\s*"
        r"\(\s*(-?\d+(?:\.\d+)?)m\s*\)",
        re.I
    )

    matches = pattern.findall(cleaned)

    tides = []

    for tide_type, tide_time, height in matches:
        tides.append({
            "type": tide_type.title(),
            "time": tide_time.replace(" ", "").lower(),
            "height_m": float(height)
        })

    return tides


def main():
    print("Downloading TideTime Nova Scotia tide data...")

    html = download_page()

    tides = extract_tides(html)

    if not tides:
        raise RuntimeError(
            "No tide entries were found. The TideTime page format may have changed."
        )

    output = {
        "source": URL,
        "location": "Nova Scotia",
        "timezone": "America/Halifax",
        "updated_utc": datetime.now(timezone.utc).isoformat(),
        "tides": tides
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print(f"Success: found {len(tides)} tide events.")
    print(f"Saved data to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
