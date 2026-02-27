import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/scatter_colorwave')
canvas.set_background()

title = Text(text='Scatter, Gather, Color Wave & Shaded Inequality', x=960, y=50,
             font_size=36, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Scatter/Gather demo ---
dots = VCollection(
    *[Dot(cx=350, cy=350, r=18,
          fill=['#FF6B6B', '#83C167', '#58C4DD', '#FFFF00', '#FF79C6', '#B8BB26'][i])
      for i in range(6)]
)
dots.distribute_radial(cx=350, cy=350, radius=80, start=0, end=0)
dots.fadein(0.5, 1)

scatter_label = Text(text='Scatter', x=350, y=230,
                     font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
scatter_label.fadein(0.5, 1)

dots.scatter_from(cx=350, cy=350, radius=150, start=2, end=3)
dots.gather_to(cx=350, cy=350, start=4, end=5)

# --- Color wave demo ---
circle = Circle(cx=900, cy=350, r=80, fill='#FF6B6B', stroke='#FF6B6B', stroke_width=3)
circle.fadein(0.5, 1)
circle.color_gradient_anim(colors=('#FF6B6B', '#58C4DD', '#83C167', '#FFFF00'),
                           start=1.5, end=5.5, attr='fill')
circle.color_gradient_anim(colors=('#FF6B6B', '#58C4DD', '#83C167', '#FFFF00'),
                           start=1.5, end=5.5, attr='stroke')

wave_label = Text(text='Color Wave', x=900, y=230,
                  font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
wave_label.fadein(0.5, 1)

# --- Shaded inequality ---
ax = Axes(x_range=(-1, 7), y_range=(-2, 4),
          plot_width=500, plot_height=300,
          x=100, y=550)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

func = lambda x: math.sin(x) * 1.5 + 1
curve = ax.plot(func, stroke='#83C167', stroke_width=3)
curve.create(1.5, 2.5)

shade = ax.add_shaded_inequality(func, direction='below', creation=2,
                                  fill='#83C167', fill_opacity=0.15)
shade.fadein(2, 2.5)

ineq_label = Text(text='y < f(x)', x=550, y=540,
                  font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
ineq_label.fadein(2, 2.5)

canvas.add_objects(ax, title, dots, scatter_label, circle, wave_label,
                   shade, ineq_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
