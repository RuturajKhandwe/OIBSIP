# Atmos — Advanced Real-Time Weather Dashboard

> **OIBSIP Internship Task 4 — Basic Weather App (Advanced Tier Submission)**  
> A standalone, production-grade Python desktop application featuring real-time weather analytics, 5-day forecasts, automatic IP-based location detection, temperature unit switching (°C / °F), and non-blocking asynchronous UI rendering built with PyQt5.

---

## 🌟 Key Features

### 🟢 Core Real-Time Weather Analytics
- **City & ZIP Code Search**: Prominent search bar supporting city names (e.g. `Pune`, `London`, `Tokyo`), country codes, and postal/ZIP codes with instant validation.
- **Hero Weather Card**: Large temperature focal display, feels-like temperature, high/low range, detailed condition description, and weather symbol.
- **Dynamic Weather Atmospheric Glow**: Background decoration adjusts dynamically according to atmospheric conditions (Warm Golden glow for Clear, Cool Sky for Clouds, Atmospheric Blue for Rain, Deep Purple for Thunderstorm, Frosted White for Snow).
- **8-Metric Atmospheric Grid**: Dedicated cards for Humidity (with comfort rating), Wind Speed & Direction, Pressure (hPa), Visibility (km), Feels Like Temp, Cloud Coverage (%), Sunrise, and Sunset.

### 🚀 Advanced Functionality & UX
- **Celsius / Fahrenheit Toggle (°C / °F)**: Instant temperature unit conversion without redundant API network calls.
- **Automatic IP Location Detection**: Integrated `ipinfo.io` lookup via `[ ◎ Use My Location ]` button. Fails gracefully to default or manual search if IP geolocation is unavailable.
- **Next 6-12 Hour Interval Forecast**: Horizontal card row displaying upcoming 3-hour interval weather forecasts with timestamps, condition icons, temperatures, and rain probabilities.
- **5-Day Weather Forecast**: Daily high/low temperature summary cards with condition descriptions and precipitation odds.
- **Non-Blocking Asynchronous Threading**: Built with `QThread` workers to ensure the PyQt5 GUI **never freezes** during network API calls.
- **In-Memory API Response Caching**: Prevents duplicate network hits within a 10-minute TTL window.

---

## 🛠️ Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **GUI Framework** | PyQt5 5.15+ | Standalone desktop application windowing & QSS dark styling |
| **Language** | Python 3.10+ | Clean syntax, robust standard library |
| **HTTP Client** | `requests` | Synchronous HTTP calls with mandatory 10s network timeouts |
| **Environment** | `python-dotenv` | Secure API key management via `.env` file |
| **Image Processing**| Pillow (PIL) | Image and icon manipulation |
| **APIs** | OpenWeatherMap API & IPInfo API | Weather data provider & IP geolocation lookup |
| **Testing** | `pytest` | Automated unit and integration test suite |

---

## 🏗️ Architecture & Component Layout

The application separates API logic, business rules, and UI components into a clean layered architecture:

```
Atmos-Weather-App/
│
├── app.py                      # Desktop application entrypoint & QApplication execution
├── config.py                   # Centralized configuration & environment loader
├── requirements.txt            # Python package dependencies
├── README.md                   # Complete documentation
├── .env.example                # Safe API key template
├── .gitignore                  # Git exclusion rules
│
├── api/
│   ├── __init__.py
│   └── weather_api.py          # Low-level HTTP client for OpenWeatherMap & IPInfo
│
├── services/
│   ├── __init__.py
│   ├── location_service.py     # IP location detection & fallbacks
│   └── weather_service.py      # Business logic, caching, unit conversion & formatting
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # AtmosMainWindow QMainWindow & QThread worker threads
│   ├── widgets.py              # Custom PyQt5 widgets (Hero card, Detail cards, Forecast)
│   └── styles.py               # Complete QSS dark theme stylesheet
│
├── utils/
│   ├── __init__.py
│   ├── validators.py           # Location query input validators
│   ├── weather_icons.py        # Weather icon symbols & dynamic gradient mappings
│   └── helpers.py              # Unit conversion (°C/°F) & timestamp formatters
│
└── tests/
    ├── __init__.py
    ├── test_weather_api.py     # Mocked HTTP API client tests
    ├── test_validators.py      # Validator unit tests
    └── test_location_service.py# Location service unit tests
```

---

## ⚙️ Installation & Setup

### 1. Clone & Navigate
```bash
cd "e:\Projects\Atmos-Weather-App"
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. API Key Configuration
Create a `.env` file in the project root based on `.env.example`:

```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
IPINFO_TOKEN=your_ipinfo_token_here
```

> **Note**: Get a free API key from [OpenWeatherMap](https://openweathermap.org/api). If no key is provided initially, the application will display a clear configuration prompt inside the GUI without crashing.

---

## 🚀 Running the Application

Execute the standalone desktop application:

```bash
python app.py
```

---

## 🧪 Running Automated Tests

Run the full test suite using `pytest`:

```bash
pytest tests
```

Expected Output:
```text
============================= 12 passed in 0.78s ==============================
```

---

## 🔒 Security & Best Practices

- **Zero Hard-coded Secrets**: API keys are loaded strictly from `.env` via `python-dotenv`.
- **Git Security**: `.env` is explicitly gitignored to prevent credential leaks.
- **Input Sanitization**: User search queries are validated and sanitized in `utils/validators.py`.
- **Timeout Guards**: All network calls enforce a strict 10-second timeout to prevent indefinite hangs.

---

## 🎓 OIBSIP Task 4 Information

- **Task Name**: Basic Weather App (Advanced Tier Implementation)
- **Domain**: Python Development Internship
- **Developer**: Portfolio Submission

---

## 📜 License

Distributed under the MIT License.
