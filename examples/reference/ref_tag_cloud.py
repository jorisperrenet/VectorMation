"""TagCloud with weighted words."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

cloud = TagCloud(
    data=[
        ('Python', 10), ('Animation', 8), ('SVG', 7), ('Math', 6),
        ('Vector', 5), ('Graphics', 4), ('Code', 3), ('Design', 3),
        ('Canvas', 2), ('Render', 2),
    ],
    x=560, y=400, width=800,
    colors=['#58C4DD', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#3498DB'],
)

v.add(cloud)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_tag_cloud.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
