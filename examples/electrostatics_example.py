"""Electrostatic field visualization — dipole charges with field arrows."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

canvas = VectorMathAnim(save_dir='svgs/electrostatics')
canvas.set_background()

# Create a positive and negative charge (dipole)
q_pos = Charge(magnitude=3, cx=660, cy=540)
q_neg = Charge(magnitude=-3, cx=1260, cy=540)

# Visualize the electric field
field = ElectricField(q_pos, q_neg, max_length=60,
                      x_range=(100, 1820, 100),
                      y_range=(100, 980, 100))

title = Text('Electric Dipole Field', x=960, y=60, font_size=36,
             text_anchor='middle', fill='#fff', stroke_width=0)

# Animations
field.fadein(start=0, end=1.5)
q_pos.fadein(start=0.5, end=1.5)
q_neg.fadein(start=0.5, end=1.5)
title.fadein(start=0, end=1)

canvas.add_objects(field, q_pos, q_neg, title)
args = parse_args()
if args.verbose:
    canvas.export_video('docs/source/_static/videos/electrostatics_example.mp4', fps=30, end=3)
if not args.no_display:
    canvas.browser_display(start=0, end=3, fps=args.fps, port=args.port)
