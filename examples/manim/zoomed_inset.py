"""Zoomed inset camera: magnify a region of the canvas."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation import (
    VectorMathAnim, Dot, Text, ZoomedInset, parse_args,
    LinearGradient, Circle
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/zoomed_inset')

# Gradient canvas background (mimics the pixelated ImageMobject in Manim)
grad = LinearGradient(
    [('0%', '#001430'), ('25%', '#643200'), ('50%', '#1e6400'), ('75%', '#0000c8'),
     ('100%', '#ff0021')],
    x1='0%', y1='0%', x2='100%', y2='100%',
)
canvas.add_def(grad)
canvas.set_background(fill=grad)

# Create some small objects that benefit from zooming
for i in range(5):
    d = Dot(cx=400 + i * 30, cy=540, r=6, fill='#e94560')
    canvas.add_objects(d)
    d.fadein(start=0, end=0.5)

label = Text('tiny dots', x=460, y=590, font_size=14, text_anchor='middle')
canvas.add_objects(label)
label.fadein(start=0, end=0.5)

# Small shape in the destination area so the inset has content after moving
cir = Circle(r=30, cx=900, cy=350, fill='BLUE', stroke='#58C4DD')
cir_label = Text('tiny circle', x=900, y=415, font_size=14, text_anchor='middle')
canvas.add_objects(cir, cir_label)

# Source and display must share the same aspect ratio (3:2 here)
zi = ZoomedInset(
    canvas,
    source=(360, 480, 200, 133),     # 3:2 region around dots
    display=(1100, 200, 600, 400),   # 3:2 display area
    frame_color='#FFFF00',
    display_color='#FFFF00',
)
canvas.add_objects(zi)
zi.fadein(start=0.5, end=1)

# Animate the source sweeping across the canvas
zi.move_source(800, 300, start=2, end=4)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/zoomed_inset.mp4', fps=30)
if not args.for_docs:
    canvas.browser_display(start=0, end=5, fps=args.fps, port=args.port)
