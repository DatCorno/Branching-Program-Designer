import json

class FileInterface:

    def __init__(self, filename):
        self.filename = filename

    def toJson(self, nodes, edges):
        json_file = dict()
        json_file["nodes"] = []
        json_file["edges"] = []
        for node in nodes:
            data = {'id': node.id,
                    'position': node.scenePos().toTuple(),
                    'text': node.text.toPlainText(),
                    "node_type": node.node_type
                    }
            json_file["nodes"].append(data)

        for edge in edges:
            data = {"start": edge.start.id,
                    "end": edge.end.id,
                    "link_type": edge.link_type,
                    "arc_mode": edge.arc_mode
                    }

            if edge.arc_mode:
                data["current_arc_point"] = edge.current_arc_point.toTuple()

            json_file["edges"].append(data)

        with open(self.filename, "w") as f:
            json.dump(json_file, f)

    def fromJson(self):
        with open(self.filename, "r") as f:
            return json.load(f)