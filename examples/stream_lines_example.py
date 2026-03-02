import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/stream_lines')
canvas.set_background()

# Create stream lines for a dipole-like field
def dipole_field(x, y):
    # Two sources of opposite sign
    cx1, cy1 = 760, 540
    cx2, cy2 = 1160, 540
    dx1, dy1 = x - cx1, y - cy1
    r1_sq = dx1**2 + dy1**2 + 100
    dx2, dy2 = x - cx2, y - cy2
    r2_sq = dx2**2 + dy2**2 + 100
    vx = dx1 / r1_sq - dx2 / r2_sq
    vy = dy1 / r1_sq - dy2 / r2_sq
    return (vx * 5000, vy * 5000)

sl = StreamLines(
    dipole_field,
    x_range=(100, 1820, 100),
    y_range=(80, 1000, 80),
    n_steps=60, step_size=8,
    stroke='#58C4DD', stroke_width=1.5,
)
sl.fadein(0, 1.5)

# Mark the source and sink
source = Dot(cx=760, cy=540, r=10, fill='#FF6666', stroke_width=0)
sink = Dot(cx=1160, cy=540, r=10, fill='#6666FF', stroke_width=0)
source.fadein(0, 0.5)
sink.fadein(0, 0.5)

src_label = Text(text='+', x=760, y=510, font_size=32,
                 fill='#FF6666', stroke_width=0, text_anchor='middle')
snk_label = Text(text='\u2013', x=1160, y=510, font_size=32,
                 fill='#6666FF', stroke_width=0, text_anchor='middle')

canvas.add_objects(sl, source, sink, src_label, snk_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/stream_lines_example.mp4', fps=30, end=2)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
