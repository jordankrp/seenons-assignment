import unittest
from integration_cli import (
    get_bagid,
    get_house_info,
    choose_house_letter,
    get_waste_streams_per_postcode,
    get_dates_per_stream,
    modify_dates,
)


class TestIntegration(unittest.TestCase):
    def test_1(self):
        # Test bag ID for correct address
        post_code = "2512HE"
        house_number = "68"
        house_letter = "A"
        bag_id = get_bagid(post_code, house_number, house_letter)
        expected_bag_id = "0518200001769844"
        self.assertEqual(bag_id, expected_bag_id)
        print("Test 1 completed")

    def test_2(self):
        # Test correct house number
        post_code = "2512HE"
        house_number = "66"
        house_info = get_house_info(post_code, house_number)
        # House info expected to be a list of dict
        self.assertNotEqual(house_info, [])
        # House letter should be a dict key
        for item in house_info:
            self.assertIn("huisletter", item)
        print("Test 2 completed")

    def test_3(self):
        # Test wrong house number
        post_code = "2512HE"
        house_number = "34"
        house_info = get_house_info(post_code, house_number)
        # House info expected to be an empty list
        expected_house_info = []
        self.assertEqual(house_info, expected_house_info)
        print("Test 3 completed")

    def test_4(self):
        # Test single house for given house number
        post_code = "2518JC"
        house_number = "15"
        house_info = get_house_info(post_code, house_number)
        # House info expected to contain 1 element
        self.assertEqual(len(house_info), 1)
        # Choose letter should automatically select huisleter from the single entry
        house_letter = choose_house_letter(house_info)
        self.assertEqual(house_letter, "")
        print("test 4 completed")

    def test_5(self):
        # Test Seenons API waste streams request
        post_code = "2566WD"
        waste_streams = get_waste_streams_per_postcode(post_code)
        # Cross check some random entries with postman API
        self.assertEqual(waste_streams["totalItems"], 3)
        self.assertEqual(waste_streams["items"][0]["stream_product_id"], 6)
        self.assertEqual(waste_streams["items"][0]["type"], "sinaasappelschillen")
        self.assertEqual(waste_streams["items"][2]["type"], "plastic-emmers")
        print("test 5 completed")

    def test_6(self):
        # Test Huisvuilkalendar API request
        bag_id = "0518200001769844"
        dates = get_dates_per_stream(bag_id)
        self.assertEqual(dates[0]["afvalstroom_id"], 4)
        self.assertEqual(dates[1]["ophaaldatum"], "2022-01-11")
        print("test 6 completed")

    def test_7(self):
        # Test modify dates list
        bag_id = "0518200001769844"
        dates = get_dates_per_stream(bag_id)
        self.assertEqual(dates[0]["afvalstroom_id"], 4)
        self.assertEqual(dates[-3]["afvalstroom_id"], 3)
        dates = modify_dates(bag_id, dates)
        # Verify that stream 3 -> 4 (papier) and stream 4 -> 3 (rest)
        self.assertEqual(dates[0]["afvalstroom_id"], 3)
        self.assertEqual(dates[-3]["afvalstroom_id"], 4)
        print("test 7 completed")

    def test_8(self):
        # Test modify dates list custom made
        bag_id = "0518200001769844"
        dates = [
            {"afvalstroom_id": 1, "ophaaldatum": "2022-01-04"},
            {"afvalstroom_id": 2, "ophaaldatum": "2022-01-05"},
            {"afvalstroom_id": 5, "ophaaldatum": "2022-01-09"},
        ]
        dates = modify_dates(bag_id, dates)
        # Verify that stream 1 -> 17 (gft), stream 2 -> 1 (pmd) and stream 5 -> 0 (kerstbomen is unknown, hence 0)
        self.assertEqual(dates[0]["afvalstroom_id"], 17)
        self.assertEqual(dates[1]["afvalstroom_id"], 1)
        self.assertEqual(dates[2]["afvalstroom_id"], 0)
        print("test 8 completed")


if __name__ == "__main__":
    tester = TestIntegration()

    tester.test_1()
    tester.test_2()
    tester.test_3()
    tester.test_4()
    tester.test_5()
    tester.test_6()
    tester.test_7()
    tester.test_8()
