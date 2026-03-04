"""NetworkGraph with nodes and edges."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

graph = NetworkGraph(
    nodes={0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E'},
    edges=[(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (1, 4)],
    radius=250,
    directed=True,
)

v.add(graph)

v.show(end=0)
