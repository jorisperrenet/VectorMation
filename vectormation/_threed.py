"""3D objects: ThreeDAxes, Surface, primitives (Line3D, Dot3D, Arrow3D, etc.)."""
import math
from copy import deepcopy
from xml.sax.saxutils import escape as _xml_escape

import vectormation.easings as easings
import vectormation.attributes as attributes
from vectormation._base import VObject, VCollection, _lerp
from vectormation._constants import TEXT_Y_OFFSET, ORIGIN, _normalize
from vectormation._axes import _nice_ticks

# ---------------------------------------------------------------------------
# Projection helpers
# ---------------------------------------------------------------------------

def _project_point(x, y, z, phi, theta, scale, cx, cy):
    """Orthographic projection of (x, y, z) to (svg_x, svg_y, depth)."""
    sp, cp = math.sin(phi), math.cos(phi)
    st, ct = math.sin(theta), math.cos(theta)
    screen_x = -st * x + ct * y
    screen_y = -cp * ct * x - cp * st * y + sp * z
    depth = sp * ct * x + sp * st * y + cp * z
    svg_x = cx + screen_x * scale
    svg_y = cy - screen_y * scale
    return svg_x, svg_y, depth

def _face_normal(p0, p1, p2):
    """Cross product of (p1 - p0) x (p2 - p0)."""
    ax, ay, az = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    bx, by, bz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    return (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx)

def _parse_color_to_rgb(color_str):
    """Parse '#rrggbb' or '#rgb' to (r, g, b) ints."""
    c = color_str.lstrip('#')
    if len(c) == 3:
        c = c[0] * 2 + c[1] * 2 + c[2] * 2
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)

def _shade_color(base_rgb, normal, light_dir):
    """Lambertian shading returning 'rgb(r,g,b)'."""
    nx, ny, nz = normal
    mag = math.hypot(nx, ny, nz) or 1
    nx, ny, nz = nx / mag, ny / mag, nz / mag
    lx, ly, lz = light_dir
    dot = nx * lx + ny * ly + nz * lz
    # Ambient + diffuse
    intensity = max(0.25, min(1.0, 0.3 + 0.7 * abs(dot)))
    r = min(255, int(base_rgb[0] * intensity))
    g = min(255, int(base_rgb[1] * intensity))
    b = min(255, int(base_rgb[2] * intensity))
    return f'rgb({r},{g},{b})'

def _arrow_tip_points(sx0, sy0, sx1, sy1, tip_length, tip_radius):
    """Compute triangle tip vertices for an arrow from (sx0,sy0) to (sx1,sy1)."""
    dx, dy = sx1 - sx0, sy1 - sy0
    ux, uy = _normalize(dx, dy)
    px, py = -uy, ux
    return ((sx1 - ux * tip_length + px * tip_radius,
             sy1 - uy * tip_length + py * tip_radius),
            (sx1 - ux * tip_length - px * tip_radius,
             sy1 - uy * tip_length - py * tip_radius))

def _flat_quad_func(corner, u_dir, v_dir):
    """Return parametric (u,v)->3D point for a flat quad: corner + u*u_dir + v*v_dir."""
    cx, cy, cz = corner
    ux, uy, uz = u_dir
    vx, vy, vz = v_dir
    def f(u, v):
        return (cx + u * ux + v * vx, cy + u * uy + v * vy, cz + u * uz + v * vz)
    return f

def _polyline_patch(points_3d, axes, time, stroke, stroke_width):
    """Project 3D points and return a (depth, svg_polyline) patch."""
    pts = []
    total_depth = 0
    for x, y, z in points_3d:
        sx, sy, d = axes.project_point(x, y, z, time)
        pts.append(f'{sx:.1f},{sy:.1f}')
        total_depth += d
    depth = total_depth / len(pts) if pts else 0
    svg = (f'<polyline points="{" ".join(pts)}" fill="none" '
           f'stroke="{stroke}" stroke-width="{stroke_width}"/>')
    return (depth, svg)

def _frange(start, stop, step):
    """Generate float range values."""
    vals = []
    v = start
    while v <= stop + 1e-9:
        vals.append(v)
        v += step
    return vals

# ---------------------------------------------------------------------------
# ThreeDAxes
# ---------------------------------------------------------------------------

class ThreeDAxes(VCollection):
    """3D coordinate axes with camera control, ticks, labels, and depth-sorted rendering."""

    def __init__(self, x_range=(-3, 3), y_range=(-3, 3), z_range=(-3, 3),
                 cx=ORIGIN[0], cy=ORIGIN[1], scale=160,
                 phi=math.radians(75), theta=math.radians(-30),
                 show_ticks=True, show_labels=True, show_grid=False,
                 x_label: str | None = 'x', y_label: str | None = 'y', z_label: str | None = 'z',
                 creation=0, z=0, **styling_kwargs):
        self._cx, self._cy = cx, cy
        self._x_range = x_range
        self._y_range = y_range
        self._z_range = z_range
        self._show_ticks = show_ticks
        self._show_labels = show_labels
        self._show_grid = show_grid
        self._axis_style = {'stroke': '#888', 'stroke_width': 2} | styling_kwargs

        # Animatable camera
        self.phi = attributes.Real(creation, phi)
        self.theta = attributes.Real(creation, theta)
        self._scale_3d = attributes.Real(creation, scale)

        # Registered 3D objects for depth-sorted rendering
        self._surfaces = []  # Surface objects
        self._threed_objects = []  # Line3D, Dot3D, Arrow3D, ParametricCurve3D

        # Light direction (normalized, in world space)
        self._light_dir = (0.5, -0.5, 1 / math.sqrt(2))

        super().__init__(creation=creation, z=z)

        # Build LaTeX axis labels as child TexObjects
        label_offset = 0.4

        for label_text, pos_3d in [
            (x_label, (x_range[1] + label_offset, 0, 0)),
            (y_label, (0, y_range[1] + label_offset, 0)),
            (z_label, (0, 0, z_range[1] + label_offset)),
        ]:
            if label_text:
                self._build_axis_label(label_text, pos_3d, creation)

    def __repr__(self):
        return 'ThreeDAxes()'

    @property
    def last_change(self):
        lc = max(self.phi.last_change, self.theta.last_change, self._scale_3d.last_change,
                 self.z.last_change, self.show.last_change)
        for obj in self.objects:
            lc = max(lc, obj.last_change)
        for s in self._surfaces:
            lc = max(lc, s.last_change)
        for o in self._threed_objects:
            lc = max(lc, o.last_change)
        return lc

    def project_point(self, x, y, z, time=0):
        """Project 3D math coords to (svg_x, svg_y, depth)."""
        p = self.phi.at_time(time)
        t = self.theta.at_time(time)
        s = self._scale_3d.at_time(time)
        return _project_point(x, y, z, p, t, s, self._cx, self._cy)

    def coords_to_point(self, x, y, z=0, time=0):
        """Project 3D coordinates to 2D SVG pixel coordinates (backward compat)."""
        sx, sy, _ = self.project_point(x, y, z, time)
        return (sx, sy)

    def set_camera_orientation(self, start, end, phi=None, theta=None, easing=easings.smooth):
        """Animate camera angles over [start, end]."""
        dur = max(end - start, 1e-9)
        if phi is not None:
            self.phi.set(start, end, _lerp(start, dur, self.phi.at_time(start), phi, easing))
        if theta is not None:
            self.theta.set(start, end, _lerp(start, dur, self.theta.at_time(start), theta, easing))
        return self

    def _build_axis_label(self, label_text, pos_3d, creation):
        """Create a TexObject for an axis label, positioned dynamically."""
        from vectormation._composites import TexObject
        tex = f'${label_text}$' if '$' not in label_text else label_text
        lbl = TexObject(tex, font_size=28, creation=creation,
                        fill='#aaa', stroke_width=0)
        _, _, lw, lh = lbl.bbox(creation)
        # Dynamic positioning based on camera projection
        def _lbl_x(t, _lw=lw, _pos=pos_3d):
            sx, _, _ = self.project_point(*_pos, t)
            return sx - _lw / 2
        def _lbl_y(t, _lh=lh, _pos=pos_3d):
            _, sy, _ = self.project_point(*_pos, t)
            return sy - _lh / 2
        lbl.x.set_onward(creation, _lbl_x)
        lbl.y.set_onward(creation, _lbl_y)
        self.add(lbl)

    def set_light_direction(self, x, y, z):
        """Set the light direction vector (will be used as-is, should be normalized)."""
        mag = math.hypot(x, y, z) or 1
        self._light_dir = (x / mag, y / mag, z / mag)
        return self

    _CAMERA_PRESETS = {
        'default': (math.radians(75), math.radians(-30)),
        'isometric': (math.radians(54.7), math.radians(-45)),
        'front': (math.radians(90), 0),
        'top': (0, 0),
        'side': (math.radians(90), math.radians(-90)),
    }

    def set_camera_preset(self, name, start=0, end=0.5, easing=easings.smooth):
        """Animate camera to a named preset: 'default', 'isometric', 'front', 'top', 'side'."""
        phi, theta = self._CAMERA_PRESETS[name]
        return self.set_camera_orientation(start, end, phi=phi, theta=theta, easing=easing)

    def set_camera_zoom(self, start, end, factor, easing=easings.smooth):
        """Animate the 3D camera zoom (scale) over [start, end]."""
        dur = max(end - start, 1e-9)
        s0 = self._scale_3d.at_time(start)
        self._scale_3d.set(start, end, _lerp(start, dur, s0, s0 * factor, easing))
        return self

    def begin_ambient_camera_rotation(self, start: float = 0, end=None, rate=0.1):
        """Continuously rotate the camera theta at *rate* radians per second."""
        theta0 = self.theta.at_time(start)
        if end is None:
            self.theta.set_onward(start, lambda t: theta0 + rate * (t - start))
        else:
            self.theta.set(start, end, lambda t: theta0 + rate * (t - start))
        return self

    def add_surface(self, surface):
        """Register a Surface for depth-sorted rendering."""
        self._surfaces.append(surface)
        return self

    def add_3d(self, obj):
        """Register a 3D primitive (Line3D, Dot3D, etc.) for depth-sorted rendering."""
        self._threed_objects.append(obj)
        return self

    def plot_surface(self, func, u_range=None, v_range=None, resolution=(20, 20),
                     fill_color='#4488ff', checkerboard_colors=None,
                     stroke_color='#333', stroke_width=0.5, fill_opacity=0.8,
                     creation=0, z=0):
        """Create and register a Surface for z = func(x, y)."""
        if u_range is None:
            u_range = self._x_range
        if v_range is None:
            v_range = self._y_range
        surface = Surface(func, u_range, v_range, resolution=resolution,
                          fill_color=fill_color, checkerboard_colors=checkerboard_colors,
                          stroke_color=stroke_color, stroke_width=stroke_width,
                          fill_opacity=fill_opacity, creation=creation, z=z)
        self.add_surface(surface)
        return surface

    def get_graph_3d(self, func, x_range=None, plane='xz', num_points=100,
                     stroke='#FFFF00', stroke_width=2, creation=0, z=0):
        """Plot a 2D function as a curve in 3D space."""
        if x_range is None:
            x_range = self._x_range
        x0, x1 = x_range
        def _make_curve_func(p, _x0, _x1, _yr, _f):
            _dx = _x1 - _x0
            if p == 'xz':
                return lambda t, _x0=_x0, _dx=_dx, _f=_f: (
                    (_v := _x0 + _dx * t), 0, _f(_v))
            elif p == 'xy':
                return lambda t, _x0=_x0, _dx=_dx, _f=_f: (
                    (_v := _x0 + _dx * t), _f(_v), 0)
            else:
                _y0, _y1 = _yr
                _dy = _y1 - _y0
                return lambda t, _y0=_y0, _dy=_dy, _f=_f: (
                    0, (_v := _y0 + _dy * t), _f(_v))
        curve_func = _make_curve_func(plane, x0, x1, self._y_range, func)
        curve = ParametricCurve3D(curve_func, t_range=(0, 1), num_points=num_points,
                                  stroke=stroke, stroke_width=stroke_width,
                                  creation=creation, z=z)
        self.add_3d(curve)
        return curve

    def plot_surface_wireframe(self, func, x_steps=20, y_steps=20,
                               creation=0, z=0, **styling_kwargs):
        """Plot a z=f(x,y) surface as a wireframe (backward compat)."""
        line_style = {'stroke': '#4488ff', 'stroke_width': 1} | styling_kwargs
        wrapped = lambda u, v, _fn=func: (u, v, _fn(u, v))
        wireframe = _Wireframe(wrapped, self._x_range, self._y_range,
                               x_steps, y_steps, line_style, creation=creation, z=z)
        self._threed_objects.append(wireframe)
        return wireframe

    def plot_parametric_surface(self, func, u_range=(0, math.tau),
                                v_range=(-math.pi / 2, math.pi / 2),
                                u_steps=32, v_steps=16,
                                creation=0, z=0, **styling_kwargs):
        """Plot a parametric wireframe surface (backward compat)."""
        line_style = {'stroke': '#4488ff', 'stroke_width': 1} | styling_kwargs
        wireframe = _Wireframe(func, u_range, v_range,
                               u_steps, v_steps, line_style, creation=creation, z=z)
        self._threed_objects.append(wireframe)
        return wireframe

    def add_grid_plane(self, plane='xz', step=1, color='#444444', opacity=0.3,
                        stroke_width=0.5, creation=0):
        """Add a grid plane to the 3D axes."""
        from vectormation._shapes import Line
        lines = []
        x_min, x_max = self._x_range[0], self._x_range[1]
        y_min, y_max = self._y_range[0], self._y_range[1]
        z_min, z_max = self._z_range[0], self._z_range[1]
        line_kw = dict(stroke=color, stroke_opacity=opacity,
                       stroke_width=stroke_width, creation=creation)

        def _grid_line(p1_3d, p2_3d):
            p1 = self.project_point(*p1_3d, creation)
            p2 = self.project_point(*p2_3d, creation)
            lines.append(Line(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1], **line_kw))

        if plane == 'xz':
            for x in _frange(x_min, x_max, step):
                _grid_line((x, 0, z_min), (x, 0, z_max))
            for z in _frange(z_min, z_max, step):
                _grid_line((x_min, 0, z), (x_max, 0, z))
        elif plane == 'xy':
            for x in _frange(x_min, x_max, step):
                _grid_line((x, y_min, 0), (x, y_max, 0))
            for y in _frange(y_min, y_max, step):
                _grid_line((x_min, y, 0), (x_max, y, 0))
        elif plane == 'yz':
            for y in _frange(y_min, y_max, step):
                _grid_line((0, y, z_min), (0, y, z_max))
            for z in _frange(z_min, z_max, step):
                _grid_line((0, y_min, z), (0, y_max, z))

        grid = VCollection(*lines, creation=creation)
        self.add(grid)
        return grid

    # -- Rendering --

    def _render_axis_svg(self, sx0, sy0, sx1, sy1, tip_size=8):
        """Render axis line + arrowhead from pre-projected screen coords."""
        stroke = self._axis_style.get('stroke', '#888')
        sw = self._axis_style.get('stroke_width', 2)
        (ax, ay), (bx, by) = _arrow_tip_points(sx0, sy0, sx1, sy1, tip_size, tip_size * 0.4)
        return (f'<line x1="{sx0:.1f}" y1="{sy0:.1f}" x2="{sx1:.1f}" y2="{sy1:.1f}" '
                f'stroke="{stroke}" stroke-width="{sw}"/>\n'
                f'<polygon points="{sx1:.1f},{sy1:.1f} {ax:.1f},{ay:.1f} {bx:.1f},{by:.1f}" '
                f'fill="{stroke}" stroke="none"/>')

    def _render_tick_3d(self, pos_3d, perp_3d, value, time, font_size=18):
        """Render a tick mark and optional label at a 3D position."""
        sp = self.project_point(*pos_3d, time)
        tick_len = 4
        pp = self.project_point(pos_3d[0] + perp_3d[0] * 0.1,
                                pos_3d[1] + perp_3d[1] * 0.1,
                                pos_3d[2] + perp_3d[2] * 0.1, time)
        # Tick direction in screen space
        tdx, tdy = pp[0] - sp[0], pp[1] - sp[1]
        _tux, _tuy = _normalize(tdx, tdy)
        tdx, tdy = _tux * tick_len, _tuy * tick_len
        stroke = self._axis_style.get('stroke', '#888')
        parts = [f'<line x1="{sp[0] - tdx:.1f}" y1="{sp[1] - tdy:.1f}" '
                 f'x2="{sp[0] + tdx:.1f}" y2="{sp[1] + tdy:.1f}" '
                 f'stroke="{stroke}" stroke-width="1"/>']
        if self._show_labels:
            label = f'{value:g}'
            lx = sp[0] + tdx * 4
            ly = sp[1] + tdy * 4 + font_size * TEXT_Y_OFFSET
            parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="{font_size}" '
                         f'fill="#aaa" text-anchor="middle" font-family="sans-serif">'
                         f'{_xml_escape(label)}</text>')
        return '\n'.join(parts), sp[2]

    def _render_grid_line(self, p0_3d, p1_3d, time):
        """Render a grid line in 3D space."""
        sx0, sy0, d0 = self.project_point(*p0_3d, time)
        sx1, sy1, d1 = self.project_point(*p1_3d, time)
        depth = (d0 + d1) / 2
        return (f'<line x1="{sx0:.1f}" y1="{sy0:.1f}" x2="{sx1:.1f}" y2="{sy1:.1f}" '
                f'stroke="#444" stroke-width="0.5" opacity="0.4"/>'), depth

    def _render_axes_patches(self, time):
        """Generate (depth, svg_str) patches for axes, ticks, labels, grid."""
        patches = []
        xr, yr, zr = self._x_range, self._y_range, self._z_range

        # Axis lines + arrow tips
        for axis_start, axis_end in [
            ((xr[0], 0, 0), (xr[1], 0, 0)),
            ((0, yr[0], 0), (0, yr[1], 0)),
            ((0, 0, zr[0]), (0, 0, zr[1])),
        ]:
            sx0, sy0, d0 = self.project_point(*axis_start, time)
            sx1, sy1, d1 = self.project_point(*axis_end, time)
            depth = (d0 + d1) / 2
            svg = self._render_axis_svg(sx0, sy0, sx1, sy1)
            patches.append((depth, svg))

        # Ticks
        if self._show_ticks:
            for rng, pos_fn, perp in [
                (xr, lambda v: (v, 0, 0), (0, 1, 0)),
                (yr, lambda v: (0, v, 0), (1, 0, 0)),
                (zr, lambda v: (0, 0, v), (1, 0, 0)),
            ]:
                for val in _nice_ticks(rng[0], rng[1], 5):
                    svg, depth = self._render_tick_3d(pos_fn(val), perp, val, time)
                    patches.append((depth, svg))

        # Grid
        if self._show_grid:
            # XY plane at z = z_min
            z_grid = zr[0]
            for val in _nice_ticks(xr[0], xr[1], 5):
                svg, depth = self._render_grid_line(
                    (val, yr[0], z_grid), (val, yr[1], z_grid), time)
                patches.append((depth, svg))
            for val in _nice_ticks(yr[0], yr[1], 5):
                svg, depth = self._render_grid_line(
                    (xr[0], val, z_grid), (xr[1], val, z_grid), time)
                patches.append((depth, svg))

        return patches

    def to_svg(self, time):
        if not self.show.at_time(time):
            return ''

        # Collect all patches with depth
        patches = self._render_axes_patches(time)

        # Child VObjects (rendered as flat 2D overlays, e.g. TexObjects)
        for obj in self.objects:
            if obj.show.at_time(time):
                z_val = obj.z.at_time(time) if hasattr(obj, 'z') else 0
                patches.append((z_val, obj.to_svg(time)))

        # Surface patches
        for surface in self._surfaces:
            if surface.show.at_time(time):
                patches.extend(surface.to_patches(self, time))

        # 3D primitive patches
        for obj3d in self._threed_objects:
            if obj3d.show.at_time(time):
                patches.extend(obj3d.to_patches(self, time))

        # Depth sort: back to front (lowest depth first)
        patches.sort(key=lambda p: p[0])
        inner = '\n'.join(svg for _, svg in patches)
        return f'<g>\n{inner}\n</g>'

    def bbox(self, time=0, start_idx=0, end_idx=None):  # noqa: ARG002 (start_idx, end_idx unused; overrides VCollection.bbox signature)
        """Bounding box based on projected axis endpoints."""
        xr, yr, zr = self._x_range, self._y_range, self._z_range
        corners = [
            (xr[0], yr[0], zr[0]), (xr[1], yr[0], zr[0]),
            (xr[0], yr[1], zr[0]), (xr[1], yr[1], zr[0]),
            (xr[0], yr[0], zr[1]), (xr[1], yr[0], zr[1]),
            (xr[0], yr[1], zr[1]), (xr[1], yr[1], zr[1]),
        ]
        projected = [self.project_point(*c, time) for c in corners]
        xs = [p[0] for p in projected]
        ys = [p[1] for p in projected]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        return (xmin, ymin, xmax - xmin, ymax - ymin)

# ---------------------------------------------------------------------------
# Surface
# ---------------------------------------------------------------------------

class Surface(VObject):
    """Filled surface with depth sorting and Lambertian shading."""

    def __init__(self, func, u_range=(-3, 3), v_range=(-3, 3),
                 resolution=(20, 20),
                 fill_color='#4488ff', checkerboard_colors=None,
                 stroke_color='#333', stroke_width=0.5, fill_opacity=0.8,
                 creation=0, z=0):
        self.show = attributes.Real(creation, True)
        self.z = attributes.Real(creation, z)
        self._func = func
        self._u_range = u_range
        self._v_range = v_range
        self._resolution = resolution
        self._fill_color = fill_color
        self._checkerboard_colors = checkerboard_colors
        self._fill_rgb = _parse_color_to_rgb(fill_color)
        self._checker_rgb = (tuple(_parse_color_to_rgb(c) for c in checkerboard_colors)
                             if checkerboard_colors else None)
        self._stroke_color = stroke_color
        self._stroke_width = stroke_width
        self._fill_opacity = fill_opacity
        self._is_parametric = None  # auto-detect

    def __repr__(self):
        return 'Surface()'

    @property
    def last_change(self):
        return max(self.show.last_change, self.z.last_change)

    def _eval(self, u, v):
        """Evaluate func and return (x, y, z)."""
        result = self._func(u, v)
        if isinstance(result, (tuple, list)) and len(result) == 3:
            if self._is_parametric is None:
                self._is_parametric = True
            return tuple(result)
        # Height-map: u=x, v=y, result=z
        if self._is_parametric is None:
            self._is_parametric = False
        return (u, v, result)

    def to_patches(self, axes, time):
        """Generate (depth, svg_str) for each face quad."""
        u_steps, v_steps = max(self._resolution[0], 1), max(self._resolution[1], 1)
        u0, u1 = self._u_range
        v0, v1 = self._v_range
        du = (u1 - u0) / u_steps
        dv = (v1 - v0) / v_steps

        # Build vertex grid
        grid = []
        for i in range(u_steps + 1):
            row = []
            for j in range(v_steps + 1):
                u = u0 + i * du
                v = v0 + j * dv
                row.append(self._eval(u, v))
            grid.append(row)

        # Parse colors
        if self._checker_rgb:
            rgb_a, rgb_b = self._checker_rgb
        else:
            rgb_a = rgb_b = self._fill_rgb

        light_dir = axes._light_dir

        patches = []
        for i in range(u_steps):
            for j in range(v_steps):
                # 4 corners of the quad in 3D
                p00 = grid[i][j]
                p10 = grid[i + 1][j]
                p11 = grid[i + 1][j + 1]
                p01 = grid[i][j + 1]

                # Project
                s00 = axes.project_point(*p00, time)
                s10 = axes.project_point(*p10, time)
                s11 = axes.project_point(*p11, time)
                s01 = axes.project_point(*p01, time)

                # Average depth
                depth = (s00[2] + s10[2] + s11[2] + s01[2]) / 4

                # Face normal for shading
                normal = _face_normal(p00, p10, p01)

                # Pick color
                base_rgb = rgb_a if (i + j) % 2 == 0 else rgb_b
                fill = _shade_color(base_rgb, normal, light_dir)

                points_str = (f'{s00[0]:.1f},{s00[1]:.1f} {s10[0]:.1f},{s10[1]:.1f} '
                              f'{s11[0]:.1f},{s11[1]:.1f} {s01[0]:.1f},{s01[1]:.1f}')

                stroke_attr = ''
                if self._stroke_width > 0:
                    stroke_attr = f' stroke="{self._stroke_color}" stroke-width="{self._stroke_width}"'

                svg = (f'<polygon points="{points_str}" fill="{fill}" '
                       f'fill-opacity="{self._fill_opacity}"{stroke_attr}/>')
                patches.append((depth, svg))

        return patches

    def set_checkerboard(self, color_a, color_b):
        """Update the checkerboard colors for this surface."""
        self._checkerboard_colors = (color_a, color_b)
        return self

    def to_svg(self, time):
        return ''

    def path(self, time):
        return ''

    def bbox(self, time=0):
        return (0, 0, 0, 0)

    def _extra_attrs(self):
        return []

    def _shift_coors(self):
        return []

    def _shift_reals(self):
        return []

# ---------------------------------------------------------------------------
# Wireframe helpers (backward compat, rendered as 3D patches)
# ---------------------------------------------------------------------------

class _Wireframe:
    """Internal: wireframe rendered via to_patches.  *func(u, v) -> (x, y, z)*."""

    def __init__(self, func, u_range, v_range, u_steps, v_steps, style, creation=0, z=0):
        self.show = attributes.Real(creation, True)
        self.z = attributes.Real(creation, z)
        self._func = func
        self._u_range, self._v_range = u_range, v_range
        self._u_steps, self._v_steps = u_steps, v_steps
        self._style = style

    @property
    def last_change(self):
        return max(self.show.last_change, self.z.last_change)

    def to_patches(self, axes, time):
        patches = []
        u0, u1 = self._u_range
        v0, v1 = self._v_range
        du = (u1 - u0) / max(self._u_steps, 1)
        dv = (v1 - v0) / max(self._v_steps, 1)
        stroke = self._style.get('stroke', '#4488ff')
        sw = self._style.get('stroke_width', 1)
        for j in range(self._v_steps + 1):
            vv = v0 + j * dv
            patches.append(_polyline_patch(
                [self._func(u0 + i * du, vv) for i in range(self._u_steps + 1)],
                axes, time, stroke, sw))
        for i in range(self._u_steps + 1):
            uu = u0 + i * du
            patches.append(_polyline_patch(
                [self._func(uu, v0 + j * dv) for j in range(self._v_steps + 1)],
                axes, time, stroke, sw))
        return patches

# ---------------------------------------------------------------------------
# 3D Primitives
# ---------------------------------------------------------------------------

def _shift3(pt, dx, dy, dz):
    """Shift a 3D tuple by (dx, dy, dz)."""
    return (pt[0] + dx, pt[1] + dy, pt[2] + dz)

class _Primitive3D:
    """Base for 3D primitives with show/z attributes and copy()."""

    def __init__(self, creation=0, z=0):
        self.show = attributes.Real(creation, True)
        self.z = attributes.Real(creation, z)

    @property
    def last_change(self):
        return max(self.show.last_change, self.z.last_change)

    def copy(self):
        """Return a deep copy of this object."""
        return deepcopy(self)

class _SegmentPrimitive3D(_Primitive3D):
    """Base for 3D primitives defined by _start/_end endpoints."""

    def shift(self, dx=0, dy=0, dz=0):
        """Shift both endpoints by (dx, dy, dz). Returns self for chaining."""
        self._start, self._end = _shift3(self._start, dx, dy, dz), _shift3(self._end, dx, dy, dz)
        return self

    def move_to(self, x, y, z):
        """Move the midpoint to (x, y, z). Returns self for chaining."""
        mx, my, mz = self.get_midpoint()
        return self.shift(x - mx, y - my, z - mz)

    def get_midpoint(self):
        """Return the 3D midpoint."""
        return ((self._start[0] + self._end[0]) / 2,
                (self._start[1] + self._end[1]) / 2,
                (self._start[2] + self._end[2]) / 2)

    def get_length(self):
        """Return the 3D Euclidean length."""
        return math.hypot(self._end[0] - self._start[0],
                          self._end[1] - self._start[1],
                          self._end[2] - self._start[2])

    def set_color(self, color):
        """Set the stroke color. Returns self for chaining."""
        self._stroke = color
        return self

class _PointPrimitive3D(_Primitive3D):
    """Base for 3D primitives located at a single point."""

    def shift(self, dx=0, dy=0, dz=0):
        """Shift the point by (dx, dy, dz). Returns self for chaining."""
        self._point = _shift3(self._point, dx, dy, dz)
        return self

    def move_to(self, x, y, z):
        """Move to (x, y, z). Returns self for chaining."""
        self._point = (x, y, z)
        return self

    def get_position(self):
        """Return the 3D position as a tuple."""
        return self._point

    def set_color(self, color):
        """Set the fill color. Returns self for chaining."""
        self._fill = color
        return self

class Line3D(_SegmentPrimitive3D):
    """A line segment in 3D space."""

    def __init__(self, start, end, stroke='#fff', stroke_width=2, creation=0, z=0):
        super().__init__(creation, z)
        self._start = tuple(start)
        self._end = tuple(end)
        self._stroke = stroke
        self._stroke_width = stroke_width

    def __repr__(self):
        return 'Line3D()'

    def to_patches(self, axes, time):
        sx0, sy0, d0 = axes.project_point(*self._start, time)
        sx1, sy1, d1 = axes.project_point(*self._end, time)
        depth = (d0 + d1) / 2
        svg = (f'<line x1="{sx0:.1f}" y1="{sy0:.1f}" x2="{sx1:.1f}" y2="{sy1:.1f}" '
               f'stroke="{self._stroke}" stroke-width="{self._stroke_width}"/>')
        return [(depth, svg)]

class Dot3D(_PointPrimitive3D):
    """A dot in 3D space."""

    def __init__(self, point=(0, 0, 0), radius=5, fill='#fff', creation=0, z=0):
        super().__init__(creation, z)
        self._point = tuple(point)
        self._radius = radius
        self._fill = fill

    def __repr__(self):
        return 'Dot3D()'

    def set_radius(self, radius):
        """Set the dot radius. Returns self for chaining."""
        self._radius = radius
        return self

    def to_patches(self, axes, time):
        sx, sy, depth = axes.project_point(*self._point, time)
        svg = (f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{self._radius}" '
               f'fill="{self._fill}" stroke="none"/>')
        return [(depth, svg)]

class Arrow3D(_SegmentPrimitive3D):
    """An arrow in 3D space with a cone tip."""

    def __init__(self, start, end, stroke='#fff', stroke_width=2,
                 tip_length=12, tip_radius=4, creation=0, z=0):
        super().__init__(creation, z)
        self._start = tuple(start)
        self._end = tuple(end)
        self._stroke = stroke
        self._stroke_width = stroke_width
        self._tip_length = tip_length
        self._tip_radius = tip_radius

    def __repr__(self):
        return 'Arrow3D()'

    def to_patches(self, axes, time):
        patches = []
        sx0, sy0, d0 = axes.project_point(*self._start, time)
        sx1, sy1, d1 = axes.project_point(*self._end, time)
        depth = (d0 + d1) / 2

        # Shaft line
        svg = (f'<line x1="{sx0:.1f}" y1="{sy0:.1f}" x2="{sx1:.1f}" y2="{sy1:.1f}" '
               f'stroke="{self._stroke}" stroke-width="{self._stroke_width}"/>')
        patches.append((depth, svg))

        # Arrow tip (2D triangle at the projected tip)
        (ax, ay), (bx, by) = _arrow_tip_points(sx0, sy0, sx1, sy1,
                                                 self._tip_length, self._tip_radius)
        tip_svg = (f'<polygon points="{sx1:.1f},{sy1:.1f} {ax:.1f},{ay:.1f} {bx:.1f},{by:.1f}" '
                   f'fill="{self._stroke}" stroke="none"/>')
        patches.append((d1, tip_svg))

        return patches

class ParametricCurve3D(_Primitive3D):
    """A parametric curve in 3D space."""

    def __init__(self, func, t_range=(0, 1), num_points=100,
                 stroke='#fff', stroke_width=2, creation=0, z=0):
        super().__init__(creation, z)
        self._func = func
        self._t_range = t_range
        self._num_points = num_points
        self._stroke = stroke
        self._stroke_width = stroke_width

    def __repr__(self):
        return 'ParametricCurve3D()'

    def set_color(self, color):
        """Set the stroke color. Returns self for chaining."""
        self._stroke = color
        return self

    def to_patches(self, axes, time):
        t0, t1 = self._t_range
        dt = (t1 - t0) / max(self._num_points, 1)
        pts3d = [self._func(t0 + i * dt) for i in range(self._num_points + 1)]
        return [_polyline_patch(pts3d, axes, time, self._stroke, self._stroke_width)]

# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

def _make_surface(func, u_range, v_range, resolution, **kw):
    """Shared factory: create a Surface with common styling kwargs."""
    return Surface(func, u_range=u_range, v_range=v_range, resolution=resolution, **kw)

def Sphere3D(radius=1.5, center=(0, 0, 0), resolution=(16, 32),
             fill_color='#FC6255', checkerboard_colors=None,
             stroke_color='#333', stroke_width=0.3, fill_opacity=0.9,
             creation=0, z=0):
    """Create a Surface representing a sphere."""
    cx, cy, cz = center
    def f(u, v):
        return (cx + radius * math.cos(u) * math.cos(v),
                cy + radius * math.cos(u) * math.sin(v),
                cz + radius * math.sin(u))
    return _make_surface(f, (-math.pi / 2, math.pi / 2), (0, math.tau), resolution,
                         fill_color=fill_color, checkerboard_colors=checkerboard_colors,
                         stroke_color=stroke_color, stroke_width=stroke_width,
                         fill_opacity=fill_opacity, creation=creation, z=z)

class Text3D(_PointPrimitive3D):
    """A text label placed at a 3D position."""

    def __init__(self, text, point=(0, 0, 0), font_size=20, fill='#fff',
                 creation=0, z=0):
        super().__init__(creation, z)
        self._text = text
        self._point = tuple(point)
        self._font_size = font_size
        self._fill = fill

    def __repr__(self):
        return 'Text3D()'

    def set_text(self, text):
        """Set the displayed text. Returns self for chaining."""
        self._text = text
        return self

    def to_patches(self, axes, time):
        sx, sy, depth = axes.project_point(*self._point, time)
        svg = (f'<text x="{sx:.1f}" y="{sy:.1f}" font-size="{self._font_size}" '
               f'fill="{self._fill}" text-anchor="middle" dominant-baseline="middle" '
               f'font-family="sans-serif">{_xml_escape(self._text)}</text>')
        return [(depth, svg)]

def Cube(side_length=2, center=(0, 0, 0), fill_color='#58C4DD',
         stroke_color='#333', stroke_width=0.5, fill_opacity=0.8,
         creation=0, z=0):
    """Create a list of 6 Surface objects representing a cube."""
    cx, cy, cz = center
    h = side_length / 2
    faces = []
    # Each face is a parametric surface mapping (u, v) to a flat quad
    face_defs = [
        # (corner, u_dir, v_dir) — each face spans corner + u*u_dir + v*v_dir
        ((cx - h, cy - h, cz + h), (side_length, 0, 0), (0, side_length, 0)),  # top (z+)
        ((cx - h, cy - h, cz - h), (side_length, 0, 0), (0, side_length, 0)),  # bottom (z-)
        ((cx - h, cy - h, cz - h), (side_length, 0, 0), (0, 0, side_length)),  # front (y-)
        ((cx - h, cy + h, cz - h), (side_length, 0, 0), (0, 0, side_length)),  # back (y+)
        ((cx - h, cy - h, cz - h), (0, side_length, 0), (0, 0, side_length)),  # left (x-)
        ((cx + h, cy - h, cz - h), (0, side_length, 0), (0, 0, side_length)),  # right (x+)
    ]
    for corner, u_dir, v_dir in face_defs:
        faces.append(Surface(_flat_quad_func(corner, u_dir, v_dir),
                             u_range=(0, 1), v_range=(0, 1),
                             resolution=(1, 1),
                             fill_color=fill_color, stroke_color=stroke_color,
                             stroke_width=stroke_width, fill_opacity=fill_opacity,
                             creation=creation, z=z))
    return faces

def Cylinder3D(radius=1, height=2, center=(0, 0, 0), resolution=(16, 16),
               fill_color='#58C4DD', checkerboard_colors=None,
               stroke_color='#333', stroke_width=0.3, fill_opacity=0.9,
               creation=0, z=0):
    """Create a Surface representing a cylinder (open-ended, side only)."""
    cx, cy, cz = center
    def f(u, v):
        return (cx + radius * math.cos(u), cy + radius * math.sin(u),
                cz - height / 2 + v * height)
    return _make_surface(f, (0, math.tau), (0, 1), resolution,
                         fill_color=fill_color, checkerboard_colors=checkerboard_colors,
                         stroke_color=stroke_color, stroke_width=stroke_width,
                         fill_opacity=fill_opacity, creation=creation, z=z)

def Cone3D(radius=1, height=2, center=(0, 0, 0), resolution=(16, 16),
           fill_color='#58C4DD', checkerboard_colors=None,
           stroke_color='#333', stroke_width=0.3, fill_opacity=0.9,
           creation=0, z=0):
    """Create a Surface representing a cone (open-ended, side only)."""
    cx, cy, cz = center
    def f(u, v):
        r = radius * v
        return (cx + r * math.cos(u), cy + r * math.sin(u),
                cz + height / 2 - v * height)
    return _make_surface(f, (0, math.tau), (0, 1), resolution,
                         fill_color=fill_color, checkerboard_colors=checkerboard_colors,
                         stroke_color=stroke_color, stroke_width=stroke_width,
                         fill_opacity=fill_opacity, creation=creation, z=z)

def Torus3D(major_radius=2, minor_radius=0.5, center=(0, 0, 0),
            resolution=(24, 12),
            fill_color='#58C4DD', checkerboard_colors=None,
            stroke_color='#333', stroke_width=0.3, fill_opacity=0.9,
            creation=0, z=0):
    """Create a Surface representing a torus."""
    cx, cy, cz = center
    R, r = major_radius, minor_radius
    def f(u, v):
        return (cx + (R + r * math.cos(v)) * math.cos(u),
                cy + (R + r * math.cos(v)) * math.sin(u),
                cz + r * math.sin(v))
    return _make_surface(f, (0, math.tau), (0, math.tau), resolution,
                         fill_color=fill_color, checkerboard_colors=checkerboard_colors,
                         stroke_color=stroke_color, stroke_width=stroke_width,
                         fill_opacity=fill_opacity, creation=creation, z=z)

def Prism3D(n_sides=6, radius=1, height=2, center=(0, 0, 0),
            fill_color='#58C4DD', stroke_color='#333', stroke_width=0.5,
            fill_opacity=0.8, creation=0, z=0):
    """Create a list of Surfaces representing an n-sided prism."""
    cx, cy, cz = center
    h = height / 2
    faces = []

    # Side faces — each is a flat quad
    for i in range(n_sides):
        a0 = math.tau * i / n_sides
        a1 = math.tau * (i + 1) / n_sides
        c0 = (cx + radius * math.cos(a0), cy + radius * math.sin(a0))
        c1 = (cx + radius * math.cos(a1), cy + radius * math.sin(a1))

        faces.append(Surface(_flat_quad_func(
            (c0[0], c0[1], cz - h),
            (c1[0] - c0[0], c1[1] - c0[1], 0),
            (0, 0, 2 * h)), u_range=(0, 1), v_range=(0, 1),
                             resolution=(1, 1),
                             fill_color=fill_color, stroke_color=stroke_color,
                             stroke_width=stroke_width, fill_opacity=fill_opacity,
                             creation=creation, z=z))

    # Top and bottom caps as triangle fans (each triangle is a Surface)
    for z_off in [h, -h]:
        for i in range(n_sides):
            a0 = math.tau * i / n_sides
            a1 = math.tau * (i + 1) / n_sides

            def _make_cap(angle0, angle1, _cx=cx, _cy=cy, _r=radius, _cz=cz, _zo=z_off):
                def f(u, v):
                    # Map (u, v) in [0,1]x[0,1] to triangle: center, p0, p1
                    p0x = _cx + _r * math.cos(angle0)
                    p0y = _cy + _r * math.sin(angle0)
                    p1x = _cx + _r * math.cos(angle1)
                    p1y = _cy + _r * math.sin(angle1)
                    # Interpolate: center*(1-u) + edge*u, then between p0 and p1 via v
                    ex = p0x + v * (p1x - p0x)
                    ey = p0y + v * (p1y - p0y)
                    x = _cx + u * (ex - _cx)
                    y = _cy + u * (ey - _cy)
                    return (x, y, _cz + _zo)
                return f

            faces.append(Surface(_make_cap(a0, a1), u_range=(0, 1), v_range=(0, 1),
                                 resolution=(1, 1),
                                 fill_color=fill_color, stroke_color=stroke_color,
                                 stroke_width=stroke_width, fill_opacity=fill_opacity,
                                 creation=creation, z=z))

    return faces


# ---------------------------------------------------------------------------
# Platonic solids
# ---------------------------------------------------------------------------

def _polyhedron_faces(vertices, face_indices, *,
                      fill_color='#58C4DD', stroke_color='#FFFFFF',
                      stroke_width=1, fill_opacity=0.8,
                      cx=0, cy=0, cz=0, scale=1.0,
                      creation=0, z=0):
    """Build a list of Surface patches from vertex coords and face index lists."""
    verts = [(cx + x * scale, cy + y * scale, cz + zz * scale) for x, y, zz in vertices]
    faces = []
    for idxs in face_indices:
        pts = [verts[i] for i in idxs]
        if len(pts) < 3:
            continue

        def _make_face(_pts=pts):
            n = len(_pts)
            def f(u, v):
                # Fan triangulation from pts[0]; u selects triangle, v interpolates edge
                tri = min(int(u * (n - 2)), n - 3)
                a, b, c = _pts[0], _pts[tri + 1], _pts[tri + 2]
                local_u = u * (n - 2) - tri
                edge = (b[0] + local_u * (c[0] - b[0]),
                        b[1] + local_u * (c[1] - b[1]),
                        b[2] + local_u * (c[2] - b[2]))
                return (a[0] + v * (edge[0] - a[0]),
                        a[1] + v * (edge[1] - a[1]),
                        a[2] + v * (edge[2] - a[2]))
            return f

        faces.append(Surface(_make_face(), u_range=(0, 1), v_range=(0, 1),
                             resolution=(1, 1),
                             fill_color=fill_color, stroke_color=stroke_color,
                             stroke_width=stroke_width, fill_opacity=fill_opacity,
                             creation=creation, z=z))
    return faces


def _platonic(vertices, face_indices, cx, cy, cz, size, **kw):
    """Shared factory for platonic solid construction."""
    return _polyhedron_faces(vertices, face_indices,
                             cx=cx, cy=cy, cz=cz, scale=size, **kw)

_PHI = (1 + 5 ** 0.5) / 2  # golden ratio

def Tetrahedron(cx=0, cy=0, cz=0, size=1.0, *,
                fill_color='#58C4DD', stroke_color='#FFFFFF',
                stroke_width=1, fill_opacity=0.8, creation=0, z=0):
    """Regular tetrahedron (4 triangular faces)."""
    return _platonic(
        [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)],
        [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)],
        cx, cy, cz, size, fill_color=fill_color, stroke_color=stroke_color,
        stroke_width=stroke_width, fill_opacity=fill_opacity,
        creation=creation, z=z)

def Octahedron(cx=0, cy=0, cz=0, size=1.0, *,
               fill_color='#58C4DD', stroke_color='#FFFFFF',
               stroke_width=1, fill_opacity=0.8, creation=0, z=0):
    """Regular octahedron (8 triangular faces)."""
    return _platonic(
        [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)],
        [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4),
         (0, 2, 5), (2, 1, 5), (1, 3, 5), (3, 0, 5)],
        cx, cy, cz, size, fill_color=fill_color, stroke_color=stroke_color,
        stroke_width=stroke_width, fill_opacity=fill_opacity,
        creation=creation, z=z)

def Icosahedron(cx=0, cy=0, cz=0, size=1.0, *,
                fill_color='#58C4DD', stroke_color='#FFFFFF',
                stroke_width=1, fill_opacity=0.8, creation=0, z=0):
    """Regular icosahedron (20 triangular faces)."""
    p = _PHI
    return _platonic(
        [(-1, p, 0), (1, p, 0), (-1, -p, 0), (1, -p, 0),
         (0, -1, p), (0, 1, p), (0, -1, -p), (0, 1, -p),
         (p, 0, -1), (p, 0, 1), (-p, 0, -1), (-p, 0, 1)],
        [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
         (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
         (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)],
        cx, cy, cz, size, fill_color=fill_color, stroke_color=stroke_color,
        stroke_width=stroke_width, fill_opacity=fill_opacity,
        creation=creation, z=z)

def Dodecahedron(cx=0, cy=0, cz=0, size=1.0, *,
                 fill_color='#58C4DD', stroke_color='#FFFFFF',
                 stroke_width=1, fill_opacity=0.8, creation=0, z=0):
    """Regular dodecahedron (12 pentagonal faces)."""
    p, ip = _PHI, 1 / _PHI
    return _platonic(
        [(1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
         (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1),
         (0, ip, p), (0, ip, -p), (0, -ip, p), (0, -ip, -p),
         (ip, p, 0), (ip, -p, 0), (-ip, p, 0), (-ip, -p, 0),
         (p, 0, ip), (p, 0, -ip), (-p, 0, ip), (-p, 0, -ip)],
        [(0, 8, 10, 2, 16), (0, 16, 17, 1, 12), (0, 12, 14, 4, 8),
         (1, 17, 3, 11, 9), (1, 9, 5, 14, 12), (2, 10, 6, 15, 13),
         (2, 13, 3, 17, 16), (3, 13, 15, 7, 11), (4, 14, 5, 19, 18),
         (4, 18, 6, 10, 8), (5, 9, 11, 7, 19), (6, 18, 19, 7, 15)],
        cx, cy, cz, size, fill_color=fill_color, stroke_color=stroke_color,
        stroke_width=stroke_width, fill_opacity=fill_opacity,
        creation=creation, z=z)
