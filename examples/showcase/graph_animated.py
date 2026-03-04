from vectormation.objects import *
import math

# Initialize the animation frame
canvas = VectorMathAnim()
canvas.set_background()

# Plot sin(x) with animated curve drawing
graph = Graph(math.sin, x_range=(-2 * math.pi, 2 * math.pi),
              y_range=(-1.5, 1.5), x_label='x', y_label='y')

# Animate the sin curve being drawn left to right
sin_path = graph.curve.create(start=0, end=2)

# Add a second function (cos) after the first is drawn
cos_curve = graph.add_function(math.cos, stroke='#FC6255')
cos_path = cos_curve.create(start=2.5, end=4.5)

canvas.add_objects(graph, sin_path, cos_path)

canvas.show(end=5.5)
