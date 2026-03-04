"""StandingWave: third harmonic."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

wave = StandingWave(
    x1=300, y1=540, x2=1620, y2=540,
    amplitude=100, harmonics=3, frequency=2.0,
    start=0, end=5, stroke='#58C4DD', stroke_width=3,
)

v.add(wave)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_standing_wave.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
