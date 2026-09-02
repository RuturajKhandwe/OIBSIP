import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import AtmosMainWindow
from config import Config

def main():
    """Main application entry point."""
    # Enable High DPI scaling for modern high-res displays
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName(Config.APP_NAME)
    app.setOrganizationName("OIBSIP")

    window = AtmosMainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
