"""Side-by-side circles shifting with different easings."""
from vectormation.objects import *
from vectormation.easings import linear, smooth, ease_out_bounce

v = VectorMathAnim()
v.set_background()

labels = ['linear', 'smooth', 'bounce']
easings = [linear, smooth, ease_out_bounce]
colors = ['#E74C3C', '#3498DB', '#2ECC71']

for i, (label, easing, color) in enumerate(zip(labels, easings, colors)):
    y = 270 + i * 270
    # Label
    txt = Text(label, x=100, y=y, font_size=36, fill=color)
    txt.fadein(start=0, end=0.3)
    # Circle that shifts right using this easing
    c = Circle(r=30, cx=400, cy=y, fill=color, fill_opacity=0.8)
    c.fadein(start=0, end=0.3)
    c.shift(dx=800, start=0.5, end=3, easing=easing)
    v.add(txt, c)

v.show(end=3.5)
