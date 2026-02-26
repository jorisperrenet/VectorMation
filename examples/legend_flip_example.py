import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/legend_flip')
canvas.set_background()

title = Text(text='Legend, Flip & Wave Animation', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with legend
ax = Axes(x_range=(-2, 5), y_range=(-2, 10),
          plot_width=700, plot_height=400,
          x=100, y=150)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

f1 = lambda x: x ** 2
f2 = lambda x: 2 * x + 1
c1 = ax.plot(f1, stroke='#58C4DD', stroke_width=3)
c2 = ax.plot(f2, stroke='#FF6B6B', stroke_width=3)
c1.create(1.5, 2.5)
c2.create(2, 3)

legend = ax.add_legend([('x²', '#58C4DD'), ('2x + 1', '#FF6B6B')],
                        position='upper left')
legend.fadein(3, 3.5)

# Flip demo
rect = Rectangle(width=120, height=80, x=1000, y=200, fill='#83C167',
                 stroke_width=2, stroke='#fff')
rect.fadein(0.5, 1)
rect.flip('horizontal', start=2, end=2.5)
rect.flip('vertical', start=3.5, end=4)

flip_label = Text(text='Flip!', x=1060, y=310, font_size=24,
                  fill='#83C167', stroke_width=0, text_anchor='middle')
flip_label.fadein(1.5, 2)

# Shrink to point demo
star = Star(n=5, outer_radius=40, inner_radius=20, cx=1400, cy=250,
            fill='#FFFF00', stroke_width=0)
star.fadein(1, 1.5)
star.shrink_to_point(1500, 350, start=4, end=5)

# Wave animation on a row of dots
dots = VGroup(
    *[Dot(cx=200 + i * 60, cy=700, r=10,
          fill='#FF6B6B', stroke_width=0) for i in range(15)]
)
dots.cascade('fadein', start=1, end=2.5, overlap=0.6)
dots.wave_anim(start=3, end=7, amplitude=30, waves=2)

canvas.add_objects(ax, rect, flip_label, star, dots, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
