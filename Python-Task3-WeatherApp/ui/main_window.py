import os
from typing import Dict, Any
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QPushButton, QGridLayout, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont

from config import Config
from services.weather_service import WeatherService
from services.location_service import LocationService
from api.weather_api import WeatherAPIError
from utils.validators import validate_location_query
from ui.styles import MAIN_QSS
from ui.widgets import (
    SearchBarWidget, TempToggleWidget, HeroWeatherCard,
    HourlyForecastCard, DailyForecastCard, DetailCard, EmptyStateWidget
)

class FetchWeatherWorker(QThread):
    """Background worker thread to fetch weather data without blocking the PyQt5 main thread."""
    
    dataFetched = pyqtSignal(dict)
    errorOccurred = pyqtSignal(str)

    def __init__(self, weather_service: WeatherService, location: str, units: str, force_refresh: bool = False):
        super().__init__()
        self.weather_service = weather_service
        self.location = location
        self.units = units
        self.force_refresh = force_refresh

    def run(self):
        try:
            data = self.weather_service.fetch_full_weather_dashboard(
                self.location, units=self.units, force_refresh=self.force_refresh
            )
            self.dataFetched.emit(data)
        except WeatherAPIError as e:
            self.errorOccurred.emit(str(e))
        except Exception as e:
            self.errorOccurred.emit(f"Unexpected error: {str(e)}")


class DetectLocationWorker(QThread):
    """Background worker thread to detect IP location without blocking GUI."""

    locationDetected = pyqtSignal(str)
    detectionFailed = pyqtSignal(str)

    def run(self):
        success, location_str, _ = LocationService.detect_user_location()
        if success:
            self.locationDetected.emit(location_str)
        else:
            self.detectionFailed.emit(location_str)


class AtmosMainWindow(QMainWindow):
    """Main Application Window for Atmos Weather Dashboard."""

    def __init__(self):
        super().__init__()
        self.weather_service = WeatherService()
        self.current_units = Config.DEFAULT_UNITS
        self.current_location = ""
        self.cached_payload = None

        self.setWindowTitle(f"{Config.APP_NAME} — {Config.APP_SUBTITLE}")
        self.resize(1180, 780)
        self.setMinimumSize(950, 650)

        self.init_ui()

        # Check API key configuration on startup
        if not Config.is_api_key_configured():
            self.show_error("OpenWeatherMap API key is missing or not configured. Please add your key to .env file.")
        else:
            self.auto_detect_location()

    def init_ui(self):
        """Initializes GUI structure and QSS styling."""
        self.setStyleSheet(MAIN_QSS)

        # Central Root Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(16)

        # 1. Header Bar
        root_layout.addLayout(self._create_header_layout())

        # 2. Search Component Bar
        self.search_widget = SearchBarWidget()
        self.search_widget.searchRequested.connect(self.fetch_weather)
        self.search_widget.autoLocationRequested.connect(self.auto_detect_location)
        root_layout.addWidget(self.search_widget)

        # 3. Loading & Error Feedback Banner Containers
        self.lbl_loading = QLabel("Fetching real-time weather data...")
        self.lbl_loading.setStyleSheet("font-size: 13px; color: #38BDF8; font-weight: 500; padding: 4px 0;")
        self.lbl_loading.hide()
        root_layout.addWidget(self.lbl_loading)

        self.error_banner = QFrame()
        self.error_banner.setObjectName("errorCard")
        err_layout = QHBoxLayout(self.error_banner)
        err_layout.setContentsMargins(14, 10, 14, 10)
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("errorText")
        self.lbl_error.setWordWrap(True)
        err_layout.addWidget(self.lbl_error)
        self.error_banner.hide()
        root_layout.addWidget(self.error_banner)

        # 4. Scrollable Dashboard Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.dashboard_container = QWidget()
        self.dashboard_layout = QVBoxLayout(self.dashboard_container)
        self.dashboard_layout.setContentsMargins(0, 0, 8, 0)
        self.dashboard_layout.setSpacing(20)

        # Empty State Placeholder Widget
        self.empty_state = EmptyStateWidget()
        self.empty_state.searchRequested.connect(self.fetch_weather)
        self.dashboard_layout.addWidget(self.empty_state)

        # Hero Weather Card
        self.hero_card = HeroWeatherCard()
        self.hero_card.hide()
        self.dashboard_layout.addWidget(self.hero_card)

        # Hourly Forecast Section Container
        self.hourly_container = QWidget()
        hourly_layout = QVBoxLayout(self.hourly_container)
        hourly_layout.setContentsMargins(0, 0, 0, 0)
        hourly_layout.setSpacing(10)

        lbl_hourly_title = QLabel("Next Available Forecast Intervals (Next 6-12 Hours)")
        lbl_hourly_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #F8FAFC;")
        hourly_layout.addWidget(lbl_hourly_title)

        self.hourly_cards_layout = QHBoxLayout()
        self.hourly_cards_layout.setSpacing(12)
        hourly_layout.addLayout(self.hourly_cards_layout)
        self.hourly_container.hide()
        self.dashboard_layout.addWidget(self.hourly_container)

        # 5-Day Forecast Section Container
        self.daily_container = QWidget()
        daily_layout = QVBoxLayout(self.daily_container)
        daily_layout.setContentsMargins(0, 0, 0, 0)
        daily_layout.setSpacing(10)

        lbl_daily_title = QLabel("5-Day Weather Forecast")
        lbl_daily_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #F8FAFC;")
        daily_layout.addWidget(lbl_daily_title)

        self.daily_cards_layout = QHBoxLayout()
        self.daily_cards_layout.setSpacing(12)
        daily_layout.addLayout(self.daily_cards_layout)
        self.daily_container.hide()
        self.dashboard_layout.addWidget(self.daily_container)

        # Weather Details Grid Section Container
        self.details_container = QWidget()
        details_layout = QVBoxLayout(self.details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(10)

        lbl_details_title = QLabel("Atmospheric & Weather Details")
        lbl_details_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #F8FAFC;")
        details_layout.addWidget(lbl_details_title)

        self.details_grid_layout = QGridLayout()
        self.details_grid_layout.setSpacing(12)
        details_layout.addLayout(self.details_grid_layout)
        self.details_container.hide()
        self.dashboard_layout.addWidget(self.details_container)

        self.dashboard_layout.addStretch()
        scroll_area.setWidget(self.dashboard_container)
        root_layout.addWidget(scroll_area, stretch=1)

        # 5. Bottom Status Footer Bar
        root_layout.addLayout(self._create_footer_layout())

    def _create_header_layout(self) -> QHBoxLayout:
        header = QHBoxLayout()
        
        # Branding
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        
        lbl_app = QLabel(f"🌤️ {Config.APP_NAME}")
        lbl_app.setStyleSheet("font-size: 26px; font-weight: 800; color: #F8FAFC; letter-spacing: -0.5px;")
        
        lbl_sub = QLabel(Config.APP_SUBTITLE)
        lbl_sub.setStyleSheet("font-size: 13px; color: #94A3B8; font-weight: 500;")

        title_box.addWidget(lbl_app)
        title_box.addWidget(lbl_sub)

        header.addLayout(title_box)
        header.addStretch()

        # Temperature Unit Toggle
        self.unit_toggle = TempToggleWidget(self.current_units)
        self.unit_toggle.unitChanged.connect(self._on_unit_changed)
        header.addWidget(self.unit_toggle)

        # Refresh Button
        self.btn_refresh = QPushButton("↻  Refresh")
        self.btn_refresh.setObjectName("refreshBtn")
        self.btn_refresh.setToolTip("Refresh current weather data")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_weather)
        header.addWidget(self.btn_refresh)

        return header

    def _create_footer_layout(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 4, 0, 0)

        self.status_pill = QFrame()
        self.status_pill.setObjectName("statusPill")
        pill_layout = QHBoxLayout(self.status_pill)
        pill_layout.setContentsMargins(10, 4, 10, 4)

        self.lbl_status = QLabel("●  Live  •  Ready")
        self.lbl_status.setObjectName("statusText")
        pill_layout.addWidget(self.lbl_status)

        self.lbl_updated = QLabel("")
        self.lbl_updated.setStyleSheet("font-size: 12px; color: #94A3B8; font-weight: 500; margin-left: 10px;")

        footer.addWidget(self.status_pill)
        footer.addWidget(self.lbl_updated)
        footer.addStretch()

        lbl_credit = QLabel("Data provided by OpenWeatherMap  •  Atmos v2.0")
        lbl_credit.setStyleSheet("font-size: 12px; color: #6B7280;")
        footer.addWidget(lbl_credit)

        return footer

    def auto_detect_location(self):
        """Triggers IP location detection in a background thread."""
        self.hide_error()
        self.show_loading("Detecting your location from IP...")

        self.loc_worker = DetectLocationWorker()
        self.loc_worker.locationDetected.connect(self._on_location_detected)
        self.loc_worker.detectionFailed.connect(self._on_location_detection_failed)
        self.loc_worker.start()

    def _on_location_detected(self, location_str: str):
        self.hide_loading()
        self.search_widget.input_field.setText(location_str)
        self.fetch_weather(location_str)

    def _on_location_detection_failed(self, error_msg: str):
        self.hide_loading()
        default_city = Config.DEFAULT_CITY
        self.fetch_weather(default_city)

    def fetch_weather(self, location: str, force_refresh: bool = False):
        """Triggers weather fetching in a background worker thread."""
        valid, msg = validate_location_query(location)
        if not valid:
            self.show_error(msg)
            return

        self.hide_error()
        self.current_location = location.strip()
        self.show_loading(f"Fetching weather data for '{self.current_location}'...")

        self.weather_worker = FetchWeatherWorker(
            self.weather_service, self.current_location, self.current_units, force_refresh
        )
        self.weather_worker.dataFetched.connect(self._on_weather_fetched)
        self.weather_worker.errorOccurred.connect(self._on_weather_error)
        self.weather_worker.start()

    def refresh_weather(self):
        """Refreshes weather for currently displayed location."""
        if self.current_location:
            self.fetch_weather(self.current_location, force_refresh=True)
        else:
            self.auto_detect_location()

    def _on_weather_fetched(self, data: Dict[str, Any]):
        self.hide_loading()
        self.cached_payload = data
        self._populate_dashboard(data)

    def _on_weather_error(self, error_msg: str):
        self.hide_loading()
        self.show_error(error_msg)

    def _on_unit_changed(self, new_unit: str):
        """Switches temperature units (°C <-> °F) instantly without hitting API."""
        self.current_units = new_unit
        if self.cached_payload:
            self.cached_payload["units"] = new_unit
            self._populate_dashboard(self.cached_payload)

    def _populate_dashboard(self, data: Dict[str, Any]):
        """Populates all dashboard cards and updates UI controls."""
        self.empty_state.hide()

        # Update Hero Weather Card
        self.hero_card.update_data(data, self.current_units)
        self.hero_card.show()

        # Populate Next 6-Hour Forecast Section
        self._clear_layout(self.hourly_cards_layout)
        hourly_list = data.get("next_6h_forecast", [])
        for item in hourly_list:
            temp_str = f"{item['temp_f']}°F" if self.current_units == "imperial" else f"{item['temp_c']}°C"
            card = HourlyForecastCard(item["time"], item["icon"], temp_str, item.get("pop", 0))
            self.hourly_cards_layout.addWidget(card)
        self.hourly_container.show()

        # Populate 5-Day Forecast Section
        self._clear_layout(self.daily_cards_layout)
        daily_list = data.get("five_day_forecast", [])
        for item in daily_list:
            if self.current_units == "imperial":
                hi_str = f"{item['high_f']}°"
                lo_str = f"{item['low_f']}°"
            else:
                hi_str = f"{item['high_c']}°"
                lo_str = f"{item['low_c']}°"
            
            card = DailyForecastCard(
                item["day"], item["icon"], hi_str, lo_str, item["condition"], item.get("pop", 0)
            )
            self.daily_cards_layout.addWidget(card)
        self.daily_container.show()

        # Populate Weather Details Grid Section
        self._clear_layout(self.details_grid_layout)
        metrics = [
            ("💧", "Humidity", f"{data['humidity']}%", data['humidity_comfort']),
            ("💨", "Wind Speed", f"{data['wind_speed']} m/s" if self.current_units == "metric" else f"{data['wind_speed']} mph", "Surface wind"),
            ("⏲️", "Atmospheric Pressure", f"{data['pressure_hpa']} hPa", "Normal sea level"),
            ("👁️", "Visibility", f"{data['visibility_km']} km", "Clear line of sight"),
            ("🌡️", "Feels Like", f"{round(data['feels_like_f'] if self.current_units == 'imperial' else data['feels_like_c'])}°", "Apparent temp"),
            ("☁️", "Cloud Coverage", f"{data['cloudiness']}%", "Total sky cover"),
            ("🌅", "Sunrise", data['sunrise'], "Local morning"),
            ("🌇", "Sunset", data['sunset'], "Local evening")
        ]

        row, col = 0, 0
        for icon, title, val, sub in metrics:
            card = DetailCard(icon, title, val, sub)
            self.details_grid_layout.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        self.details_container.show()

        # Update Last Updated Footers
        last_updated = data.get("last_updated", "")
        self.lbl_updated.setText(f"Last updated: {last_updated}")
        self.lbl_status.setText("●  Live  •  Updated")

    def _clear_layout(self, layout):
        """Safely removes and deletes all widgets inside a QLayout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def show_loading(self, message: str):
        self.lbl_loading.setText(f"⏳  {message}")
        self.lbl_loading.show()
        self.search_widget.set_loading(True)

    def hide_loading(self):
        self.lbl_loading.hide()
        self.search_widget.set_loading(False)

    def show_error(self, message: str):
        self.lbl_error.setText(f"⚠️  {message}")
        self.error_banner.show()

    def hide_error(self):
        self.error_banner.hide()
