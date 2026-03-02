import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/slope_wave')
canvas.set_background()

title = Text(text='Slope Field (add_slope_field)', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Slope field for dy/dx = -x/y (circle field)
ax = Axes(x_range=(-3, 3), y_range=(-3, 3),
          plot_width=500, plot_height=500,
          x=100, y=150)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

field = ax.add_slope_field(
    lambda x, y: -x / y if abs(y) > 0.01 else 0,
    x_step=0.5, y_step=0.5, seg_length=0.2,
    stroke='#58C4DD', stroke_width=1)
field.fadein(1.5, 2.5)

canvas.add_objects(ax, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/slope_wave_example.mp4', fps=30, end=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
