from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/moving_dots')
canvas.set_background()

# Draw the objects
d1, d2 = Dot(), Dot(fill='#58C4DD')
l = Line(x1=500, y1=500, x2=450, y2=500, stroke_width=2.5)
d1.c.set_to(l.p1)
d2.c.set_to(l.p2)
l.p1.move_to(1.5, 3, (500, 200))
l.p2.move_to(1, 2.5, (800, 500))

# Add the objects to the canvas
canvas.add_objects(l, d1, d2)

# Display the window
canvas.standard_display(fps=60)
