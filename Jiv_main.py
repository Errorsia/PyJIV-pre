import sys

from PySide6.QtWidgets import QApplication

import Jiv_logic
import Jiv_adapter
import Jiv_gui
import Jiv_worker


class JIVMain:
    def __init__(self):
        app = QApplication(sys.argv)

        logic = Jiv_logic.JIVLogic()
        gui = Jiv_gui.MainWindow()
        adapters = Jiv_adapter.AdapterManager(logic, gui)
        gui.adapter_signal_connect(adapters)

        gui.show()

        jiv_worker = Jiv_worker.WorkerManager(logic, gui)

        sys.exit(app.exec())



if __name__ == "__main__":
    JIVMain()
