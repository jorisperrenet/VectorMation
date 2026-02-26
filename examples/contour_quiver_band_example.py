import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/contour_quiver_band')
canvas.set_background()

title = Text(text='Contour, Quiver, Reference Band & Color Bar', x=960, y=40,
             font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Contour plot ---
import math
ax1 = Axes(x_range=(-3, 3), y_range=(-3, 3),
           plot_width=350, plot_height=350, x=50, y=100)
ax1.add_coordinates()
ax1.fadein(0.5, 1.5)

contours = ax1.plot_contour(
    lambda x, y: math.sin(x) * math.cos(y),
    levels=6, x_samples=30, y_samples=30)
contours.fadein(1.5, 2.5)

c_label = Text(text='Contour Plot', x=225, y=85,
               font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
c_label.fadein(1, 1.5)

# --- Quiver field ---
ax2 = Axes(x_range=(-2, 2), y_range=(-2, 2),
           plot_width=300, plot_height=300, x=500, y=100)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

quiver = ax2.plot_quiver(lambda x, y: (-y, x), x_step=0.5, y_step=0.5, scale=0.3)
quiver.fadein(1.5, 2.5)

q_label = Text(text='Quiver Field', x=650, y=85,
               font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
q_label.fadein(1, 1.5)

# --- Reference band ---
ax3 = Axes(x_range=(0, 10), y_range=(0, 10),
           plot_width=300, plot_height=250, x=950, y=100)
ax3.add_coordinates()
ax3.fadein(0.5, 1.5)

band = ax3.add_reference_band(3, 7, axis='y', fill='#83C167', fill_opacity=0.15)
band.fadein(1, 2)

line = ax3.plot(lambda x: 5 + 3 * math.sin(x), stroke='#58C4DD', stroke_width=2)
line.fadein(1.5, 2.5)

lbl = ax3.add_text_annotation(5, 8, 'Target Zone')
lbl.fadein(2, 2.5)

r_label = Text(text='Reference Band', x=1100, y=85,
               font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
r_label.fadein(1, 1.5)

# --- Color bar + heatmap combo ---
ax4 = Axes(x_range=(0, 5), y_range=(0, 5),
           plot_width=300, plot_height=250, x=300, y=550)
ax4.add_coordinates()
ax4.fadein(0.5, 1.5)

hm = ax4.plot_heatmap(
    [[1, 3, 5, 7, 9], [2, 4, 6, 8, 10],
     [0, 2, 4, 6, 8], [1, 3, 5, 7, 9], [3, 5, 7, 9, 11]])
hm.fadein(1.5, 2.5)

cb = ax4.add_color_bar(vmin=0, vmax=11, n_segments=25)
cb.fadein(2, 2.5)

hm_label = Text(text='Heatmap + Color Bar', x=480, y=535,
                font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
hm_label.fadein(1, 1.5)

canvas.add_objects(title, ax1, contours, c_label,
                   ax2, quiver, q_label,
                   ax3, band, line, lbl, r_label,
                   ax4, hm, cb, hm_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
