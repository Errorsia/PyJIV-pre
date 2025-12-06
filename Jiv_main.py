import sys

from PySide6.QtWidgets import QApplication

import Jiv_logic
import Jiv_adapter
import Jiv_gui
import Jiv_service


class JIVMain:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.logic = Jiv_logic.JIVLogic()
        self.gui = Jiv_gui.MainWindow()
        self.adapters = Jiv_adapter.AdapterManager(self.logic, self.gui)
        self.gui.adapter_signal_connect(self.adapters)

        self.gui.show()

        self.services = Jiv_service.ServiceManager(self.logic, self.gui)

        self.gui.close_event.connect(self.handle_close_event)

        # self.app.aboutToQuit.connect(self.handle_close_event)

        sys.exit(self.app.exec())

    def handle_close_event(self):
        self.adapters.stop_all()
        self.services.stop_all()


if __name__ == "__main__":
    JIVMain()
