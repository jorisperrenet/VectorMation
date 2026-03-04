"""ZoomedInset Demo — magnify a region of the canvas."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/zoomed_inset')
canvas.set_background()

title = TexObject(r'ZoomedInset', x=960, y=70, font_size=52,
                  fill='#FFFFFF', stroke_width=0, anchor='center')
title.fadein(0.0, 0.5)
canvas.add(title)

# --- Small detailed scene to magnify (left side) ---
source_label = TexObject(r'Source region', x=350, y=770, font_size=22,
                         fill='#FFFFFF', stroke_width=0, anchor='center')
source_label.fadein(0.3, 0.7)
canvas.add(source_label)

tiny_sq = Square(side=40, x=300, y=550, fill='#4ECDC4',
                 stroke='#FFFFFF', stroke_width=1)
tiny_sq.fadein(0.0, 0.4)
canvas.add(tiny_sq)

tiny_circle = Circle(r=18, cx=360, cy=575, fill='#E84D60',
                     stroke='#FFFFFF', stroke_width=1)
tiny_circle.fadein(0.0, 0.4)
canvas.add(tiny_circle)

tiny_tri = EquilateralTriangle(side_length=35, cx=330, cy=510,
                               fill='#FFFF00', fill_opacity=0.6,
                               stroke='#FFFF00', stroke_width=1)
tiny_tri.fadein(0.0, 0.4)
canvas.add(tiny_tri)

tiny_dot1 = Dot(cx=310, cy=490, r=6, fill='#9B59B6', stroke_width=0)
tiny_dot2 = Dot(cx=370, cy=530, r=5, fill='#83C167', stroke_width=0)
tiny_dot3 = Dot(cx=295, cy=590, r=7, fill='#F5A623', stroke_width=0)
for d in [tiny_dot1, tiny_dot2, tiny_dot3]:
    d.fadein(0.0, 0.4)
    canvas.add(d)

# Connector line from source to display
connect_line = DashedLine(x1=420, y1=500, x2=600, y2=300,
                          stroke='#FFFF00', stroke_width=1, stroke_opacity=0.5)
connect_line.fadein(0.4, 0.8)
canvas.add(connect_line)

# ZoomedInset: magnify the tiny scene
zoomed_inset = ZoomedInset(
    canvas,
    source=(270, 475, 130, 140),
    display=(600, 200, 700, 600),
    creation=0, z=100,
    frame_color='#FFFF00', display_color='#FFFF00', frame_width=2,
)
zoomed_inset.fadein(0.5, 1.0)
canvas.add(zoomed_inset)

zoom_label = TexObject(r'Magnified detail', x=950, y=830, font_size=24,
                       fill='#FFFF00', stroke_width=0, anchor='center')
zoom_label.fadein(0.8, 1.2)
canvas.add(zoom_label)

T = 4.0
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/zoomed_inset.mp4', fps=30, end=T)
if not args.for_docs:
    canvas.browser_display(start=args.start or 0, end=args.end or T, fps=args.fps, port=args.port)
