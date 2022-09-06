import sys

from PyQt6.QtWidgets import QApplication

from main import MainWindow


class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r',  encoding='UTF-8') as file:
            return file.read()

app = QApplication(sys.argv)
window = MainWindow()

style_file = './style.qss'
style_sheet = QSSLoader.read_qss_file(style_file)
window.setStyleSheet(style_sheet)

window.show()
sys.exit(app.exec_())