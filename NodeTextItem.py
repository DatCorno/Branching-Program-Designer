from PySide2.QtWidgets import (QGraphicsItem, QGraphicsTextItem)
from PySide2.QtCore import (Slot, QPointF, Qt, QObject)

import PySide2


class NodeTextItem(QGraphicsTextItem):

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.document().contentsChanged.connect(self.resizeText)

    def focusOutEvent(self, event:PySide2.QtGui.QFocusEvent):
        self.setTextInteractionFlags(Qt.NoTextInteraction)

        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def mouseDoubleClickEvent(self, event:PySide2.QtWidgets.QGraphicsSceneMouseEvent):
        self.setTextInteractionFlags(Qt.TextEditable)
        self.setFocus()

    @Slot()
    def resizeText(self):
        center = self.parentItem().boundingRect().center()
        circle_center = self.boundingRect().center()
        adjusted_pos = QPointF(center.x() - circle_center.x(), center.y() - circle_center.y())
        self.setPos(adjusted_pos)
