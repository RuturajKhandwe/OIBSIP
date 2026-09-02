import unittest
from utils.validators import validate_location_query, is_zip_code

class TestValidators(unittest.TestCase):
    """Test suite for location input validation routines."""

    def test_valid_city_queries(self):
        """Test valid city name inputs."""
        valid, msg = validate_location_query("Pune")
        self.assertTrue(valid)
        self.assertEqual(msg, "")

        valid, msg = validate_location_query("New York, US")
        self.assertTrue(valid)

        valid, msg = validate_location_query("St. John's")
        self.assertTrue(valid)

    def test_empty_query_rejection(self):
        """Test empty string and whitespace input rejection."""
        valid, msg = validate_location_query("")
        self.assertFalse(valid)
        self.assertIn("enter a city", msg.lower())

        valid, msg = validate_location_query("   ")
        self.assertFalse(valid)

    def test_too_short_query_rejection(self):
        """Test single character input rejection."""
        valid, msg = validate_location_query("a")
        self.assertFalse(valid)
        self.assertIn("at least 2 characters", msg.lower())

    def test_invalid_character_rejection(self):
        """Test queries containing illegal characters."""
        valid, msg = validate_location_query("London<script>")
        self.assertFalse(valid)
        self.assertIn("invalid characters", msg.lower())

    def test_zip_code_detection(self):
        """Test postal / zip code identification."""
        self.assertTrue(is_zip_code("90210"))
        self.assertTrue(is_zip_code("411001"))
        self.assertFalse(is_zip_code("Pune"))
        self.assertFalse(is_zip_code("London"))

if __name__ == '__main__':
    unittest.main()
