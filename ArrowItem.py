from PySide2.QtWidgets import (QAbstractGraphicsShapeItem, QGraphicsItem, QGraphicsTextItem, QGraphicsEllipseItem)
from PySide2.QtGui import (QPen, Qt, QFont, QPainterPath, QPolygonF, QBrush, QTransform)
from PySide2.QtCore import (QRectF, QSizeF, QLineF, QPointF)
import PySide2

from utils import LinkType, det
from NodeItem import NodeItem

import math
import typing
import copy


class ArrowItem(QAbstractGraphicsShapeItem):

    def __init__(self, start, end, link_type):
        super().__init__()
        self.start = start
        self.end = end
        self.link_type = link_type
        self.line = None
        self.arrow_head = QPolygonF()
        self.arc_mode = False
        self.text = QGraphicsTextItem("", self)
        self.current_arc_point = QPointF()
        self.arc_object = None
        self.arc_start_angle = 0
        self.arc_span_angle = 0
        self.local_start_pos = QPointF()
        self.local_end_pos = QPointF()

        self.setFlags(QGraphicsItem.ItemIsSelectable)

        self.updatePosition()

        self.setPen(QPen(Qt.black, 2))
        self.default_pen = QPen(Qt.black, 3)
        self.selected_pen = QPen(Qt.blue, 3)

        self.createText()

    def createText(self):
        displayed_text = "1"

        if self.link_type == LinkType.ZeroLink:
            displayed_text = "0"

        self.text.document().setPlainText(displayed_text)
        self.text.setFont(QFont("Helvetica", 14))

    def boundingRect(self) -> PySide2.QtCore.QRectF:
        extra = (self.pen().width() + 20) / 2.0
        boundingRect = QRectF()

        if self.arc_mode and self.arc_object is not None:
            boundingRect = self.arc_object.boundingRect()
        else:
            boundingRect = QRectF(self.line.p1(), QSizeF(self.line.p2().x() - self.line.p1().x(),
                                  self.line.p2().y() - self.line.p1().y()))

        return boundingRect.normalized() \
            .adjusted(-extra, -extra, extra, extra)

    def shape(self) -> PySide2.QtGui.QPainterPath:
        path = QPainterPath(QPointF(0, 0))

        if self.arc_mode:
            path.arcTo(self.arc_object.boundingRect(), self.arc_start_angle, self.arc_span_angle)
        else:
            p2 = self.line.p2()
            mid_point = QPointF(p2.x() / 2, p2.y() / 2)

            path.lineTo(mid_point)
            path.addEllipse(mid_point, 5, 5)
            path.moveTo(mid_point)
            path.lineTo(p2)
            path.addPolygon(self.arrow_head)

        return path

    def updatePosition(self):
        # Here we set our position relative to the scene and we work in local coordinate with start's position
        # as our origin point.
        self.setPos(self.start.pos())

        self.prepareGeometryChange()
        self.line = QLineF(self.mapFromItem(self.start, 0, 0), self.mapFromItem(self.end, 0, 0))
        self.local_start_pos = self.mapFromScene(self.start.pos())
        self.local_end_pos = self.mapFromScene(self.end.pos())

        if self.arc_mode:
            self.findCircle()

        self.update()

    def mouseMoveEvent(self, event:PySide2.QtWidgets.QGraphicsSceneMouseEvent):
        pos = self.mapToItem(self, event.pos())
        path = self.calculateDragDeadZone()

        if not self.arc_mode:
            if not path.contains(pos):
                self.arc_mode = True
        else:
            self.current_arc_point = self.mapFromScene(event.scenePos())
            self.findCircle()
            if path.contains(pos):
                self.arc_mode = False
                self.arc_object = None

            self.update()

    def calculateDragDeadZone(self):
        drag_dead_zone = QPainterPath()
        drag_dead_zone.addRect(-5, 0, 10, self.line.length())

        transform = QTransform()
        transform.rotate(270 - self.line.angle())

        path = transform.map(drag_dead_zone)

        return path

    def findCircle(self):
        p1 = self.local_start_pos
        p2 = self.current_arc_point
        p3 = self.local_end_pos
        x1 = p1.x()
        x2 = p2.x()
        x3 = p3.x()
        y1 = p1.y()
        y2 = p2.y()
        y3 = p3.y()

        a = det(x1, y1, 1, x2, y2, 1, x3, y3, 1)
        bx = -det(x1 * x1 + y1 * y1, y1, 1, x2 * x2 + y2 * y2, y2, 1, x3 * x3 + y3 * y3, y3, 1)
        by = det(x1 * x1 + y1 * y1, x1, 1, x2 * x2 + y2 * y2, x2, 1, x3 * x3 + y3 * y3, x3, 1)
        c = -det(x1 * x1 + y1 * y1, x1, y1, x2 * x2 + y2 * y2, x2, y2, x3 * x3 + y3 * y3, x3, y3)

        x = -bx / (2 * a)
        y = -by / (2 * a)
        rad = math.sqrt(bx * bx + by * by - 4 * a * c) / (2 * abs(a))

        self.arc_object = QGraphicsEllipseItem(x - rad, y - rad, rad * 2, rad * 2)

        center = QPointF(x, y)
        lineOP1 = QLineF(center, p1)
        lineOP3 = QLineF(center, p3)

        if self.isPointBelow(p2):
            self.arc_start_angle = lineOP1.angle()

            if self.isPointBelow(center):
                self.arc_span_angle = lineOP3.angle() + 360 - self.arc_start_angle
            else:
                self.arc_span_angle = lineOP3.angle() - self.arc_start_angle
        else:
            self.arc_start_angle = lineOP3.angle()

            if self.isPointBelow(center):
                self.arc_span_angle = lineOP1.angle() - self.arc_start_angle
            else:
                self.arc_span_angle = lineOP1.angle() + 360 - self.arc_start_angle

    def isPointBelow(self, pos):
        slope = self.line.dy() / self.line.dx()

        return pos.y() > slope * pos.x()

    def paint(self, painter:PySide2.QtGui.QPainter, option:PySide2.QtWidgets.QStyleOptionGraphicsItem, widget:typing.Optional[PySide2.QtWidgets.QWidget]=...):
        if self.start.collidesWithItem(self.end):
            return

        painter.setBrush(self.brush())

        if self.isSelected():
            painter.setPen(self.selected_pen)
        else:
            painter.setPen(self.default_pen)

        if self.arc_mode:
            self.drawArc(painter)
        else:
            self.drawLine(painter)

    def drawArc(self, painter):
        path = QPainterPath()

        path.arcMoveTo(self.arc_object.boundingRect(), self.arc_start_angle)
        path.arcTo(self.arc_object.boundingRect(), self.arc_start_angle, self.arc_span_angle)

        painter.drawPath(path)

        text_pos = self.calculateTextPosition()
        self.text.setPos(text_pos)

    def drawLine(self, painter):
        # Calculate the intersection point between the line and the circle made by the end node
        intersection_point = self.calculateIntersectionPoint(self.line.p2(), NodeItem.NODE_RADIUS)
        drawn_line = copy.deepcopy(self.line)
        drawn_line.setP2(intersection_point)

        painter.drawLine(drawn_line)
        painter.setBrush(QBrush(Qt.white))

        arrow_size = 20.0
        angle = math.atan2(-self.line.dy(), self.line.dx())

        arrowP1 = drawn_line.p2() - QPointF(math.sin(angle + math.pi / 3) * arrow_size,
                                            math.cos(angle + math.pi / 3) * arrow_size)
        arrowP2 = drawn_line.p2() - QPointF(math.sin(angle + math.pi - math.pi / 3) * arrow_size,
                                            math.cos(angle + math.pi - math.pi / 3) * arrow_size)

        self.arrow_head.clear()
        self.arrow_head.push_back(arrowP1)
        self.arrow_head.push_back(intersection_point)
        self.arrow_head.push_back(arrowP2)

        painter.drawPolyline(self.arrow_head)

        text_pos = self.calculateTextPosition()
        self.text.setPos(text_pos)

    def calculateIntersectionPoint(self, center, radius):
        angle = self.line.angle()

        radians = math.radians(angle)
        circle = QPointF(radius * math.cos(radians), radius * -math.sin(radians))
        return center - circle

    def calculateTextPosition(self):
        if self.arc_mode:
            arc_bb = self.arc_object.boundingRect()

            if self.isPointBelow(self.current_arc_point):
                return QPointF(arc_bb.center().x(), arc_bb.bottomRight().y())
            else:
                return QPointF(arc_bb.center().x(), arc_bb.topRight().y())
        else:
            intersection_point = self.calculateIntersectionPoint(self.line.p2(), NodeItem.NODE_RADIUS)
            drawn_line = copy.deepcopy(self.line)
            drawn_line.setP2(intersection_point)
            x = drawn_line.p2().x() / 2
            y = drawn_line.p2().y() / 2

            angle = math.radians(self.line.angle())
            width = self.text.document().size().width()
            height = self.text.document().size().height()

            cos = math.cos(angle)
            sin = math.sin(angle)

            if cos > 0:
                width = 0

            if sin > 0:
                height = 0

            x -= width
            y -= height

            return QPointF(x, y)
