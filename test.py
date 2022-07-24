import unittest
from integration import (
    get_bagid,
    get_house_info,
    choose_house_letter,
    get_waste_streams_per_postcode,
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
        # Test Seenons API waste streams
        post_code = "2566WD"
        waste_streams = get_waste_streams_per_postcode(post_code)
        # Cross check some random entries with postman API
        self.assertEqual(waste_streams["totalItems"], 3)
        self.assertEqual(waste_streams["items"][0]["stream_product_id"], 6)
        self.assertEqual(waste_streams["items"][0]["type"], "sinaasappelschillen")
        self.assertEqual(waste_streams["items"][2]["type"], "plastic-emmers")
        print("test 5 completed")


if __name__ == "__main__":
    tester = TestIntegration()

    tester.test_1()
    tester.test_2()
    tester.test_3()
    tester.test_4()
    tester.test_5()
