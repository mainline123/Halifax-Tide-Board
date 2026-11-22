import json
import urllib.request
from datetime import datetime, timezone

OUTPUT_FILE = "weather.json"

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


def get_english(value):

    if isinstance(value, dict):
        return value.get("en", "")

    return value or ""


def find_halifax(data):

    features = data.get("features", [])

    # FIRST CHOICE:
    # Exact Halifax city record.
    for feature in features:

        properties = feature.get(
            "properties",
            {}
        )

        name = get_english(
            properties.get("name")
        ).strip()

        if name.lower() == "halifax":
            print(
                "Exact Halifax record found."
            )
            return feature

    # SECOND CHOICE:
    # Exact Dartmouth city record.
    for feature in features:

        properties = feature.get(
            "properties",
            {}
        )

        name = get_english(
            properties.get("name")
        ).strip()

        if name.lower() == "dartmouth":
            print(
                "Exact Dartmouth record found."
            )
            return feature

    # Diagnostic output if neither exists.
    print(
        "Exact Halifax/Dartmouth record "
        "was not found."
    )

    print(
        "Possible Halifax-area records:"
    )

    for feature in features:

        properties = feature.get(
            "properties",
            {}
        )

        name = get_english(
            properties.get("name")
        )

        region = get_english(
            properties.get("region")
        )

        combined = (
            str(name) + " " + str(region)
        ).lower()

        if (
            "halifax" in combined
            or "dartmouth" in combined
        ):
            print(
                f"NAME: {name} | "
                f"REGION: {region}"
            )

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
            "An exact Halifax or Dartmouth "
            "weather record was not found."
        )

    properties = feature.get(
        "properties",
        {}
    )

    selected_name = get_english(
        properties.get("name")
    )

    selected_region = get_english(
        properties.get("region")
    )

    print(
        f"Selected location: {selected_name}"
    )

    print(
        f"Selected region: {selected_region}"
    )

    output = {
        "location":
            "Halifax–Dartmouth",

        "weather_location":
            selected_name,

        "weather_region":
            selected_region,

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


if __name__ == "__main__":
    main()
