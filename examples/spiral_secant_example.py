import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/spiral_secant')
canvas.set_background()

title = Text(text='Secant & Tangent Lines', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Secant line on Axes
ax = Axes(x_range=(-2, 4), y_range=(-1, 10),
          plot_width=800, plot_height=500,
          x=500, y=200)
ax.fadein(0.5, 1)

func = lambda x: 0.5 * x ** 2
curve = ax.plot(func, stroke='#58C4DD', stroke_width=3)

# Secant line between x=0 and x=3
sec = ax.get_secant_line(func, x1=0, x2=3, length=400, stroke='#FF6B6B')
sec.fadein(2, 2.5)

# Tangent line at x=1.5 for comparison
tan = ax.get_tangent_line(func, x_val=1.5, length=300, stroke='#83C167')
tan.fadein(3, 3.5)

# Labeled dots
d1, l1 = ax.add_dot_label(0, func(0), label='(0, 0)', dot_color='#FF6B6B')
d2, l2 = ax.add_dot_label(3, func(3), label='(3, 4.5)', dot_color='#FF6B6B')
d1.fadein(2, 2.5)
l1.fadein(2, 2.5)
d2.fadein(2, 2.5)
l2.fadein(2, 2.5)

canvas.add_objects(ax, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/spiral_secant_example.mp4', fps=30, end=5)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
