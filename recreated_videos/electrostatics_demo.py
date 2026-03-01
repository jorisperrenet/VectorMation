"""Electrostatics demo: charges, electric fields, and interactions."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    Charge, ElectricField,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/electrostatics')

# Title
title = Text(text='Electrostatics & Electric Fields', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: Single positive charge field ────────────────────────────
label1 = Text(text='Positive Point Charge', x=480, y=100,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

q1 = Charge(magnitude=3, cx=480, cy=340, creation=0.5)
q1.fadein(0.5, 1.0)
canvas.add(q1)

field1 = ElectricField(q1, x_range=(200, 760, 80), y_range=(160, 520, 80),
                       creation=1.0)
field1.fadein(1.0, 2.0)
canvas.add(field1)

# ── Section 2: Dipole field ────────────────────────────────────────────
label2 = Text(text='Electric Dipole', x=1440, y=100,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label2)

q_pos = Charge(magnitude=2, cx=1340, cy=340, creation=0.5)
q_neg = Charge(magnitude=-2, cx=1540, cy=340, creation=0.5)
q_pos.fadein(0.5, 1.0)
q_neg.fadein(0.5, 1.0)
canvas.add(q_pos)
canvas.add(q_neg)

field2 = ElectricField(q_pos, q_neg,
                       x_range=(1160, 1720, 80), y_range=(160, 520, 80),
                       creation=2.0)
field2.fadein(2.0, 3.0)
canvas.add(field2)

# ── Section 3: Quadrupole ─────────────────────────────────────────────
label3 = Text(text='Quadrupole Configuration', x=ORIGIN[0], y=590,
              font_size=22, fill='#aaa', text_anchor='middle', creation=3.5)
canvas.add(label3)

charges = [
    Charge(magnitude=2, cx=860, cy=720, creation=3.5),
    Charge(magnitude=-2, cx=1060, cy=720, creation=3.5),
    Charge(magnitude=-2, cx=860, cy=920, creation=3.5),
    Charge(magnitude=2, cx=1060, cy=920, creation=3.5),
]
for ch in charges:
    ch.fadein(3.5, 4.0)
    canvas.add(ch)

field3 = ElectricField(*charges,
                       x_range=(700, 1220, 60), y_range=(640, 1000, 60),
                       creation=4.0)
field3.fadein(4.0, 5.0)
canvas.add(field3)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 6,
                           fps=args.fps, port=args.port)
