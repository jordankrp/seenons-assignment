import requests
import argparse

SEENONS_BASE = 'https://api-dev-593.seenons.com/api/me/streams'
QUERY_KEY = 'postal_code'
HUISVUILKALENDAR = 'https://huisvuilkalender.denhaag.nl/rest/adressen/0518200001769843/kalender/2022'

def get_waste_streams(post_code):
    url = f'{SEENONS_BASE}?{QUERY_KEY}={post_code}'
    waste_streams = requests.get(url).json()
    return waste_streams
    
def get_days_per_stream():
    url = HUISVUILKALENDAR
    days = requests.get(url).json()
    return days

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Postal code parser')
    parser.add_argument('-p', '--postalcode', help='Post code (4 integers only)', required=True)
    args = parser.parse_args()

    waste_streams = get_waste_streams(args.postalcode)
    days = get_days_per_stream()

    print('All available waste streams:')
    for stream in waste_streams['items']:
        print(f"{stream['type']} ({stream['stream_product_id']})")
        for day in days:
            if day['afvalstroom_id'] == stream['stream_product_id']:
                print(f"Stream available on day {day['ophaaldatum']}")



    
