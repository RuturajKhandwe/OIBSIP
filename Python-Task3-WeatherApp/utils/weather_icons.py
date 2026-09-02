from typing import Dict

# Weather Condition to Unicode Emoji Icon mapping
WEATHER_ICON_MAP: Dict[str, str] = {
    "01d": "☀️",   # Clear sky day
    "01n": "🌙",   # Clear sky night
    "02d": "⛅",   # Few clouds day
    "02n": "☁️",   # Few clouds night
    "03d": "☁️",   # Scattered clouds
    "03n": "☁️",
    "04d": "☁️",   # Broken / overcast clouds
    "04n": "☁️",
    "09d": "🌧️",   # Shower rain
    "09n": "🌧️",
    "10d": "🌦️",   # Rain day
    "10n": "🌧️",   # Rain night
    "11d": "⛈️",   # Thunderstorm
    "11n": "⛈️",
    "13d": "❄️",   # Snow
    "13n": "❄️",
    "50d": "🌫️",   # Mist / Fog / Haze
    "50n": "🌫️"
}

# Fallback by weather condition main string
MAIN_CONDITION_MAP: Dict[str, str] = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
    "Smoke": "🌫️",
    "Dust": "🌫️",
    "Tornado": "🌪️"
}

# Dynamic Hero Background Glow Styling per weather condition
HERO_GLOW_STYLES: Dict[str, str] = {
    "Clear": "linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(21, 29, 46, 0.95) 100%)",
    "Clouds": "linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(21, 29, 46, 0.95) 100%)",
    "Rain": "linear-gradient(135deg, rgba(59, 130, 246, 0.18) 0%, rgba(21, 29, 46, 0.95) 100%)",
    "Drizzle": "linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(21, 29, 46, 0.95) 100%)",
    "Thunderstorm": "linear-gradient(135deg, rgba(147, 51, 234, 0.22) 0%, rgba(21, 29, 46, 0.95) 100%)",
    "Snow": "linear-gradient(135deg, rgba(224, 242, 254, 0.18) 0%, rgba(21, 29, 46, 0.95) 100%)",
    "Atmosphere": "linear-gradient(135deg, rgba(148, 163, 184, 0.15) 0%, rgba(21, 29, 46, 0.95) 100%)"
}

def get_weather_icon(icon_code: str = "", main_condition: str = "") -> str:
    """Returns suitable weather emoji icon based on OpenWeatherMap icon code or condition name."""
    if icon_code and icon_code in WEATHER_ICON_MAP:
        return WEATHER_ICON_MAP[icon_code]
    
    if main_condition and main_condition in MAIN_CONDITION_MAP:
        return MAIN_CONDITION_MAP[main_condition]
        
    return "🌤️"

def get_hero_background_gradient(main_condition: str = "") -> str:
    """Returns CSS linear-gradient background string tailored for the weather condition."""
    return HERO_GLOW_STYLES.get(main_condition, "linear-gradient(135deg, rgba(108, 99, 255, 0.12) 0%, rgba(21, 29, 46, 0.95) 100%)")
