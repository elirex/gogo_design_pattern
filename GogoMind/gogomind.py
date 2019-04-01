#!/usr/bin/env python3

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from model import MindMapModel, Component, Root, Node
import os
import sys

import math


class MapItem(QGraphicsItem):
    HEIGHT = 100
    WIDTH = 200

    def __init__(self, x, y, desc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.desc = desc
        self.rect = QRectF(x, y, self.WIDTH, self.HEIGHT)
        self.setZValue(10)

    def paint(self, QPainter: QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.fillRect(self.rect, QBrush(Qt.white))
        QPainter.drawRect(self.rect)
        QPainter.drawText(self.rect, Qt.AlignCenter, self.desc)

    def boundingRect(self):
        return self.rect

    def __repr__(self):
        return '<MapItem: %s>' % self.desc


class MapScene(QGraphicsScene):

    def mousePressEvent(self, QGraphicsSceneMouseEvent):
        point: QPointF = QGraphicsSceneMouseEvent.scenePos()
        item = self.itemAt(point.x(), point.y(), QTransform())
        print(point)
        print(item)


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
        # undo_action.triggered.connect(self.editor.undo)
        edit_toolbar.addAction(undo_action)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Redo", self)
        redo_action.setStatusTip("Redo last change")
        # redo_action.triggered.connect(self.editor.redo)
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
        # selection_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(selection_action)
        edit_menu.addAction(selection_action)

        delete_action = QAction(QIcon(os.path.join('images', 'deletion.png')), "Deletion", self)
        delete_action.setStatusTip("Deletion State")
        # delete_action.triggered.connect(self.input_dialog)
        edit_toolbar.addAction(delete_action)
        edit_menu.addAction(delete_action)

        sibling_action = QAction(QIcon(os.path.join('images', 'parent.png')), "Sibling", self)
        sibling_action.setStatusTip("Add Sibling Node")
        # sibling_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(sibling_action)
        edit_menu.addAction(sibling_action)

        child_action = QAction(QIcon(os.path.join('images', 'child.png')), "Child", self)
        child_action.setStatusTip("Add Child Node")
        # child_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(child_action)
        edit_menu.addAction(child_action)

        insert_action = QAction(QIcon(os.path.join('images', 'plus.png')), "Insert a node", self)
        insert_action.setStatusTip("Insert a node")
        insert_action.triggered.connect(self.insert_node_dialog)
        edit_toolbar.addAction(insert_action)
        edit_menu.addAction(insert_action)


        self._mind_map = MindMapModel()

        self.update_title()
        self.show()

        ### Just for demo
        # root = MapItem(0, 0, 'Computer <Root, ID:0>')
        # node = MapItem(300, 0, 'OS <Node, ID:1>')
        # node2 = MapItem(300, 150, 'Network <Node, ID:2>')
        # line1 = QGraphicsLineItem(50, 50, 350, 50)
        # line2 = QGraphicsLineItem(200, 50, 300, 200)

        # node3 = MapItem(600, 0, 'MacOS <Node, ID:3>')
        # line3 = QGraphicsLineItem(350, 50, 600, 50)
        # self.scene.addItem(node3)
        # self.scene.addItem(line3)

        # self.scene.addItem(line1)
        # self.scene.addItem(line2)
        # self.scene.addItem(root)
        # self.scene.addItem(node)
        # self.scene.addItem(node2)
        ###

    def draw(self):
        # self.scene.clear()
        print("map: {}".format(self._mind_map.map))
        location_map = {}
        map = self._mind_map.map
        basic_r = 50
        center = (MapItem.WIDTH / 2, MapItem.HEIGHT / 2)
        for i, layer in enumerate(map):
            num_of_node = len(layer)
            for j, pair in enumerate(layer):
                node = self._mind_map.get_node(pair[0])
                if (node):
                    if (len(location_map) == 0):
                        item = MapItem(0, 0, node.info)
                        location_map[node.id] = (0, 0, MapItem.WIDTH, MapItem.HEIGHT)
                    else:
                        pl = location_map[pair[1]]
                        print(pl)
                        left = pl[2] + 50 + ((50 + MapItem.WIDTH) * j)
                        top = pl[3] + 50 
                        right = left + MapItem.WIDTH
                        bottom = top + MapItem.HEIGHT
                        location_map[node.id] = (left, top, right, bottom)
                        item = MapItem(left, top, node.info)
                    self.scene.addItem(item)



    def insert_node_dialog(self):
        if (self._mind_map.is_empty()):
            desc, okPressed = QInputDialog.getText(self, "Create a root", "Root description:", QLineEdit.Normal, "")
            if (desc):
                if (self._mind_map.create_mind_map(desc)):
                    print("Add {} node to map".format(self._mind_map.root.info)) 
            else:
                print("Descrption is empty.")
        else:
            pid, okPressed = QInputDialog.getText(self, "Insert a node", "Node ID:", QLineEdit.Normal, "")
            desc, okPressed = QInputDialog.getText(self, "Insert a node", "Node description:", QLineEdit.Normal, "")
            print("<pid: {}, desc: {}>".format(pid, desc))
            if (pid and desc):
                try:
                    pid = int(pid)
                    node = self._mind_map.create_node(desc)
                    if (self._mind_map.insert_node(node, pid)):
                        print("Add {} node to map".format(node.info))
                    else:
                        print("Add {} node to map is failed".format(node.info))
                except ValueError:
                   print("The parent id is not an integer!")
            else:
                print("The parent id o description is empty.")
        self.draw()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("GogoMind")

    window = MainWindow()
    window.resize(900, 600)
    window.setWindowIcon(QIcon(os.path.join('images', 'icon.png')))
    app.exec_()
