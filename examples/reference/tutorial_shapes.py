"""Basic shapes intro: circle, rectangle, text with animations."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

# Create three shapes
circle = Circle(r=80, cx=400, cy=540, fill='#58C4DD', fill_opacity=0.8)
rect = Rectangle(160, 160, x=880, y=460, fill='#E74C3C', fill_opacity=0.8)
text = Text('Hello!', x=1440, y=540, font_size=64, fill='WHITE')

# Fade them in one at a time
circle.fadein(start=0, end=1)
rect.fadein(start=0.5, end=1.5)
text.fadein(start=1, end=2)

# Move them together
circle.shift(dy=-150, start=2.5, end=3.5)
rect.shift(dy=-150, start=2.5, end=3.5)
text.shift(dy=-150, start=2.5, end=3.5)

v.add(circle, rect, text)

v.show(end=4)
