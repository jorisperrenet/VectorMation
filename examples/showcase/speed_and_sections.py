from vectormation.objects import *

# Initialize the animation frame
canvas = VectorMathAnim()
canvas.set_background()

# Section 1: A circle appears
circle = Circle(r=80, cx=760, cy=540, fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD')
circle.write(start=0, end=2)
canvas.add_section(2)

# Section 2: A square appears
square = Rectangle(140, 140, x=890, y=470, fill='#FC6255', fill_opacity=0.8,
                   stroke='#FC6255', rx=5, ry=5)
square.write(start=2, end=4)
canvas.add_section(4)

# Section 3: A triangle appears
tri = EquilateralTriangle(160, cx=1160, cy=540, fill='#83C167', fill_opacity=0.8, stroke='#83C167')
tri.center_to_pos(1160, 540)
tri.write(start=4, end=6)

# Instructions text
hint = Text(text='Press Space to advance sections, +/- to change speed',
            x=960, y=950, font_size=16, fill='#888', stroke_width=0, text_anchor='middle')

canvas.add_objects(circle, square, tri, hint)

canvas.show(end=7)
