#!/usr/bin/env python3
"""Generate arrow parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 440, 240
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

X1, Y1, X2, Y2 = 60, 120, 340, 120
TIP_L, TIP_W = 30, 20

# Main arrow
canvas.add_objects(Arrow(x1=X1, y1=Y1, x2=X2, y2=Y2,
                         tip_length=TIP_L, tip_width=TIP_W,
                         stroke='#58C4DD', stroke_width=2.5))

# Start dot + label
canvas.add_objects(
    Dot(r=4, cx=X1, cy=Y1, fill='#f38ba8', stroke_width=0),
    Text('(x1, y1)', x=X1 - 20, y=Y1 - 15, font_size=11, fill='#f38ba8'),
)

# End dot + label
canvas.add_objects(
    Dot(r=4, cx=X2, cy=Y2, fill='#f38ba8', stroke_width=0),
    Text('(x2, y2)', x=X2 + 5, y=Y2 - 15, font_size=11, fill='#f38ba8'),
)

# tip_length dimension
tip_base_x = X2 - TIP_L
canvas.add_objects(
    DashedLine(x1=tip_base_x, y1=Y1 + TIP_W//2, x2=tip_base_x, y2=Y1 + 50, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=X2, y1=Y1 + TIP_W//2, x2=X2, y2=Y1 + 50, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=tip_base_x + 3, y1=Y1 + 45, x2=X2, y2=Y1 + 45, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=X2 - 3, y1=Y1 + 45, x2=tip_base_x, y2=Y1 + 45, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Text('tip_length', x=tip_base_x - 5, y=Y1 + 65, font_size=11, fill='#cdd6f4'),
)

# tip_width dimension
canvas.add_objects(
    DashedLine(x1=tip_base_x, y1=Y1 - TIP_W//2, x2=X2 + 40, y2=Y1 - TIP_W//2, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=tip_base_x, y1=Y1 + TIP_W//2, x2=X2 + 40, y2=Y1 + TIP_W//2, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=X2 + 35, y1=Y1 - TIP_W//2 + 3, x2=X2 + 35, y2=Y1 + TIP_W//2, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=X2 + 35, y1=Y1 + TIP_W//2 - 3, x2=X2 + 35, y2=Y1 - TIP_W//2, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Text('tip_width', x=X2 + 42, y=Y1 + 5, font_size=11, fill='#cdd6f4'),
)

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'arrow_params.svg')
canvas.write_frame(time=0, filename=out)
