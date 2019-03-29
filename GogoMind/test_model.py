#!/usr/bin/env python3

from model import *
import unittest


class ComponentTest(unittest.TestCase):

    def test_root(self):
        root = Root(0, "Root")
        fake_root = Root(1, "Fake Root")
        child = Node(1, "Child")

        self.assertFalse(root.add_child(fake_root)) 
        self.assertTrue(root.add_child(child)) 
        self.assertFalse(root.add_child(child))

        try:
            root.add_sibling(child) 
        except ValueError as e:
            self.assertEqual(type(e), ValueError)
         
        try:
            root.get_siblings()
        except ValueError as e:
            self.assertEqual(type(e), ValueError)

        try:
            root.set_parent(fake_root)
        except ValueError as e:
            self.assertEqual(type(e), ValueError)

        childern = root.get_childern() 
        self.assertEqual(len(childern), 1)


    def test_node(self):
        root = Root(0, "Root")
        child_1 = Node(1, "Child_1")
        child_2 = Node(2, "Child_2")

        self.assertFalse(child_1.add_child(child_1))
        self.assertFalse(child_1.add_sibling(child_1))



if __name__ == "__main__":
    unittest.main()

