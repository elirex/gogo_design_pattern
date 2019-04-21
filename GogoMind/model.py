#!/usr/bin/env python3

from core import *
import os
import json

__all__ = ["Component", "Root", "Node"]

COMPONENT_TYPE_ROOT = 0
COMPONENT_TYPE_NODE = 1


class Component(abc.ABC):

    def __init__(self, id:int, desc:str):
        self._id = id
        self._desc = desc
        self._children = []
        self._siblings = []
        self._parent = None
        self._is_delete = False
    
    @property
    def is_delete(self) -> bool:
        return self._is_delete

    def delete(self, deleted: bool, with_child: bool=False) -> None:
        self._is_delete = deleted
        if (with_child):
            for child in self._children:
                child.delete(deleted, with_child)

    @property
    def id(self) -> int:
        return self._id
   
    @property
    def desc(self) -> str:
        return self._desc

    @desc.setter
    def desc(self, desc: str) -> None:
        self._desc = desc

    def get_parent(self) -> 'Component':
        return self._parent

    @abc.abstractmethod
    def add_child(self, node: 'Component') -> bool:
        if (node in self._children or self == node):
            return False
        else:
            self._children.append(node)
            return True


    @abc.abstractmethod
    def add_sibling(self, node: 'Component') -> bool:
        if (node in self._siblings or self == node):
            return False
        else:
            self._siblings.append(Component)
            return True

    
    @abc.abstractmethod
    def get_childern(self) -> List['Component']:
        return self._children

    
    @abc.abstractmethod
    def get_siblings(self) -> List['Component']:
        return self._siblings

   
    @abc.abstractmethod
    def set_parent(self, parent:'Component') -> bool:
        if (not self._parent and self != parent):
            self._parent = parent
            return True
        else:
            return False

    @property
    @abc.abstractmethod
    def info(self) -> Dict[str, str]:
        return {"desc": self._desc, "id": str(self._id)}


class Root(Component):

    def __init__(self, id:int, desc:str):
        super().__init__(id, desc)

    
    def add_child(self, node:Component) -> bool:
        if (isinstance(node, Node)):
            return super().add_child(node) 
        else:
            return False
        
    
    def add_sibling(self, node:Component) -> None:
        raise ValueError("Root cannot add sibling.")


    def get_childern(self) -> List[Component]:
        return super().get_childern()


    def get_siblings(self) -> None:
        raise ValueError("Root hasn't any siblings.")


    def set_parent(self, parent: Component) -> None:
        raise ValueError("Root hasn't the parent.")

    @property 
    def info(self) -> str:
        info = super().info
        info["type"] = "Root"
        return "{desc} <Id:{id}, Type:{type}>".format(**info)


class Node(Component):

    def __init__(self, id:int, desc:str):
        super().__init__(id, desc)


    def add_child(self, node:Component) -> bool:
        return super().add_child(node) 
        
    
    def add_sibling(self, node:Component) -> bool:
        return super().add_sibling(node)


    def get_childern(self) -> List[Component]:
        return super().get_childern()


    def get_siblings(self) -> List[Component]:
        return super().get_siblings()

    def set_parent(self, parent:Component) -> bool:
        return super().set_parent(parent)

    @property
    def info(self) -> str:
        info = super().info
        info["type"] = "Node"
        return "{desc} <Id:{id}, Type:{type}>".format(**info)


class MindMapModel:

    def __init__(self):
        self._root = None
        self._components = {}
        self._serial_ids = -1

    def increase_id(self) -> None:
        self._serial_ids += 1
    
    def decrease_id(self) -> None:
        self._serial_ids -= 1

    def get_node(self, id: int) -> Component:
        if (not id in self._components):
            return None
        else:
            node = self._components[id]
            if (node.is_delete):
                return None
            else:
                return self._components[id]

    @property
    def root(self) -> Root:
        return self._root

    def is_empty(self) -> bool:
        if (self._root == None or self._root.is_delete):
            return True
        else:
            return False

    def create_mind_map(self, desc:str) -> bool:
        if (self._root):
            print("MidMapModel", "Root existent")
            return False
        else:
            #self._root = self.create_node(desc)
            print("Create MidMapModel")
            return self.insert_node(self.create_node(desc))
            # return self.insert_node(self._root, None)

    def create_node(self, desc:str) -> Component:
        self.increase_id()
        return self._create_node(self._serial_ids, desc)

    def _create_node(self, id:int, desc:str) -> Component:
        type = COMPONENT_TYPE_ROOT if (id == 0) else COMPONENT_TYPE_NODE
        return SimpleNodeFactory.create_node(type, id, desc)

    def insert_node(self, node: Component, pid:int=None) -> bool:
        if (isinstance(node, Root)):
            if (self._root and not self._root.is_delete):
                raise Exception("Root exists.")
                return False
            else:
                self._root = node
        else:
            if (not node): 
                raise Exception("Node must by not None.")
                return False
            parent = self._components[pid]
            if (not parent):
                raise Exception("Parent not exists.")
                return False
            if (not self.get_node(node.id)):
                parent.add_child(node)
                node.set_parent(parent)
            else:
                raise Exception("Node({}) exists.".format(node.id))
                return False
        self._components[node.id] = node
        return True

    def remove_node(self, node: Component, with_child: bool=False) -> bool:
        if (node and not node.is_delete):
            node.delete(True, with_child)
            return True
        return False

    @property
    def map(self) -> List[List[int]]:
        def traversal(root: Component, level: int, result: List[List[int]]) -> None:
            if (not root): return
            if (level >= len(result)): result.append([])
            parent = root.get_parent()
            pid = parent.id if (parent) else -1
            pair = (root.id, pid)
            print(pair)
            result[level].append(pair)
            for child in root.get_childern():
                if (not child.is_delete):
                    traversal(child, level + 1, result)

        result = []
        if (self.is_empty()):
            return result
        traversal(self._root, 0, result)
        return result

    def save(self, path: str) -> bool:
        data = self._convert_to_json_format()
        print("Save", path, data)
        try:
            if (os.path.exists(path)):
                os.remove(path)
            with open(path, 'w') as file:
                json.dump(data, file)
            return True
        except Exception as e:
            print(e)
            print("Save failed")
            return False


    def _reset(self) -> None:
        self._root = None
        self._serial_ids = -1

    def load(self, path: str) -> bool:
        if (os.path.exists(path)):
            try:
                with open(path, 'r') as file:
                    data = json.load(file)
                print("Load", path, data)
                self._reset()
                self._build_from_json(data)
                return True
            except Exception as e:
                print("Load failed")
                print(e)
                return False
        else:
            return False

    def _convert_to_json_format(self) -> List:
        data = []
        for layer in self.map:
            for pair in layer:
                node = self._components[pair[0]]
                info = {}
                info["id"] = node.id
                info["desc"] = node.desc
                info["pid"] = pair[1]
                data.append(info)
        return data

    def _build_from_json(self, data: List) -> None:
        serial_ids = -1
        for obj in data:
            node = self._create_node(obj["id"], obj["desc"])
            print(node.info)
            if (self.insert_node(node, obj["pid"])):
                if (node.id > serial_ids): serial_ids = node.id
            else:
                raise Exception("Build mind map from JSON failed.")
        self._serial_ids = serial_ids
        print("Builded mind map from JSON.")
        print(self.map)


class SimpleNodeFactory:

    @staticmethod
    def create_node(type:int, id:int, desc:str) -> Component:
        if (type == COMPONENT_TYPE_ROOT):
            return Root(id, desc)
        else:
            return Node(id, desc)

class Command(abc.ABC):

    @abc.abstractmethod
    def execute(self, mind_map: MindMapModel) -> bool:
        return False

    @abc.abstractmethod
    def unexecute(self, mind_map: MindMapModel) -> bool:
        return False

class AddComponentCommand(Command):

    def __init__(self, pid: int, desc: str):
        self._pid = pid
        self._desc = desc
        self._node = None

    def execute(self, mind_map: MindMapModel) -> bool:
        if (self._node):
            self._node.delete(False)
            mind_map.increase_id()
            return True
        else:
            node = mind_map.create_node(self._desc)
            try:
                if (mind_map.insert_node(node, self._pid)):
                    self._node = node
                    print("Add {} node to map".format(node.info))
                    return True
                else:
                    print("Add {} node to map is failed".format(node.info))
            except Exception as e:
                print(e)
        return False

    def unexecute(self, mind_map: MindMapModel) -> bool:
        if (self._node):
            if (mind_map.remove_node(self._node)):
                mind_map.decrease_id()           
                return True
        return False


class EditComponentCommand(Command):

    def __init__(self, id: int, desc: str):
        self._id = id
        self._new_desc = desc

    def execute(self, mind_map: MindMapModel) -> bool:
        return self._edit(mind_map)
    
    def unexecute(self, mind_map: MindMapModel) -> bool:
        return self._edit(mind_map)

    def _edit(self, mind_map: MindMapModel) -> bool:
        node = mind_map.get_node(self._id)
        if (node):
            temp_desc = node.desc
            node.desc = self._new_desc
            self._new_desc = temp_desc
            print("Edited the description of the node ({}) ({} - > {})".format(self._id, self._new_desc, node.desc))
            return True
        else:
            print("Not found node ({})".format(self._id))
            return False


class DeleteComponentCommand(Command):
    
    def __init__(self, id: int):
        self._id = id
        self._node = None

    def execute(self, mind_map: MindMapModel) -> bool:
        node = mind_map.get_node(self._id)
        if (mind_map.remove_node(node, True)):
            self._node = node
            return True
        else:
            return False
    
    def unexecute(self, mind_map: MindMapModel) -> bool:
        if (self._node):
            self._node.delete(False, True)
            return True
        else:
            return False

class CommandManager:

    def __init__(self, mind_map: MindMapModel):
        self._mind_map = mind_map
        self._redo_commands = []
        self._undo_commands = []

    def execute(self, command: Command) -> bool:
        if (command):
            if (command.execute(self._mind_map)):
                self._redo_commands.clear()
                self._undo_commands.append(command)
                return True
        else:
            raise ValueError("Command should not be none.")
        return False

    def redo(self) -> bool:
        if (len(self._redo_commands) == 0):
            print("Redo list is empty")
        else:
            command = self._redo_commands.pop()
            if (command.execute(self._mind_map)):
                self._undo_commands.append(command)
                return True
        return False

    def undo(self) -> bool:
        if (len(self._undo_commands) == 0):
            print("Undo list is empty.")
        else:
            command = self._undo_commands.pop()
            if (command.unexecute(self._mind_map)):
                self._redo_commands.append(command)
                return True
        return False

    
