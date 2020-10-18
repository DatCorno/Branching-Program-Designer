import sys

from PySide2.QtWidgets import (QApplication)

from BPDesigner import BPDesigner

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = BPDesigner()
    w.show()

    sys.exit(app.exec_())
