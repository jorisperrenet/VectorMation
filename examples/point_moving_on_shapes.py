from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/point_moving_on_shapes')
canvas.set_background()

# Draw the objects
cir = Circle(0, stroke='blue', fill_opacity=0)
cir.r.move_to(0, 2, 80, stay=True)
dot = Dot(fill='#fff', fill_opacity=1)
dot.c.move_to(1, 2, (580, 500), stay=True)
dot.c.rotate_around(1, 2, (500, 500), 360, stay=True)
dot.c.rotate_around(2, 3, (660, 500), 360, stay=True)
l = Line(500+3*80, 500, 500+5*80, 500)

# Add the objects to the canvas
canvas.add_objects(cir, dot, l)

# Display the window
canvas.standard_display(fps=60)
