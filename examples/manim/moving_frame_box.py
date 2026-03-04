"""Manim equivalent: MovingFrameBox -- LaTeX with animated bounding rectangles."""
from vectormation.objects import *

canvas = VectorMathAnim(width=1920, height=540)
canvas.set_background()
text = TexObject(r'$$\frac{d}{dx}f(x)g(x)=f(x)\frac{d}{dx}g(x)+g(x)\frac{d}{dx}f(x)$$', font_size=120)
text.center_to_pos(posx=960, posy=270)
text.write(0, 1)
rect1 = text.brect(0, 13, 25, follow=False, buff=12)
rect2 = text.brect(0, 26, 38, follow=False, buff=12)
obj = MorphObject(rect1, rect2, start=2, end=4)

canvas.add_objects(text, obj, rect1, rect2)

canvas.show()
