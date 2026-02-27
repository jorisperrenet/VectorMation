import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/stack_viz')
canvas.set_background()

# Create a stack with initial values
stack = StackViz([10, 20, 30], cell_width=140, cell_height=55)
stack.fadein(0, 1)

title = Text(text='Stack: Push & Pop', x=960, y=80,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Push new values
stack.push(40, start=1.5, end=2)
stack.push(50, start=2.5, end=3)

# Pop values
stack.pop(start=4, end=4.5)
stack.pop(start=5, end=5.5)

canvas.add_objects(stack, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
