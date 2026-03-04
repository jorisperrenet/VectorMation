"""MorphObject: star morphing into a circle with rotation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

star = Star(5, outer_radius=140, inner_radius=60, fill='#F1C40F', fill_opacity=0.9, stroke='#F1C40F')
circle = Circle(r=120, fill='#9B59B6', fill_opacity=0.9, stroke='#9B59B6')

morph = MorphObject(star, circle, start=0.3, end=2.3, rotation_degrees=180)

v.add(morph)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_morph2.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
