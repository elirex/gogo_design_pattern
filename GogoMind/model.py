#!/usr/bin/env python3

from core import *

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
            return self.insert_node(self._root, -1)

    def create_node(self, desc:str) -> Component:
        type = COMPONENT_TYPE_NODE if (self._root) else COMPONENT_TYPE_ROOT
        self._serial_ids += 1
        return SimpleNodeFactory.create_node(type, self._serial_ids, desc)

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

    @property
    def map(self) -> List[List[int]]:
        def traversal(root: Component, level: int, result: List[List[int]]) -> None:
            if (not root): return
            if (level >= len(result)): result.append([])
            result[level].append(root.id)
            for child in root.get_childern():
                traversal(child, level + 1, result)

        result = []
        if (self._root == None):
            return result
        traversal(self._root, 0, result)
        return result


class SimpleNodeFactory:

    @staticmethod
    def create_node(type:int, id:int, desc:str) -> Component:
        if (type == COMPONENT_TYPE_ROOT):
            return Root(id, desc)
        else:
            return Node(id, desc)


