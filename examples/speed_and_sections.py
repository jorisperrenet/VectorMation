import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

# Initialize the animation frame
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/speed_and_sections')
canvas.set_background()

# Section 1: A circle appears
circle = Circle(r=80, cx=300, cy=500, fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD')
circle.write(start=0, end=2)
canvas.add_section(2)

# Section 2: A square appears
square = Rectangle(140, 140, x=430, y=430, fill='#FC6255', fill_opacity=0.8,
                   stroke='#FC6255', rx=5, ry=5)
square.write(start=2, end=4)
canvas.add_section(4)

# Section 3: A triangle appears
tri = EquilateralTriangle(160, cx=700, cy=500, fill='#83C167', fill_opacity=0.8, stroke='#83C167')
tri.center_to_pos(700, 500)  # Align visual centre with the other shapes
tri.write(start=4, end=6)

# Instructions text
hint = Text(text='Press Space to advance sections, +/- to change speed',
            x=150, y=950, font_size=16, fill='#888', stroke_width=0)

canvas.add_objects(circle, square, tri, hint)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/speed_and_sections.mp4', fps=30, end_time=7)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
