import unittest
from integration import get_bagid


class TestIntegration(unittest.TestCase):
    def test_1(self):
        # Test if we get correct bag ID
        post_code = "2512HE"
        house_number = "68"
        house_letter = "A"
        bag_id = get_bagid(post_code, house_number, house_letter)
        expected_bag_id = "0518200001769844"
        self.assertEqual(bag_id, expected_bag_id)
        print("Test 1 completed")


if __name__ == "__main__":
    tester = TestIntegration()

    tester.test_1()
