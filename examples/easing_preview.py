import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import vectormation.easings as easings
args = parse_args()

# Initialize the animation frame
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/easing_preview')
canvas.set_background()

# List of easings to preview
easing_list = [
    ('linear', easings.linear),
    ('smooth', easings.smooth),
    ('ease_in_sine', easings.ease_in_sine),
    ('ease_out_sine', easings.ease_out_sine),
    ('ease_in_out_sine', easings.ease_in_out_sine),
    ('ease_in_quad', easings.ease_in_quad),
    ('ease_out_quad', easings.ease_out_quad),
    ('ease_in_cubic', easings.ease_in_cubic),
    ('ease_out_cubic', easings.ease_out_cubic),
    ('ease_in_out_cubic', easings.ease_in_out_cubic),
    ('ease_in_expo', easings.ease_in_expo),
    ('ease_out_expo', easings.ease_out_expo),
    ('ease_in_bounce', easings.ease_in_bounce),
    ('ease_out_bounce', easings.ease_out_bounce),
    ('ease_in_elastic', easings.ease_in_elastic),
    ('ease_out_elastic', easings.ease_out_elastic),
    ('ease_in_back', easings.ease_in_back),
    ('ease_out_back', easings.ease_out_back),
]

# Layout: grid of dots, each showing its easing
cols = 3
spacing_x = 300
spacing_y = 160
margin_x = 100
margin_y = 80
duration = 3

objects = []
for i, (name, easing) in enumerate(easing_list):
    row = i // cols
    col = i % cols
    x_start = margin_x + col * spacing_x
    y = margin_y + row * spacing_y
    x_end = x_start + 200

    # Label
    label = Text(text=name, x=x_start, y=y - 10, font_size=12,
                 fill='#aaa', stroke_width=0)

    # Dot that moves with the easing
    dot = Dot(cx=x_start, cy=y + 20, fill='#58C4DD')
    s, e = 0, duration
    dot.c.set(s, e,
        lambda t, _s=s, _e=e, _xs=x_start, _xe=x_end, _y=y+20, _ease=easing:
            (_xs + (_xe - _xs) * _ease((t - _s) / (_e - _s)), _y),
        stay=True)

    # Track line
    track = Line(x1=x_start, y1=y + 20, x2=x_end, y2=y + 20,
                 stroke='#333', stroke_width=1)

    objects.extend([track, label, dot])

canvas.add_objects(*objects)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
