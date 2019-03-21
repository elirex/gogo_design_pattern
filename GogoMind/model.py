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
        if (node in self._children):
            return False
        else:
            self._children.append(node)
            return True


    @abc.abstractmethod
    def add_sibling(self, node: 'Component') -> bool:
        if (node in self._siblings):
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
        if (not self._parent):
            self._parent = parent
            return True
        else:
            return False


class Root(Component):

    def __init__(self, id:int, desc:str):
        super().__init__(id, desc)

    
    def add_child(self, node:Component) -> bool:
        return super().add_child(node) 
        
    
    def add_sibling(self, node:Component) -> None:
        raise ValueError("Root cannot add sibling.")


    def get_childern(self) -> List[Component]:
        return super().get_childern()


    def get_siblings(self) -> None:
        raise ValueError("Root hasn't any siblings.")


    def set_parent(self, parent: Component) -> None:
        raise ValueError("Root hasn't the parent.")


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


class MindMapModel:

    def __init__(self):
        self._root = None
        self._components = {}
        self._serial_ids = -1


    def create_mind_map(self, desc:str) -> bool:
        if (self._root):
            return False
        else:
            self._root = self.create_node(desc)
            return self.insert_node(self._root, -1)


    def create_node(self, desc:str) -> Component:
        type = COMPONENT_TYPE_NODE if (self._root) else COMPONENT_TYPE_ROOT
        self._serial_ids += 1
        return SimpleNodeFactory.create_node(COMPONENT_TYPE_ROOT, self._serial_ids, desc)


    def insert_node(node: Component, parent_id:int) -> bool:
        if (not node): return False
        if (parent_id not in self._components): return False
        # TODO: insert node logic
        if (node.id in self._components): return False

        parent = self._components[parent_id]
        node.set_parent(parent)
        self._components[node.id] = node
        return True


class SimpleNodeFactory:

    @staticmethod
    def create_node(type:int, id:int. desc:str) -> Component:
        if (type == COMPONENT_TYPE_ROOT):
            return Root(id, desc)
        else:
            return Node(id, desc)
    


def test(root: Component):
    if (isinstance(root, Root)):
        print("yes")
        print("id = {}, desc = {}".format(root.id, root.desc))
        root.print()
    else:
        print("no")
    

if __name__ == "__main__":
    
    root = Root(0, 'R')
    c1 = Node(1, 'C1')
    c2 = Node(2, 'C2')

    root.add_child(c1)
    root.add_child(c2)

    for node in root.get_childern():
        print("node id={}, des={}".format(node.id, node.desc))


