import unittest
from unittest.mock import patch
from services.location_service import LocationService
from api.weather_api import LocationError

class TestLocationService(unittest.TestCase):
    """Test suite for location detection service and fallbacks."""

    @patch("api.weather_api.WeatherAPIClient.get_ip_location")
    def test_successful_location_detection(self, mock_ip_loc):
        """Test successful IP location detection."""
        mock_ip_loc.return_value = {
            "city": "Mumbai",
            "country": "IN",
            "ip": "103.21.124.1"
        }

        success, loc_str, country = LocationService.detect_user_location()
        self.assertTrue(success)
        self.assertEqual(loc_str, "Mumbai, IN")
        self.assertEqual(country, "IN")

    @patch("api.weather_api.WeatherAPIClient.get_ip_location")
    def test_failed_location_detection_fallback(self, mock_ip_loc):
        """Test IP location detection failure handling."""
        mock_ip_loc.side_effect = LocationError("Failed to detect location")

        success, msg, country = LocationService.detect_user_location()
        self.assertFalse(success)
        self.assertIsNone(country)

    def test_default_location_fallback(self):
        """Test default city retrieval."""
        default_city = LocationService.get_default_location()
        self.assertIsNotNone(default_city)
        self.assertTrue(len(default_city) > 0)

if __name__ == '__main__':
    unittest.main()
