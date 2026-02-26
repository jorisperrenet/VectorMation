"""Compute bounding boxes for SVG path strings without external dependencies.

Handles M, L, H, V, C, S, Q, T, A, Z commands (both absolute and relative).
For cubic/quadratic Bezier curves, extrema are found analytically.
For arcs, extrema are computed from the parametric ellipse equations.
"""
from __future__ import annotations

import math
import re
from typing import Any

# Regex to tokenize an SVG path string into commands and numbers
_TOKEN_RE = re.compile(r'([MmZzLlHhVvCcSsQqTtAa])|([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)')


def _tokenize(d):
    """Yield (command_or_None, number_or_None) tuples from an SVG path string."""
    for m in _TOKEN_RE.finditer(d):
        if m.group(1):
            yield m.group(1)
        else:
            yield float(m.group(2))


def _parse_path(d):
    """Parse SVG path string into a list of (command, args) tuples.
    All commands are converted to their absolute uppercase equivalents."""
    tokens: list[Any] = list(_tokenize(d))
    segments = []
    i = 0
    cx, cy = 0.0, 0.0  # current point
    sx, sy = 0.0, 0.0  # subpath start
    cmd = None
    while i < len(tokens):
        token = tokens[i]
        if isinstance(token, str):
            cmd = token
            i += 1
        elif cmd is None:
            i += 1
            continue
        else:
            # Implicit repeat: L after M, same command otherwise
            pass

        if cmd in ('M', 'm'):
            x, y = tokens[i], tokens[i + 1]
            i += 2
            if cmd == 'm':
                x, y = cx + x, cy + y
            cx, cy = x, y
            sx, sy = x, y
            segments.append(('M', [x, y]))
            cmd = 'L' if cmd == 'M' else 'l'
        elif cmd in ('Z', 'z'):
            segments.append(('Z', []))
            cx, cy = sx, sy
            cmd = None
        elif cmd in ('L', 'l'):
            x, y = tokens[i], tokens[i + 1]
            i += 2
            if cmd == 'l':
                x, y = cx + x, cy + y
            segments.append(('L', [cx, cy, x, y]))
            cx, cy = x, y
        elif cmd in ('H', 'h'):
            x = tokens[i]
            i += 1
            if cmd == 'h':
                x = cx + x
            segments.append(('L', [cx, cy, x, cy]))
            cx = x
        elif cmd in ('V', 'v'):
            y = tokens[i]
            i += 1
            if cmd == 'v':
                y = cy + y
            segments.append(('L', [cx, cy, cx, y]))
            cy = y
        elif cmd in ('C', 'c'):
            args = tokens[i:i + 6]
            i += 6
            if cmd == 'c':
                args = [args[0] + cx, args[1] + cy, args[2] + cx, args[3] + cy,
                        args[4] + cx, args[5] + cy]
            segments.append(('C', [cx, cy] + args))
            cx, cy = args[4], args[5]
        elif cmd in ('S', 's'):
            args = tokens[i:i + 4]
            i += 4
            if cmd == 's':
                args = [args[0] + cx, args[1] + cy, args[2] + cx, args[3] + cy]
            # Reflect previous control point
            if segments and segments[-1][0] == 'C':
                prev = segments[-1][1]
                c1x = 2 * cx - prev[4]
                c1y = 2 * cy - prev[5]
            else:
                c1x, c1y = cx, cy
            segments.append(('C', [cx, cy, c1x, c1y, args[0], args[1], args[2], args[3]]))
            cx, cy = args[2], args[3]
        elif cmd in ('Q', 'q'):
            args = tokens[i:i + 4]
            i += 4
            if cmd == 'q':
                args = [args[0] + cx, args[1] + cy, args[2] + cx, args[3] + cy]
            segments.append(('Q', [cx, cy] + args))
            cx, cy = args[2], args[3]
        elif cmd in ('T', 't'):
            args = tokens[i:i + 2]
            i += 2
            if cmd == 't':
                args = [args[0] + cx, args[1] + cy]
            if segments and segments[-1][0] == 'Q':
                prev = segments[-1][1]
                c1x = 2 * cx - prev[2]
                c1y = 2 * cy - prev[3]
            else:
                c1x, c1y = cx, cy
            segments.append(('Q', [cx, cy, c1x, c1y, args[0], args[1]]))
            cx, cy = args[0], args[1]
        elif cmd in ('A', 'a'):
            args = tokens[i:i + 7]
            i += 7
            rx_a, ry_a = abs(args[0]), abs(args[1])
            rotation = args[2]
            large_arc = int(args[3])
            sweep = int(args[4])
            ex, ey = args[5], args[6]
            if cmd == 'a':
                ex, ey = cx + ex, cy + ey
            segments.append(('A', [cx, cy, rx_a, ry_a, rotation, large_arc, sweep, ex, ey]))
            cx, cy = ex, ey
        else:
            # Unknown command, skip
            i += 1
    return segments


def _cubic_extrema(p0, p1, p2, p3):
    """Find t values where a cubic Bezier has extrema (derivative = 0).
    B(t) = (1-t)^3*p0 + 3*(1-t)^2*t*p1 + 3*(1-t)*t^2*p2 + t^3*p3
    B'(t) = a*t^2 + b*t + c where:
    a = -3*p0 + 9*p1 - 9*p2 + 3*p3
    b = 6*p0 - 12*p1 + 6*p2
    c = -3*p0 + 3*p1
    """
    a = -3 * p0 + 9 * p1 - 9 * p2 + 3 * p3
    b = 6 * p0 - 12 * p1 + 6 * p2
    c = -3 * p0 + 3 * p1
    ts = []
    if abs(a) < 1e-12:
        if abs(b) > 1e-12:
            t = -c / b
            if 0 < t < 1:
                ts.append(t)
    else:
        disc = b * b - 4 * a * c
        if disc >= 0:
            sq = math.sqrt(disc)
            for t in ((-b + sq) / (2 * a), (-b - sq) / (2 * a)):
                if 0 < t < 1:
                    ts.append(t)
    return ts


def _quadratic_extrema(p0, p1, p2):
    """Find t value where a quadratic Bezier has extrema.
    B'(t) = 2*(1-t)*(p1-p0) + 2*t*(p2-p1) = 0
    t = (p0-p1) / (p0 - 2*p1 + p2)
    """
    denom = p0 - 2 * p1 + p2
    if abs(denom) < 1e-12:
        return []
    t = (p0 - p1) / denom
    if 0 < t < 1:
        return [t]
    return []


def _cubic_eval(p0, p1, p2, p3, t):
    u = 1 - t
    return u * u * u * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t * t * t * p3


def _quadratic_eval(p0, p1, p2, t):
    u = 1 - t
    return u * u * p0 + 2 * u * t * p1 + t * t * p2


def _arc_bbox(cx_cur, cy_cur, rx, ry, rotation, large_arc, sweep, ex, ey):
    """Compute bounding box of an SVG arc segment."""
    if rx < 1e-12 or ry < 1e-12:
        return (min(cx_cur, ex), min(cy_cur, ey), max(cx_cur, ex), max(cy_cur, ey))

    phi = math.radians(rotation)
    cos_phi, sin_phi = math.cos(phi), math.sin(phi)

    # Step 1: compute center parameterization (SVG spec F.6.5)
    dx2, dy2 = (cx_cur - ex) / 2, (cy_cur - ey) / 2
    x1p = cos_phi * dx2 + sin_phi * dy2
    y1p = -sin_phi * dx2 + cos_phi * dy2

    x1p2, y1p2 = x1p * x1p, y1p * y1p
    rx2, ry2 = rx * rx, ry * ry

    # Correct radii if needed
    lam = x1p2 / rx2 + y1p2 / ry2
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
        rx2, ry2 = rx * rx, ry * ry

    num = max(0, rx2 * ry2 - rx2 * y1p2 - ry2 * x1p2)
    den = rx2 * y1p2 + ry2 * x1p2
    sq = math.sqrt(num / den) if den > 1e-12 else 0
    if large_arc == sweep:
        sq = -sq

    cxp = sq * rx * y1p / ry
    cyp = -sq * ry * x1p / rx

    # Center in original coords
    center_x = cos_phi * cxp - sin_phi * cyp + (cx_cur + ex) / 2
    center_y = sin_phi * cxp + cos_phi * cyp + (cy_cur + ey) / 2

    # Step 2: compute start and end angles
    def angle(ux, uy, vx, vy):
        n = math.sqrt(ux * ux + uy * uy) * math.sqrt(vx * vx + vy * vy)
        if n < 1e-12:
            return 0
        c = (ux * vx + uy * vy) / n
        c = max(-1, min(1, c))
        a = math.acos(c)
        if ux * vy - uy * vx < 0:
            a = -a
        return a

    theta1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dtheta = angle((x1p - cxp) / rx, (y1p - cyp) / ry,
                   (-x1p - cxp) / rx, (-y1p - cyp) / ry)

    if sweep == 0 and dtheta > 0:
        dtheta -= 2 * math.pi
    elif sweep == 1 and dtheta < 0:
        dtheta += 2 * math.pi

    theta2 = theta1 + dtheta

    # Step 3: find extrema
    # The parametric ellipse: x(t) = cx + rx*cos(t)*cos(phi) - ry*sin(t)*sin(phi)
    #                         y(t) = cy + rx*cos(t)*sin(phi) + ry*sin(t)*cos(phi)
    # dx/dt = 0 => tan(t) = -ry*sin(phi) / (rx*cos(phi)) for x
    # dy/dt = 0 => tan(t) = ry*cos(phi) / (rx*sin(phi)) for y

    xmin, xmax = min(cx_cur, ex), max(cx_cur, ex)
    ymin, ymax = min(cy_cur, ey), max(cy_cur, ey)

    # Critical angles for x extrema
    tx = math.atan2(-ry * sin_phi, rx * cos_phi)
    # Critical angles for y extrema
    ty = math.atan2(ry * cos_phi, rx * sin_phi)

    t1 = min(theta1, theta2)
    t2 = max(theta1, theta2)

    for base in (tx, ty):
        for k in range(-4, 5):
            t = base + k * math.pi
            if t1 <= t <= t2:
                px = center_x + rx * math.cos(t) * cos_phi - ry * math.sin(t) * sin_phi
                py = center_y + rx * math.cos(t) * sin_phi + ry * math.sin(t) * cos_phi
                xmin, xmax = min(xmin, px), max(xmax, px)
                ymin, ymax = min(ymin, py), max(ymax, py)

    return (xmin, ymin, xmax, ymax)


def path_bbox(d):
    """Compute the bounding box of an SVG path string.

    Args:
        d: SVG path d attribute string

    Returns:
        (xmin, xmax, ymin, ymax) matching svgpathtools convention
    """
    if not d or not d.strip():
        return (0, 0, 0, 0)

    segments = _parse_path(d)
    if not segments:
        return (0, 0, 0, 0)

    xmin = float('inf')
    xmax = float('-inf')
    ymin = float('inf')
    ymax = float('-inf')

    def update(x, y):
        nonlocal xmin, xmax, ymin, ymax
        xmin = min(xmin, x)
        xmax = max(xmax, x)
        ymin = min(ymin, y)
        ymax = max(ymax, y)

    for cmd, args in segments:
        if cmd == 'M':
            update(args[0], args[1])
        elif cmd == 'L':
            update(args[0], args[1])
            update(args[2], args[3])
        elif cmd == 'C':
            # args: x0, y0, c1x, c1y, c2x, c2y, ex, ey
            x0, y0, c1x, c1y, c2x, c2y, ex, ey = args
            update(x0, y0)
            update(ex, ey)
            for t in _cubic_extrema(x0, c1x, c2x, ex):
                update(_cubic_eval(x0, c1x, c2x, ex, t), _cubic_eval(y0, c1y, c2y, ey, t))
            for t in _cubic_extrema(y0, c1y, c2y, ey):
                update(_cubic_eval(x0, c1x, c2x, ex, t), _cubic_eval(y0, c1y, c2y, ey, t))
        elif cmd == 'Q':
            # args: x0, y0, c1x, c1y, ex, ey
            x0, y0, c1x, c1y, ex, ey = args
            update(x0, y0)
            update(ex, ey)
            for t in _quadratic_extrema(x0, c1x, ex):
                update(_quadratic_eval(x0, c1x, ex, t), _quadratic_eval(y0, c1y, ey, t))
            for t in _quadratic_extrema(y0, c1y, ey):
                update(_quadratic_eval(x0, c1x, ex, t), _quadratic_eval(y0, c1y, ey, t))
        elif cmd == 'A':
            sx_a, sy_a, rx_a, ry_a, rot, la, sw, ex_a, ey_a = args
            bx1, by1, bx2, by2 = _arc_bbox(sx_a, sy_a, rx_a, ry_a, rot, la, sw, ex_a, ey_a)
            update(bx1, by1)
            update(bx2, by2)

    if xmin == float('inf'):
        return (0, 0, 0, 0)
    return (xmin, xmax, ymin, ymax)
