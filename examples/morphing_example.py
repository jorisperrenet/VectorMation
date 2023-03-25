from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/morphing_example')
canvas.set_background()

# Draw the objects
text_from = TexObject('Who is the best?', scale_x=10, scale_y=10)
text_from.center_to_pos()
text_to = TexObject('You are the best!', scale_x=10, scale_y=10, fill='blue')
text_to.center_to_pos()

text_from.fadein(start=0, end=1)
obj = MorphObject(text_from, text_to, start=1, end=3)

# Add the objects to the canvas
canvas.add_objects(text_from, obj, text_to)

# Display the window
canvas.standard_display(fps=60)
