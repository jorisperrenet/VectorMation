import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/variable')
canvas.set_background()

# Create a variable display that tracks a changing value
var = Variable('x', 0)
var.fadein(0, 0.5)
var.to_edge(UP, start_time=0)
var.animate_value(10, 0.5, 3)  # animate from 0 to 10

# Show a circle whose radius grows with the value
circle = Circle(r=20, fill='#58C4DD', fill_opacity=0.5)
circle.scale(5, start=0.5, end=3)

canvas.add_objects(var, circle)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
