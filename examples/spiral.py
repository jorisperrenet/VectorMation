import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()


# Initialize the animation frame
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/spiral')
canvas.set_background()

# Draw the objects
point = Dot()
trace = Trace(point.c)
# point.c.move_to(0, 5, (900, 500))
point.c.set(0, 5, lambda t: (t*80 + 500, 500))
point.c.rotate_around(0, 5, (500, 500), 360*4)

# Add the objects to the canvas
canvas.add_objects(trace, point)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/spiral.mp4', fps=30, end=6)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
