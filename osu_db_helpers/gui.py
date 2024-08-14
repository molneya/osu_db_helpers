
import sys
from PySide6.QtWidgets import QApplication
from widget import OsuDbHelpersWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OsuDbHelpersWidget()
    window.show()
    sys.exit(app.exec())
