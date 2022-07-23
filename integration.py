import requests
import argparse
import inquirer
from datetime import datetime, date

HUISVUILKALENDAR = "https://huisvuilkalender.denhaag.nl"
ADDRESS = "https://huisvuilkalender.denhaag.nl/adressen/2512HE:68"
SEENONS_BASE = "https://api-dev-593.seenons.com/api/me/streams"
QUERY_KEY = "postal_code"
YEAR = date.today().year


def get_waste_streams(postalcode):
    url = f"{SEENONS_BASE}?{QUERY_KEY}={postalcode}"
    waste_streams = requests.get(url).json()
    return waste_streams


def get_dates_per_stream(bagid):
    url = f"{HUISVUILKALENDAR}/rest/adressen/{bagid}/kalender/{YEAR}"
    dates = requests.get(url).json()
    return dates


def translate_date_to_weekday(calendar_date):
    datetime_object = datetime.strptime(calendar_date, "%Y-%m-%d")
    # return datetime_object.weekday()
    return datetime_object.strftime("%A")


def get_house_letter(postcode, housenumber):
    url = f"{HUISVUILKALENDAR}/adressen/{postcode}:{housenumber}"
    response = requests.get(url).json()
    letters = []
    for item in response:
        letters.append(item["huisletter"])
    question = [
        inquirer.List(
            "houseletter", message="Which is the house letter?", choices=letters
        ),
    ]
    answer = inquirer.prompt(question)
    return answer["houseletter"]


def get_bagid(postcode, housenumber, houseletter):
    url = f"{HUISVUILKALENDAR}/adressen/{postcode}:{housenumber}"
    response = requests.get(url).json()
    for item in response:
        if item["huisletter"] == houseletter:
            return item["bagid"]


def create_availability_dict(dates, seenons_stream_ids):
    # Create a dict with stream ID as keys and all available dates per stream as their values
    stream_dict = {}
    available_dates = []
    for item in dates:
        # If stream ID of (filtered) dates dict is in the Seenons API list
        if item["afvalstroom_id"] in seenons_stream_ids:
            # First append the list of dates
            available_dates.append(item["ophaaldatum"])
            # Add waste stream ID as key to the dict and assign the dates list as its value
            stream_dict[item["afvalstroom_id"]] = available_dates
    return stream_dict


def main(postcode, housenumber, weekdays=None):
    # Get house letter
    house_letter = get_house_letter(postcode, housenumber)
    print(f"House letter: {house_letter}")

    # Get bag ID
    bag_id = get_bagid(postcode, housenumber, house_letter)
    print(f"Bag ID: {bag_id}")

    # Available waste streams for the postal code given (using Seenons API)
    waste_streams = get_waste_streams(postcode)

    # Make list of stream IDs
    seenons_stream_ids = []
    for stream in waste_streams["items"]:
        seenons_stream_ids.append(stream["stream_product_id"])

    # Available dates per stream (using huisvuilkalendar API)
    dates = get_dates_per_stream(bag_id)

    # Add weekday data to the dates
    for item in dates:
        item["weekday"] = translate_date_to_weekday(item["ophaaldatum"])

    # Check if weekdays are given by the user, if so filter out dates accordingly
    if weekdays is not None:
        # Need to filter dates list to contain only weekdays asked by the user
        dates[:] = [d for d in dates if d.get("weekday") in weekdays]

    available_streams = create_availability_dict(dates, seenons_stream_ids)

    # Visualise output
    print(
        f"Available waste streams for postal code {postcode}, housenumber {housenumber}{house_letter}:"
    )
    for stream_id, available_dates in available_streams.items():
        for waste_stream in waste_streams["items"]:
            if stream_id == waste_stream["stream_product_id"]:
                print(f"{(waste_stream['type'])} (ID: {stream_id})")

        print(f"Available dates (user requested {weekdays}):")
        for i in available_dates:
            print(i)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--postcode", help="Post code (no space)", required=True)
    parser.add_argument("-n", "--housenumber", help="House Number", required=True)
    parser.add_argument(
        "-wd",
        "--weekdays",
        nargs="+",
        help="Weekdays (Monday, Tuesday etc...)",
        required=False,
    )
    args = parser.parse_args()

    main(args.postcode, args.housenumber, args.weekdays)
