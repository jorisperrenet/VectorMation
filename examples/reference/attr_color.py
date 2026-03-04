"""Color interpolation: RGB vs HSL."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

# Top: RGB interpolation (goes through muddy middle)
rgb_label = Text('RGB', x=150, y=340, font_size=36, fill='WHITE')
rgb_circle = Circle(r=80, cx=960, cy=340, fill='#FF0000', fill_opacity=1, stroke_width=0)
rgb_circle.set_color(start=0.5, end=3.5, fill='#0000FF', color_space='rgb')

# Bottom: HSL interpolation (smooth hue transition through rainbow)
hsl_label = Text('HSL', x=150, y=740, font_size=36, fill='WHITE')
hsl_circle = Circle(r=80, cx=960, cy=740, fill='#FF0000', fill_opacity=1, stroke_width=0)
hsl_circle.set_color(start=0.5, end=3.5, fill='#0000FF', color_space='hsl')

v.add(rgb_label, rgb_circle, hsl_label, hsl_circle)

v.show(end=4)
