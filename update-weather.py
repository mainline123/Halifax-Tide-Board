import json
import urllib.request
from datetime import datetime, timezone

OUTPUT_FILE = "weather.json"

# Environment and Climate Change Canada
# Halifax/Dartmouth area
API_URL = (
    "https://api.weather.gc.ca/collections/"
    "citypageweather-realtime/items"
    "?f=json"
    "&lang=en"
    "&limit=1000"
)


def download_weather():

    request = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent":
            "Halifax-Tide-Weather-Board/1.0"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


def find_halifax(data):

    features = data.get("features", [])

    # Look for Halifax first,
    # then Dartmouth if Halifax isn't returned.
    for target in ["Halifax", "Dartmouth"]:

        for feature in features:

            properties = feature.get(
                "properties",
                {}
            )

            text = json.dumps(
                properties
            ).lower()

            if target.lower() in text:
                return feature

    return None


def main():

    print(
        "Downloading Environment Canada "
        "weather data..."
    )

    data = download_weather()

    print(
        "Downloaded",
        len(data.get("features", [])),
        "weather locations."
    )

    feature = find_halifax(data)

    if feature is None:

        raise RuntimeError(
            "Halifax/Dartmouth weather "
            "record was not found."
        )

    properties = feature.get(
        "properties",
        {}
    )

    output = {
        "location":
            "Halifax–Dartmouth",

        "source":
            "Environment and Climate "
            "Change Canada",

        "updated_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "weather":
            properties
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        "SUCCESS: Halifax/Dartmouth "
        "weather saved to weather.json"
    )

    print(
        "Weather fields received:"
    )

    for key, value in properties.items():

        if value is not None:
            print(
                f"{key}: {value}"
            )


if __name__ == "__main__":
    main()
