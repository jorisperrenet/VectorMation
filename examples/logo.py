from vectormation.objects import *
from math import atan, pi

# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/logo', width=60, height=80)
canvas.set_background(fill='#1BD')

# Draw the objects
v = Lines((0, 0), (30, 80), (60, 0), stroke='#333', stroke_width=7)
text = TexObject(r'$\mathbb{V}$ector$\mathbb{M}$ation', rotation=(-atan(80/30)/pi*180, 0, 0))
text.center_to_pos(45, 40)


# Add the objects to the canvas
canvas.add_objects(v, text)
# Display the window
canvas.standard_display(fps=60)
