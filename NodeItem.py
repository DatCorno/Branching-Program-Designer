from PySide2.QtWidgets import (QGraphicsEllipseItem, QGraphicsItem, QApplication)
from PySide2.QtGui import (Qt, QPen, QFont)
from PySide2.QtCore import (QPointF, QObject)
import PySide2
import typing

from utils import NodeType
from NodeTextItem import NodeTextItem


class NodeItem(QGraphicsEllipseItem):
    NODE_RADIUS = 40

    def __init__(self, pos, index, node_type):
        super(NodeItem, self).__init__(-self.NODE_RADIUS, -self.NODE_RADIUS, self.NODE_RADIUS * 2, self.NODE_RADIUS * 2)
        self.node_type = node_type
        self.id = index
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setPos(pos)
        self.arrows = []
        self.text = NodeTextItem("", self)

        if self.node_type == NodeType.Yes:
            self.default_pen = QPen(Qt.green, 3)
            node_text = "Yes"
            self.text.setEnabled(False)
        elif self.node_type == NodeType.No:
            self.default_pen = QPen(Qt.red, 3)
            node_text = "No"
            self.text.setEnabled(False)
        else:
            self.default_pen = QPen(Qt.black, 3)
            node_text = str(index)

        self.selected_pen = QPen(Qt.blue, 3)

        self.setPen(self.default_pen)
        self.setBrush(Qt.white)

        self.text.setPlainText(node_text)
        self.text.setFont(QFont("Helvetica", 14))
        self.text.resizeText()

    def paint(self, painter:PySide2.QtGui.QPainter, option:PySide2.QtWidgets.QStyleOptionGraphicsItem, widget:typing.Optional[PySide2.QtWidgets.QWidget]=...):
        if self.isSelected():
            self.setPen(self.selected_pen)
        else:
            self.setPen(self.default_pen)

        super(NodeItem, self).paint(painter, option, widget)

    def removeArrow(self, arrow):
        self.arrows = list(filter(arrow.__ne__, self.arrows))

    def removeArrows(self):
        for arrow in self.arrows:
            arrow.start.removeArrow(arrow)
            arrow.end.removeArrow(arrow)
            self.scene().removeItem(arrow)

        self.arrows = []

    def addArrow(self, arrow):
        self.arrows.append(arrow)

    def itemChange(self, change:PySide2.QtWidgets.QGraphicsItem.GraphicsItemChange, value:typing.Any) -> typing.Any:
        if change == QGraphicsItem.ItemPositionChange and self.scene() is not None:
            new_pos = value

            if QApplication.mouseButtons() == Qt.LeftButton:
                grid_pos = self.getClosestPointOnGrid(new_pos)
                self.updateArrowsPosition()
                return grid_pos
            else:
                self.updateArrowsPosition()
                return new_pos

        else:
            return super().itemChange(change, value)

    def updateArrowsPosition(self):
        for arrow in self.arrows:
            arrow.updatePosition()

    def getClosestPointOnGrid(self, pos: QPointF):
        grid_size = self.scene().grid_size

        x_value = round(pos.x() / grid_size) * grid_size
        y_value = round(pos.y() / grid_size) * grid_size

        return QPointF(x_value, y_value)