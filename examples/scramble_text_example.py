import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/scramble_text')
canvas.set_background()

# Scramble decode effect
heading = Text(text='VECTORMATION', x=960, y=250,
               font_size=72, fill='#58C4DD', stroke_width=0, text_anchor='middle')
heading.scramble(0, 2)

subtitle = Text(text='SVG Animation Library', x=960, y=340,
                font_size=36, fill='#83C167', stroke_width=0, text_anchor='middle')
subtitle.scramble(1, 3)

# Typewriter for comparison
typed = Text(text='> pip install vectormation', x=300, y=500,
             font_size=28, fill='#FFFF00', stroke_width=0)
typed.typewrite(2, 4, cursor='_')

canvas.add_objects(heading, subtitle, typed)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
