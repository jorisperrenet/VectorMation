import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

# Initialize the animation frame
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/rotating_morph')
canvas.set_background()

# Create a circle and a square
circle = Circle(r=150, cx=500, cy=500, fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD')
square = Rectangle(250, 250, x=575, y=375, fill='#FC6255', fill_opacity=0.8, stroke='#FC6255')

# Fade in the circle first
circle.fadein(start=0, end=1)

# Morph the circle into the square with a 360-degree spin
morph = MorphObject(circle, square, start=1.5, end=4, rotation_degrees=360)

canvas.add_objects(circle, morph, square)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/rotating_morph.mp4', fps=30, end=5)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
