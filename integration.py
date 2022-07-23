import requests
import argparse

BASE = 'https://api-dev-593.seenons.com/api/me/streams'
QUERY_KEY = 'postal_code'

def get_waste_streams(post_code):
    url = f'{BASE}?{QUERY_KEY}={post_code}'
    waste_streams = requests.get(url).json()
    print(waste_streams)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Postal code parser')
    parser.add_argument('-p', '--postalcode', help='Post code (4 integers only)', required=True)
    args = parser.parse_args()

    get_waste_streams(args.postalcode)
