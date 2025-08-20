def get_dark_theme():
    return """
        QWidget {
            background-color: #2E2E2E;
            color: #FFF;
            font-family: "Malgun Gothic", sans-serif;
            font-size: 25px;
        }
        QMainWindow {
            background-color: #2E2E2E;
        }
        QStackedWidget {
            background-color: #2E2E2E;
        }
        QLabel {
            color: #FFFFFF;
        }
        QLabel#title_label {
            font-size: 42px;
            font-weight: bold;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #555555;
            color: #FFFFFF;
            border: 1px solid #777777;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:focus {
            outline: none;
        }
        QPushButton:hover {
            background-color: #777777;
        }
        QPushButton:pressed {
            background-color: #333333;
        }
        QLineEdit {
            background-color: #3D3D3D;
            color: #FFFFFF;
            border: 1px solid #555555;
            padding: 8px;
            border-radius: 5px;
        }
        QComboBox {
            background-color: #3D3D3D;
            color: #FFFFFF;
            border: 1px solid #555555;
            padding: 8px;
            border-radius: 5px;
        }
        QComboBox::drop-down {
            width: 20px;
        }
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 5px;
            text-align: center;
            background-color: #3D3D3D;
            color: #FFFFFF;
        }
        QProgressBar::chunk {
            background-color: #007BFF;
            border-radius: 5px;
        }
        QToolBar {
            background-color: #3D3D3D;
            border: none;
        }
    """

def get_light_theme():
    return """
        QWidget {
            background-color: #FFFFFF;
            color: #000000;
            font-family: "Malgun Gothic", sans-serif;
            font-size: 25px;
        }
        QMainWindow {
            background-color: #FFFFFF;
        }
        QStackedWidget {
            background-color: #FFFFFF;
        }
        QLabel {
            color: #000000;
        }
        QLabel#title_label {
            font-size: 42px;
            font-weight: bold;
            color: #000000;
        }
        QPushButton {
            background-color: #F0F0F0;
            color: #000000;
            border: 1px solid #DDDDDD;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:focus {
            outline: none;
        }
        QPushButton:hover {
            background-color: #E0E0E0;
        }
        QPushButton:pressed {
            background-color: #CCCCCC;
        }
        QLineEdit {
            background-color: #F0F0F0;
            color: #000000;
            border: 1px solid #DDDDDD;
            padding: 8px;
            border-radius: 5px;
        }
        QComboBox {
            background-color: #F0F0F0;
            color: #000000;
            border: 1px solid #DDDDDD;
            padding: 8px;
            border-radius: 5px;
        }
        QComboBox::drop-down {
            width: 20px;
        }
        QProgressBar {
            border: 1px solid #DDDDDD;
            border-radius: 5px;
            text-align: center;
            background-color: #F0F0F0;
            color: #000000;
        }
        QProgressBar::chunk {
            background-color: #007BFF;
            border-radius: 5px;
        }
        QToolBar {
            background-color: #F0F0F0;
            border: none;
        }
    """