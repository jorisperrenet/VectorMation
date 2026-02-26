import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/heatmap_waterfall')
canvas.set_background()

title = Text(text='Heatmap, Crosshair, Violin & Waterfall', x=960, y=50,
             font_size=36, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Heatmap ---
ax = Axes(x_range=(0, 6), y_range=(0, 6),
          plot_width=350, plot_height=350,
          x=50, y=100)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

data = [[math.sin(r * 0.5 + c * 0.3) * 5 + 5 for c in range(6)] for r in range(6)]
hm = ax.plot_heatmap(data, creation=1)
hm.fadein(1, 2)

hm_label = Text(text='Heatmap', x=225, y=90,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
hm_label.fadein(1, 1.5)

# --- Crosshair ---
ax2 = Axes(x_range=(0, 7), y_range=(-2, 2),
           plot_width=350, plot_height=250,
           x=500, y=100)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

func = lambda x: math.sin(x) * 1.5
curve = ax2.plot(func, stroke='#83C167', stroke_width=3)
curve.create(1.5, 2.5)

cross = ax2.add_crosshair(func, x_start=0.5, x_end=6.5, start=2, end=5)
cross.fadein(2, 2.3)

cross_label = Text(text='Crosshair', x=675, y=90,
                   font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
cross_label.fadein(1, 1.5)

# --- Violin plot ---
import random
random.seed(42)
ax3 = Axes(x_range=(0, 4), y_range=(0, 25),
           plot_width=350, plot_height=250,
           x=1000, y=100)
ax3.add_coordinates()
ax3.fadein(0.5, 1.5)

vdata = [
    [random.gauss(10, 3) for _ in range(80)],
    [random.gauss(15, 2) for _ in range(80)],
    [random.gauss(8, 4) for _ in range(80)],
]
violins = ax3.add_violin_plot(vdata, x_positions=[1, 2, 3],
                               fill='#FF79C6', stroke='#FF79C6')
violins.fadein(1.5, 2.5)

violin_label = Text(text='Violin Plot', x=1175, y=90,
                    font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
violin_label.fadein(1, 1.5)

# --- Waterfall chart ---
wf = WaterfallChart([100, -30, 50, -20, 80, -40],
                    labels=['Revenue', 'COGS', 'Growth', 'Tax', 'New Biz', 'Expenses'],
                    x=300, y=550, width=900, height=350)
wf.fadein(1, 2)

wf_label = Text(text='Waterfall Chart', x=750, y=530,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
wf_label.fadein(1, 1.5)

canvas.add_objects(ax, ax2, ax3, title, hm, cross, violins, wf,
                   hm_label, cross_label, violin_label, wf_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
