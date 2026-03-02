import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/cascade_shake')
canvas.set_background()

title = Text(text='Slope Field', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Slope field for dy/dx = -x/y (circles)
ax = Axes(x_range=(-3, 3), y_range=(-3, 3),
          plot_width=600, plot_height=400,
          x=650, y=300)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

slope_field = ax.get_slope_field(lambda x, y: -x / y if abs(y) > 0.1 else 0,
                                  x_step=0.5, y_step=0.5, length=0.35,
                                  stroke='#83C167')
slope_field.fadein(1.5, 3)

canvas.add_objects(ax, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/cascade_shake_example.mp4', fps=30, end=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
