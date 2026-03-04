"""Animation timing -- same motion at different durations."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

labels = ['1 second', '2 seconds', '4 seconds']
durations = [1, 2, 4]
colors = ['#E74C3C', '#3498DB', '#2ECC71']

for i, (label, dur, color) in enumerate(zip(labels, durations, colors)):
    y = 270 + i * 270
    txt = Text(label, x=100, y=y, font_size=32, fill=color)
    c = Circle(r=25, cx=400, cy=y, fill=color, fill_opacity=0.8)
    c.shift(dx=800, start=0.5, end=0.5 + dur)
    v.add(txt, c)

v.show(end=5)
