"""Manim equivalent: ManimCELogo -- community edition logo with shapes and M."""
from vectormation.objects import *

# Initialize the animation frame
canvas = VectorMathAnim()
canvas.set_background(fill='#ece6e2')
# 1 manim unit = 135px
unit = 135

# Shapes at manim default sizes (radius=1u, side=2u), centered at screen center
cir = Circle(unit, fill='#87c2a5', stroke_width=0, fill_opacity=1).shift(dx=-unit)
sq = Rectangle(2 * unit, 2 * unit, fill='#525893', stroke_width=0, fill_opacity=1).center_to_pos().shift(dy=-unit)
tr = EquilateralTriangle(2 * unit, fill='#e07a5f', stroke_width=0, fill_opacity=1).shift(dx=unit)

# M character: Manim uses MathTex("\mathbb{M}").scale(7), shifted 2.25*LEFT + 1.5*UP
char = TexObject(r'$$\mathbb{M}$$', font_size=350, fill='#343434').objects[0]
char.center_to_pos()
char.shift(dx=round(-2.25 * unit), dy=round(-1.5 * unit))

# Group and center (order matters for z-layering: triangle, square, circle, M)
logo = VCollection(tr, sq, cir, char)
logo.center_to_pos()

canvas.add_objects(logo)

canvas.show()
