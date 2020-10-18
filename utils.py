class LinkType:
    OneLink = 1
    ZeroLink = 2


class NodeType:
    Normal = 1
    Yes = 2
    No = 3


def det(a, b, c, d, e, f, g, h, i):
    return a * e * i + b * f * g + c * d * h - a * f * h - b * d * i - c * e * g


def getOfType(items, _cls):
    found = []

    for item in items:
        if type(item) is _cls:
            found.append(item)

    return found

