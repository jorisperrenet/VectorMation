import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/code_highlight_lines')
canvas.set_background()

code = Code("""
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b
""", language='python', x=500, y=200, font_size=28, line_height=1.6)
code.fadein(0, 1)

# Highlight the base case (lines 2-3)
hl1 = code.highlight_lines([2, 3], start=1.5, end=3, color='#83C167', opacity=0.2)

# Highlight the loop (lines 5-6)
hl2 = code.highlight_lines([5, 6], start=3.5, end=5, color='#58C4DD', opacity=0.2)

# Highlight the return (line 7)
hl3 = code.highlight_lines(7, start=5.5, end=7, color='#FFFF00', opacity=0.2)

title = Text(text='Code Walkthrough', x=960, y=100,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(hl1, hl2, hl3, code, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
