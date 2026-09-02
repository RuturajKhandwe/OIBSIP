"""
QSS Styling System for Atmos Real-Time Weather Dashboard
Modern Dark SaaS / Apple Weather Aesthetics
"""

MAIN_QSS = """
/* Global Window & Widget Defaults */
QWidget {
    font-family: 'Inter', 'Segoe UI', -apple-system, sans-serif;
    color: #F8FAFC;
    background-color: transparent;
}

QMainWindow {
    background-color: #0B1020;
}

/* ScrollArea Customization */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #0B1020;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.15);
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #6C63FF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Base Buttons */
QPushButton {
    background-color: #151D2E;
    color: #F8FAFC;
    border: 1px solid #22303D;
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1C273C;
    border-color: #6C63FF;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #111827;
}

/* Primary Action Buttons */
QPushButton#primaryBtn {
    background: linear-gradient(135deg, #6C63FF 0%, #5A51E0 100%);
    background-color: #6C63FF;
    color: #FFFFFF;
    font-weight: 600;
    border: none;
}

QPushButton#primaryBtn:hover {
    background-color: #5A51E0;
}

/* Location Auto Detect Button */
QPushButton#locationBtn {
    background-color: rgba(56, 189, 248, 0.1);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.3);
}

QPushButton#locationBtn:hover {
    background-color: rgba(56, 189, 248, 0.2);
    border-color: #38BDF8;
}

/* Refresh Button */
QPushButton#refreshBtn {
    background-color: rgba(255, 255, 255, 0.05);
    color: #94A3B8;
    border: 1px solid #22303D;
}

QPushButton#refreshBtn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #F8FAFC;
}

/* Search Line Edit Input */
QLineEdit#searchInput {
    background-color: #151D2E;
    color: #F8FAFC;
    border: 1px solid #22303D;
    border-radius: 12px;
    padding: 10px 16px;
    font-size: 14px;
}

QLineEdit#searchInput:focus {
    border-color: #6C63FF;
    background-color: #182338;
}

/* Segmented Temperature Unit Toggle Buttons */
QPushButton#unitBtnActive {
    background-color: #6C63FF;
    color: #FFFFFF;
    font-weight: 700;
    border: 1px solid #6C63FF;
    border-radius: 8px;
    padding: 6px 12px;
}

QPushButton#unitBtnInactive {
    background-color: rgba(255, 255, 255, 0.05);
    color: #94A3B8;
    font-weight: 500;
    border: 1px solid #22303D;
    border-radius: 8px;
    padding: 6px 12px;
}

QPushButton#unitBtnInactive:hover {
    color: #F8FAFC;
    background-color: rgba(255, 255, 255, 0.1);
}

/* Metric Detail & Forecast Cards Frame */
QFrame#cardFrame {
    background-color: #151D2E;
    border: 1px solid #22303D;
    border-radius: 14px;
}

QFrame#cardFrame:hover {
    border-color: rgba(108, 99, 255, 0.4);
}

/* Status Indicator Pill */
QFrame#statusPill {
    background-color: rgba(52, 211, 153, 0.12);
    border: 1px solid rgba(52, 211, 153, 0.3);
    border-radius: 12px;
    padding: 4px 10px;
}

QLabel#statusText {
    color: #34D399;
    font-size: 12px;
    font-weight: 600;
}

/* Error Banner Card */
QFrame#errorCard {
    background-color: rgba(248, 113, 113, 0.12);
    border: 1px solid rgba(248, 113, 113, 0.35);
    border-radius: 12px;
    padding: 12px 16px;
}

QLabel#errorText {
    color: #F87171;
    font-size: 13px;
    font-weight: 500;
}
"""
