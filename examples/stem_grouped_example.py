import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/stem_grouped')
canvas.set_background()

title = Text(text='Stem Plot, Grouped Bars & Uncreate', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Stem plot
ax = Axes(x_range=(0, 8), y_range=(0, 10),
          plot_width=400, plot_height=300,
          x=50, y=130)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

stems = ax.plot_stem([1, 2, 3, 4, 5, 6, 7], [3, 7, 2, 8, 5, 9, 4],
                      creation=1.5, stroke='#83C167', dot_fill='#83C167')
stems.fadein(1.5, 2.5)

# Grouped bar chart
ax2 = Axes(x_range=(0, 5), y_range=(0, 12),
           plot_width=400, plot_height=300,
           x=600, y=130)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

data = [[3, 7, 5, 8], [5, 4, 9, 6], [2, 8, 3, 7]]
bars = ax2.plot_grouped_bar(data, bar_width=0.25, creation=1.5)
bars.fadein(1.5, 2.5)

# Uncreate demo
circle = Circle(cx=400, cy=750, r=80, stroke='#FF6B6B', stroke_width=4,
                fill_opacity=0)
circle.fadein(0.5, 1)
trail = circle.uncreate(start=3, end=5)

label = Text(text='Uncreate', x=400, y=640,
             font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
label.fadein(0.5, 1)

canvas.add_objects(ax, ax2, title, stems, bars, circle, trail, label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
