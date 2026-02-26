#!/usr/bin/env python3
"""Generate line parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 400, 260
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

X1, Y1, X2, Y2 = 60, 190, 340, 60

# Main line
canvas.add_objects(Line(x1=X1, y1=Y1, x2=X2, y2=Y2, stroke='#58C4DD', stroke_width=2.5))

# Start point dot + label
canvas.add_objects(
    Dot(r=5, cx=X1, cy=Y1, fill='#f38ba8', stroke_width=0),
    Text('p1 (x1, y1)', x=X1 - 10, y=Y1 + 22, font_size=12, fill='#f38ba8'),
)

# End point dot + label
canvas.add_objects(
    Dot(r=5, cx=X2, cy=Y2, fill='#a6e3a1', stroke_width=0),
    Text('p2 (x2, y2)', x=X2 - 30, y=Y2 - 15, font_size=12, fill='#a6e3a1'),
)

# Midpoint indicator
mx, my = (X1 + X2) / 2, (Y1 + Y2) / 2
canvas.add_objects(
    Dot(r=3, cx=mx, cy=my, fill='#f9e2af', stroke_width=0),
    Text('center()', x=mx + 8, y=my - 8, font_size=10, fill='#f9e2af'),
)

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'line_params.svg')
canvas.write_frame(time=0, filename=out)
