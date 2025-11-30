import sys

from PySide6.QtWidgets import QApplication

import Jiv_logic
import Jiv_adapter
import Jiv_gui


class JIVMain:
    def __init__(self):
        app = QApplication(sys.argv)

        logic = Jiv_logic.JIVLogic()
        adapters = Jiv_adapter.AdapterManager(logic)
        gui = Jiv_gui.MainWindow(adapters)

        gui.show()
        # adapter.start()

        sys.exit(app.exec())



if __name__ == "__main__":
    JIVMain()
