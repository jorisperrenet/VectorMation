import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/sankey_lollipop')
canvas.set_background()

title = Text(text='Threshold, Data Labels, Lollipop & Sankey', x=960, y=50,
             font_size=36, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Axes with threshold + data labels ---
ax = Axes(x_range=(0, 6), y_range=(0, 12),
          plot_width=350, plot_height=250,
          x=50, y=120)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

bars = ax.plot_bar([1, 2, 3, 4, 5], [6, 9, 4, 11, 7], bar_width=0.6, creation=1.5)
bars.fadein(1.5, 2)

threshold = ax.add_threshold_line(8, label='Target', creation=1.5,
                                   stroke='#FFFF00')
threshold.fadein(1.5, 2)

labels = ax.add_data_labels([1, 2, 3, 4, 5], [6, 9, 4, 11, 7], creation=2)
labels.fadein(2, 2.5)

ax_label = Text(text='Threshold + Labels', x=225, y=110,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
ax_label.fadein(1, 1.5)

# --- Horizontal lollipop chart ---
ax2 = Axes(x_range=(0, 100), y_range=(0, 6),
           plot_width=350, plot_height=250,
           x=500, y=120)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

lp = ax2.plot_lollipop([1, 2, 3, 4, 5], [65, 82, 45, 93, 58],
                        fill='#FF79C6', stroke='#FF79C6', creation=1.5)
lp.fadein(1.5, 2.5)

lp_label = Text(text='Lollipop Chart', x=675, y=110,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
lp_label.fadein(1, 1.5)

# --- Sankey diagram ---
flows = [
    ('Budget', 'Engineering', 40),
    ('Budget', 'Marketing', 25),
    ('Budget', 'Operations', 20),
    ('Budget', 'HR', 15),
    ('Engineering', 'Frontend', 20),
    ('Engineering', 'Backend', 15),
    ('Engineering', 'QA', 5),
]
sankey = SankeyDiagram(flows, x=200, y=500, width=1000, height=400)
sankey.fadein(1, 2)

sankey_label = Text(text='Sankey Diagram', x=700, y=480,
                    font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
sankey_label.fadein(1, 1.5)

canvas.add_objects(ax, ax2, title, bars, threshold, labels, lp,
                   sankey, ax_label, lp_label, sankey_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
