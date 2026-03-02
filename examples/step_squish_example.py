import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/step_squish')
canvas.set_background()

title = Text(text='Step Plot & Highlight Range', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with step function
ax = Axes(x_range=(0, 8), y_range=(0, 10),
          plot_width=700, plot_height=400,
          x=150, y=180)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

# Step function data
xs = [0, 1, 2, 3, 4, 5, 6, 7]
ys = [2, 2, 5, 5, 3, 7, 7, 4]
step = ax.plot_step(xs, ys, stroke='#83C167', stroke_width=3)
step.create(1.5, 2.5)

# Horizontal labels
lbl1 = ax.add_horizontal_label(5, 'threshold', side='right', fill='#FF6B6B')
lbl1.fadein(2.5, 3)

# Highlight the y-range
band = ax.highlight_y_range(4, 6, fill='#FF6B6B', fill_opacity=0.1)
band.fadein(2.5, 3)

canvas.add_objects(ax, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/step_squish_example.mp4', fps=30, end=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
