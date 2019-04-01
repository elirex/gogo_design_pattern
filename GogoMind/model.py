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
            print("MidMapModel", "Create", self._root.info)
            return self.insert_node(self._root, None)

    def create_node(self, desc:str) -> Component:
        # type = COMPONENT_TYPE_NODE if (self._root) else COMPONENT_TYPE_ROOT
        self._serial_ids += 1
        return self._create_node(self._serial_ids, desc)
        # return SimpleNodeFactory.create_node(type, self._serial_ids, desc)

    def insert_node(self, node: Component, pid:int) -> bool:
        if (isinstance(node, Root)):
            if (node.id in self._components): return False
        else:
            if (not node): return False
            if (pid not in self._components): return False
            if (node.id in self._components): return False
            parent = self._components[pid]
            parent.add_child(node)
            node.set_parent(parent)

        self._components[node.id] = node
        return True

    def _create_node(self, id:int, desc:str) -> Component:
        type = COMPONENT_TYPE_ROOT if (id == 0) else COMPONENT_TYPE_NODE
        return SimpleNodeFactory.create_node(type, id, desc)
        

    @property
    def map(self) -> List[List[int]]:
        def traversal(root: Component, level: int, result: List[List[int]]) -> None:
            if (not root): return
            if (level >= len(result)): result.append([])
            parent = root.get_parent()
            pid = parent.id if (parent) else -1
            pair = (root.id, pid)
            result[level].append(pair)
            # result[level].append((root.id, root.get_parent().id)
            for child in root.get_childern():
                traversal(child, level + 1, result)

        result = []
        if (self._root == None):
            return result
        traversal(self._root, 0, result)
        return result

    def save(self, path: str) -> bool:
        if (os.path.exists(path)):
            os.remove(path)
        data = []
        for id, node in self._components.items():
            node_info = {}
            node_info["id"] = node.id
            node_info["desc"] = node.desc
            parent = node.get_parent()
            if (parent):
                node_info["pid"] = parent.id
            else:
                node_info["pid"] = -1
            data.append(node_info)
        print("Save", path, data)
        try:
            with open(path, 'w') as file:
                json.dump(content, file)
            return True
        except:
            print("Save failed")
            return False

    def load(self, path: str) -> bool:
        if (os.path.exists(path)):
            try:
                with open(path, 'r') as file:
                    data = json.load(file)
                print("Load", path, data)
                self._build_map_from_json(data)
                return True
            except:
                print("Load failed")
                return False
        else:
            return False

    # TODO: Need to refactor
    def _build_map_from_json(self, data: List) -> None:
        self._serial_ids = -1
        for node_info in data:
          n = self._create_node(node_info["id"], node_info["desc"])
          if (isinstance(n, Root)):
              self._root = n
          self._components[n.id] = n
          if (n.id > self._serial_ids):
              self._serial_ids = n.id
        for node_info in data:
            if (node_info["pid"] != -1):
                n = self._components[node_info["id"]]
                p = self._components[node_info["pid"]]
                p.add_child(n)
                n.set_parent(p)
        print(self.map)


class SimpleNodeFactory:

    @staticmethod
    def create_node(type:int, id:int, desc:str) -> Component:
        if (type == COMPONENT_TYPE_ROOT):
            return Root(id, desc)
        else:
            return Node(id, desc)


