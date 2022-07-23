import requests
import argparse
import inquirer
from datetime import datetime, date

HUISVUILKALENDAR = 'https://huisvuilkalender.denhaag.nl'
ADDRESS = 'https://huisvuilkalender.denhaag.nl/adressen/2512HE:68'
SEENONS_BASE = 'https://api-dev-593.seenons.com/api/me/streams'
QUERY_KEY = 'postal_code'
YEAR = date.today().year

def get_waste_streams(postalcode):
    url = f'{SEENONS_BASE}?{QUERY_KEY}={postalcode}'
    waste_streams = requests.get(url).json()
    return waste_streams
    
def get_dates_per_stream(bagid):
    url = f'{HUISVUILKALENDAR}/rest/adressen/{bagid}/kalender/{YEAR}'
    dates = requests.get(url).json()
    return dates

def translate_date_to_weekday(date):
    datetime_object = datetime.strptime(date, '%Y-%m-%d')
    #return datetime_object.weekday()
    return datetime_object.strftime('%A')

def get_house_letter(postcode, housenumber):
    url = f'{HUISVUILKALENDAR}/adressen/{postcode}:{housenumber}'
    response = requests.get(url).json()
    letters = []
    for item in response:
        letters.append(item['huisletter'])
    question = [
        inquirer.List('houseletter',
                       message="Which is the house letter?",
                       choices=letters
                    ),
    ]
    answer = inquirer.prompt(question)
    return answer['houseletter']

def get_bagid(postcode, housenumber, houseletter):
    url = f'{HUISVUILKALENDAR}/adressen/{postcode}:{housenumber}'
    response = requests.get(url).json()
    for item in response:
        if item['huisletter'] == houseletter:
            return item['bagid']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Postal code parser')
    parser.add_argument('-p', '--postalcode', help='Post code (no space)', required=True)
    parser.add_argument('-n', '--housenumber', help='House Number', required=True)
    parser.add_argument('-wd', '--weekday', nargs='+', help='Weekdays (Monday, Tuesday etc...)', required=False)
    args = parser.parse_args()

    # Get house letter
    house_letter = get_house_letter(args.postalcode, args.housenumber)
    print(f'House letter: {house_letter}')

    # Get bag ID
    bag_id = get_bagid(args.postalcode, args.housenumber, house_letter)
    print(f'Bag ID: {bag_id}')

    # Available waste streams for the postal code given (using Seenons API)
    waste_streams = get_waste_streams(args.postalcode)

    # Available dates per stream (using huisvuilkalendar API)
    dates = get_dates_per_stream(bag_id)

    # Add weekday data to the dates
    for date in dates:
        date['weekday'] = translate_date_to_weekday(date['ophaaldatum'])

    # Check if weekdays are given by the user
    if args.weekday is not None:
        # Need to filter date list to contain only weekdays asked by the user
        dates[:] = [d for d in dates if d.get('weekday') in args.weekday]

    print('All available waste streams:')
    for stream in waste_streams['items']:
        print(f"{stream['type']} ({stream['stream_product_id']})")
        for date in dates:
            if date['afvalstroom_id'] == stream['stream_product_id']:
                print(f"Stream {stream['stream_product_id']} available on day {date['ophaaldatum']} which is {date['weekday']}")



    
