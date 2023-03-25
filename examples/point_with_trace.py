from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/point_with_trace')
canvas.set_background()

# Draw the objects
point = Dot()
point.c.rotate_around(1, 2, (600, 500), 180)
point.c.move_to(2.5, 3.5, (700, 400))
point.c.move_to(4, 5, (600, 400))
trace = Trace(point.c, start=0, end=5, dt=1/60)

# Add the objects to the canvas
canvas.add_objects(trace, point)

# Display the window
canvas.standard_display(fps=60)
