"""Taylor series approximation: progressive polynomial terms converging to sin(x)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import math
from vectormation.objects import (
    VectorMathAnim, Axes, Text, parse_args,
)

args = parse_args()
v = VectorMathAnim(save_dir='out')

title = Text(text='Taylor Series Approximation of sin(x)', x=960, y=40,
             font_size=36, fill='#fff', stroke_width=0, text_anchor='middle')
title.fadein(0, 1)
v.add(title)

ax = Axes(x_range=(-7, 7), y_range=(-3, 3), show_grid=True,
          x_label='x', y_label='y', creation=0)

# Plot sin(x) as reference
sin_curve = ax.plot(math.sin, stroke='#fff', stroke_width=3, creation=0.5)

# Taylor series for sin(x): sum of (-1)^n * x^(2n+1) / (2n+1)!
colors = ['#FF6B6B', '#58C4DD', '#50FA7B', '#BD93F9', '#FF79C6', '#F1FA8C']


def make_taylor_sin(order):
    """Return a function computing the Taylor approximation of sin(x) up to order terms."""
    def taylor(x):
        result = 0
        for n in range(order):
            result += ((-1) ** n) * (x ** (2 * n + 1)) / math.factorial(2 * n + 1)
        return result
    return taylor


# Stagger each approximation
for i in range(6):
    n = i + 1  # number of terms: 1, 2, 3, 4, 5, 6
    t_start = 1 + i * 1.5
    color = colors[i % len(colors)]
    curve = ax.plot(make_taylor_sin(n), stroke=color, stroke_width=2,
                    stroke_opacity=0.8, creation=t_start)
    curve.fadein(t_start, t_start + 0.5)

    # Label showing the order
    degree = 2 * n - 1  # highest degree term
    label = Text(text=f'n={n} (degree {degree})', x=1600, y=95 + i * 35,
                 font_size=18, fill=color, stroke_width=0, text_anchor='start')
    label.fadein(t_start, t_start + 0.5)
    v.add(label)

# Label for the original function
sin_label = Text(text='sin(x)', x=1600, y=75,
                 font_size=18, fill='#fff', stroke_width=0, text_anchor='start')
sin_label.fadein(0.5, 1.5)
v.add(sin_label)

v.add(ax)

v.browser_display(start=args.start or 0, end=args.end or 11,
                      fps=args.fps, port=args.port)
