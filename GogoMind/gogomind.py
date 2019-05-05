#!/usr/bin/env python3

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import traceback

from core import *

from model import Command, AddComponentCommand, EditComponentCommand, DeleteComponentCommand
from model import MindMapModel, CommandManager
from model import Component, Root, Node

import os
import sys

import math

class State(abc.ABC):
    
    def __init__(self):
        self._context = None

    def set_context(self, context) -> None:
        self._context = context

    @abc.abstractmethod
    def mouse_press_event(self) -> None:
        print(str(self.__class__) + " mouse_press_event") 

class PointerState(State):

    def mouse_press_event(self, node_id: int) -> None:
        super().mouse_press_event()

class EditState(State):

    def mouse_press_event(self, node_id: int) -> None:
        super().mouse_press_event()
        title = "Edit Node {}'s description".format(node_id)
        desc, okPressed = QInputDialog.getText(self._context.main_window, title, "Node description:", QLineEdit.Normal, "")
        if (desc):
            try:
                self._context.command_manager.execute(EditComponentCommand(node_id, desc))
                self._context.main_window.draw()
            except Exception as e:
                traceback.print_exc()

class DeleteState(State):

    def mouse_press_event(self, node_id: int) -> None:
        super().mouse_press_event()
        title = "Delete Node"
        message = "Do you want to delete Node {}?".format(node_id)
        reply = QMessageBox.information(self._context.main_window, 
                title,
                message,
                QMessageBox.Yes | QMessageBox.No)
        if (node_id != None and reply == QMessageBox.Yes):
            try:
                self._context.command_manager.execute(DeleteComponentCommand(node_id))
                self._context.main_window.draw()
            except Exception as e:
                traceback.print_exc()

class PresentationModel:

    def __init__(self, main_window, command_manager: CommandManager):
        self._state = None
        self.state = PointerState()
        self._command_manager = command_manager
        self._main_window =  main_window

    @property
    def command_manager(self) -> CommandManager:
        return self._command_manager

    @property
    def main_window(self):
        return self._main_window

    @property
    def state(self) -> State:
        return self._state
    
    @state.setter
    def state(self, state) -> None:
        print("set state as " + str(state.__class__))
        self._state = state
        self._state.set_context(self)

    def mouse_press_event(self, id: int) -> None:
        print(str(self.__class__) + " mouse_press_event")
        print("selected node {}".format(id))
        self._state.mouse_press_event(id)


class MapEdge(QGraphicsItem):

    def __init__(self, src_node: Component, dest_node: Component):
        super(MapEdge,self).__init__()
        self._src_node = src_node
        self._dest_node = dest_node
        self._src_point = None
        self._dest_point = None
        self.adjust() 

        
    def adjust(self):
        if not self._src_node or not self._dest_node:
            return
        src_center = self._src_node.ellipsisCenter()
        dest_center = self._dest_node.ellipsisCenter()
        line=QLineF(self.mapFromItem(self._src_node, src_center.x(), src_center.y()), \
                        self.mapFromItem(self._dest_node, dest_center.x(), dest_center.y()))
        length = line.length()

        self.prepareGeometryChange()

        if length > 20.0:
            offset = QPointF((line.dx() *10 ) / length,(line.dy() * 10) / length)
            self._src_point = line.p1() + offset
            self._dest_point = line.p2() - offset
        else:
            self._src_point = self._dest_point = line.p1()

    def boundingRect(self):
        if not self._src_node or not self._dest_node: return QRectF()
        return QRectF(self._src_point, QSizeF(self._dest_point.x() - self._src_point.x(),
                                              self._dest_point.y() - self._src_point.y())).normalized()

    def paint(self,painter, option=None, widget=None):
        """Paint edge on a scene"""
        if not self._src_node or not self._dest_node: return QRectF()
        line = QLineF(self._src_point, self._dest_point)
        if (line.length() == 0.0): return
        color = QColor(Qt.black)
        painter.setPen(QPen(color,1,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        painter.drawLine(line)

        # if not self.visible: color=QColor(Qt.green)


class MapItem(QGraphicsItem):
    HEIGHT = 100
    WIDTH = 200

    def __init__(self, x, y, id, desc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.desc = desc
        self._id = id
        self.rect = QRectF(x, y, self.WIDTH, self.HEIGHT)
        self.setZValue(10)
        self._selected = False

    @property
    def id(self) -> int:
        return self._id

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value

    def paint(self, QPainter: QPainter, QStyleOptionGraphicsItem, widget=None):
        if self._selected:
            QPainter.setPen(QColor(Qt.red))
        QPainter.fillRect(self.rect, QBrush(Qt.white))
        QPainter.drawRect(self.rect)
        QPainter.drawText(self.rect, Qt.AlignCenter, self.desc)

    def boundingRect(self):
        return self.rect

    def ellipsisCenter(self):
        return self.boundingRect().center()

    def __repr__(self):
        return '<MapItem: %s>' % self.desc


class MapScene(QGraphicsScene):

    _selected_item = None
    _presentation_model = None

    @property
    def selected_item(self):
        return self._selected_item

    def set_presentation_model(self, model) -> None:
        self._presentation_model = model

    def mousePressEvent(self, QGraphicsSceneMouseEvent):
        point: QPointF = QGraphicsSceneMouseEvent.scenePos()
        item = self.itemAt(point.x(), point.y(), QTransform())
        print(point)
        print(item)
        self.reset()

        if (item and isinstance(item, MapItem)):
            item._selected = True
            self._selected_item = item
            self.update()
            self._presentation_model.mouse_press_event(self._selected_item.id)

    def reset(self) -> None:
        if (self._selected_item):
            self._selected_item.selected = False
            self._selected_item = None
            self.update()


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.scene = MapScene()
        self.scene_view = QGraphicsView(self.scene)
        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

        layout.addWidget(self.scene_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        file_toolbar = QToolBar("File")
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Open file...", self)
        open_file_action.setStatusTip("Open file")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join('images', 'disk.png')), "Save", self)
        save_file_action.setStatusTip("Save current page")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)

        edit_toolbar = QToolBar("Edit")
        edit_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(edit_toolbar)
        edit_menu = self.menuBar().addMenu("&Edit")

        undo_action = QAction(QIcon(os.path.join('images', 'arrow-curve-180-left.png')), "Undo", self)
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.undo)
        edit_toolbar.addAction(undo_action)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(os.path.join('images', 'scissors.png')), "Cut", self)
        cut_action.setStatusTip("Cut selected node")
        # cut_action.triggered.connect(self.editor.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(os.path.join('images', 'document-copy.png')), "Copy", self)
        copy_action.setStatusTip("Copy selected node")
        # copy_action.triggered.connect(self.editor.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(os.path.join('images', 'clipboard-paste-document-text.png')), "Paste", self)
        paste_action.setStatusTip("Paste from clipboard")
        # paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        selection_action = QAction(QIcon(os.path.join('images', 'selection.png')), "Selection", self)
        selection_action.setStatusTip("Selection State")
        selection_action.triggered.connect(self._pressed_selection_action)
        edit_toolbar.addAction(selection_action)
        edit_menu.addAction(selection_action)
        self._selection_action = selection_action

        edit_action = QAction(QIcon(os.path.join('images', 'icon_edit.png')), "Edit a node", self)
        edit_action.setStatusTip("Edit a node")
        # edit_action.triggered.connect(self.edit_node_dialog)
        edit_action.triggered.connect(self._pressed_edit_action)
        edit_toolbar.addAction(edit_action)
        edit_menu.addAction(edit_action)
        self._edit_action = edit_action

        delete_action = QAction(QIcon(os.path.join('images', 'deletion.png')), "Deletion", self)
        delete_action.setStatusTip("Deletion State")
        # delete_action.triggered.connect(self.delete_node_dialog)
        delete_action.triggered.connect(self._pressed_delete_action)
        edit_toolbar.addAction(delete_action)
        edit_menu.addAction(delete_action)
        self._delete_action = delete_action

        sibling_action = QAction(QIcon(os.path.join('images', 'parent.png')), "Sibling", self)
        sibling_action.setStatusTip("Add Sibling Node")
        sibling_action.triggered.connect(self._pressed_sibling_action)
        edit_toolbar.addAction(sibling_action)
        edit_menu.addAction(sibling_action)
        self._sibling_action = sibling_action

        child_action = QAction(QIcon(os.path.join('images', 'child.png')), "Child", self)
        child_action.setStatusTip("Add Child Node")
        child_action.triggered.connect(self._pressed_child_action)
        edit_toolbar.addAction(child_action)
        edit_menu.addAction(child_action)
        self._child_action = child_action

        insert_action = QAction(QIcon(os.path.join('images', 'plus.png')), "Insert a node", self)
        insert_action.setStatusTip("Insert a node")
        insert_action.triggered.connect(self._pressed_insert_node)
        edit_toolbar.addAction(insert_action)
        edit_menu.addAction(insert_action)

        self._mind_map = None
        self._command_manager = None
        self._presentation_model = None
        self._init_mind_map()

        self.scene.set_presentation_model(self._presentation_model)
        self.update_title()
        self.show()



    def _init_mind_map(self) -> None:
        self._mind_map = MindMapModel()
        self._command_manager = CommandManager(self._mind_map)
        self._presentation_model = PresentationModel(self, self._command_manager) 
        self._pressed_selection_action()
        self._insert_node(-1, "Root")

    def _pressed_delete_action(self):
        self._presentation_model.state = DeleteState()
        self._selection_action.setEnabled(False)
        self._edit_action.setEnabled(False)

    def _pressed_edit_action(self):
        self._presentation_model.state = EditState()
        self._selection_action.setEnabled(False)
        self._delete_action.setEnabled(False)

    def _pressed_selection_action(self):
        self._presentation_model.state = PointerState()
        self._edit_action.setEnabled(False)
        self._delete_action.setEnabled(False)

    def _pressed_child_action(self):
        state = self._is_pointer_state()
        if (state):
            node = self._get_selected_node()
            if (node):
                title = "Insert a child to Node {}".format(node.id)
                desc, okPressed = QInputDialog.getText(self, title, "Node description:", QLineEdit.Normal, "")
                self._insert_node(node.id, desc)

    def _pressed_sibling_action(self):
        state = self._is_pointer_state()
        if (state):
            node = self._get_selected_node()
            if (node):
                title = "Insert a sliging to Node {}".format(node.id)
                desc, okPressed = QInputDialog.getText(self, title, "Node description:", QLineEdit.Normal, "")
                self._insert_node(node.get_parent().id, desc)

    def _get_selected_node(self) -> Component:
        selected_item = self.scene.selected_item
        if (selected_item):
            return self._mind_map.get_node(selected_item.id)
        else:
            return None

    def _is_pointer_state(self) -> State:
        state = self._presentation_model.state
        if (isinstance(state, PointerState)):
            return state
        else:
            return None

    def _insert_node(self, pid: int, desc: str) -> None:
        print("<pid: {}, desc: {}>".format(pid, desc))
        if (pid != None and desc != None):
            try:
                self._command_manager.execute(AddComponentCommand(pid, desc))
                self.draw()
            except Exception as e:
                traceback.print_exc()

    def undo(self):
        if (self._command_manager.undo()):
            print("Undo succeed")
            self.draw()
        else:
            print("Undo Failed")

    def redo(self):
        if (self._command_manager.redo()):
            print("Redo succeed")
            self.draw()
        else:
            print("Redo Failed")

    def _pressed_insert_node(self):
        pid = -1
        desc = None
        if (self._mind_map.is_empty()):
            desc, okPressed = QInputDialog.getText(self, "Create a root", "Root description:", QLineEdit.Normal, "")
        else:
            pid, okPressed = QInputDialog.getText(self, "Insert a node", "Parent node ID:", QLineEdit.Normal, "")
            desc, okPressed = QInputDialog.getText(self, "Insert a node", "Node description:", QLineEdit.Normal, "")
        self._insert_node(pid, desc)

    def _reset(self):
        self._selection_action.setEnabled(True)
        self._edit_action.setEnabled(True)
        self._delete_action.setEnabled(True)
        self.scene.reset()

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "All Files (*);;GogoMind documents (*.ggm)")
        if (self._mind_map.load(path)):
            self.draw()
            self.path = path
            self.update_title()
            return True
        else:
            return False

    def file_save(self):
        if self.path is None:
            # If we do not have a path, we need to use Save As.
            return self.file_saveas()
        else:
            return self._mind_map.save(self.path)

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "GogoMind documents (*.ggm)")
        if not path:
            # If dialog is cancelled, will return ''
            return False
        else:
            if (self._mind_map.save(path)):
                self.path = path
                self.update_title()
                return True
            else:
                return False

    def update_title(self):
        self.setWindowTitle("%s - GogoMind" % (os.path.basename(self.path) if self.path else "Untitled"))

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Escape):
            print("Pressed ESC")
            self._reset()

    def draw(self):
        self.scene.clear()
        print("map: {}".format(self._mind_map.map))
        location_map = {}
        p = {}
        map = self._mind_map.map
        basic_r = 50
        center = (MapItem.WIDTH / 2, MapItem.HEIGHT / 2)
        for i, layer in enumerate(map):
            num_of_node = len(layer)
            for j, pair in enumerate(layer):
                node = self._mind_map.get_node(pair[0])
                if (node):
                    item = None
                    edge = None
                    if (len(location_map) == 0):
                        item = MapItem(0, 0, node.id,node.info)
                        location_map[node.id] = (0, 0, MapItem.WIDTH, MapItem.HEIGHT)
                    else:
                        pl = location_map[pair[1]]
                        print(pl)
                        left = pl[2] + 50 + ((50 + MapItem.WIDTH) * j)
                        top = pl[3] + 50 
                        right = left + MapItem.WIDTH
                        bottom = top + MapItem.HEIGHT
                        location_map[node.id] = (left, top, right, bottom)
                        item = MapItem(left, top, node.id, node.info)
                        edge = MapEdge(item, p[pair[1]])
                    p[node.id] = item
                    self.scene.addItem(item)
                    if (edge != None):
                        self.scene.addItem(edge)

    # def delete_node_dialog(self):
    #     id, okPressed = QInputDialog.getText(self, "Delete a node", "Node ID:", QLineEdit.Normal, "")
    #     if (id):
    #         try:
    #             id = int(id)
    #             self._command_manager.execute(DeleteComponentCommand(id))
    #             self.draw()
    #         except Exception as e:
    #             traceback.print_exc()

    # def edit_node_dialog(self):
    #     id, okPressed = QInputDialog.getText(self, "Edit a node", "Node ID:", QLineEdit.Normal, "")
    #     desc, okPressed = QInputDialog.getText(self, "Edit a node", "Node description:", QLineEdit.Normal, "")
    #     if (id and desc):
    #         try:
    #             id = int(id)
    #             self._command_manager.execute(EditComponentCommand(id, desc))
    #             self.draw()
    #         except Exception as e:
    #             traceback.print_exc()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("GogoMind")

    window = MainWindow()
    window.resize(900, 600)
    window.setWindowIcon(QIcon(os.path.join('images', 'icon.png')))
    app.exec_()
