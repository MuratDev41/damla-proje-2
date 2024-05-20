import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class ConnectionPoint(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, component, is_input, scene):
        super().__init__(x, y, radius * 2, radius * 2)
        self.component = component
        self.is_input = is_input
        self.radius = radius
        self.setPen(QPen(Qt.black, 2))
        self.setBrush(QBrush(Qt.green if is_input else Qt.blue))
        scene.addItem(self)
        self.setZValue(2)  # Ensure connection points are above gates

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.orig_pos = self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_pos = self.orig_pos + event.scenePos() - event.lastScenePos()
            self.setPos(new_pos)
            self.update_connection()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)

    def update_connection(self):
        if self.is_input:
            self.scene().update_connection(self.component, self.pos())
        else:
            self.scene().update_connection(self.pos(), self.component)

class LogicGate(QGraphicsItem):
    def __init__(self, gate_type, x, y, scene):
        super().__init__()
        self.gate_type = gate_type
        self.setPos(x, y)
        self.inputs = [ConnectionPoint(100, 95, 5, self, is_input=True, scene=scene),
                       ConnectionPoint(100, 95, 5, self, is_input=True, scene=scene)]
        self.output = ConnectionPoint(50, 15, 5, self, is_input=False, scene=scene)
        self.label = QLabel(gate_type)
        scene.addWidget(self.label)
        self.label.move(x, y - 20)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)  # Ensure gates are above connections
        self.label_pos_offset = QPointF(0, -20)  # Offset for label position relative to gate

        # Adjust initial positions of nodes based on gate type
        if self.gate_type == "AND":
            self.inputs[0].setPos(-5, 10)
            self.inputs[1].setPos(-5, 20)
            self.output.setPos(50, 15)
        elif self.gate_type == "OR":
            self.inputs[0].setPos(-5, 10)
            self.inputs[1].setPos(-5, 20)
            self.output.setPos(50, 15)
        elif self.gate_type == "NOT":
            self.inputs[0].setPos(-5, 15)
            self.output.setPos(50, 15)

    def boundingRect(self):
        return QRectF(0, 0, 50, 30)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(Qt.white))
        if self.gate_type == "AND":
            painter.drawRect(0, 0, 50, 30)
            painter.drawLine(0, 10, 10, 10)
            painter.drawLine(0, 20, 10, 20)
        elif self.gate_type == "OR":
            painter.drawRect(0, 0, 50, 30)
            painter.drawEllipse(25, 5, 10, 20)
        elif self.gate_type == "NOT":
            painter.drawRect(0, 0, 50, 30)
            painter.drawLine(0, 15, 10, 5)
            painter.drawLine(0, 15, 10, 25)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.drag_start_pos = self.mapToScene(event.pos())
            self.orig_pos = self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.scenePos() - event.lastScenePos()
            new_pos = self.pos() + delta
            self.setPos(new_pos)
            self.label.move(QPoint(int(self.pos().x() + self.label_pos_offset.x()),
                                   int(self.pos().y() + self.label_pos_offset.y())))
            for point in self.inputs + [self.output]:
                point.setPos(point.pos() + delta)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)
            self.update()

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)

class CircuitDesigner(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.setWindowTitle("Circuit Designer")
        self.setGeometry(100, 100, 800, 600)

        self.add_and_button = QPushButton("Add AND Gate")
        self.add_and_button.clicked.connect(self.add_and_gate)
        layout.addWidget(self.add_and_button)

        self.add_or_button = QPushButton("Add OR Gate")
        self.add_or_button.clicked.connect(self.add_or_gate)
        layout.addWidget(self.add_or_button)

        self.add_not_button = QPushButton("Add NOT Gate")
        self.add_not_button.clicked.connect(self.add_not_gate)
        layout.addWidget(self.add_not_button)

        self.view.setMouseTracking(True)
        self.prev_item = None

    def add_and_gate(self):
        gate = LogicGate("AND", 100, 100, self.scene)
        self.scene.addItem(gate)

    def add_or_gate(self):
        gate = LogicGate("OR", 100, 100, self.scene)
        self.scene.addItem(gate)

    def add_not_gate(self):
        gate = LogicGate("NOT", 100, 100, self.scene)
        self.scene.addItem(gate)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircuitDesigner()
    window.show()
    sys.exit(app.exec_())
