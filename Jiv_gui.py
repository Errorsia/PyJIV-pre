from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QLabel


class MainWindow(QMainWindow):
    close_event = Signal()
    def __init__(self):
        super().__init__()
        self.initialization_window()

        self.adapter = None

        # Set central widget
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)

    def closeEvent(self, event):
        self.close_event.emit()
        event.accept()

    def initialization_window(self):
        self.setWindowTitle("Jiv test")
        self.setMinimumSize(360, 480)
        self.resize(360, 480)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

    def adapter_signal_connect(self, adapter):
        self.adapter = adapter
        self.main_widget.adapter_signal_connect(adapter)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label_studentmain_state = None
        self.adapter = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.label_studentmain_state = QLabel()

        self.label_studentmain_state.setText(f'Not detecting')

        main_layout.addWidget(self.label_studentmain_state)

        self.setLayout(main_layout)

    def adapter_signal_connect(self, adapter):
        self.adapter = adapter
        self.adapter.ui_change.connect(self.signal_handler)

    def signal_handler(self, name, value):
        print(f'Signal: {name}, {value}')
        match name:
            case 'MonitorAdapter':
                self.set_studentmain_state(value)

    def set_studentmain_state(self, state):
        status = "not running" if not state else "running"
        self.label_studentmain_state.setText(f"Studentmain state: {status}")
