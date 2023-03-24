from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/community_logo')
canvas.set_background(fill='#ece6e2')

# Draw the objects
char = TexObject(r'$$\mathbb{M}$$', scale_x=38, scale_y=38, fill='#343434').objects[0]
char.center_to_pos(posx=275, posy=350)
cir = Circle(100, fill='#87c2a5', stroke_width=0, fill_opacity=1).shift(dx=-100)
sq = Rectangle(200, 200, fill='#525893', stroke_width=0, fill_opacity=1).shift(dx=-100, dy=-200)
tr = EquilateralTriangle(200, fill='#e07a5f', stroke_width=0, fill_opacity=1).shift(dx=100)

# Group and center the objects
logo = VCollection(tr, sq, cir, char)
logo.center_to_pos()

# Add the objects to the canvas
canvas.add_objects(logo)

# Display the window
canvas.standard_display(fps=60)
