import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/spline_follow')
canvas.set_background()

# Draw waypoint dots
waypoints = [(200, 400), (500, 200), (900, 600), (1300, 300), (1700, 500)]
for px, py in waypoints:
    dot = Dot(cx=px, cy=py, fill='#555', fill_opacity=0.5)
    dot.fadein(0, 0.5)
    canvas.add_objects(dot)

# A circle following a smooth spline through the waypoints
ball = Circle(r=25, cx=200, cy=400, fill='#58C4DD', fill_opacity=0.9)
ball.fadein(0, 0.5)
ball.follow_spline(waypoints, start=0.5, end=4)

# Draw the spline path for reference
path_parts = [f'M{waypoints[0][0]},{waypoints[0][1]}']
n = len(waypoints)
for i in range(n - 1):
    p0 = waypoints[max(i - 1, 0)]
    p1 = waypoints[i]
    p2 = waypoints[min(i + 1, n - 1)]
    p3 = waypoints[min(i + 2, n - 1)]
    c1x = p1[0] + (p2[0] - p0[0]) / 6
    c1y = p1[1] + (p2[1] - p0[1]) / 6
    c2x = p2[0] - (p3[0] - p1[0]) / 6
    c2y = p2[1] - (p3[1] - p1[1]) / 6
    path_parts.append(f'C{c1x},{c1y} {c2x},{c2y} {p2[0]},{p2[1]}')
guide = Path(' '.join(path_parts), stroke='#83C167', stroke_width=2,
             stroke_opacity=0.4, fill_opacity=0)
guide.fadein(0, 0.5)

title = Text(text='Spline Path Following', x=960, y=80,
             font_size=48, fill='#FFFF00', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(guide, ball, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
