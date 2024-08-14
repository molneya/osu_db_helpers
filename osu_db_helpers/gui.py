
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from widget import OsuDbHelpersWidget

def main():
    app = QApplication(sys.argv)
    icon = os.path.join(os.path.dirname(__file__), "icon.ico")
    app.setWindowIcon(QIcon(icon))
    window = OsuDbHelpersWidget()
    window.show()
    app.exec()

if __name__ == "__main__":
    sys.exit(main())
