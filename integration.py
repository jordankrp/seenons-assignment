import requests
import argparse
from datetime import datetime

HUISVUILKALENDAR = 'https://huisvuilkalender.denhaag.nl/rest/adressen/0518200001769843/kalender/2022'
SEENONS_BASE = 'https://api-dev-593.seenons.com/api/me/streams'
QUERY_KEY = 'postal_code'

def get_waste_streams(post_code):
    url = f'{SEENONS_BASE}?{QUERY_KEY}={post_code}'
    waste_streams = requests.get(url).json()
    return waste_streams
    
def get_dates_per_stream():
    url = HUISVUILKALENDAR
    dates = requests.get(url).json()
    return dates

def translate_date_to_weekday(date):
    datetime_object = datetime.strptime(date, '%Y-%m-%d')
    #return datetime_object.weekday()
    return datetime_object.strftime('%A')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Postal code parser')
    parser.add_argument('-p', '--postalcode', help='Post code (4 integers only)', required=True)
    parser.add_argument('-wd', '--weekday', nargs='+', help='Weekdays (Monday, Tuesday ...)', required=False)
    args = parser.parse_args()

    # Available waste streams for the postal code given (using Seenons API)
    waste_streams = get_waste_streams(args.postalcode)

    # Available dates per stream (using huisvuilkalendar API)
    dates = get_dates_per_stream()

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



    
