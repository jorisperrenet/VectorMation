from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim()
canvas.set_background()

# Draw the objects
point = Dot()
trace = Trace(point.c)
# point.c.move_to(0, 5, (900, 500))
point.c.set(0, 5, lambda t: (t*80 + 960, 540))
point.c.rotate_around(0, 5, (960, 540), 360*4)

# Add the objects to the canvas
canvas.add_objects(trace, point)

canvas.show(end=6)
