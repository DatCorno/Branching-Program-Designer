import json


class Graph:

    def __init__(self):
        self.nodes = []
        self.edges = []

    def insertNode(self, id):
        self.nodes.append(id)

    def insertEdge(self, origin, dest):
        if not self.ensureNoCycles(origin, dest) or [origin, dest] in self.edges:
            return False

        self.edges.append([origin, dest])

        return True

    def ensureNoCycles(self, start, end):
        vertex_to_look = [end]

        while len(vertex_to_look):
            current = vertex_to_look[0]
            edge = [current, start]

            if edge in self.edges:
                return False

            vertex_to_look.pop(0)

            for edge in self.edges:
                if edge[0] == current:
                    vertex_to_look.append(edge[1])
        return True
