#!/usr/bin/env python3
"""Generate numberline parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 500, 200
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

# NumberLine
canvas.add_objects(NumberLine(
    x_range=(-4, 3, 1), length=380, x=60, y=90,
    include_arrows=True, include_numbers=True,
    tick_size=10, font_size=12,
    stroke='#58C4DD', stroke_width=2, fill='#cdd6f4',
))

# x_range annotation (below)
# Ticks span from x=60 (val=-4) to x=60+380 (val=3)
left_x, right_x = 60, 440
canvas.add_objects(
    DashedLine(x1=left_x + 20, y1=118, x2=left_x + 20, y2=140, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=right_x - 20, y1=118, x2=right_x - 20, y2=140, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=left_x + 25, y1=138, x2=right_x - 20, y2=138, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=right_x - 25, y1=138, x2=left_x + 20, y2=138, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Text('x_range = (-4, 3, 1)', x=170, y=160, font_size=12, fill='#cdd6f4'),
)

# tick_size annotation
tick_x = 330
canvas.add_objects(
    Arrow(x1=tick_x, y1=68, x2=tick_x, y2=80, tip_length=4, tip_width=3, stroke='#a6e3a1', stroke_width=1.2),
    Arrow(x1=tick_x, y1=82, x2=tick_x, y2=68, tip_length=4, tip_width=3, stroke='#a6e3a1', stroke_width=0),
    Text('tick_size', x=tick_x + 8, y=72, font_size=11, fill='#a6e3a1'),
)

# Subtitle
canvas.add_objects(Text('length controls total pixel width', x=130, y=185, font_size=11, fill='#585b70'))

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'numberline_params.svg')
canvas.write_frame(time=0, filename=out)
