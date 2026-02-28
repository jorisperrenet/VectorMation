"""Showcase VCollection animation methods: fadein, fadeout, grow, spin, etc."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/collection_animations')

# Create a group of circles
circles = VGroup(*[
    Circle(r=30, cx=400 + i * 80, cy=200, fill=c, fill_opacity=0.8, stroke_width=2)
    for i, c in enumerate(('#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
                           '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'))
])

# Fade in the whole group at once
circles.fadein(start=0, end=1.5)

# Create some rectangles
rects = VGroup(*[
    RoundedRectangle(60, 40, x=400 + i * 80, y=400, corner_radius=8, fill=c, fill_opacity=0.8)
    for i, c in enumerate(('#E74C3C', '#3498DB', '#2ECC71', '#F39C12',
                           '#9B59B6', '#1ABC9C', '#E67E22', '#34495E'))
])

# Grow from center
rects.grow_from_center(start=2, end=3.5)

# Create stars
stars = VGroup(*[
    Star(5, outer_radius=25, inner_radius=12, cx=400 + i * 80, cy=600,
         fill='#FFD700', fill_opacity=0.9, stroke='#DAA520')
    for i in range(8)
])

# Spin in
stars.spin_in(start=4, end=5.5)

# Indicate the circles
circles.indicate(start=6, end=7)

# Fade out everything with stagger
circles.fadeout(start=8, end=9)
rects.fadeout(start=8.3, end=9.3)
stars.spin_out(start=8.6, end=9.6)

v.add(circles, rects, stars)
if not args.no_display:
    v.browser_display(end=args.duration or 10, fps=args.fps, port=args.port, hot_reload=args.hot_reload)
