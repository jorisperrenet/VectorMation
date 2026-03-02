import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/code_highlight')
canvas.set_background()

# Show syntax-highlighted Python code
code = Code("""def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b""",
    language='python',
    font_size=32,
)
code.fadein(0, 1)

# Add a title
title = Text(text='Fibonacci', x=960, y=100, font_size=56,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(code, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/code_highlight.mp4', fps=30, end=2)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
