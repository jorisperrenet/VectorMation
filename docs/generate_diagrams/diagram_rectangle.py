#!/usr/bin/env python3
"""Generate rectangle parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 440, 300
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

RW, RH = 220, 130
X, Y = 110, 60  # top-left corner
CORNER = 18

# Main rectangle with rounded corners
canvas.add_objects(Rectangle(RW, RH, x=X, y=Y, rx=CORNER, ry=CORNER,
                             fill_opacity=0, stroke='#58C4DD', stroke_width=2.5))

# (x, y) top-left label
canvas.add_objects(
    Dot(r=4, cx=X, cy=Y, fill='#f38ba8', stroke_width=0),
    Text('(x, y)', x=X - 42, y=Y + 5, font_size=11, fill='#f38ba8'),
)

# width dimension (below rect)
bot = Y + RH
canvas.add_objects(
    DashedLine(x1=X, y1=bot, x2=X, y2=bot + 25, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=X + RW, y1=bot, x2=X + RW, y2=bot + 25, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=X + 5, y1=bot + 20, x2=X + RW, y2=bot + 20, tip_length=6, tip_width=5, stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=X + RW - 5, y1=bot + 20, x2=X, y2=bot + 20, tip_length=6, tip_width=5, stroke='#cdd6f4', stroke_width=1.2),
    Text('width', x=X + RW//2 - 18, y=bot + 38, font_size=13, fill='#cdd6f4'),
)

# height dimension (right of rect)
canvas.add_objects(
    DashedLine(x1=X + RW, y1=Y, x2=X + RW + 30, y2=Y, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=X + RW, y1=bot, x2=X + RW + 30, y2=bot, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=X + RW + 25, y1=Y + 5, x2=X + RW + 25, y2=bot, tip_length=6, tip_width=5, stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=X + RW + 25, y1=bot - 5, x2=X + RW + 25, y2=Y, tip_length=6, tip_width=5, stroke='#cdd6f4', stroke_width=1.2),
    Text('height', x=X + RW + 32, y=Y + RH//2 + 5, font_size=13, fill='#cdd6f4'),
)

# Corner rounding annotation
canvas.add_objects(
    Dot(r=2.5, cx=X + CORNER, cy=Y + CORNER, fill='#a6e3a1', stroke_width=0),
    DashedLine(x1=X, y1=Y + CORNER, x2=X + CORNER, y2=Y + CORNER, dash='3,2', stroke='#a6e3a1', stroke_width=1),
    DashedLine(x1=X + CORNER, y1=Y, x2=X + CORNER, y2=Y + CORNER, dash='3,2', stroke='#a6e3a1', stroke_width=1),
    Text('rx, ry', x=X + CORNER + 5, y=Y + CORNER - 3, font_size=11, fill='#a6e3a1'),
)

# x position label
canvas.add_objects(
    DashedLine(x1=X, y1=250, x2=X, y2=265, dash='3,2', stroke='#a6adc8', stroke_width=1),
    Arrow(x1=25, y1=260, x2=X, y2=260, tip_length=8, tip_width=6, stroke='#a6adc8', stroke_width=1),
    Text('x', x=58, y=278, font_size=12, fill='#a6adc8'),
)

# y position label
canvas.add_objects(
    DashedLine(x1=30, y1=Y, x2=45, y2=Y, dash='3,2', stroke='#a6adc8', stroke_width=1),
    Arrow(x1=35, y1=15, x2=35, y2=Y, tip_length=8, tip_width=6, stroke='#a6adc8', stroke_width=1),
    Text('y', x=22, y=40, font_size=12, fill='#a6adc8'),
)

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'rectangle_params.svg')
canvas.write_frame(time=0, filename=out)
