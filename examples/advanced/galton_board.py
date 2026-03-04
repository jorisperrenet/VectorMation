"""Galton Board simulation -- balls bounce through pegs into buckets,
forming a binomial/normal distribution.

Inspired by 3Blue1Brown's Central Limit Theorem video (2023).
"""
import math
import random
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from vectormation.objects import *

random.seed(42)

args = parse_args()

# --- Configuration ---
N_ROWS = 7
N_PEGS_ROW = 11
SPACING = 90  # px between pegs
PEG_RADIUS = 8
BALL_RADIUS = 10
TOP_Y = 120
N_BALLS = 400

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/galton_board')
v.set_background(fill='#1a1a2e')

# --- Build pegs ---
pegs = VCollection(creation=0)
peg_positions = []  # row -> list of (cx, cy)

center_x = CANVAS_WIDTH / 2
for row in range(N_ROWS):
    row_pegs = []
    n_in_row = N_PEGS_ROW - (row % 2)
    offset_x = center_x - (n_in_row - 1) * SPACING / 2
    cy = TOP_Y + row * SPACING * math.sqrt(3) / 2
    for i in range(n_in_row):
        cx = offset_x + i * SPACING
        peg = Dot(r=PEG_RADIUS, cx=cx, cy=cy, fill='#888',
                  fill_opacity=1, stroke='#aaa', stroke_width=1, creation=0, z=0)
        pegs.add(peg)
        row_pegs.append((cx, cy))
    peg_positions.append(row_pegs)

pegs.stagger_fadein(start=0, end=1.5, shift_dir=DOWN)

# --- Build buckets using U-shaped Lines ---
bucket_y_top = TOP_Y + N_ROWS * SPACING * math.sqrt(3) / 2 + SPACING * 0.6
bucket_height = CANVAS_HEIGHT - bucket_y_top - 40
bucket_width = SPACING * 0.8

bottom_row = peg_positions[-1]
bucket_centers = []
for i in range(len(bottom_row) + 1):
    if i == 0:
        bx = bottom_row[0][0] - SPACING / 2
    elif i == len(bottom_row):
        bx = bottom_row[-1][0] + SPACING / 2
    else:
        bx = (bottom_row[i - 1][0] + bottom_row[i][0]) / 2
    bucket_centers.append(bx)

buckets = VCollection(creation=0)
for bx in bucket_centers:
    hw = bucket_width / 2
    bucket = Lines(
        (bx - hw, bucket_y_top),
        (bx - hw, bucket_y_top + bucket_height),
        (bx + hw, bucket_y_top + bucket_height),
        (bx + hw, bucket_y_top),
        stroke='#555', stroke_width=2, fill_opacity=0, creation=0,
    )
    buckets.add(bucket)

buckets.fadein(start=0.5, end=1.5)


# --- Simulate ball trajectories ---
def simulate_ball():
    """Simulate a ball bouncing through the peg grid.
    Returns list of (x, y, time_offset) waypoints."""
    x = center_x
    y = TOP_Y - 60  # start above pegs
    waypoints = [(x, y, 0)]
    t = 0
    fall_time = 0.10

    for row in range(N_ROWS):
        row_pegs = peg_positions[row]
        direction = random.choice([-1, 1])
        closest = min(row_pegs, key=lambda p: abs(p[0] - x))
        x = closest[0] + direction * SPACING / 2
        y = closest[1] + SPACING * math.sqrt(3) / 2 * 0.5
        t += fall_time
        waypoints.append((x, y, t))
        y = closest[1] + SPACING * math.sqrt(3) / 2
        t += fall_time * 0.5
        waypoints.append((x, y, t))

    closest_bucket = min(range(len(bucket_centers)),
                         key=lambda i: abs(bucket_centers[i] - x))
    bx = bucket_centers[closest_bucket]
    t += fall_time
    waypoints.append((bx, bucket_y_top + 20, t))

    return waypoints, closest_bucket


# --- Color palette: gradient from center (warm) to edges (cool) ---
n_buckets = len(bucket_centers)
mid = (n_buckets - 1) / 2
BUCKET_COLORS = []
for bi in range(n_buckets):
    frac = abs(bi - mid) / mid  # 0 at center, 1 at edges
    # Gold at center → teal at edges
    r = int(255 * (1 - frac * 0.6))
    g = int(200 + 55 * frac)
    b = int(50 + 180 * frac)
    BUCKET_COLORS.append(f'#{r:02x}{g:02x}{b:02x}')


# --- Eased interpolation for ball motion ---
def _ease_quad_in(t):
    """Quadratic ease-in: balls accelerate as they fall."""
    return t * t


# --- Create balls with slow-then-fast pacing ---
bucket_counts = [0] * len(bucket_centers)
balls = []
ball_start = 2.0

# First 15 balls: slow (interval=0.3) so viewer can follow trajectories
# Remaining 45: fast (interval=0.08) to fill up quickly
SLOW_COUNT = 15
SLOW_INTERVAL = 0.2
FAST_INTERVAL = 0.005

for i in range(N_BALLS):
    waypoints, bucket_idx = simulate_ball()
    ball_count = bucket_counts[bucket_idx]
    bucket_counts[bucket_idx] += 1

    bx = bucket_centers[bucket_idx]
    final_y = bucket_y_top + bucket_height - BALL_RADIUS - ball_count * BALL_RADIUS * 0.3

    if i < SLOW_COUNT:
        start_t = ball_start + i * SLOW_INTERVAL
    else:
        start_t = ball_start + SLOW_COUNT * SLOW_INTERVAL + (i - SLOW_COUNT) * FAST_INTERVAL
    total_fall = waypoints[-1][2]

    # Color by destination bucket
    color = BUCKET_COLORS[bucket_idx]
    ball = Dot(r=BALL_RADIUS, cx=center_x, cy=TOP_Y - 60,
               fill=color, fill_opacity=0.9, stroke=lighten(color, 0.3),
               stroke_width=1, creation=start_t, z=1)

    # Animate through waypoints with eased motion
    for j in range(len(waypoints) - 1):
        x0, y0, t0 = waypoints[j]
        x1, y1, t1 = waypoints[j + 1]
        t_s = start_t + t0
        t_e = start_t + t1
        if t_e > t_s:
            ball.c.set(t_s, t_e,
                       lambda t, _s=t_s, _e=t_e, _x0=x0, _y0=y0, _x1=x1, _y1=y1:
                       (
                           _x0 + (_x1 - _x0) * _ease_quad_in((t - _s) / (_e - _s)),
                           _y0 + (_y1 - _y0) * _ease_quad_in((t - _s) / (_e - _s)),
                       ),
                       stay=False)

    # Settle into bucket
    settle_start = start_t + total_fall
    ball.c.set_onward(settle_start, (bx, final_y))

    balls.append(ball)

# --- Labels ---
title = Text(text='Galton Board', x=CANVAS_WIDTH / 2, y=50,
             font_size=42, text_anchor='middle', fill='#fff',
             stroke_width=0, creation=0)
title.fadein(start=0, end=1)

subtitle = Text(text='Central Limit Theorem', x=CANVAS_WIDTH / 2, y=85,
                font_size=24, text_anchor='middle', fill='#888',
                stroke_width=0, creation=0)
subtitle.fadein(start=0.5, end=1.5)

# --- Ball counter ---
last_ball_start = ball_start + SLOW_COUNT * SLOW_INTERVAL + (N_BALLS - SLOW_COUNT) * FAST_INTERVAL
last_ball_end = last_ball_start + waypoints[-1][2]  # approximate


# --- Normal curve overlay (appears shortly after balls settle) ---
curve_start = last_ball_end + 0.5
mu = center_x
sigma = SPACING * math.sqrt(N_ROWS) / 2
curve_points = []
for i in range(200):
    x = mu - 4 * sigma + i * 8 * sigma / 199
    y_val = math.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))
    y_screen = bucket_y_top + bucket_height - y_val * sigma * bucket_height * 3
    curve_points.append((x, y_screen))

normal_curve = Lines(*curve_points, stroke='#FF6B6B', stroke_width=3,
                     fill_opacity=0, creation=curve_start, z=2)
normal_curve.create(start=curve_start, end=curve_start + 1.5)

curve_label = TexObject(r'$\mathcal{N}(\mu, \sigma^2)$',
                        x=center_x + 280, y=bucket_y_top - 25,
                        font_size=28, fill='#FF6B6B', creation=curve_start)
curve_label.fadein(start=curve_start, end=curve_start + 1)

# --- Add everything to canvas ---
v.add_objects(title, subtitle, buckets, pegs, *balls, normal_curve, curve_label)

total_time = curve_start + 3
if args.for_docs:
    v.export_video('docs/source/_static/videos/galton_board.mp4', fps=30, end=total_time)
if not args.for_docs:
    v.browser_display(start=args.start or 0, end=args.end or total_time,
    fps=args.fps, port=args.port)
