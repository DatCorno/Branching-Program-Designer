from PySide2.QtWidgets import (QMainWindow, QHBoxLayout, QWidget, QFileDialog)
from PySide2.QtGui import (QPainter, Qt)

import PySide2

from BPDesignerScene import BPDesignerScene
from BPGraphicsView import BPGraphicsView


class BPDesigner(QMainWindow):

    def __init__(self):
        super().__init__()
        self.scene = BPDesignerScene(self)
        self.scene.setSceneRect(0, 0, 2500, 2500)

        layout = QHBoxLayout()

        self.view = BPGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)
        layout.addWidget(self.view)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)
        self.setWindowTitle("Branching Program Designer")

    def keyPressEvent(self, event:PySide2.QtGui.QKeyEvent):
        key = event.key()

        if event.modifiers() == Qt.ControlModifier:
            if key == Qt.Key_O:
                filename = QFileDialog.getOpenFileName(self, "Open file", "", "Files (*.json)")[0]
                if filename == "":
                    return

                self.scene.loadGraph(filename)
            elif key == Qt.Key_S:
                filename = QFileDialog.getSaveFileName(self, "Save file", "", "Files (*.json)")[0]
                if filename == "":
                    return
                self.scene.saveGraph(filename)