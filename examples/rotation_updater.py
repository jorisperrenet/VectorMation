from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/rotation_updater')
canvas.set_background()

# Draw the objects
l1 = Line(x1=300, y1=500, x2=500, y2=500)
l2 = Line(x1=300, y1=500, x2=500, y2=500, stroke=(255,0,0))
l2.p1.rotate_around(1, 3, l2.p2.at_time(0), degrees=130)
l2.p1.rotate_around(3, 5, l2.p2.at_time(0), degrees=130, clockwise=True)

# Add the objects to the canvas
canvas.add_objects(l1, l2)

# Display the window
canvas.standard_display(fps=60)
