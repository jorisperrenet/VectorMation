"""Demonstrates NumberPlane transformations, coordinate labels, and apply_matrix.

Shows a grid being transformed by a 2x2 matrix, with basis vectors i-hat and j-hat.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/number_plane_transform')
canvas.set_background()

# Create number plane with coordinate labels
plane = NumberPlane(x_range=(-5, 5, 1), y_range=(-4, 4, 1))
plane.add_coordinate_labels(font_size=14)
plane.fadein(0, 1)

# Add basis vectors
o = plane.coords_to_point(0, 0)
i_end = plane.coords_to_point(1, 0)
j_end = plane.coords_to_point(0, 1)
i_hat = Arrow(x1=o[0], y1=o[1], x2=i_end[0], y2=i_end[1],
              stroke='#83C167', fill='#83C167', stroke_width=5)
j_hat = Arrow(x1=o[0], y1=o[1], x2=j_end[0], y2=j_end[1],
              stroke='#FC6255', fill='#FC6255', stroke_width=5)
i_hat.fadein(0.5, 1.5)
j_hat.fadein(0.5, 1.5)

# Apply a rotation matrix (90 degrees CCW)
import math
angle = math.pi / 4  # 45 degrees
matrix = [[math.cos(angle), -math.sin(angle)],
          [math.sin(angle), math.cos(angle)]]
plane.apply_matrix(matrix, start=2, end=4)

# Title
title = Text(text='Number Plane Transformations', x=960, y=50,
             font_size=36, fill='#fff', stroke_width=0, text_anchor='middle')
title.fadein(0, 0.5)

canvas.add(plane, i_hat, j_hat, title)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 5,
                           fps=args.fps, port=args.port)
