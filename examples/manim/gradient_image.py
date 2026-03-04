"""Manim equivalent: GradientImageFromArray -- linear gradient with bounding rectangle."""
from vectormation.objects import *
from vectormation.colors import LinearGradient

canvas = VectorMathAnim()
canvas.set_background()

# Black-to-white linear gradient
grad = LinearGradient([('0%', '#000'), ('100%', '#fff')])
canvas.add_gradient(grad)

# Gradient rectangle centered on screen
rect = Rectangle(width=600, height=400, x=660, y=340, fill=grad, stroke_width=0)

# Green bounding rectangle
border = SurroundingRectangle(rect, buff=0, stroke='#00FF00', stroke_width=4,
                              fill_opacity=0)

canvas.add_objects(rect, border)

canvas.show()
