import unittest

from policy import can_auto_resolve, resolution_amount, validate_dispute


class PolicyTests(unittest.TestCase):
    def test_supported_surge(self):
        trip = {"verified_category": "SURGE_OVERCHARGE_CONFIRMED"}
        result = validate_dispute("SURGE_OVERCHARGE", trip)
        self.assertTrue(result["supported"])

    def test_unsupported_rider_cancel(self):
        trip = {"verified_category": "RIDER_INITIATED_CANCELLATION"}
        result = validate_dispute("RIDER_CANCELLED", trip)
        self.assertFalse(result["supported"])

    def test_threshold(self):
        self.assertTrue(can_auto_resolve(25, True))
        self.assertFalse(can_auto_resolve(50.01, True))
        self.assertFalse(can_auto_resolve(25, False))

    def test_trip_amount(self):
        self.assertEqual(
            resolution_amount({"fare_value": 40, "credit_value": 40}),
            40,
        )
        self.assertEqual(
            resolution_amount({"fare_value": 40, "credit_value": -12.5}),
            40,
        )


if __name__ == "__main__":
    unittest.main()
