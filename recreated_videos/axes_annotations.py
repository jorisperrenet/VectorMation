import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Axes, Text, parse_args,
)
import math

args = parse_args()
v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/axes_annotations')
v.set_background()

# --- Set up axes with a sin(x) base curve ---

ax = Axes(
    x_range=(-1, 7),
    y_range=(-1.5, 1.5),
    plot_width=1400,
    plot_height=700,
    x=260, y=160,
)
ax.add_coordinates()
ax.fadein(0, 1)

title = ax.add_title('Axes Annotation Methods', font_size=36, fill='#58C4DD')
title.fadein(0, 1)

f = lambda x: math.sin(x)
curve = ax.add_function(f, stroke='#58C4DD', stroke_width=3, creation=0.5)

# --- 1. add_asymptote: vertical asymptote at x=pi ---
asym = ax.add_asymptote(math.pi, direction='vertical', creation=1.5,
                        stroke='#FF6B6B', stroke_dasharray='10 5')

# --- 2. get_secant_line: secant through x=1 and x=2.5 ---
secant = ax.get_secant_line(f, 1, 2.5, length=400, creation=2.5,
                            stroke='#83C167', stroke_width=2.5)

# --- 3. add_min_max_labels: label extrema of sin(x) ---
mm = ax.add_min_max_labels(f, x_range=(0, 6.5), creation=3.5, font_size=16)

# --- 4. add_horizontal_label / add_vertical_label ---
hlabel = ax.add_horizontal_label(1.0, 'y=1', side='right', creation=4.5,
                                  fill='#FFFF00')
vlabel = ax.add_vertical_label(math.pi, 'x=pi', side='bottom', creation=4.5,
                                fill='#FF6B6B')

# --- 5. add_interval: mark [1, 3] on the x-axis ---
interval = ax.add_interval(1, 3, creation=5.5, stroke='#FFD700', stroke_width=2.5)

# --- 6. add_vector: draw a vector from origin to (2, 0.9) ---
vec = ax.add_vector(2, 0.9, creation=6.5, stroke='#E07CFF', fill='#E07CFF')

# --- 7. coords_label: labeled point at (pi/2, 1) ---
cl = ax.coords_label(math.pi / 2, 1.0, creation=7.5,
                      stroke='#58C4DD', fill='#58C4DD')

# --- 8. add_arrow_annotation: annotated arrow pointing to (3*pi/2, -1) ---
ann = ax.add_arrow_annotation(
    3 * math.pi / 2, -1, 'minimum', direction='down',
    length=60, creation=8.5, fill='#FF6B6B', stroke='#FF6B6B',
)

# --- 9. highlight_y_range: shade -0.5 to 0.5 ---
hy = ax.highlight_y_range(-0.5, 0.5, creation=9.5,
                           fill='#FFFF00', fill_opacity=0.1, stroke_width=0)

# --- 10. get_area_between: area between sin(x) and 0.3*sin(2x) ---
g = lambda x: 0.3 * math.sin(2 * x)
curve2 = ax.add_function(g, stroke='#E07CFF', stroke_width=2, creation=10.5)
area = ax.get_area_between(f, g, x_range=(0, 6), creation=10.5,
                            fill='#58C4DD', fill_opacity=0.25, stroke_width=0)

# --- 11. get_dashed_line: dashed line from (0, -1) to (6, 1) ---
dashed = ax.get_dashed_line(0, -1, 6, 1, creation=11.5,
                             stroke='#aaa', stroke_width=1.5)

# --- 12. get_line_from_to: solid line from (1, -1) to (5, 1) ---
solid = ax.get_line_from_to(1, -1, 5, 1, creation=12.5,
                             stroke='#FFD700', stroke_width=2)

v.add_objects(ax)

T = 14
if not args.no_display:
    v.browser_display(start=args.start or 0, end=args.end or T,
                      fps=args.fps, port=args.port)
