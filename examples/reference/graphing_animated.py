"""Animated sin + cos graph creation."""
import math
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

graph = Graph(math.sin, x_range=(-2 * math.pi, 2 * math.pi),
              y_range=(-1.5, 1.5))

# Draw sin curve
graph.curve.create(start=0, end=2)

# Add and draw cos curve
cos_curve = graph.add_function(math.cos, stroke='#FC6255')
cos_curve.create(start=2.5, end=4.5)

v.add(graph)

v.show(end=5)
