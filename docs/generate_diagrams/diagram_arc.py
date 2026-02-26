#!/usr/bin/env python3
"""Generate arc parameter diagram."""
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 400, 320
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

CX, CY, R = 200, 170, 100
START, END = 30, 150

# Reference circle (faint)
canvas.add_objects(Circle(r=R, cx=CX, cy=CY,
                          fill_opacity=0, stroke='#45475a', stroke_width=0.8,
                          stroke_dasharray='4,3'))

# Arc
canvas.add_objects(Arc(cx=CX, cy=CY, r=R, start_angle=START, end_angle=END,
                       stroke='#58C4DD', stroke_width=3, fill_opacity=0))

# Centre dot
canvas.add_objects(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))
canvas.add_objects(Text('(cx, cy)', x=CX + 8, y=CY + 18, font_size=11, fill='#f38ba8'))

# r dimension line (to start of arc)
sx = CX + R * math.cos(math.radians(START))
sy = CY - R * math.sin(math.radians(START))
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=sx, y2=sy, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Text('r', x=(CX + sx) / 2 + 8, y=(CY + sy) / 2 + 4, font_size=14, fill='#cdd6f4'),
)

# start_angle reference line (horizontal)
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=CX + R + 10, y2=CY, dash='3,2', stroke='#a6adc8', stroke_width=0.8),
)

# start_angle arc indicator (small arc from 0° to start_angle)
canvas.add_objects(
    Arc(cx=CX, cy=CY, r=40, start_angle=0, end_angle=START,
        stroke='#a6e3a1', stroke_width=1.5, fill_opacity=0),
    Text('start_angle', x=CX + 43, y=CY - 22, font_size=11, fill='#a6e3a1'),
)

# end_angle arc indicator
canvas.add_objects(
    Arc(cx=CX, cy=CY, r=50, start_angle=0, end_angle=END,
        stroke='#f9e2af', stroke_width=1.5, fill_opacity=0),
    Text('end_angle', x=CX - 140, y=CY - 50, font_size=11, fill='#f9e2af'),
)

# Subtitle
canvas.add_objects(Text('Angles in degrees, counter-clockwise', x=82, y=300, font_size=11, fill='#585b70'))

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'arc_params.svg')
canvas.write_frame(time=0, filename=out)
