import requests
import argparse
import inquirer
import sys
from datetime import datetime, date

HUISVUILKALENDAR = "https://huisvuilkalender.denhaag.nl"
SEENONS_BASE = "https://api-dev-593.seenons.com/api/me/streams"
QUERY_KEY = "postal_code"
YEAR = date.today().year


def get_waste_streams(postalcode):
    # Get waste streams for given post code using the Seenons API.
    url = f"{SEENONS_BASE}?{QUERY_KEY}={postalcode}"
    waste_streams = requests.get(url).json()
    return waste_streams


def get_dates_per_stream(bagid):
    # Get dates and waste streams IDs from the Huisvuilkalendar API using bag ID.
    url = f"{HUISVUILKALENDAR}/rest/adressen/{bagid}/kalender/{YEAR}"
    dates = requests.get(url).json()
    return dates


def translate_date_to_weekday(calendar_date):
    # Translate calendar date format to weekday (Monday, Tuesday etc).
    datetime_object = datetime.strptime(calendar_date, "%Y-%m-%d")
    return datetime_object.strftime("%A")


def get_house_info(postcode, housenumber):
    # Display options for available house letters given the post code and house number.
    url = f"{HUISVUILKALENDAR}/adressen/{postcode}:{housenumber}"
    house_info = requests.get(url).json()
    return house_info


def choose_house_letter(house_info):
    # Ask user to insert house letter from the ones available.
    letters = []
    # If house info contains more than one entry, prompt user to select house letter
    if len(house_info) > 1:
        for item in house_info:
            letters.append(item["huisletter"])
        question = [
            inquirer.List(
                "houseletter", message="Which is the house letter?", choices=letters
            ),
        ]
        answer = inquirer.prompt(question)
        return answer["houseletter"]
    # Else house info contains one entries, so the house letter of this single entry is used
    else:
        return house_info[0]["huisletter"]


def get_bagid(postcode, housenumber, houseletter):
    # Get bag ID from the address details
    url = f"{HUISVUILKALENDAR}/adressen/{postcode}:{housenumber}"
    response = requests.get(url).json()
    for item in response:
        if item["huisletter"] == houseletter:
            return item["bagid"]


def create_availability_dict(dates, seenons_stream_ids):
    # Create a dict with matching stream ID as keys and all available dates per stream as values
    stream_dict = {}
    available_dates = []
    for item in dates:
        # If stream ID of (filtered) dates dict is in the Seenons API list
        if item["afvalstroom_id"] in seenons_stream_ids:
            # First append available date to the list of dates
            available_dates.append(item["ophaaldatum"])
            # Then add waste stream ID as key to the dict and assign the dates list as its value
            stream_dict[item["afvalstroom_id"]] = available_dates
    return stream_dict


def main(postcode, housenumber, weekdays=None):
    # Get house letter
    house_info = get_house_info(postcode, housenumber)
    # If post code / house number is wrong, we get an empty list for house info and need to exit
    if house_info == []:
        print("Postal address does not exist")
        sys.exit()
    house_letter = choose_house_letter(house_info)
    print(f"House letter: {house_letter}")

    # Get bag ID
    bag_id = get_bagid(postcode, housenumber, house_letter)
    print(f"Bag ID: {bag_id}")

    # Available waste streams for the postal code given (using Seenons API)
    waste_streams = get_waste_streams(postcode)

    # Make list of available stream IDs
    seenons_stream_ids = []
    for stream in waste_streams["items"]:
        seenons_stream_ids.append(stream["stream_product_id"])

    # Available dates per stream (using Huisvuilkalendar API)
    dates = get_dates_per_stream(bag_id)

    # Add weekday info to the dates list
    for item in dates:
        item["weekday"] = translate_date_to_weekday(item["ophaaldatum"])

    # Check if weekdays are given by the user, if so filter out dates accordingly
    if weekdays is not None:
        # Need to filter dates list to contain only weekdays asked by the user
        dates[:] = [d for d in dates if d.get("weekday") in weekdays]

    # Dictionary to save available waste stream data
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
