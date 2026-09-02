import time
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from api.weather_api import WeatherAPIClient, WeatherAPIError
from utils.validators import validate_location_query
from utils.helpers import (
    celsius_to_fahrenheit, fahrenheit_to_celsius, format_timestamp,
    format_hour_timestamp, format_day_name, get_humidity_comfort
)
from utils.weather_icons import get_weather_icon, get_hero_background_gradient
from config import Config

class WeatherService:
    """Service encapsulating weather business logic, data normalization, caching, and unit conversion."""

    def __init__(self, api_client: Optional[WeatherAPIClient] = None):
        self.client = api_client or WeatherAPIClient()
        self._cache: Dict[Tuple[str, str], Tuple[Dict[str, Any], float]] = {}

    def fetch_full_weather_dashboard(self, location: str, units: str = "metric", force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetches and compiles complete current weather and forecast data payload.
        Utilizes in-memory caching to avoid redundant API hits.
        """
        valid, msg = validate_location_query(location)
        if not valid:
            raise WeatherAPIError(msg)

        cache_key = (location.strip().lower(), units)
        current_time = time.time()

        # Check cache if not forcing refresh
        if not force_refresh and cache_key in self._cache:
            cached_data, cached_timestamp = self._cache[cache_key]
            if current_time - cached_timestamp < Config.CACHE_TTL_SECONDS:
                return cached_data

        # Fetch current weather & forecast from API
        current_raw = self.client.get_current_weather(location, units=units)
        forecast_raw = self.client.get_weather_forecast(location, units=units)

        # Parse & normalize data payload
        dashboard_data = self._build_dashboard_payload(current_raw, forecast_raw, units)

        # Store in cache
        self._cache[cache_key] = (dashboard_data, current_time)
        return dashboard_data

    def _build_dashboard_payload(self, current: Dict[str, Any], forecast: Dict[str, Any], units: str) -> Dict[str, Any]:
        """Parses raw OpenWeatherMap JSON responses into a structured dictionary."""
        tz_offset = current.get("timezone", 0)
        sys_data = current.get("sys", {})
        main_data = current.get("main", {})
        weather_list = current.get("weather", [{}])
        weather_obj = weather_list[0] if weather_list else {}
        wind_data = current.get("wind", {})

        temp = main_data.get("temp", 0.0)
        feels_like = main_data.get("feels_like", 0.0)
        temp_min = main_data.get("temp_min", temp)
        temp_max = main_data.get("temp_max", temp)

        # Calculate °C and °F values
        if units == "imperial":
            temp_f = temp
            temp_c = fahrenheit_to_celsius(temp)
            feels_f = feels_like
            feels_c = fahrenheit_to_celsius(feels_like)
            min_f, min_c = temp_min, fahrenheit_to_celsius(temp_min)
            max_f, max_c = temp_max, fahrenheit_to_celsius(temp_max)
        else:
            temp_c = temp
            temp_f = celsius_to_fahrenheit(temp)
            feels_c = feels_like
            feels_f = celsius_to_fahrenheit(feels_like)
            min_c, min_f = temp_min, celsius_to_fahrenheit(temp_min)
            max_c, max_f = temp_max, celsius_to_fahrenheit(temp_max)

        condition_main = weather_obj.get("main", "Clear")
        condition_desc = weather_obj.get("description", "").title()
        icon_code = weather_obj.get("icon", "")
        icon_symbol = get_weather_icon(icon_code, condition_main)
        bg_gradient = get_hero_background_gradient(condition_main)

        city_name = current.get("name", "Unknown")
        country_code = sys_data.get("country", "")
        location_display = f"{city_name}, {country_code}" if country_code else city_name

        humidity = main_data.get("humidity", 0)
        pressure = main_data.get("pressure", 1013)
        visibility_m = current.get("visibility", 10000)
        cloudiness = current.get("clouds", {}).get("all", 0)
        wind_speed = wind_data.get("speed", 0.0)

        sunrise = sys_data.get("sunrise", 0)
        sunset = sys_data.get("sunset", 0)

        # Parse Hourly / Next Intervals Forecast (Next 6-12 hours, 3-hour steps)
        next_intervals = self._parse_hourly_forecast(forecast.get("list", []), tz_offset, units)

        # Parse 5-Day Forecast
        five_day_list = self._parse_five_day_forecast(forecast.get("list", []), tz_offset, units)

        now_str = datetime.now().strftime("%I:%M %p").lstrip('0')

        return {
            "city": city_name,
            "country": country_code,
            "location_display": location_display,
            "units": units,
            "temp_c": round(temp_c, 1),
            "temp_f": round(temp_f, 1),
            "feels_like_c": round(feels_c, 1),
            "feels_like_f": round(feels_f, 1),
            "temp_min_c": round(min_c, 1),
            "temp_min_f": round(min_f, 1),
            "temp_max_c": round(max_c, 1),
            "temp_max_f": round(max_f, 1),
            "condition_main": condition_main,
            "condition_desc": condition_desc,
            "icon_code": icon_code,
            "icon_symbol": icon_symbol,
            "bg_gradient": bg_gradient,
            "humidity": humidity,
            "humidity_comfort": get_humidity_comfort(humidity),
            "pressure_hpa": pressure,
            "visibility_m": visibility_m,
            "visibility_km": round(visibility_m / 1000.0, 1),
            "cloudiness": cloudiness,
            "wind_speed": round(wind_speed, 1),
            "sunrise": format_timestamp(sunrise, tz_offset),
            "sunset": format_timestamp(sunset, tz_offset),
            "next_6h_forecast": next_intervals,
            "five_day_forecast": five_day_list,
            "last_updated": now_str
        }

    def _parse_hourly_forecast(self, forecast_list: List[Dict[str, Any]], tz_offset: int, units: str) -> List[Dict[str, Any]]:
        """Parses next 4 intervals (representing next ~12 hours in 3h steps) from OpenWeatherMap API list."""
        intervals = []
        for item in forecast_list[:4]:
            epoch = item.get("dt", 0)
            time_label = format_hour_timestamp(epoch, tz_offset)
            main = item.get("main", {})
            weather = item.get("weather", [{}])[0]
            pop = int(item.get("pop", 0) * 100)  # Probability of Precipitation %

            t_val = main.get("temp", 0.0)
            if units == "imperial":
                t_f = t_val
                t_c = fahrenheit_to_celsius(t_val)
            else:
                t_c = t_val
                t_f = celsius_to_fahrenheit(t_val)

            intervals.append({
                "time": time_label,
                "temp_c": round(t_c),
                "temp_f": round(t_f),
                "condition": weather.get("main", "Clear"),
                "icon": get_weather_icon(weather.get("icon", ""), weather.get("main", "")),
                "pop": pop
            })
        return intervals

    def _parse_five_day_forecast(self, forecast_list: List[Dict[str, Any]], tz_offset: int, units: str) -> List[Dict[str, Any]]:
        """Groups 3-hour forecast items by day to build 5-day daily high/low forecast summary."""
        daily_groups: Dict[str, List[Dict[str, Any]]] = {}

        for item in forecast_list:
            epoch = item.get("dt", 0)
            day_name = format_day_name(epoch, tz_offset)
            if day_name not in daily_groups:
                daily_groups[day_name] = []
            daily_groups[day_name].append(item)

        five_days = []
        for day_name, items in list(daily_groups.items())[:5]:
            temps = [it.get("main", {}).get("temp", 0.0) for it in items]
            min_t = min(temps) if temps else 0.0
            max_t = max(temps) if temps else 0.0

            if units == "imperial":
                min_f, min_c = min_t, fahrenheit_to_celsius(min_t)
                max_f, max_c = max_t, fahrenheit_to_celsius(max_t)
            else:
                min_c, min_f = min_t, celsius_to_fahrenheit(min_t)
                max_c, max_f = max_t, celsius_to_fahrenheit(max_t)

            # Midday forecast item for representative icon & condition
            mid_item = items[len(items) // 2]
            weather_obj = mid_item.get("weather", [{}])[0]
            condition = weather_obj.get("main", "Clear")
            icon = get_weather_icon(weather_obj.get("icon", ""), condition)
            humidity = mid_item.get("main", {}).get("humidity", 50)
            pop = int(max([it.get("pop", 0) for it in items]) * 100)

            five_days.append({
                "day": day_name,
                "icon": icon,
                "condition": condition,
                "high_c": round(max_c),
                "high_f": round(max_f),
                "low_c": round(min_c),
                "low_f": round(min_f),
                "humidity": humidity,
                "pop": pop
            })

        return five_days
