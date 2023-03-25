from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/moving_frame_box', height=500)
canvas.set_background()

# Draw the objects
text = TexObject(r'$$\frac{d}{dx}f(x)g(x)=f(x)\frac{d}{dx}g(x)+g(x)\frac{d}{dx}f(x)$$', scale_x=5, scale_y=5)
text.center_to_pos(posx=500, posy=250)
text.write(0, 1)
rect1 = text.brect(0, 13, 25, follow=False, dpos=10)
rect2 = text.brect(0, 26, 38, follow=False, dpos=10)
obj = MorphObject(rect1, rect2, start=3, end=5)

# Add the objects to the canvas
canvas.add_objects(text, obj, rect1, rect2)

# Display the window
canvas.standard_display(fps=60)
