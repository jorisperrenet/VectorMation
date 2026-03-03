"""Vector fields, slope fields, and tangent lines demo."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import math
from vectormation.objects import (
    VectorMathAnim, Axes, Text, ORIGIN, parse_args,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/vector_fields')

# Title
title = Text(text='Vector Fields & Slope Fields', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: Slope Field for dy/dx = x - y ────────────────────────
label1 = Text(text="dy/dx = x − y", x=480, y=120,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

ax1 = Axes(x_range=(-3, 3), y_range=(-3, 3),
           plot_width=700, plot_height=500,
           x=130, y=160, creation=0.5)
ax1.add_coordinates(creation=0.5)
ax1.fadein(0.5, 1.0)
canvas.add(ax1)

slope_field = ax1.add_slope_field(lambda x, y: x - y,
                                   x_step=0.5, y_step=0.5,
                                   seg_length=0.2,
                                   creation=1.0, stroke='#555')
slope_field.stagger('fadein', start=1.0, end=2.5)

# Solution curve overlay
curve1 = ax1.plot(lambda x: x - 1 + 2 * math.exp(-x), creation=2.5,
                  stroke='#58C4DD', stroke_width=3)
curve1.write(2.5, 3.5)

# ── Section 2: Vector Field F(x,y) = (-y, x) — circular ────────────
label2 = Text(text="F(x,y) = (−y, x)", x=1440, y=120,
              font_size=22, fill='#aaa', text_anchor='middle', creation=4)
canvas.add(label2)

ax2 = Axes(x_range=(-3, 3), y_range=(-3, 3),
           plot_width=700, plot_height=500,
           x=1090, y=160, creation=4)
ax2.add_coordinates(creation=4)
ax2.fadein(4.0, 4.5)
canvas.add(ax2)

vf = ax2.plot_vector_field(lambda x, y: (-y, x),
                            x_step=0.6, y_step=0.6,
                            creation=4.5, stroke='#83C167', fill='#83C167')
vf.stagger('fadein', start=4.5, end=6.0)

# ── Section 3: Tangent line on sin(x) ───────────────────────────────
label3 = Text(text="Tangent to sin(x) at x=1", x=480, y=720,
              font_size=22, fill='#aaa', text_anchor='middle', creation=7)
canvas.add(label3)

ax3 = Axes(x_range=(-1, 7), y_range=(-2, 2),
           plot_width=700, plot_height=300,
           x=130, y=770, creation=7)
ax3.add_coordinates(creation=7)
ax3.fadein(7, 7.5)
canvas.add(ax3)

sin_curve = ax3.plot(math.sin, creation=7.5, stroke='#FF79C6', stroke_width=2.5)
sin_curve.write(7.5, 8.5)

tangent = ax3.get_tangent_line(math.sin, 1.0, length=250,
                                creation=8.5, stroke='#FFFF00', stroke_width=2)
tangent.fadein(8.5, 9.0)

dot_label = ax3.add_dot_label(1, math.sin(1), label='(1, sin 1)',
                               dot_color='#FF6B6B', creation=8.5)

# ── Section 4: Gradient field F(x,y) = (x, y) ──────────────────────
label4 = Text(text="F(x,y) = (x, y)", x=1440, y=720,
              font_size=22, fill='#aaa', text_anchor='middle', creation=10)
canvas.add(label4)

ax4 = Axes(x_range=(-3, 3), y_range=(-3, 3),
           plot_width=700, plot_height=300,
           x=1090, y=770, creation=10)
ax4.add_coordinates(creation=10)
ax4.fadein(10, 10.5)
canvas.add(ax4)

grad_field = ax4.plot_vector_field(lambda x, y: (x, y),
                                    x_step=0.6, y_step=0.6, max_length=50,
                                    creation=10.5, stroke='#FF6B6B', fill='#FF6B6B')
grad_field.stagger('fadein', start=10.5, end=12)

canvas.browser_display(start=args.start or 0, end=args.end or 13,
                           fps=args.fps, port=args.port)
