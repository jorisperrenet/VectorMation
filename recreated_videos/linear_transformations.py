"""Linear Transformations — recreation of 3b1b's Essence of Linear Algebra Ch.3.

Shows how a 2D linear transformation warps the grid and transforms
basis vectors i-hat and j-hat.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/linear_transform')
canvas.set_background()

# ── Number plane ──────────────────────────────────────────────────────
plane = NumberPlane(x_range=(-7, 7, 1), y_range=(-4, 4, 1))
plane.add_coordinate_labels(font_size=14)
plane.fadein(0, 1)

# ── Basis vectors ─────────────────────────────────────────────────────
origin = plane.coords_to_point(0, 0)
i_end = plane.coords_to_point(1, 0)
j_end = plane.coords_to_point(0, 1)

i_hat = Arrow(x1=origin[0], y1=origin[1], x2=i_end[0], y2=i_end[1],
              stroke='#83C167', fill='#83C167', stroke_width=4, creation=0)
j_hat = Arrow(x1=origin[0], y1=origin[1], x2=j_end[0], y2=j_end[1],
              stroke='#FC6255', fill='#FC6255', stroke_width=4, creation=0)
i_hat.fadein(0.5, 1.5)
j_hat.fadein(0.5, 1.5)

i_label = Text(text='î', x=i_end[0] + 15, y=i_end[1] + 5,
               font_size=28, fill='#83C167', stroke_width=0, creation=0)
j_label = Text(text='ĵ', x=j_end[0] - 30, y=j_end[1] - 5,
               font_size=28, fill='#FC6255', stroke_width=0, creation=0)
i_label.fadein(0.8, 1.5)
j_label.fadein(0.8, 1.5)

# ── Title ─────────────────────────────────────────────────────────────
title = Text(text='Linear Transformations', x=960, y=50,
             font_size=42, fill='#fff', stroke_width=0, text_anchor='middle',
             creation=0)
title.fadein(0, 1)

# ── Transformation 1: Shear ──────────────────────────────────────────
subtitle1 = Text(text='Shear: [[1, 1], [0, 1]]', x=960, y=1030,
                 font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle',
                 creation=0)
subtitle1.fadein(1.5, 2)

# Apply the shear to the plane
plane.apply_matrix([[1, 1], [0, 1]], start=2, end=4)

# Move basis vectors to match
shear_i = plane.coords_to_point(1, 0)
shear_j = plane.coords_to_point(1, 1)
i_hat.shift(dx=shear_i[0] - i_end[0], dy=shear_i[1] - i_end[1], start=2, end=4)
j_hat.shift(dx=shear_j[0] - j_end[0], dy=shear_j[1] - j_end[1], start=2, end=4)
i_label.shift(dx=shear_i[0] - i_end[0], dy=shear_i[1] - i_end[1], start=2, end=4)
j_label.shift(dx=shear_j[0] - j_end[0], dy=shear_j[1] - j_end[1], start=2, end=4)

subtitle1.fadeout(5, 5.5)

# ── Info text ─────────────────────────────────────────────────────────
info = Text(text='Grid lines remain parallel and evenly spaced',
            x=960, y=1030, font_size=22, fill='#58C4DD', stroke_width=0,
            text_anchor='middle', creation=0)
info.fadein(5.5, 6)
info.fadeout(7, 7.5)

canvas.add(plane, i_hat, j_hat, i_label, j_label, title, subtitle1, info)

canvas.browser_display(start=args.start or 0, end=args.end or 8,
                           fps=args.fps, port=args.port)
