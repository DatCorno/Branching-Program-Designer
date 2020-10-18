from PySide2.QtWidgets import (QGraphicsView)
from PySide2.QtCore import (Qt)

import PySide2

class BPGraphicsView(QGraphicsView):

    def __init__(self, scene):
        QGraphicsView.__init__(self, scene)
        self.zoom_factor = 1.0015

    def wheelEvent(self, event:PySide2.QtGui.QWheelEvent):
        if event.modifiers() != Qt.ControlModifier:
            super().wheelEvent(event)
            return

        old_pos = self.mapToScene(event.position().toPoint())
        angle = event.angleDelta().y()
        factor = pow(self.zoom_factor, angle)
        self.scale(factor, factor)

        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos

        self.translate(delta.x(), delta.y())