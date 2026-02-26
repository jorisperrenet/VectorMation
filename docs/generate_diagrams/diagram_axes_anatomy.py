#!/usr/bin/env python3
"""Generate axes anatomy diagram showing labels, ticks, grid, and plot area."""
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 520, 380
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

# Plot area border
PX, PY, PW, PH = 90, 40, 360, 260
canvas.add_objects(Rectangle(PW, PH, x=PX, y=PY,
                             fill_opacity=0, stroke='#45475a', stroke_width=1, stroke_dasharray='4,3'))

# Axes lines
canvas.add_objects(
    # X axis
    Line(x1=PX, y1=PY + PH, x2=PX + PW, y2=PY + PH, stroke='#58C4DD', stroke_width=2),
    # Y axis
    Line(x1=PX, y1=PY, x2=PX, y2=PY + PH, stroke='#58C4DD', stroke_width=2),
)

# Tick marks on X axis
for i in range(6):
    tx = PX + i * PW // 5
    canvas.add_objects(
        Line(x1=tx, y1=PY + PH - 5, x2=tx, y2=PY + PH + 5, stroke='#58C4DD', stroke_width=1.5),
        Text(str(i - 2), x=tx - 4, y=PY + PH + 18, font_size=10, fill='#cdd6f4'),
    )

# Tick marks on Y axis
for i in range(6):
    ty = PY + PH - i * PH // 5
    canvas.add_objects(
        Line(x1=PX - 5, y1=ty, x2=PX + 5, y2=ty, stroke='#58C4DD', stroke_width=1.5),
        Text(str(i - 2), x=PX - 18, y=ty + 4, font_size=10, fill='#cdd6f4'),
    )

# A sample function curve
pts = []
for i in range(100):
    t = -2 + 5 * i / 99
    v = math.sin(t * 1.5) * 1.5
    px_pt = PX + (t + 2) / 5 * PW
    py_pt = PY + PH - (v + 2) / 5 * PH
    pts.append((px_pt, py_pt))
canvas.add_objects(Lines(*pts, stroke='#a6e3a1', stroke_width=2, fill_opacity=0))

# Annotations
# "x_label"
canvas.add_objects(
    Text('x_label', x=PX + PW // 2 - 15, y=PY + PH + 35, font_size=12, fill='#f9e2af'),
    Arrow(x1=PX + PW // 2 + 25, y1=PY + PH + 30, x2=PX + PW + 10, y2=PY + PH + 5,
          tip_length=6, tip_width=5, stroke='#f9e2af', stroke_width=0.8),
)

# "y_label"
canvas.add_objects(
    Text('y_label', x=15, y=PY + PH // 2 - 20, font_size=12, fill='#f9e2af'),
    Arrow(x1=35, y1=PY + PH // 2 - 10, x2=PX - 5, y2=PY - 5,
          tip_length=6, tip_width=5, stroke='#f9e2af', stroke_width=0.8),
)

# "plot_width"
canvas.add_objects(
    Arrow(x1=PX + 5, y1=PY - 8, x2=PX + PW, y2=PY - 8, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=PX + PW - 5, y1=PY - 8, x2=PX, y2=PY - 8, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=0.8),
    Text('plot_width', x=PX + PW // 2 - 25, y=PY - 14, font_size=10, fill='#cdd6f4'),
)

# "plot_height"
canvas.add_objects(
    Arrow(x1=PX + PW + 10, y1=PY + 5, x2=PX + PW + 10, y2=PY + PH, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=PX + PW + 10, y1=PY + PH - 5, x2=PX + PW + 10, y2=PY, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=0.8),
    Text('plot_height', x=PX + PW + 16, y=PY + PH // 2, font_size=10, fill='#cdd6f4'),
)

# "ticks" annotation
canvas.add_objects(
    Text('ticks', x=PX + PW - 30, y=PY + PH + 18, font_size=9, fill='#585b70'),
)

# "curve (plot)" label
canvas.add_objects(
    Text('plot(func)', x=PX + PW - 70, y=PY + 35, font_size=11, fill='#a6e3a1'),
)

# x_range annotation
canvas.add_objects(
    Text('x_range', x=200, y=PY + PH + 50, font_size=11, fill='#f38ba8'),
    Text('y_range', x=15, y=PY + PH // 2 + 10, font_size=11, fill='#f38ba8'),
)

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'axes_anatomy.svg')
canvas.write_frame(time=0, filename=out)
