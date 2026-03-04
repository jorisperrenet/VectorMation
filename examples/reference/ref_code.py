"""Code block with syntax highlighting."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

code = Code('''def greet(name):
    return f"Hello, {name}!"

print(greet("World"))''', language='python', x=560, y=350, font_size=28)

v.add(code)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_code.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
