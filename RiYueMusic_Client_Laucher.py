# RiYueMusic_Client_Launcher.py
from RiYueMusic_Client.ui.main_window import MainWindow
import sys
from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()