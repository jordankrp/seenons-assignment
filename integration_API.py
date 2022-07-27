#from flask import Flask, request
#from flask_restful import Resource, Api, reqparse
from datetime import datetime, date
import requests
import sys
import copy

#app = Flask(__name__)
#api = Api(app)

SEENONS_BASE = "https://api-dev-593.seenons.com/api/me/streams"
HUISVUILKALENDAR = "https://huisvuilkalender.denhaag.nl"
YEAR = date.today().year


class SeenonsAPI():

    def get_all_waste_streams(self):
        # Get all waste streams from Seenons API.
        url = SEENONS_BASE
        response = requests.get(url)
        return response.json()

    def get_waste_streams_per_postcode(self, post_code):
        # Get waste streams for given post code using the Seenons API.
        url = f"{SEENONS_BASE}?postal_code={post_code}"
        response = requests.get(url)
        return response.json()

    def get_list_of_stream_ids(self, streams):
        # Make list of available stream IDs.
        stream_ids = []
        for stream in streams["items"]:
            stream_ids.append(stream["stream_product_id"])
        return stream_ids


class HagueAPI():

    def get_waste_streams(self, bag_id):
        # Get 'afvalstromen' from the Huisvuilkalendar API.
        url = f"{HUISVUILKALENDAR}/rest/adressen/{bag_id}/afvalstromen"
        response = requests.get(url)
        return response.json()

    def get_dates_per_stream(self, bag_id):
        # Get dates and waste streams IDs from the Huisvuilkalendar API using bag ID.
        url = f"{HUISVUILKALENDAR}/rest/adressen/{bag_id}/kalender/{YEAR}"
        response = requests.get(url)
        return response.json()

    def get_house_info(self, post_code, house_number):
        # Display options for available house letters given the post code and house number.
        url = f"{HUISVUILKALENDAR}/adressen/{post_code}:{house_number}"
        response = requests.get(url).json()
        if response != []:
            return response
        # If post code / house number is wrong, we get an empty list for house info and need to exit.
        else:
            print("Postal address does not exist")
            sys.exit()

    def get_bagid(self, addresses, house_letter):
        # Get bag ID from the address details
        for address in addresses:
            if address["huisletter"] == house_letter:
                return address["bagid"]


class Integration():

    def translate_date_to_weekday(self, calendar_date):
        # Translate calendar date format to weekday (Monday, Tuesday etc).
        datetime_object = datetime.strptime(calendar_date, "%Y-%m-%d")
        return datetime_object.strftime("%A")

    def translate_hague_to_seenons_id(self, all_seenons_waste_streams, hague_available_streams):
        # Change the IDs in the Hague available streams to match those of Seenons API.
        # All IDs are considered (0) until we find a match to the Seenons API.
        for hague_stream in hague_available_streams:
            hague_stream["id"] = 0
            for seenons_stream in all_seenons_waste_streams["items"]:
                # If the stream product ID starts with the title in the Hague stream ID, then overwrite the Hague stream ID.
                if seenons_stream["type"].lower().startswith(hague_stream["title"].lower()):
                    hague_stream["id"] = seenons_stream["stream_product_id"]
        # Keep in mind that returned list is mutated
        return hague_available_streams

    def modify_hague_stream_dates(self, hague_waste_streams, all_seenons_waste_streams, hague_dates):
        # Need to map 'afvalstrrom_id' value in Hague dates list to that of Seenons API.
        # First we make a deep copy of the Hague waste streams date as the list will be mutated in the next modification step
        old_hague_waste_streams = copy.deepcopy(hague_waste_streams)
        # Now we modify Hague waste stream IDs with the Seenons IDs.
        hague_waste_streams = self.translate_hague_to_seenons_id(
            all_seenons_waste_streams, hague_waste_streams
        )
        # Create dict to map old to new waste stream IDs. Key is old ID, value is new.
        mapping_dict = {}
        for index, item in enumerate(old_hague_waste_streams):
            mapping_dict[item["id"]] = hague_waste_streams[index]["id"]
        # Modify dates according to mapping dict
        for item in hague_dates:
            if item["afvalstroom_id"] in mapping_dict:
                item["afvalstroom_id"] = mapping_dict[item["afvalstroom_id"]]
        return hague_dates

    def add_weekday_to_hague_dates(self, hague_dates):
        # Add weekday info to the Hague dates list
        for item in hague_dates:
            item["weekday"] = self.translate_date_to_weekday(item["ophaaldatum"])
        return hague_dates
    
    def create_availability_dict(self, hague_dates, seenons_stream_ids):
        # Create a dict with matching stream ID as keys and all available dates per stream as values.
        stream_dict = {}
        available_dates = []
        for item in hague_dates:
            # If stream ID of (filtered) dates dict is in the Seenons API list.
            if item["afvalstroom_id"] in seenons_stream_ids:
                # First append available date to the list of dates.
                available_dates.append(item["ophaaldatum"])
                # Then add waste stream ID as key to the dict and assign the dates list as its value.
                stream_dict[item["afvalstroom_id"]] = available_dates
        return stream_dict


if __name__ == "__main__":
    seenons_API = SeenonsAPI()
    hague_API = HagueAPI()
    integration = Integration()
