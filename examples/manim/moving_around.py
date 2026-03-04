"""Manim equivalent: MovingAround -- chain of shift, set_fill, scale, rotate."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()
square = Rectangle(200, 200, fill='#58C4DD', fill_opacity=1)
square.center_to_pos(posx=960, posy=540)
square.shift(dx=-200, start=0, end=1)
square.set_color(1, 2, '#FF862F')
square.scale(0.3, 2, 3)
square.rotate_by(3, 4, 23)

canvas.add_objects(square)

canvas.show()
