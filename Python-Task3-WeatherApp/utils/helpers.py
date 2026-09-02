from datetime import datetime, timezone, timedelta
from typing import Union

def celsius_to_fahrenheit(celsius: Union[int, float]) -> float:
    """Converts Celsius temperature to Fahrenheit."""
    return (celsius * 9.0 / 5.0) + 32.0

def fahrenheit_to_celsius(fahrenheit: Union[int, float]) -> float:
    """Converts Fahrenheit temperature to Celsius."""
    return (fahrenheit - 32.0) * 5.0 / 9.0

def format_timestamp(epoch_seconds: int, tz_offset_seconds: int = 0) -> str:
    """Formats Unix timestamp into readable local time string (e.g. '06:12 AM')."""
    if not epoch_seconds:
        return "N/A"
    try:
        tz = timezone(timedelta(seconds=tz_offset_seconds))
        dt = datetime.fromtimestamp(epoch_seconds, tz=tz)
        return dt.strftime("%I:%M %p").lstrip('0')
    except Exception:
        return "N/A"

def format_hour_timestamp(epoch_seconds: int, tz_offset_seconds: int = 0) -> str:
    """Formats Unix timestamp into hour interval string (e.g. '3 PM' or '12 PM')."""
    if not epoch_seconds:
        return "N/A"
    try:
        tz = timezone(timedelta(seconds=tz_offset_seconds))
        dt = datetime.fromtimestamp(epoch_seconds, tz=tz)
        return dt.strftime("%I %p").lstrip('0')
    except Exception:
        return "N/A"

def format_day_name(epoch_seconds: int, tz_offset_seconds: int = 0) -> str:
    """Formats Unix timestamp into short day name (e.g. 'Monday', 'Tue')."""
    if not epoch_seconds:
        return "N/A"
    try:
        tz = timezone(timedelta(seconds=tz_offset_seconds))
        dt = datetime.fromtimestamp(epoch_seconds, tz=tz)
        return dt.strftime("%a")
    except Exception:
        return "N/A"

def format_wind(speed: float, units: str = "metric") -> str:
    """Formats wind speed with appropriate units."""
    if speed is None:
        return "N/A"
    if units == "imperial":
        return f"{speed:.1f} mph"
    return f"{speed:.1f} m/s"

def format_pressure(hpa: int) -> str:
    """Formats pressure in hPa."""
    return f"{hpa} hPa" if hpa is not None else "N/A"

def format_visibility(meters: int) -> str:
    """Formats visibility distance in km."""
    if meters is None:
        return "N/A"
    km = meters / 1000.0
    return f"{km:.1f} km"

def get_humidity_comfort(humidity: int) -> str:
    """Returns human-readable humidity comfort rating."""
    if humidity is None:
        return "Unknown"
    if humidity < 30:
        return "Low (Dry)"
    elif 30 <= humidity <= 60:
        return "Comfortable"
    elif 61 <= humidity <= 80:
        return "Humid"
    else:
        return "High (Sticky)"
