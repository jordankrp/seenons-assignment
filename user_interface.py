import inquirer
import argparse
from integration_API import SeenonsAPI, HagueAPI, Integration

seenons_api = SeenonsAPI()
hague_api = HagueAPI()
integration = Integration()


def choose_house_letter(house_info):
    # Ask user to insert house letter from the ones available.
    letters = []
    # If house info contains more than one entry, prompt user to select house letter.
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
    # Else house info contains one entry, so the house letter of this single entry is used.
    else:
        return house_info[0]["huisletter"]


def main(post_code, house_number, weekdays=None):

    # Get house info
    house_info = hague_api.get_house_info(post_code, house_number)
    print(house_info)

    # Get house letter
    house_letter = choose_house_letter(house_info)
    print(f"House letter: {house_letter}")

    # Get bag ID
    bag_id = hague_api.get_bagid(house_info, house_letter)
    print(f"Bag ID: {bag_id}")

    # All available Seenons streams.
    all_seenons_waste_streams = seenons_api.get_all_waste_streams()

    # Available waste streams for the postal code given (using Seenons API).
    seenons_streams_per_postcode = seenons_api.get_waste_streams_per_postcode(post_code)

    # Make list of available stream IDs.
    seenons_stream_ids = seenons_api.get_list_of_stream_ids(
        seenons_streams_per_postcode
    )

    # Available dates per stream using Huisvuilkalendar API.
    hague_stream_dates = hague_api.get_dates_per_stream(bag_id)

    # Get waste streams from Huisvuilkalendar API fro given bag ID
    hague_available_streams = hague_api.get_waste_streams(bag_id)

    # Modify stream dates fetched from the Hague API
    hague_stream_dates = integration.modify_hague_stream_dates(
        hague_available_streams, all_seenons_waste_streams, hague_stream_dates
    )

    # Add weekday to hague API stream dates list
    hague_stream_dates = integration.add_weekday_to_hague_dates(hague_stream_dates)

    # Check if weekdays are given by the user, if so filter out dates accordingly.
    if weekdays is not None:
        # Format weekdays list in case user has used wrong case
        weekdays = [weekday.capitalize() for weekday in weekdays]
        # Need to filter Hague stream dates list to contain only weekdays asked by the user.
        hague_stream_dates[:] = [
            d for d in hague_stream_dates if d.get("weekday") in weekdays
        ]

    # Dictionary to save available waste stream data
    available_streams = integration.create_availability_dict(
        hague_stream_dates, seenons_stream_ids
    )

    # Visualise output
    print(
        f"Available waste streams for postal code {post_code}, housenumber {house_number}{house_letter}:"
    )
    for stream_id, available_dates in available_streams.items():
        for waste_stream in seenons_streams_per_postcode["items"]:
            if stream_id == waste_stream["stream_product_id"]:
                print(f"{(waste_stream['type'])} (ID: {stream_id})")

        print(f"Available dates (user requested {weekdays}):")
        for i in available_dates:
            print(i)


if __name__ == "__main__":
    post_code = "2512HE"
    house_number = "68"
    house_letter = "A"

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--postcode", help="Post code (no space)", required=True)
    parser.add_argument("-n", "--housenumber", help="House Number", required=True)
    parser.add_argument(
        "-wd",
        "--weekday",
        nargs="+",
        help="Weekdays (Monday, Tuesday etc...)",
        required=False,
    )
    args = parser.parse_args()

    main(args.postcode, args.housenumber, args.weekday)
