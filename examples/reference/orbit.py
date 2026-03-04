"""Planet orbiting a point."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

sun = Dot(cx=960, cy=540, r=30, fill='#FFFF00')
sun.fadein(start=0, end=0.5)

planet = Dot(cx=1200, cy=540, r=12, fill='#58C4DD')
planet.fadein(start=0, end=0.5)
planet.orbit(960, 540, start=0.5, end=4.5)

trail = planet.trace_path(start=0.5, end=4.5, stroke='#58C4DD',
                          stroke_width=1, stroke_opacity=0.4)

v.add(sun, trail, planet)
if args.for_docs:
    v.export_video('docs/source/_static/videos/orbit.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
