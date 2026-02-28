"""Kepler Orbital Mechanics — equal areas in equal times.

Visualizes an elliptical orbit around a central sun, demonstrating
Kepler's three laws of planetary motion:
  1. Planets orbit in ellipses with the Sun at one focus.
  2. A line from Sun to planet sweeps equal areas in equal times.
  3. T^2 is proportional to a^3 (shown via a second planet).

Uses Newton's method to solve Kepler's equation M = E - e sin(E),
converting mean anomaly (uniform in time) to eccentric anomaly,
then to true anomaly for correct non-uniform orbital speed.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/orbital_mechanics')
canvas.set_background()

# ── Orbital parameters ──────────────────────────────────────────────
CX, CY = 960, 480  # canvas center for orbital display (shifted up for text)

# Planet 1 (inner orbit, higher eccentricity)
a1 = 300            # semi-major axis (pixels)
e1 = 0.6            # eccentricity
b1 = a1 * math.sqrt(1 - e1**2)  # semi-minor axis
c1 = a1 * e1        # focal distance

# Planet 2 (outer orbit, lower eccentricity)
a2 = 450
e2 = 0.3
b2 = a2 * math.sqrt(1 - e2**2)
c2 = a2 * e2

# Sun position: at the right focus of planet 1's ellipse
# Ellipse centered at (CX, CY), foci at (CX +/- c, CY)
# Place sun at left focus so perihelion is on the right
sun_x = CX - c1
sun_y = CY

# Kepler's third law: T^2 proportional to a^3
# Planet 1 orbital period (in animation seconds)
orbit_period_1 = 5.0
# Planet 2: T2/T1 = (a2/a1)^(3/2)
orbit_period_2 = orbit_period_1 * (a2 / a1) ** 1.5

T = 15.0  # total animation duration

# ── Kepler's equation solver ────────────────────────────────────────
def solve_kepler(M, e, tol=1e-10, max_iter=50):
    """Solve M = E - e*sin(E) for E using Newton's method."""
    E = M  # initial guess
    for _ in range(max_iter):
        dE = (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        E -= dE
        if abs(dE) < tol:
            break
    return E

def kepler_position(t_frac, a, e, cx_ellipse, cy_ellipse):
    """Get (x, y) on ellipse at fractional orbit time t_frac in [0, 1).

    The ellipse is centered at (cx_ellipse, cy_ellipse).
    """
    M = 2 * math.pi * t_frac  # mean anomaly
    E = solve_kepler(M, e)     # eccentric anomaly
    # Position on ellipse (parametric via eccentric anomaly)
    b = a * math.sqrt(1 - e**2)
    x = cx_ellipse + a * math.cos(E)
    y = cy_ellipse + b * math.sin(E)
    return x, y

def true_anomaly_from_E(E, e):
    """Convert eccentric anomaly E to true anomaly theta."""
    return 2 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2),
                          math.sqrt(1 - e) * math.cos(E / 2))

# ── Precompute orbit paths (for drawing the ellipse) ────────────────
def ellipse_path_d(a, e, cx_ellipse, cy_ellipse, n_pts=200):
    """Return SVG path d-string for a full ellipse."""
    b = a * math.sqrt(1 - e**2)
    pts = []
    for i in range(n_pts + 1):
        angle = 2 * math.pi * i / n_pts
        x = cx_ellipse + a * math.cos(angle)
        y = cy_ellipse + b * math.sin(angle)
        pts.append((x, y))
    d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
    for px, py in pts[1:]:
        d += f'L{px:.1f},{py:.1f}'
    d += 'Z'
    return d

# ── Sun ─────────────────────────────────────────────────────────────
sun = Circle(r=30, cx=sun_x, cy=sun_y, fill='#FFD700',
             stroke='#FFA500', stroke_width=2, fill_opacity=1, creation=0)
sun_glow = Circle(r=45, cx=sun_x, cy=sun_y, fill='#FFD700',
                  stroke_width=0, fill_opacity=0.15, creation=0)
sun_label = Text(text='Sun', x=sun_x, y=sun_y + 55, font_size=18,
                 fill='#FFD700', stroke_width=0, text_anchor='middle', creation=0)

# ── Orbit ellipse 1 ────────────────────────────────────────────────
orbit1_d = ellipse_path_d(a1, e1, CX, CY)
orbit1_path = Path(orbit1_d, stroke='#58C4DD', stroke_width=1.5,
                   stroke_opacity=0.5, fill_opacity=0, stroke_dasharray='6 3',
                   creation=0)

# ── Planet 1 ────────────────────────────────────────────────────────
planet1_start = 2.0  # animation time when planet starts orbiting

def planet1_pos(t):
    if t < planet1_start:
        return kepler_position(0, a1, e1, CX, CY)
    elapsed = t - planet1_start
    frac = (elapsed / orbit_period_1) % 1.0
    return kepler_position(frac, a1, e1, CX, CY)

planet1 = Dot(r=11, fill='#58C4DD', stroke='#fff', stroke_width=1.5, creation=0)
planet1.c.set_onward(0, planet1_pos)
planet1_label = Text(text='Planet 1', x=0, y=0, font_size=16,
                     fill='#58C4DD', stroke_width=0, text_anchor='middle', creation=0)
planet1_label.x.set_onward(0, lambda t: planet1_pos(t)[0])
planet1_label.y.set_onward(0, lambda t: planet1_pos(t)[1] - 22)

# ── Swept area sectors (Kepler's 2nd law) ────────────────────────────
# Show sectors at regular time intervals to demonstrate equal areas
n_sectors = 6
sector_duration = orbit_period_1 / n_sectors  # equal time intervals
sector_colors = ['#FF6B6B', '#83C167', '#FFFF00', '#C77DFF', '#58C4DD', '#FF9F43']

sectors = []
for i in range(n_sectors):
    sector_start_time = planet1_start + i * sector_duration
    sector_end_time = sector_start_time + sector_duration

    # Precompute the sector shape: sun -> arc from t_start to t_end -> back to sun
    n_arc_pts = 60
    arc_pts = []
    for j in range(n_arc_pts + 1):
        frac_in_sector = j / n_arc_pts
        orbit_frac_start = (i * sector_duration / orbit_period_1) % 1.0
        orbit_frac_end = ((i + 1) * sector_duration / orbit_period_1) % 1.0

        # Interpolate mean anomaly linearly (that is the whole point: equal time = equal M)
        M_start = 2 * math.pi * orbit_frac_start
        M_end = 2 * math.pi * orbit_frac_end
        if M_end < M_start:
            M_end += 2 * math.pi
        M = M_start + frac_in_sector * (M_end - M_start)
        E = solve_kepler(M, e1)
        x = CX + a1 * math.cos(E)
        y = CY + b1 * math.sin(E)
        arc_pts.append((x, y))

    sector_d = f'M{sun_x:.1f},{sun_y:.1f}'
    for px, py in arc_pts:
        sector_d += f'L{px:.1f},{py:.1f}'
    sector_d += 'Z'

    color = sector_colors[i % len(sector_colors)]
    sector = Path(sector_d, fill=color, fill_opacity=0, stroke=color,
                  stroke_width=0.5, stroke_opacity=0, creation=0)

    # Fade sector in as the planet sweeps through it
    appear_time = sector_start_time
    sector.set_opacity(0, start=0)
    sector.set_opacity(0.25, start=appear_time, end=appear_time + sector_duration)

    # Keep sector visible but slightly more transparent after
    sector.set_opacity(0.15, start=appear_time + sector_duration + 0.5,
                       end=appear_time + sector_duration + 0.8)

    sectors.append(sector)

# ── Radius line (Sun to Planet 1) ────────────────────────────────────
radius_line = Line(x1=sun_x, y1=sun_y, x2=0, y2=0,
                   stroke='#fff', stroke_width=1, stroke_opacity=0.4,
                   stroke_dasharray='4 3', creation=0)
radius_line.p2.set_onward(0, planet1_pos)

# ── Orbit ellipse 2 & Planet 2 (Kepler's 3rd law) ──────────────────
# Ellipse 2 is also centered so that the sun is at its left focus
# Sun at sun_x = CX - c1; for orbit 2, center_x2 = sun_x + c2
cx2 = sun_x + c2
cy2 = CY
orbit2_d = ellipse_path_d(a2, e2, cx2, cy2)
orbit2_path = Path(orbit2_d, stroke='#FC6255', stroke_width=1.5,
                   stroke_opacity=0.4, fill_opacity=0, stroke_dasharray='6 3',
                   creation=0)

planet2_start = 8.0

def planet2_pos(t):
    if t < planet2_start:
        return kepler_position(0, a2, e2, cx2, cy2)
    elapsed = t - planet2_start
    frac = (elapsed / orbit_period_2) % 1.0
    return kepler_position(frac, a2, e2, cx2, cy2)

planet2 = Dot(r=8, fill='#FC6255', stroke='#fff', stroke_width=1, creation=0)
planet2.c.set_onward(0, planet2_pos)
planet2_label = Text(text='Planet 2', x=0, y=0, font_size=14,
                     fill='#FC6255', stroke_width=0, text_anchor='middle', creation=0)
planet2_label.x.set_onward(0, lambda t: planet2_pos(t)[0])
planet2_label.y.set_onward(0, lambda t: planet2_pos(t)[1] - 18)

# Fade in orbit 2 and planet 2
orbit2_path.set_opacity(0, start=0)
orbit2_path.set_opacity(1, start=7.5, end=8.5)
planet2.set_opacity(0, start=0)
planet2.set_opacity(1, start=7.8, end=8.5)
planet2_label.set_opacity(0, start=0)
planet2_label.set_opacity(1, start=7.8, end=8.5)

# ── Orbital parameter labels ────────────────────────────────────────
# Semi-major axis line for planet 1
sma_line = Line(x1=CX - a1, y1=CY, x2=CX + a1, y2=CY,
                stroke='#58C4DD', stroke_width=1.5, stroke_opacity=0.6,
                stroke_dasharray='3 3', creation=0)
sma_label = Text(text='a (semi-major axis)', x=CX, y=CY + 20,
                 font_size=14, fill='#58C4DD', stroke_width=0,
                 text_anchor='middle', creation=0)

# Focus markers
focus1 = Dot(r=3, cx=CX - c1, cy=CY, fill='#FFD700', stroke_width=0, creation=0)
focus2 = Dot(r=3, cx=CX + c1, cy=CY, fill='#888', stroke_width=0, creation=0)
focus2_label = Text(text='F2', x=CX + c1, y=CY + 18, font_size=12,
                    fill='#888', stroke_width=0, text_anchor='middle', creation=0)

# Perihelion / Aphelion labels
perihelion_x = CX + a1
aphelion_x = CX - a1
perihelion_label = Text(text='Perihelion', x=perihelion_x, y=CY - 18,
                        font_size=13, fill='#aaa', stroke_width=0,
                        text_anchor='middle', creation=0)
aphelion_label = Text(text='Aphelion', x=aphelion_x, y=CY - 18,
                      font_size=13, fill='#aaa', stroke_width=0,
                      text_anchor='middle', creation=0)

# ── Title ────────────────────────────────────────────────────────────
title = Text(text="Kepler's Laws of Planetary Motion", x=960, y=50,
             font_size=40, fill='#fff', stroke_width=0, text_anchor='middle',
             creation=0)
title.fadein(0, 1)

subtitle = Text(text='Elliptical orbits with equal areas in equal times',
                x=960, y=90, font_size=20, fill='#888', stroke_width=0,
                text_anchor='middle', creation=0)
subtitle.fadein(0.3, 1.3)

# ── Fade-in schedule: 0-2s ──────────────────────────────────────────
sun.fadein(0.5, 1.5)
sun_glow.fadein(0.5, 1.5)
sun_label.fadein(0.8, 1.5)

orbit1_path.fadein(1, 2)
sma_line.fadein(1.2, 2)
sma_label.fadein(1.2, 2)
focus1.fadein(1, 2)
focus2.fadein(1, 2)
focus2_label.fadein(1, 2)
perihelion_label.fadein(1.5, 2)
aphelion_label.fadein(1.5, 2)

planet1.fadein(1.5, 2)
planet1_label.fadein(1.5, 2)
radius_line.fadein(1.5, 2)

# Fade out parameter labels after a bit to reduce clutter
sma_line.fadeout(4, 5)
sma_label.fadeout(4, 5)
focus2.fadeout(4, 5)
focus2_label.fadeout(4, 5)
perihelion_label.fadeout(4, 5)
aphelion_label.fadeout(4, 5)

# ── Kepler's laws text (12-15s) ──────────────────────────────────────
law1 = Text(text="1st Law: Orbits are ellipses with the Sun at one focus",
            x=960, y=820, font_size=22, fill='#83C167', stroke_width=0,
            text_anchor='middle', creation=0)
law1.fadein(12, 13)

law2 = Text(text="2nd Law: Equal areas are swept in equal times",
            x=960, y=855, font_size=22, fill='#FFFF00', stroke_width=0,
            text_anchor='middle', creation=0)
law2.fadein(12.5, 13.5)

# Kepler's 3rd law with actual computed periods
t1_str = f'{orbit_period_1:.1f}'
t2_str = f'{orbit_period_2:.1f}'
law3 = Text(text=f"3rd Law: T\u00b2 \u221d a\u00b3  (T1={t1_str}s, T2={t2_str}s)",
            x=960, y=890, font_size=22, fill='#C77DFF', stroke_width=0,
            text_anchor='middle', creation=0)
law3.fadein(13, 14)

# Eccentricity info
ecc_text = Text(text=f'e1 = {e1}    e2 = {e2}', x=960, y=925,
                font_size=18, fill='#aaa', stroke_width=0,
                text_anchor='middle', creation=0)
ecc_text.fadein(13.5, 14.5)

# ── Speed indicator (shows velocity changing around orbit) ───────────
speed_label = Text(text='', x=0, y=0, font_size=13, fill='#aaa',
                   stroke_width=0, text_anchor='start', creation=0)

def speed_label_x(t):
    if t < planet1_start or t > 12:
        return -100  # off screen
    return planet1_pos(t)[0] + 20

def speed_label_y(t):
    if t < planet1_start or t > 12:
        return -100  # off screen
    return planet1_pos(t)[1] + 5

speed_label.x.set_onward(0, speed_label_x)
speed_label.y.set_onward(0, speed_label_y)

def speed_text_update(t):
    if t < planet1_start or t > 12:
        return ''
    elapsed = t - planet1_start
    frac = (elapsed / orbit_period_1) % 1.0
    M = 2 * math.pi * frac
    E = solve_kepler(M, e1)
    r = a1 * (1 - e1 * math.cos(E))
    v_rel = a1 / r
    if v_rel > 1.2:
        return 'FAST'
    elif v_rel < 0.8:
        return 'slow'
    return ''

speed_label.text.set_onward(0, speed_text_update)

# ── Equal area annotation ────────────────────────────────────────────
area_note = Text(text='Each colored sector has equal area',
                 x=960, y=770, font_size=18, fill='#aaa', stroke_width=0,
                 text_anchor='middle', creation=0)
area_note.set_opacity(0, start=0)
area_note.set_opacity(1, start=5, end=6)
area_note.set_opacity(0, start=11, end=12)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(sun_glow, sun, sun_label)
canvas.add(orbit1_path, sma_line, sma_label)
canvas.add(focus1, focus2, focus2_label)
canvas.add(perihelion_label, aphelion_label)
canvas.add(*sectors)
canvas.add(radius_line, planet1, planet1_label, speed_label)
canvas.add(orbit2_path, planet2, planet2_label)
canvas.add(title, subtitle)
canvas.add(law1, law2, law3, ecc_text)
canvas.add(area_note)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
