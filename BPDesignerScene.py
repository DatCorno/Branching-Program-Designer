from PySide2.QtWidgets import (QGraphicsScene, QGraphicsLineItem, QGraphicsSceneMouseEvent)
from PySide2.QtGui import (QKeyEvent, QPen, Qt)
from PySide2.QtCore import (QPoint, QPointF, QLineF)

import PySide2

from utils import (LinkType, NodeType, getOfType)
from NodeItem import NodeItem
from ArrowItem import ArrowItem
from Graph import Graph
from FileInterface import FileInterface


class BPDesignerScene(QGraphicsScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_node_index = 1
        self.grid_size = 40
        self.current_link_type = LinkType.OneLink
        self.current_node_type = NodeType.Normal
        self.line = None
        self.draw_background = True
        self.graph = Graph()

    def drawBackground(self, painter: PySide2.QtGui.QPainter, rect: PySide2.QtCore.QRectF):
        if not self.draw_background:
            return

        pen = QPen()
        painter.setPen(pen)

        left = int(rect.left()) - int(rect.left() % self.grid_size)
        top = int(rect.top()) - int(rect.top() % self.grid_size)

        points = []
        for x in range(left, int(rect.right()), self.grid_size):
            for y in range(top, int(rect.bottom()), self.grid_size):
                points.append(QPoint(x, y))

        painter.drawPoints(points)

    def mouseDoubleClickEvent(self, event: PySide2.QtWidgets.QGraphicsSceneMouseEvent):
        super().mouseDoubleClickEvent(event)

        if not event.isAccepted():
            if event.button() == Qt.LeftButton:
                pos = event.scenePos()
                x_value = round(pos.x() / self.grid_size) * self.grid_size
                y_value = round(pos.y() / self.grid_size) * self.grid_size

                node = self.addNode(QPointF(x_value, y_value), self.current_node_index, self.current_node_type)

                self.graph.insertNode(node.id)
                self.current_node_index += 1
                self.current_node_type = NodeType.Normal

    def addNode(self, point: QPointF, _id: int, node_type: int):
        item = NodeItem(point, _id, node_type)
        self.addItem(item)
        return item

    def mousePressEvent(self, event: PySide2.QtWidgets.QGraphicsSceneMouseEvent):
        if event.button() == Qt.RightButton:
            start = event.scenePos()
            line = QLineF(start, start)
            self.line = QGraphicsLineItem()
            self.line.setLine(line)
            self.line.setPen(QPen(Qt.black, 3))
            self.addItem(self.line)

        super(BPDesignerScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: PySide2.QtWidgets.QGraphicsSceneMouseEvent):
        if self.line is not None:
            _pos = event.scenePos()

            end_items = self.topLevel(_pos)

            if len(end_items):
                if type(end_items[0]) is NodeItem:
                    item = end_items[0]
                    _pos = item.scenePos()

            new_line = QLineF(self.line.line().p1(), _pos)
            self.line.setLine(new_line)

        super(BPDesignerScene, self).mouseMoveEvent(event)

    def topLevel(self, pos):
        top_levels = []
        for item in self.items(pos):
            if self.line != item:
                if type(item) is NodeItem:
                    top_levels.append(item)

        return top_levels

    def deleteSelectedItem(self):
        selected_items = self.selectedItems()

        for item in selected_items:
            if type(item) is ArrowItem:
                self.removeItem(item)
                item.start.removeArrow(item)
                item.end.removeArrow(item)

        selected_items = self.selectedItems()

        for item in selected_items:
            if type(item.parentItem()) is NodeItem:
                self.deleteNode(item)
            elif type(item) is NodeItem:
                self.deleteNode(item)

    def deleteNode(self, item):
        item.removeArrows()
        self.removeItem(item)

    def deleteLine(self):
        self.removeItem(self.line)
        self.line = None

    def mouseReleaseEvent(self, event: PySide2.QtWidgets.QGraphicsSceneMouseEvent):
        if self.line is not None:
            start_items = self.topLevel(self.line.line().p1())
            end_items = self.topLevel(self.line.line().p2())

            self.deleteLine()

            if len(start_items) and len(end_items):
                start = start_items[0]
                end = end_items[0]

                if start.node_type != NodeType.No and start.node_type != NodeType.Yes:
                    if start != end:
                        if self.graph.insertEdge(start.id, end.id):
                            self.addArrow(start, end, self.current_link_type)

        super(BPDesignerScene, self).mouseReleaseEvent(event)

    def addArrow(self, start, end, link_type):
        arrow = ArrowItem(start, end, link_type)

        start.addArrow(arrow)
        end.addArrow(arrow)
        arrow.setZValue(-1000)
        self.addItem(arrow)

        return arrow

    def keyPressEvent(self, event: PySide2.QtGui.QKeyEvent):
        key = event.key()

        if key == Qt.Key_0:
            self.current_link_type = LinkType.ZeroLink
        elif key == Qt.Key_1:
            self.current_link_type = LinkType.OneLink
        elif key == Qt.Key_Delete:
            self.deleteSelectedItem()
        elif key == Qt.Key_Y:
            self.current_node_type = NodeType.Yes
        elif key == Qt.Key_N:
            self.current_node_type = NodeType.No
        elif key == Qt.Key_H:
            self.draw_background = not self.draw_background
            self.update()

        super().keyPressEvent(event)

    def loadGraph(self, filename):
        fi = FileInterface(filename)
        json = fi.fromJson()

        graph = Graph()
        self.clear()

        self.current_node_index = -1

        nodes = dict()

        for node in json["nodes"]:
            id = node["id"]
            pos_t = node["position"]
            pos_p = QPointF(pos_t[0], pos_t[1])
            text = node["text"]
            node_type = node["node_type"]
            node_item = self.addNode(pos_p, id, node_type)
            node_item.text.setPlainText(text)
            nodes[id] = node_item
            graph.insertNode(id)

            if self.current_node_index < id + 1:
                self.current_node_index = id + 1

        for edge in json["edges"]:
            start = edge["start"]
            end = edge["end"]
            link_type = edge["link_type"]
            arc_mode = edge["arc_mode"]

            arrow = self.addArrow(nodes[start], nodes[end], link_type)
            graph.insertEdge(start, end)
            arrow.arc_mode = arc_mode

            if arc_mode:
                pos = edge["current_arc_point"]
                arrow.current_arc_point = QPointF(pos[0], pos[1])
                arrow.updatePosition()

        self.graph = graph

    def saveGraph(self, filename):
        fi = FileInterface(filename)

        fi.toJson(self.getNodes(), self.getEdges())

    def getNodes(self):
        return getOfType(self.items(), NodeItem)

    def getEdges(self):
        return getOfType(self.items(), ArrowItem)
