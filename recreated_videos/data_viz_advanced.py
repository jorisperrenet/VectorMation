"""Advanced data visualization demo: candlestick, dumbbell, lollipop, swarm,
population pyramid, error bars, stacked area, contour, quiver, and dot plot."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import random
from vectormation.objects import (
    VectorMathAnim, Axes, Text, parse_args,
)

args = parse_args()
v = VectorMathAnim(save_dir='out')

title = Text(text='Advanced Data Visualizations', x=960, y=50,
             font_size=36, fill='#fff', stroke_width=0, text_anchor='middle')
title.fadein(0, 1)
v.add(title)

# ── 1. Candlestick chart ──────────────────────────────────────────────
cs_label = Text(text='Candlestick (OHLC)', x=480, y=140,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
cs_label.fadein(0.5, 1.5)
v.add(cs_label)

ax1 = Axes(x_range=(0, 7), y_range=(90, 130),
           plot_width=700, plot_height=280, x=130, y=160, creation=0.5)
ohlc = [
    (1, 100, 115, 98, 112),
    (2, 112, 120, 108, 105),
    (3, 105, 118, 100, 116),
    (4, 116, 125, 110, 108),
    (5, 108, 122, 106, 120),
    (6, 120, 128, 115, 125),
]
ax1.plot_candlestick(ohlc, bar_width=0.5, creation=1)
v.add(ax1)

# ── 2. Dumbbell chart ─────────────────────────────────────────────────
db_label = Text(text='Dumbbell Chart', x=1440, y=140,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
db_label.fadein(1.5, 2.5)
v.add(db_label)

ax2 = Axes(x_range=(0, 100), y_range=(0, 6),
           plot_width=700, plot_height=280, x=1090, y=160, creation=1.5)
y_pos = [1, 2, 3, 4, 5]
starts = [30, 45, 20, 60, 35]
ends = [70, 65, 80, 90, 55]
ax2.plot_dumbbell(y_pos, starts, ends, creation=2,
                  start_color='#FF6B6B', end_color='#83C167')
v.add(ax2)

# ── 3. Lollipop chart ─────────────────────────────────────────────────
ll_label = Text(text='Lollipop Chart', x=480, y=560,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
ll_label.fadein(2.5, 3.5)
v.add(ll_label)

ax3 = Axes(x_range=(0, 50), y_range=(0, 6),
           plot_width=700, plot_height=280, x=130, y=580, creation=2.5)
lp_y = [1, 2, 3, 4, 5]
lp_vals = [15, 35, 25, 40, 20]
ax3.plot_lollipop(lp_y, lp_vals, creation=3, stroke='#FF79C6', dot_fill='#FF79C6')
v.add(ax3)

# ── 4. Swarm plot ──────────────────────────────────────────────────────
sw_label = Text(text='Swarm Plot', x=1440, y=560,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
sw_label.fadein(3.5, 4.5)
v.add(sw_label)

ax4 = Axes(x_range=(0, 4), y_range=(0, 20),
           plot_width=700, plot_height=280, x=1090, y=580, creation=3.5)
rng = random.Random(42)
groups = [
    [rng.gauss(8, 2) for _ in range(15)],
    [rng.gauss(12, 3) for _ in range(15)],
    [rng.gauss(10, 1.5) for _ in range(15)],
]
ax4.plot_swarm([1, 2, 3], groups, r=5, creation=4, fill='#BD93F9')
v.add(ax4)

if not args.no_display:
    v.browser_display(start=args.start or 0, end=args.end or 6,
                      fps=args.fps, port=args.port)
