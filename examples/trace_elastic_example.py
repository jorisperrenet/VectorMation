import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/trace_elastic')
canvas.set_background()

title = Text(text='Trace, Elastic In/Out & Secant Fade', x=960, y=50,
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

# Right side: elastic in/out demo
shapes = VCollection(
    Circle(cx=1350, cy=700, r=35, fill='#FF6B6B', fill_opacity=0.5,
           stroke='#FF6B6B', stroke_width=2),
    Rectangle(70, 70, x=1445, y=665, fill='#83C167', fill_opacity=0.5,
              stroke='#83C167', stroke_width=2),
    Star(outer_radius=35, inner_radius=18, cx=1550, cy=700,
         fill='#FFFF00', fill_opacity=0.5, stroke='#FFFF00', stroke_width=2),
)

# Elastic in each shape
shapes[0].elastic_in(start=3, end=4)
shapes[1].elastic_in(start=3.3, end=4.3)
shapes[2].elastic_in(start=3.6, end=4.6)

# Swap children demo
label = Text(text='Swap Children', x=1450, y=630,
             font_size=22, fill='#aaa', stroke_width=0, text_anchor='middle')
label.fadein(4.5, 5)

shapes.swap_children(0, 2, start=5, end=6)

canvas.add_objects(ax, title, shapes, label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
