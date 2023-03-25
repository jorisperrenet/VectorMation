from vectormation.objects import *
import math
from math import sin, cos


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/heart')
canvas.set_background()

# Draw the objects
point = Dot()
point.c.set(0, 2*math.pi, lambda t: (
    500 + 20*16*sin(t)**3,
    500 - 20*(13*cos(t) - 5*cos(2*t) - 2*cos(3*t) - cos(4*t)),
), stay=True)
trace = Trace(point.c, start=0, end=2*math.pi, dt=1/60, stroke_width=4, stroke=(255,0,0))

pol = trace.to_polygon(2*math.pi)
trace.show.set_onward(7, 0)
pol.styling.fill.set_onward(7, (255,0,0))
pol.styling.fill_opacity.set(7, 8, lambda t: 0.6*(t-7), stay=True)

# Add the objects to the canvas
canvas.add_objects(trace, pol)

# Display the window
canvas.standard_display(fps=60)
