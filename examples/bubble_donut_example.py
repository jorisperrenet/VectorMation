import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/bubble_donut')
canvas.set_background()

title = Text(text='Bubble Chart, Stacked Area, Color Bar & Donut', x=960, y=50,
             font_size=36, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Bubble chart ---
ax = Axes(x_range=(0, 10), y_range=(0, 10),
          plot_width=400, plot_height=300,
          x=50, y=130)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

bubbles = ax.plot_bubble(
    [1, 2, 4, 6, 8, 3, 7, 5],
    [3, 7, 2, 8, 5, 9, 4, 6],
    [10, 50, 25, 80, 40, 60, 30, 70],
    max_radius=25, fill='#FF79C6', creation=1)
bubbles.fadein(1, 2)

bubble_label = Text(text='Bubble Chart', x=250, y=120,
                    font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
bubble_label.fadein(1, 1.5)

# --- Stacked area with color bar ---
ax2 = Axes(x_range=(0, 6), y_range=(0, 20),
           plot_width=400, plot_height=300,
           x=550, y=130)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

data = [
    [2, 3, 4, 3, 5, 4],
    [3, 2, 5, 4, 3, 5],
    [1, 4, 2, 3, 2, 3],
]
areas = ax2.plot_stacked_area(data, creation=1.5)
areas.fadein(1.5, 2.5)

area_label = Text(text='Stacked Area', x=750, y=120,
                  font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
area_label.fadein(1, 1.5)

# --- Color bar on heatmap ---
ax3 = Axes(x_range=(0, 5), y_range=(0, 5),
           plot_width=280, plot_height=280,
           x=1100, y=130)
ax3.add_coordinates()
ax3.fadein(0.5, 1.5)

hm_data = [[math.sin(r * 0.7 + c * 0.5) * 5 + 5 for c in range(5)] for r in range(5)]
hm = ax3.plot_heatmap(hm_data, creation=1.5)
hm.fadein(1.5, 2)

cb = ax3.add_color_bar(vmin=0, vmax=10, label='Value', creation=1.5)
cb.fadein(1.5, 2.5)

hm_label = Text(text='Heatmap + Color Bar', x=1300, y=120,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
hm_label.fadein(1, 1.5)

# --- Donut chart ---
donut = DonutChart([35, 25, 20, 20],
                   labels=['A', 'B', 'C', 'D'],
                   center_text='Total',
                   cx=400, cy=700, r=150, inner_radius=80)
donut.fadein(1, 2)

donut_label = Text(text='Donut Chart', x=400, y=520,
                   font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
donut_label.fadein(1, 1.5)

canvas.add_objects(ax, ax2, ax3, title, bubbles, areas, hm, cb,
                   donut, bubble_label, area_label, hm_label, donut_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/bubble_donut_example.mp4', fps=30, end=2)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
