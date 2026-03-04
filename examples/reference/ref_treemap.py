"""TreeMap visualization of category sizes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = TreeMap(
    data=[
        ('Python', 35),
        ('JavaScript', 28),
        ('TypeScript', 18),
        ('Rust', 12),
        ('Go', 10),
        ('Java', 8),
        ('C++', 6),
        ('Ruby', 4),
    ],
    x=260, y=140, width=1400, height=800,
    font_size=18,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_treemap.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
