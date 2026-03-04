"""Updater-driven pulsing opacity."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

dot = Dot(cx=960, cy=540, r=40, fill='#83C167')
dot.add_updater(lambda obj, t: obj.styling.opacity.set_onward(
    0, 0.3 + 0.7 * abs(math.sin(t * 3))))

label = Text('opacity = sin(t)', x=960, y=650, font_size=28,
             fill='#888', text_anchor='middle')
label.fadein(start=0, end=0.5)

v.add(dot, label)

v.show(end=4)
