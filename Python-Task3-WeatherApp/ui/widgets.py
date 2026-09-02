from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QFont
from typing import Dict, Any

class SearchBarWidget(QWidget):
    """Search Bar Component containing Search Input, Search Button, and Auto-Location Button."""
    
    searchRequested = pyqtSignal(str)
    autoLocationRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Search Input Field
        self.input_field = QLineEdit()
        self.input_field.setObjectName("searchInput")
        self.input_field.setPlaceholderText("🔍  Search city name or ZIP code (e.g. Pune, London, 90210)...")
        self.input_field.setClearButtonEnabled(True)
        self.input_field.returnPressed.connect(self._on_search)

        # Search Action Button
        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("primaryBtn")
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.clicked.connect(self._on_search)

        # Auto Location Button
        self.location_btn = QPushButton("◎  Use My Location")
        self.location_btn.setObjectName("locationBtn")
        self.location_btn.setToolTip("Detect my approximate location using IP address")
        self.location_btn.setCursor(Qt.PointingHandCursor)
        self.location_btn.clicked.connect(self.autoLocationRequested.emit)

        layout.addWidget(self.input_field, stretch=4)
        layout.addWidget(self.search_btn, stretch=1)
        layout.addWidget(self.location_btn, stretch=2)

    def _on_search(self):
        text = self.input_field.text().strip()
        if text:
            self.searchRequested.emit(text)

    def set_loading(self, is_loading: bool):
        self.search_btn.setEnabled(not is_loading)
        self.location_btn.setEnabled(not is_loading)
        self.input_field.setEnabled(not is_loading)


class TempToggleWidget(QWidget):
    """Segmented Temperature Unit Toggle Control (°C / °F)."""
    
    unitChanged = pyqtSignal(str)

    def __init__(self, current_unit: str = "metric", parent=None):
        super().__init__(parent)
        self.current_unit = current_unit
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.btn_c = QPushButton("°C")
        self.btn_c.setCursor(Qt.PointingHandCursor)
        self.btn_c.setToolTip("Switch to Celsius")
        self.btn_c.clicked.connect(lambda: self.set_unit("metric"))

        self.btn_f = QPushButton("°F")
        self.btn_f.setCursor(Qt.PointingHandCursor)
        self.btn_f.setToolTip("Switch to Fahrenheit")
        self.btn_f.clicked.connect(lambda: self.set_unit("imperial"))

        layout.addWidget(self.btn_c)
        layout.addWidget(self.btn_f)
        self._update_styles()

    def set_unit(self, unit: str):
        if self.current_unit != unit:
            self.current_unit = unit
            self._update_styles()
            self.unitChanged.emit(self.current_unit)

    def _update_styles(self):
        if self.current_unit == "metric":
            self.btn_c.setObjectName("unitBtnActive")
            self.btn_f.setObjectName("unitBtnInactive")
        else:
            self.btn_c.setObjectName("unitBtnInactive")
            self.btn_f.setObjectName("unitBtnActive")
        
        self.btn_c.setStyle(self.btn_c.style())
        self.btn_f.setStyle(self.btn_f.style())


class HeroWeatherCard(QFrame):
    """Hero Component displaying Main Weather Information and Dynamic Atmospheric Glow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        
        # Left Info Column
        left_col = QVBoxLayout()
        left_col.setSpacing(6)

        self.lbl_location = QLabel("Pune, India")
        self.lbl_location.setStyleSheet("font-size: 24px; font-weight: 700; color: #F8FAFC;")

        self.lbl_temp = QLabel("28°C")
        self.lbl_temp.setStyleSheet("font-size: 72px; font-weight: 800; color: #F8FAFC; line-height: 1;")

        self.lbl_feels_like = QLabel("Feels like 30°C  •  High: 31°C  Low: 24°C")
        self.lbl_feels_like.setStyleSheet("font-size: 14px; color: #94A3B8; font-weight: 500;")

        self.lbl_condition = QLabel("Partly Cloudy")
        self.lbl_condition.setStyleSheet("font-size: 18px; color: #38BDF8; font-weight: 600; margin-top: 4px;")

        left_col.addWidget(self.lbl_location)
        left_col.addWidget(self.lbl_temp)
        left_col.addWidget(self.lbl_feels_like)
        left_col.addWidget(self.lbl_condition)
        left_col.addStretch()

        # Right Icon Column
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignCenter)

        self.lbl_icon = QLabel("☀️")
        self.lbl_icon.setStyleSheet("font-size: 96px; background: transparent;")
        self.lbl_icon.setAlignment(Qt.AlignCenter)

        right_col.addWidget(self.lbl_icon)

        layout.addLayout(left_col, stretch=3)
        layout.addLayout(right_col, stretch=2)

    def update_data(self, data: Dict[str, Any], units: str = "metric"):
        loc = data.get("location_display", "Unknown")
        self.lbl_location.setText(loc)

        if units == "imperial":
            temp_val = f"{round(data.get('temp_f', 0))}°F"
            feels_val = f"Feels like {round(data.get('feels_like_f', 0))}°F"
            hi_lo = f"High: {round(data.get('temp_max_f', 0))}°F  Low: {round(data.get('temp_min_f', 0))}°F"
        else:
            temp_val = f"{round(data.get('temp_c', 0))}°C"
            feels_val = f"Feels like {round(data.get('feels_like_c', 0))}°C"
            hi_lo = f"High: {round(data.get('temp_max_c', 0))}°C  Low: {round(data.get('temp_min_c', 0))}°C"

        self.lbl_temp.setText(temp_val)
        self.lbl_feels_like.setText(f"{feels_val}  •  {hi_lo}")
        
        cond_desc = data.get("condition_desc", "Clear")
        self.lbl_condition.setText(cond_desc)

        icon_symbol = data.get("icon_symbol", "🌤️")
        self.lbl_icon.setText(icon_symbol)

        # Apply Dynamic Hero Background Gradient
        bg_gradient = data.get("bg_gradient", "linear-gradient(135deg, rgba(108, 99, 255, 0.12) 0%, rgba(21, 29, 46, 0.95) 100%)")
        self.setStyleSheet(f"""
            QFrame#cardFrame {{
                background: {bg_gradient};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
            }}
        """)


class HourlyForecastCard(QFrame):
    """Individual Card Component for Next 6-Hour Forecast Interval."""

    def __init__(self, time_str: str, icon: str, temp_str: str, pop_pct: int = 0, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.init_ui(time_str, icon, temp_str, pop_pct)

    def init_ui(self, time_str: str, icon: str, temp_str: str, pop_pct: int):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        self.lbl_time = QLabel(time_str)
        self.lbl_time.setStyleSheet("font-size: 13px; font-weight: 600; color: #94A3B8;")
        self.lbl_time.setAlignment(Qt.AlignCenter)

        self.lbl_icon = QLabel(icon)
        self.lbl_icon.setStyleSheet("font-size: 28px;")
        self.lbl_icon.setAlignment(Qt.AlignCenter)

        self.lbl_temp = QLabel(temp_str)
        self.lbl_temp.setStyleSheet("font-size: 16px; font-weight: 700; color: #F8FAFC;")
        self.lbl_temp.setAlignment(Qt.AlignCenter)

        pop_text = f"💧 {pop_pct}%" if pop_pct > 0 else ""
        self.lbl_pop = QLabel(pop_text)
        self.lbl_pop.setStyleSheet("font-size: 11px; font-weight: 500; color: #38BDF8;")
        self.lbl_pop.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.lbl_time)
        layout.addWidget(self.lbl_icon)
        layout.addWidget(self.lbl_temp)
        layout.addWidget(self.lbl_pop)


class DailyForecastCard(QFrame):
    """Card Component for 5-Day Daily Forecast Summary."""

    def __init__(self, day_str: str, icon: str, high_str: str, low_str: str, condition: str, pop: int = 0, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.init_ui(day_str, icon, high_str, low_str, condition, pop)

    def init_ui(self, day_str: str, icon: str, high_str: str, low_str: str, condition: str, pop: int):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        lbl_day = QLabel(day_str)
        lbl_day.setStyleSheet("font-size: 14px; font-weight: 700; color: #F8FAFC;")
        lbl_day.setAlignment(Qt.AlignCenter)

        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 32px;")
        lbl_icon.setAlignment(Qt.AlignCenter)

        lbl_temps = QLabel(f"{high_str}  /  <span style='color:#94A3B8;'>{low_str}</span>")
        lbl_temps.setStyleSheet("font-size: 14px; font-weight: 600; color: #F8FAFC;")
        lbl_temps.setAlignment(Qt.AlignCenter)

        lbl_cond = QLabel(condition)
        lbl_cond.setStyleSheet("font-size: 12px; color: #94A3B8;")
        lbl_cond.setAlignment(Qt.AlignCenter)

        layout.addWidget(lbl_day)
        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_temps)
        layout.addWidget(lbl_cond)


class DetailCard(QFrame):
    """Metric Card Widget displaying weather metrics (Humidity, Wind, Pressure, Visibility, Sunrise, etc.)."""

    def __init__(self, icon: str, title: str, value: str, subtext: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.init_ui(icon, title, value, subtext)

    def init_ui(self, icon: str, title: str, value: str, subtext: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        header_layout = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 18px;")

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #94A3B8;")

        header_layout.addWidget(lbl_icon)
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()

        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC; margin-top: 4px;")

        self.lbl_subtext = QLabel(subtext)
        self.lbl_subtext.setStyleSheet("font-size: 12px; color: #6C63FF; font-weight: 500;")

        layout.addLayout(header_layout)
        layout.addWidget(self.lbl_value)
        if subtext:
            layout.addWidget(self.lbl_subtext)
        layout.addStretch()


class EmptyStateWidget(QFrame):
    """Hero Empty State Component displayed when no search has been performed."""

    searchRequested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 60, 40, 60)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        icon = QLabel("🌤️")
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignCenter)

        title = QLabel("Search for a City to Get Started")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #F8FAFC;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Get real-time weather conditions, atmospheric metrics, and 5-day forecasts.")
        subtitle.setStyleSheet("font-size: 14px; color: #94A3B8;")
        subtitle.setAlignment(Qt.AlignCenter)

        btn = QPushButton("Explore Pune Weather")
        btn.setObjectName("primaryBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.searchRequested.emit("Pune"))

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
