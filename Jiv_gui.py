from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QLabel


class MainWindow(QMainWindow):
    def __init__(self, adapter):
        super().__init__()
        self.initialization_window()
        self.adapter = adapter

        # Set central widget
        self.main_widget = MainWidget(adapter)
        self.setCentralWidget(self.main_widget)




    def closeEvent(self, event):
        self.adapter.stop_all()
        event.accept()

    def initialization_window(self):
        self.setWindowTitle("Jiv test")
        self.setMinimumSize(960, 540)
        self.resize(960, 540)


class MainWidget(QWidget):
    def __init__(self, adapter):
        super().__init__()
        self.adapter = adapter
        self.init_ui()

        self.adapter.signal.connect(self.signal_handler)

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.label_studentmain_state = QLabel()

        self.label_studentmain_state.setText(f'Not detecting')

        main_layout.addWidget(self.label_studentmain_state)

        self.setLayout(main_layout)

    def signal_handler(self, name, value):
        print(f'Signal: {name}, {value}')
        match name:
            case 'MonitorWorker':
                self.set_studentmain_state(value)

    def set_studentmain_state(self, state):
        self.label_studentmain_state.setText(f'Studentmain state: {'not' if not state else ''} running')
