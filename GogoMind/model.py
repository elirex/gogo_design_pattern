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
        
   
    @property
    def id(self) -> int:
        return self._id

   
    @property
    def desc(self) -> str:
        return self._desc

    
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


    def get_node(self, id: int) -> Component:
        if (not id in self._components):
            return None
        else:
            return self._components[id]

    @property
    def root(self) -> Root:
        return self._root

    def is_empty(self) -> bool:
        return self._root == None

    def create_mind_map(self, desc:str) -> bool:
        if (self._root):
            print("MidMapModel", "Root existent")
            return False
        else:
            self._root = self.create_node(desc)
            print("Create MidMapModel")
            return self.insert_node(self.create_node(desc), None)
            # return self.insert_node(self._root, None)

    def create_node(self, desc:str) -> Component:
        self._serial_ids += 1
        return self._create_node(self._serial_ids, desc)

    def _create_node(self, id:int, desc:str) -> Component:
        type = COMPONENT_TYPE_ROOT if (id == 0) else COMPONENT_TYPE_NODE
        return SimpleNodeFactory.create_node(type, id, desc)

    def insert_node(self, node: Component, pid:int) -> bool:
        if (isinstance(node, Root)):
            if (self._root):
                raise Exception("Root exists.")
                return False
            else:
                self._root = node
        else:
            if (not node): 
                raise Exception("Node must by not None.")
                return False
            if (pid not in self._components): 
                raise Exception("Parent not exists.")
                return False
            if (node.id in self._components): 
                raise Exception("Node({}) exists.".format(node.id))
                return False
            parent = self._components[pid]
            parent.add_child(node)
            node.set_parent(parent)

        self._components[node.id] = node
        return True

    @property
    def map(self) -> List[List[int]]:
        def traversal(root: Component, level: int, result: List[List[int]]) -> None:
            if (not root): return
            if (level >= len(result)): result.append([])
            parent = root.get_parent()
            pid = parent.id if (parent) else -1
            pair = (root.id, pid)
            result[level].append(pair)
            for child in root.get_childern():
                traversal(child, level + 1, result)

        result = []
        if (self._root == None):
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

    def load(self, path: str) -> bool:
        if (os.path.exists(path)):
            try:
                with open(path, 'r') as file:
                    data = json.load(file)
                print("Load", path, data)
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


