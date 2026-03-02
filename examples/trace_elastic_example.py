import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/trace_elastic')
canvas.set_background()

title = Text(text='Trace & Secant Fade', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with a curve
ax = Axes(x_range=(-1, 5), y_range=(-1, 10),
          plot_width=700, plot_height=400,
          x=150, y=180)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

f = lambda x: 0.5 * x ** 2
curve = ax.plot(f, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

# Trace along the curve (dot + trail)
trace = ax.add_trace(f, 0, 4, start=2.5, end=4.5,
                      r=6, trail_width=2, fill='#FF6B6B', stroke='#FF6B6B')

# Secant line fading to tangent at x=2
secant = ax.add_secant_fade(f, x=2, dx_start=2, dx_end=0.01,
                             start=3, end=5, stroke='#83C167')
secant.fadein(3, 3.3)

canvas.add_objects(ax, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/trace_elastic_example.mp4', fps=30, end=6)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
