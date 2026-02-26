#!/usr/bin/env python3
"""Generate wedge/sector parameter diagram."""
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 400, 320
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

CX, CY, R = 200, 165, 100
START, END = 30, 120

# Wedge
canvas.add_objects(Wedge(cx=CX, cy=CY, r=R, start_angle=START, end_angle=END,
                         fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=2.5))

# Centre dot
canvas.add_objects(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))
canvas.add_objects(Text('(cx, cy)', x=CX + 6, y=CY + 18, font_size=11, fill='#f38ba8'))

# r dimension
sx = CX + R * math.cos(math.radians(START))
sy = CY - R * math.sin(math.radians(START))
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=sx, y2=sy, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Text('r', x=(CX + sx) / 2 + 8, y=(CY + sy) / 2 + 4, font_size=14, fill='#cdd6f4'),
)

# start_angle reference line
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=CX + R + 10, y2=CY, dash='3,2', stroke='#a6adc8', stroke_width=0.8),
)

# start_angle indicator
canvas.add_objects(
    Arc(cx=CX, cy=CY, r=40, start_angle=0, end_angle=START,
        stroke='#a6e3a1', stroke_width=1.5, fill_opacity=0),
    Text('start_angle', x=CX + 43, y=CY - 15, font_size=11, fill='#a6e3a1'),
)

# end_angle indicator
canvas.add_objects(
    Arc(cx=CX, cy=CY, r=50, start_angle=0, end_angle=END,
        stroke='#f9e2af', stroke_width=1.5, fill_opacity=0),
    Text('end_angle', x=CX - 115, y=CY - 65, font_size=11, fill='#f9e2af'),
)

# Subtitle
canvas.add_objects(Text('Wedge: arc closed through the centre', x=80, y=295, font_size=11, fill='#585b70'))

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'wedge_params.svg')
canvas.write_frame(time=0, filename=out)
