import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/asymptote_coords')
canvas.set_background()

title = Text(text='Asymptotes, Coords Labels & Pulsate', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with rational function that has asymptotes
ax = Axes(x_range=(-4, 6), y_range=(-5, 10),
          plot_width=800, plot_height=450,
          x=200, y=200)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

# f(x) = 1/(x-2) + 3 — vertical asymptote at x=2, horizontal at y=3
def f(x):
    if abs(x - 2) < 0.05:
        return float('nan')
    return 1 / (x - 2) + 3

# Plot left and right branches separately
f_left = lambda x: 1 / (x - 2) + 3
f_right = lambda x: 1 / (x - 2) + 3
curve_left = ax.plot(f_left, x_range=(-4, 1.8), stroke='#58C4DD', stroke_width=3)
curve_right = ax.plot(f_right, x_range=(2.2, 6), stroke='#58C4DD', stroke_width=3)
curve_left.create(1.5, 2.5)
curve_right.create(1.5, 2.5)

# Asymptote lines
v_asymp = ax.add_asymptote(2, direction='vertical', stroke='#FF6B6B')
v_asymp.fadein(2, 2.5)

h_asymp = ax.add_asymptote(3, direction='horizontal', stroke='#83C167')
h_asymp.fadein(2, 2.5)

# Label a specific point with coords_label
cl = ax.coords_label(4, f_right(4), fill='#FFFF00')
cl.fadein(3, 3.5)

# Highlight child demo (right side)
dots = VCollection(
    Circle(cx=1450, cy=750, r=30, fill='#FF6B6B', fill_opacity=0.6, stroke='#FF6B6B'),
    Circle(cx=1550, cy=750, r=30, fill='#83C167', fill_opacity=0.6, stroke='#83C167'),
    Circle(cx=1650, cy=750, r=30, fill='#58C4DD', fill_opacity=0.6, stroke='#58C4DD'),
)
dots.fadein(3.5, 4)

# Highlight the middle one
dots.highlight_child(1, start=4.5, end=6)

# Pulsate demo
star = Star(outer_radius=40, inner_radius=20, cx=1550, cy=900,
            fill='#FFFF00', fill_opacity=0.6, stroke='#FFFF00', stroke_width=2)
star.fadein(4, 4.5)
star.pulsate(start=4.5, end=7, n_pulses=4, scale_factor=1.4)

canvas.add_objects(ax, title, dots, star)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/asymptote_coords_example.mp4', fps=30, end=7)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
