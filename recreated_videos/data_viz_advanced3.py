"""Advanced data visualization demo part 3: quiver (vector field), dot plot,
density plot, and ribbon chart."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Axes, Text, parse_args,
)

args = parse_args()
v = VectorMathAnim(save_dir='out')

title = Text(text='Vector Fields & Statistical Plots', x=960, y=50,
             font_size=36, fill='#fff', stroke_width=0, text_anchor='middle')
title.fadein(0, 1)
v.add(title)

# ── 1. Quiver (vector field) ──────────────────────────────────────────
q_label = Text(text='Quiver (Vector Field)', x=480, y=140,
               font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
q_label.fadein(0.5, 1.5)
v.add(q_label)

ax1 = Axes(x_range=(-3, 3), y_range=(-3, 3),
           plot_width=700, plot_height=350, x=130, y=160, creation=0.5)
ax1.plot_quiver(lambda x, y: (-y, x), x_step=0.8, y_step=0.8,
                scale=0.25, creation=1, stroke='#50FA7B')
v.add(ax1)

# ── 2. Dot plot ────────────────────────────────────────────────────────
dp_label = Text(text='Dot Plot', x=1440, y=140,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
dp_label.fadein(1.5, 2.5)
v.add(dp_label)

ax2 = Axes(x_range=(0, 8), y_range=(0, 5),
           plot_width=700, plot_height=350, x=1090, y=160, creation=1.5)
# Dice roll results with duplicates
rolls = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 7]
ax2.plot_dot_plot(rolls, stack_spacing=0.5, r=6, creation=2, fill='#FF79C6')
v.add(ax2)

# ── 3. Density plot ───────────────────────────────────────────────────
dn_label = Text(text='Density (KDE)', x=480, y=610,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
dn_label.fadein(2.5, 3.5)
v.add(dn_label)

ax3 = Axes(x_range=(-5, 15), y_range=(0, 0.2),
           plot_width=700, plot_height=350, x=130, y=630, creation=2.5)
import random
rng = random.Random(123)
data1 = [rng.gauss(3, 2) for _ in range(50)]
data2 = [rng.gauss(8, 1.5) for _ in range(50)]
ax3.plot_density(data1, creation=3, stroke='#FF6B6B')
ax3.plot_density(data2, creation=3, stroke='#58C4DD')
v.add(ax3)

# ── 4. Ribbon chart ───────────────────────────────────────────────────
rb_label = Text(text='Ribbon (Confidence Band)', x=1440, y=610,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
rb_label.fadein(3.5, 4.5)
v.add(rb_label)

ax4 = Axes(x_range=(0, 10), y_range=(0, 12),
           plot_width=700, plot_height=350, x=1090, y=630, creation=3.5)
xs = list(range(11))
y_mid = [2, 3, 5, 4, 6, 7, 6, 8, 9, 8, 10]
y_lo = [v - 1.2 for v in y_mid]
y_hi = [v + 1.2 for v in y_mid]
ax4.plot_ribbon(xs, y_lo, y_hi, creation=4,
                fill='#BD93F9', stroke='#BD93F9')
# Add center line
ax4.plot(lambda x: [2, 3, 5, 4, 6, 7, 6, 8, 9, 8, 10][min(int(x), 10)]
         if 0 <= x <= 10 else 0,
         creation=4, stroke='#fff', stroke_width=2)
v.add(ax4)

v.browser_display(start=args.start or 0, end=args.end or 6,
                      fps=args.fps, port=args.port)
