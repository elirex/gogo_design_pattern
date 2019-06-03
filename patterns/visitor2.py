
class Component:

    def json(self):
        pass

    def xml(self):
        pass

    def save(self, visit):
        visit.visit(self)


class Root(Component):
    
    _type = "Root"
    children = [1, 2, 3]


class Node(Component):

    _type = "Node"

class Visitor:

    def visit(self, component):
        pass


class JSONVisitor(Visitor):

    def visit(self, component):
        if (isinstance(component, Root)):
            json = "{type: Root, children:" + str(component.children) + "}"
        else:
            json = "{type: Node}"
        print(json)


class XMLVisitor(Visitor):

    def visit(self, component):
        if (isinstance(component, Root)):
            xml = "<Root>\n"
            for child in component.children:
                xml += "<Children>" + str(child) + "</Children>\n"
            xml += "</Root>"
        else:
            xml = "<Node></Node>"
        print(xml)


class Map:

    def save(self, component, visit):
       component.save(visit) 
       print()

if __name__ == "__main__":
    map = Map()
    root = Root()
    node = Node()

    json_visitor = JSONVisitor()
    xml_visitor = XMLVisitor()
    
    map.save(root, json_visitor)
    map.save(node, json_visitor)
    map.save(root, xml_visitor)
    map.save(node, xml_visitor)
    


# JSONVisitor
# XMLVisitor
# 
# JSON:
# {"type": "Root", "children": []}
# {"type": "Node"}
# 
# XML:
# <Root>
#     <Children>
#     </Children>
# </Root>
# 
# <Node>
# </Node>
