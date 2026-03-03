"""2D physics engine for vectormation.

Provides a pre-computed physics simulation that maps trajectories onto
time-varying VObject attributes.  Physics is stepped via Verlet integration
at a configurable dt, then positions are baked as time functions so the
SVG renderer can sample any frame.

Usage
-----
    space = PhysicsSpace(gravity=(0, 980), dt=1/120)
    b = space.add_body(Circle(r=20, cx=960, cy=100), mass=1)
    space.add_wall(y=900)                         # floor
    space.simulate(duration=5)                     # pre-compute
    canvas.add(b.obj)                              # add the circle

The body's VObject position attributes are automatically updated so the
object follows the simulated trajectory.
"""
import math
from vectormation._constants import ORIGIN

_MIN_DIST = 0.001  # guard against near-zero distance in collisions/springs


def _detect_shape(obj, radius_override=None):
    """Detect collision shape from a VObject.

    Returns ('circle', radius, []) or ('polygon', bounding_radius, local_verts).
    local_verts are centred on (0,0) relative to the body center.
    """
    if radius_override is not None:
        r = float(radius_override)
        return ('circle', r, [])
    # Wedge / AnnularSector (Arc subclasses with start/end angle) — approximate
    # as polygon.  Must come before the 'r' check to avoid treating them as circles.
    if hasattr(obj, 'start_angle') and hasattr(obj, 'end_angle') and hasattr(obj, 'r'):
        return _detect_arc_shape(obj)
    # Circle / Dot — true circle collision
    if hasattr(obj, 'r') and not hasattr(obj, 'start_angle'):
        a = getattr(obj, 'r')
        r = float(a.at_time(0)) if hasattr(a, 'at_time') else float(a)
        return ('circle', r, [])
    # Ellipse (rx, ry without width/height) — approximate as polygon
    try:
        if hasattr(obj, 'rx') and hasattr(obj, 'ry') and not hasattr(obj, 'width'):
            rx_attr = getattr(obj, 'rx')
            ry_attr = getattr(obj, 'ry')
            rx = float(rx_attr.at_time(0)) if hasattr(rx_attr, 'at_time') else float(rx_attr)
            ry = float(ry_attr.at_time(0)) if hasattr(ry_attr, 'at_time') else float(ry_attr)
            n = 16  # sample points for polygon approximation
            local = [(rx * math.cos(2 * math.pi * i / n),
                       ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
            bounding_r = max(rx, ry)
            return ('polygon', bounding_r, local)
    except Exception:
        pass
    # Any shape with vertices — use convex polygon collision
    if hasattr(obj, 'get_vertices'):
        try:
            verts = obj.get_vertices(0)
            if len(verts) >= 3:
                cx = sum(v[0] for v in verts) / len(verts)
                cy = sum(v[1] for v in verts) / len(verts)
                local = [(v[0] - cx, v[1] - cy) for v in verts]
                bounding_r = max(math.hypot(lx, ly) for lx, ly in local)
                return ('polygon', bounding_r, local)
        except Exception:
            pass
    raise TypeError(
        f"Physics simulation does not support {type(obj).__name__}. "
        "The object must be a Circle, Ellipse, or a polygon with get_vertices()."
    )


def _detect_arc_shape(obj):
    """Approximate a Wedge or AnnularSector as a convex polygon for collision.

    Local verts are relative to (cx, cy) to match _body_center.
    """
    r = float(obj.r.at_time(0))
    cx = float(obj.cx.at_time(0))
    cy = float(obj.cy.at_time(0))
    sa = math.radians(float(obj.start_angle.at_time(0)))
    ea = math.radians(float(obj.end_angle.at_time(0)))
    inner_r = float(obj.inner_r.at_time(0)) if hasattr(obj, 'inner_r') else 0
    # Sample arc boundary as local offsets from (cx, cy)
    n = 12
    sweep = ea - sa
    local = []
    # Outer arc
    for i in range(n + 1):
        a = sa + sweep * i / n
        local.append((r * math.cos(a), -r * math.sin(a)))
    if inner_r > 0:
        # Inner arc (reversed)
        for i in range(n, -1, -1):
            a = sa + sweep * i / n
            local.append((inner_r * math.cos(a), -inner_r * math.sin(a)))
    else:
        # Wedge: close through center
        local.append((0.0, 0.0))
    bounding_r = max(math.hypot(lx, ly) for lx, ly in local)
    return ('polygon', bounding_r, local)


class Body:
    """A physics body wrapping a VObject.

    Parameters
    ----------
    obj : VObject
        The visual object to move.
    mass : float
        Mass (kg).  Use ``math.inf`` for static bodies.
    restitution : float
        Coefficient of restitution (bounciness), 0..1.
    friction : float
        Simple friction coefficient applied during collisions.
    radius : float | None
        Collision radius.  Auto-detected from Circle/Dot objects.
    angle : float
        Initial rotation angle in degrees.
    angular_velocity : float
        Initial angular velocity in degrees/sec.
    moment_of_inertia : float | None
        Rotational inertia.  Auto-computed as ``0.5 * mass * radius**2`` if
        *None*.
    """

    def __init__(self, obj, mass: float = 1.0, restitution: float = 0.8, friction: float = 0.0,
                 radius=None, vx=0.0, vy=0.0, fixed=False,
                 angle: float = 0.0, angular_velocity=0.0, moment_of_inertia=None):
        if not fixed and mass <= 0:
            raise ValueError("Body mass must be > 0")
        if friction < 0:
            raise ValueError("Body friction must be >= 0")
        if restitution < 0:
            raise ValueError("Body restitution must be >= 0")
        if radius is not None and radius < 0:
            raise ValueError(f"Body radius must be >= 0, got {radius}")
        self.obj = obj
        self.mass = mass if not fixed else math.inf
        self.restitution = restitution
        self.friction = friction
        self.fixed = fixed
        # Position: extract from object center at creation time
        cx, cy = _body_center(obj, 0)
        self.x, self.y = float(cx), float(cy)
        self.vx, self.vy = float(vx), float(vy)
        self.fx, self.fy = 0.0, 0.0  # accumulated force
        # Collision shape: 'circle' or 'polygon'
        self.shape, self.radius, self._local_verts = _detect_shape(obj, radius)
        # Rotation / angular dynamics
        self.angle = float(angle)
        self.angular_velocity = float(angular_velocity)
        self.moment_of_inertia = (float(moment_of_inertia) if moment_of_inertia is not None
                                  else 0.5 * self.mass * self.radius ** 2)
        self.torque = 0.0  # accumulated torque for current step
        self._is_wall = False  # set to True for wall bodies (fast-path collision)
        # Trajectories (filled by simulate)
        self._trajectory: list[tuple[float, float]] = []
        self._angle_trajectory: list[float] = []

    def apply_force(self, fx, fy):
        """Accumulate a force for the current step."""
        self.fx += fx
        self.fy += fy

    def apply_torque(self, torque):
        """Accumulate a torque for the current step."""
        self.torque += torque

    def __repr__(self):
        return f'Body(x={self.x:.0f}, y={self.y:.0f}, mass={self.mass})'


class Wall:
    """An axis-aligned infinite wall for collision."""

    def __init__(self, x=None, y=None, restitution: float = 0.9):
        if x is None and y is None:
            raise ValueError("Wall needs at least x or y")
        self.x = x  # vertical wall at x
        self.y = y  # horizontal wall at y
        self.restitution = restitution

    def __repr__(self):
        if self.x is not None:
            return f'Wall(x={self.x})'
        return f'Wall(y={self.y})'


class Spring:
    """A spring constraint between two bodies (or a body and a fixed point).

    Parameters
    ----------
    a, b : Body or tuple
        Two bodies, or a body and a fixed (x, y) anchor.
    stiffness : float
        Spring constant k (N/px).
    rest_length : float
        Natural length (pixels).  If None, uses the initial distance.
    damping : float
        Damping coefficient.
    """

    def __init__(self, a, b, stiffness: float = 0.5, rest_length=None, damping: float = 0.02):
        if stiffness < 0:
            raise ValueError("Spring stiffness must be >= 0")
        if damping < 0:
            raise ValueError("Spring damping must be >= 0")
        self.a = a
        self.b = b
        self.stiffness = stiffness
        self.damping = damping
        ax, ay = _spring_pos(a)
        bx, by = _spring_pos(b)
        if rest_length is None:
            rest_length = math.hypot(bx - ax, by - ay)
        self.rest_length = rest_length

    def __repr__(self):
        return f'Spring(k={self.stiffness}, rest={self.rest_length:.0f})'


class PhysicsSpace:
    """Pre-computed 2D physics simulation.

    Parameters
    ----------
    gravity : tuple
        Gravity vector in px/s^2.  Default ``(0, 980)`` (down in SVG coords).
    dt : float
        Simulation timestep (seconds).
    start : float
        Animation start time.
    """

    def __init__(self, gravity=(0, 980), dt=1 / 120, start: float = 0.0):
        if dt <= 0:
            raise ValueError("PhysicsSpace dt must be > 0")
        self.gravity = gravity
        self.dt = dt
        self.start = start
        self.bodies: list[Body] = []
        self.springs: list[Spring] = []
        self._forces: list = []  # (callable(body, t) -> (fx, fy))
        self._angular_forces: list = []  # (callable(body) -> None, mutates torque)
        self._wall_count = 0  # for repr

    # ── Adding objects ──────────────────────────────────────────────

    def add_body(self, obj, mass: float = 1.0, restitution: float = 0.8, friction: float = 0.0,
                 radius=None, vx=0.0, vy=0.0, fixed=False,
                 angle: float = 0.0, angular_velocity=0.0,
                 moment_of_inertia=None) -> Body:
        """Register a VObject as a physics body and return the Body handle."""
        b = Body(obj, mass=mass, restitution=restitution, friction=friction,
                 radius=radius, vx=vx, vy=vy, fixed=fixed,
                 angle=angle, angular_velocity=angular_velocity,
                 moment_of_inertia=moment_of_inertia)
        self.bodies.append(b)
        return b

    def add_wall(self, x=None, y=None, restitution: float = 0.9,
                 friction: float = 1.0, _outward=1):
        """Add an axis-aligned wall (internally a large static rectangle body).

        Can also accept a pre-built Wall object as the first argument.

        ``_outward`` controls which direction the solid part extends:
        +1 = wall extends in the positive direction (right / down),
        -1 = wall extends in the negative direction (left / up).
        """
        if isinstance(x, Wall):
            # Backward compat: convert Wall to a static rectangle body
            if x.x is not None:
                self.add_wall(x=x.x, restitution=x.restitution)
            if x.y is not None:
                self.add_wall(y=x.y, restitution=x.restitution)
            return
        if x is None and y is None:
            raise ValueError("Wall needs at least x or y")
        from vectormation._shapes import Polygon  # lazy import
        _W, _H = 20000, 500  # wall dimensions (large enough to cover any scene)
        if y is not None:  # horizontal wall at y
            y2 = y + _outward * _H
            verts = [(-_W, y), (_W, y), (_W, y2), (-_W, y2)]
        else:  # vertical wall at x
            x2 = x + _outward * _H
            verts = [(x, -_W), (x, _W), (x2, _W), (x2, -_W)]
        obj = Polygon(*verts)
        b = self.add_body(obj, mass=1, restitution=restitution, friction=friction, fixed=True)
        b._is_wall = True
        # Tag for fast axis-aligned collision (avoids full SAT)
        if y is not None:
            b._wall_axis = 'y'
            b._wall_pos = float(y)
            b._wall_normal = (0.0, -float(_outward))  # points away from solid
        else:
            b._wall_axis = 'x'
            b._wall_pos = float(x)
            b._wall_normal = (-float(_outward), 0.0)
        self._wall_count += 1

    def add_spring(self, a, b, stiffness: float = 0.5, rest_length=None,
                   damping=0.02) -> Spring:
        """Add a spring constraint between two bodies or a body and point."""
        s = Spring(a, b, stiffness=stiffness, rest_length=rest_length,
                   damping=damping)
        self.springs.append(s)
        return s

    def add(self, *bodies):
        """Add pre-constructed Body, Spring, or Wall objects to the simulation."""
        for b in bodies:
            if isinstance(b, Body):
                self.bodies.append(b)
            elif isinstance(b, Spring):
                self.springs.append(b)
            elif isinstance(b, Wall):
                self.add_wall(b)
        return self

    def add_walls(self, left=None, right=None, top=None, bottom=None, restitution: float = 0.9):
        """Add multiple axis-aligned walls at once."""
        if left is not None:
            self.add_wall(x=left, restitution=restitution, _outward=-1)
        if right is not None:
            self.add_wall(x=right, restitution=restitution, _outward=1)
        if top is not None:
            self.add_wall(y=top, restitution=restitution, _outward=-1)
        if bottom is not None:
            self.add_wall(y=bottom, restitution=restitution, _outward=1)
        return self

    def add_force(self, func):
        """Add a global force function ``func(body, t) -> (fx, fy)``."""
        self._forces.append(func)
        return self

    def __repr__(self):
        return f'PhysicsSpace({len(self.bodies)} bodies, {self._wall_count} walls, {len(self.springs)} springs)'

    # ── Simulation ──────────────────────────────────────────────────

    def simulate(self, duration: float = 5.0):
        """Run the simulation for *duration* seconds and bake trajectories.

        After calling this, each body's VObject will have its position
        attributes set as time functions that follow the computed path.
        """
        steps = int(math.ceil(duration / self.dt))
        gx, gy = self.gravity

        # Partition bodies for optimised collision loops
        _walls = [b for b in self.bodies if b._is_wall]
        _dynamic = [b for b in self.bodies if not b.fixed]
        _non_wall = [b for b in self.bodies if not b._is_wall]

        # Initialize trajectories
        for b in self.bodies:
            b._trajectory = [(b.x, b.y)]
            b._angle_trajectory = [b.angle]

        for step in range(steps):
            t = self.start + step * self.dt

            # Reset forces and torques, apply gravity
            for b in _dynamic:
                b.fx, b.fy = gx * b.mass, gy * b.mass
                b.torque = 0.0

            # Apply spring forces
            for s in self.springs:
                _apply_spring(s)

            # Apply custom forces
            for b in _dynamic:
                for force_fn in self._forces:
                    fx, fy = force_fn(b, t)
                    b.fx += fx
                    b.fy += fy

            # Apply angular drag forces
            for drag_fn in self._angular_forces:
                for b in _dynamic:
                    drag_fn(b)

            # Integrate (semi-implicit Euler for stability)
            dt = self.dt
            for b in _dynamic:
                ax = b.fx / b.mass if b.mass else 0
                ay = b.fy / b.mass if b.mass else 0
                b.vx += ax * dt
                b.vy += ay * dt
                b.x += b.vx * dt
                b.y += b.vy * dt
                # Angular integration
                if b.moment_of_inertia > 0:
                    angular_acc = b.torque / b.moment_of_inertia
                    b.angular_velocity += angular_acc * dt
                b.angle += b.angular_velocity * dt

            # Wall-body collisions (fast axis-aligned check)
            for w in _walls:
                for b in _dynamic:
                    _collide_wall(w, b)

            # Body-body collisions (non-wall pairs only)
            for i, a in enumerate(_non_wall):
                for b in _non_wall[i + 1:]:
                    if a.fixed and b.fixed:
                        continue
                    _collide_bodies(a, b)

            # Separation passes to resolve remaining overlaps from stacking
            for _pass in range(2):
                for w in _walls:
                    for b in _dynamic:
                        _separate_wall(w, b)
                for i, a in enumerate(_non_wall):
                    for b in _non_wall[i + 1:]:
                        if a.fixed and b.fixed:
                            continue
                        _separate_bodies(a, b)

            # Record positions and angles
            for b in self.bodies:
                b._trajectory.append((b.x, b.y))
                b._angle_trajectory.append(b.angle)

        # Bake trajectories onto VObjects
        for b in self.bodies:
            _bake_trajectory(b, self.start, self.dt)

    # ── Convenience forces ──────────────────────────────────────────

    def add_drag(self, coefficient: float = 0.01):
        """Add velocity-proportional drag to all bodies."""
        self._forces.append(
            lambda b, t, _c=coefficient: (-b.vx * _c * b.mass, -b.vy * _c * b.mass))
        return self

    def add_attraction(self, target, strength: float = 50000):
        """Add point attraction towards a Body or (x, y) point."""
        self._forces.append(_point_force(target, strength))
        return self

    def add_repulsion(self, target, strength: float = 50000, max_dist: float = 500):
        """Add point repulsion away from a Body or (x, y) point."""
        self._forces.append(_point_force(target, -strength, max_dist))
        return self

    def add_mutual_repulsion(self, strength: float = 5000, max_dist: float = 300):
        """Add pairwise repulsion between all bodies."""
        bodies = self.bodies
        def _mutual(b, _t, _s=strength, _md=max_dist):  # noqa: ARG002
            fx, fy = 0.0, 0.0
            for other in bodies:
                if other is b or other.fixed:
                    continue
                dx, dy = b.x - other.x, b.y - other.y
                dist = math.hypot(dx, dy)
                if dist < 1 or dist > _md:
                    continue
                f = _s / (dist * dist)
                fx += dx / dist * f
                fy += dy / dist * f
            return (fx, fy)
        self._forces.append(_mutual)
        return self

    def add_angular_drag(self, coefficient: float = 0.01):
        """Add angular-velocity-proportional drag (resistance to rotation)."""
        def _drag(b, _c=coefficient):
            b.torque -= b.angular_velocity * _c * b.moment_of_inertia
        self._angular_forces.append(_drag)
        return self


# ── Cloth simulation ────────────────────────────────────────────────

class Cloth:
    """A simple 2D cloth simulation using a grid of particles and springs.

    Parameters
    ----------
    x, y : float
        Top-left corner position.
    width, height : float
        Cloth dimensions in pixels.
    cols, rows : int
        Grid resolution.
    pin_top : bool
        If True, the top row is fixed (pinned).
    stiffness : float
        Spring constant for structural springs.
    """

    def __init__(self, x: float = 560, y: float = 200, width: float = 800, height: float = 500,
                 cols=15, rows=10, pin_top=True, stiffness=2.0,
                 color='#58C4DD', creation: float = 0):
        if cols < 1:
            raise ValueError("Cloth cols must be >= 1")
        if rows < 1:
            raise ValueError("Cloth rows must be >= 1")
        from vectormation._shapes import Line, Dot  # lazy import (circular dep)
        self.cols = cols
        self.rows = rows
        self.space = PhysicsSpace(gravity=(0, 400), dt=1 / 120, start=creation)
        self._bodies: list[list[Body]] = []
        self._lines: list = []

        dx = width / (cols - 1) if cols > 1 else 0
        dy = height / (rows - 1) if rows > 1 else 0

        # Create dots as tiny invisible circles
        for r in range(rows):
            row = []
            for c in range(cols):
                px = x + c * dx
                py = y + r * dy
                dot = Dot(r=2, cx=px, cy=py, fill=color, creation=creation)
                fixed = pin_top and r == 0
                b = self.space.add_body(dot, mass=0.1, restitution=0.2,
                                        radius=2, fixed=fixed)
                row.append(b)
            self._bodies.append(row)

        # Structural springs (horizontal + vertical)
        for r in range(rows):
            for c in range(cols):
                if c < cols - 1:
                    self.space.add_spring(self._bodies[r][c],
                                          self._bodies[r][c + 1],
                                          stiffness=stiffness, damping=0.05)
                if r < rows - 1:
                    self.space.add_spring(self._bodies[r][c],
                                          self._bodies[r + 1][c],
                                          stiffness=stiffness, damping=0.05)

        # Create visual lines between adjacent nodes, storing body pairs
        self._line_pairs: list[tuple] = []  # (line, body_a, body_b)
        for r in range(rows):
            for c in range(cols):
                neighbors = []
                if c < cols - 1:
                    neighbors.append(self._bodies[r][c + 1])
                if r < rows - 1:
                    neighbors.append(self._bodies[r + 1][c])
                ba = self._bodies[r][c]
                for bb in neighbors:
                    ln = Line(x1=ba.x, y1=ba.y, x2=bb.x, y2=bb.y,
                              stroke=color, stroke_width=1, creation=creation)
                    self._lines.append(ln)
                    self._line_pairs.append((ln, ba, bb))

    def simulate(self, duration: float = 5.0):
        """Run the cloth simulation and bake all trajectories."""
        self.space.simulate(duration)
        start, dt = self.space.start, self.space.dt
        for ln, ba, bb in self._line_pairs:
            _bake_line_to_bodies(ln, ba, bb, start, dt)

    def objects(self):
        """Return all VObjects for adding to the canvas."""
        return list(self._lines) + [b.obj for row in self._bodies for b in row]

    def __repr__(self):
        return f'Cloth({self.cols}x{self.rows})'


# ── Internal helpers ────────────────────────────────────────────────

def _body_center(obj, time):
    """Extract the center position of a VObject."""
    # Circles / Ellipses — cx, cy is the true center
    if hasattr(obj, 'cx') and hasattr(obj, 'cy'):
        try:
            return (getattr(obj, 'cx').at_time(time),
                    getattr(obj, 'cy').at_time(time))
        except AttributeError:
            pass
    # Polygon / Star / Rectangle — use vertex centroid (must match _detect_shape)
    if hasattr(obj, 'get_vertices'):
        try:
            verts = obj.get_vertices(time)
            if len(verts) >= 3:
                cx = sum(v[0] for v in verts) / len(verts)
                cy = sum(v[1] for v in verts) / len(verts)
                return (cx, cy)
        except Exception:
            pass
    # Fallback: bbox center
    if hasattr(obj, 'bbox'):
        try:
            bx, by, bw, bh = obj.bbox(time)
            return (bx + bw / 2, by + bh / 2)
        except Exception:
            pass
    # Fallback: x/y (e.g. Text)
    for xa, ya in (('x', 'y'),):
        try:
            return (getattr(obj, xa).at_time(time),
                    getattr(obj, ya).at_time(time))
        except AttributeError:
            pass
    return ORIGIN  # last resort




def _spring_pos(thing):
    """Get (x, y) from a Body or a tuple."""
    if isinstance(thing, Body):
        return (thing.x, thing.y)
    return (float(thing[0]), float(thing[1]))


def _body_velocity(thing):
    """Get (vx, vy) from a Body, or (0, 0) for fixed points."""
    if isinstance(thing, Body):
        return (thing.vx, thing.vy)
    return (0.0, 0.0)


def _point_force(target, strength, max_dist=None):
    """Return a force function for attraction (strength>0) or repulsion (<0).

    The force magnitude is ``|strength| / dist^2``, directed toward or away
    from *target* depending on the sign of *strength*.
    """
    def _force(b, _t):  # noqa: ARG002
        tx, ty = _spring_pos(target)
        dx, dy = tx - b.x, ty - b.y
        dist = math.hypot(dx, dy)
        if dist < 1 or (max_dist is not None and dist > max_dist):
            return (0, 0)
        f = strength / (dist * dist)
        return (dx / dist * f, dy / dist * f)
    return _force


def _apply_spring(s):
    """Apply spring forces to connected bodies."""
    ax, ay = _spring_pos(s.a)
    bx, by = _spring_pos(s.b)
    dx, dy = bx - ax, by - ay
    dist = math.hypot(dx, dy)
    if dist < _MIN_DIST:
        return
    # Spring force: F = -k * (dist - rest) * direction
    stretch = dist - s.rest_length
    ux, uy = dx / dist, dy / dist
    force = s.stiffness * stretch

    # Damping: relative velocity along spring axis
    va = _body_velocity(s.a)
    vb = _body_velocity(s.b)
    dvx, dvy = vb[0] - va[0], vb[1] - va[1]
    rel_v = dvx * ux + dvy * uy
    force += s.damping * rel_v

    fx, fy = force * ux, force * uy
    if isinstance(s.a, Body) and not s.a.fixed:
        s.a.fx += fx
        s.a.fy += fy
    if isinstance(s.b, Body) and not s.b.fixed:
        s.b.fx -= fx
        s.b.fy -= fy


def _contact_offset(b, nx, ny):
    """Return the contact point offset (rx, ry) from body center along normal.

    For circles: the point on the surface toward the collision.
    For polygons: the centroid of vertices closest to the collision boundary.
    """
    if b.shape == 'circle':
        return (nx * b.radius, ny * b.radius)
    rverts = _rotated_local_verts(b)
    if not rverts:
        return (nx * b.radius, ny * b.radius)
    # Project vertices onto normal; contact verts are those with max projection
    projs = [lx * nx + ly * ny for lx, ly in rverts]
    max_p = max(projs)
    tol = 1.5
    contact = [(lx, ly) for (lx, ly), p in zip(rverts, projs) if p > max_p - tol]
    cx = sum(lx for lx, _ in contact) / len(contact)
    cy = sum(ly for _, ly in contact) / len(contact)
    return (cx, cy)


def _rotated_local_verts(b):
    """Return local vertices rotated by the body's current angle."""
    angle = getattr(b, 'angle', 0.0)
    if angle == 0.0:
        return b._local_verts
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return [(lx * cos_a - ly * sin_a, lx * sin_a + ly * cos_a)
            for lx, ly in b._local_verts]


def _world_verts(b):
    """Return the polygon vertices in world space, rotated by body angle."""
    rverts = _rotated_local_verts(b)
    return [(b.x + lx, b.y + ly) for lx, ly in rverts]


# ── SAT helpers ─────────────────────────────────────────────────────

def _project_polygon(verts, ax, ay):
    """Project polygon vertices onto axis (ax, ay). Returns (min, max)."""
    dots = [vx * ax + vy * ay for vx, vy in verts]
    return min(dots), max(dots)


def _project_circle(cx, cy, r, ax, ay):
    """Project a circle onto axis (ax, ay). Returns (min, max)."""
    c = cx * ax + cy * ay
    return c - r, c + r


def _overlap_on_axis(min1, max1, min2, max2):
    """Return overlap amount on a 1D axis, or None if separated."""
    if max1 < min2 or max2 < min1:
        return None
    return min(max1, max2) - max(min1, min2)


def _edge_normals(verts):
    """Yield normalised perpendicular vectors for each edge of a polygon."""
    n = len(verts)
    for i in range(n):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        length = math.hypot(ex, ey)
        if length < _MIN_DIST:
            continue
        yield -ey / length, ex / length  # outward normal


# ── Overlap tests ───────────────────────────────────────────────────

def _overlap_circle_circle(a, b):
    """Return (overlap, ux, uy) or None if no collision."""
    dx, dy = b.x - a.x, b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = a.radius + b.radius
    if dist >= min_dist or dist < _MIN_DIST:
        return None
    ux, uy = dx / dist, dy / dist
    return (min_dist - dist, ux, uy)


def _overlap_polygon_polygon(a, b):
    """SAT test for two convex polygons. Returns (overlap, nx, ny) or None."""
    verts_a = _world_verts(a)
    verts_b = _world_verts(b)
    min_overlap = math.inf
    best_nx, best_ny = 0.0, 0.0
    for ax, ay in _edge_normals(verts_a):
        min1, max1 = _project_polygon(verts_a, ax, ay)
        min2, max2 = _project_polygon(verts_b, ax, ay)
        o = _overlap_on_axis(min1, max1, min2, max2)
        if o is None:
            return None
        if o < min_overlap:
            min_overlap = o
            best_nx, best_ny = ax, ay
    for ax, ay in _edge_normals(verts_b):
        min1, max1 = _project_polygon(verts_a, ax, ay)
        min2, max2 = _project_polygon(verts_b, ax, ay)
        o = _overlap_on_axis(min1, max1, min2, max2)
        if o is None:
            return None
        if o < min_overlap:
            min_overlap = o
            best_nx, best_ny = ax, ay
    # Ensure normal points from a → b
    dx, dy = b.x - a.x, b.y - a.y
    if dx * best_nx + dy * best_ny < 0:
        best_nx, best_ny = -best_nx, -best_ny
    return (min_overlap, best_nx, best_ny)


def _overlap_circle_polygon(circ, poly):
    """SAT test for circle vs convex polygon. Returns (overlap, nx, ny) or None.

    Normal points from circ → poly.
    """
    verts = _world_verts(poly)
    min_overlap = math.inf
    best_nx, best_ny = 0.0, 0.0
    # Test polygon edge normals
    for ax, ay in _edge_normals(verts):
        cmin, cmax = _project_circle(circ.x, circ.y, circ.radius, ax, ay)
        pmin, pmax = _project_polygon(verts, ax, ay)
        o = _overlap_on_axis(cmin, cmax, pmin, pmax)
        if o is None:
            return None
        if o < min_overlap:
            min_overlap = o
            best_nx, best_ny = ax, ay
    # Test axis from circle center to closest polygon vertex
    closest_dsq = math.inf
    closest_vx, closest_vy = verts[0]
    for vx, vy in verts:
        dsq = (vx - circ.x) ** 2 + (vy - circ.y) ** 2
        if dsq < closest_dsq:
            closest_dsq = dsq
            closest_vx, closest_vy = vx, vy
    ax, ay = closest_vx - circ.x, closest_vy - circ.y
    length = math.hypot(ax, ay)
    if length >= _MIN_DIST:
        ax, ay = ax / length, ay / length
        cmin, cmax = _project_circle(circ.x, circ.y, circ.radius, ax, ay)
        pmin, pmax = _project_polygon(verts, ax, ay)
        o = _overlap_on_axis(cmin, cmax, pmin, pmax)
        if o is None:
            return None
        if o < min_overlap:
            min_overlap = o
            best_nx, best_ny = ax, ay
    # Ensure normal points from circ → poly
    dx, dy = poly.x - circ.x, poly.y - circ.y
    if dx * best_nx + dy * best_ny < 0:
        best_nx, best_ny = -best_nx, -best_ny
    return (min_overlap, best_nx, best_ny)


# ── Fast wall overlap ──────────────────────────────────────────────

def _overlap_wall_body(wall, body):
    """Fast axis-aligned wall vs body overlap. Returns (overlap, nx, ny) or None.

    Normal points from wall toward body (push direction).
    """
    nx, ny = wall._wall_normal  # points away from solid
    pos = wall._wall_pos
    # Project body extent onto wall normal axis
    if body.shape == 'circle':
        extent = body.radius
    else:
        rverts = _rotated_local_verts(body)
        # Max projection toward the wall (into the solid)
        extent = max(lx * (-nx) + ly * (-ny) for lx, ly in rverts) if rverts else body.radius
    # For y-wall with ny=-outward, wall_pos = y
    if wall._wall_axis == 'y':
        outward = -ny  # +1 for floor, -1 for ceiling
        if outward > 0:  # floor: body penetrates if body_bottom > wall_pos
            body_edge = body.y + extent
            overlap = body_edge - pos
        else:  # ceiling: body penetrates if body_top < wall_pos
            body_edge = body.y - extent
            overlap = pos - body_edge
    else:  # x-wall
        outward = -nx
        if outward > 0:  # right wall
            body_edge = body.x + extent
            overlap = body_edge - pos
        else:  # left wall
            body_edge = body.x - extent
            overlap = pos - body_edge
    if overlap <= 0:
        return None
    return (overlap, nx, ny)


def _collide_wall(wall, body):
    """Resolve collision between an axis-aligned wall and a dynamic body."""
    result = _overlap_wall_body(wall, body)
    if result is None:
        return
    overlap, ux, uy = result
    # Separate: push body away from wall
    body.x += ux * overlap
    body.y += uy * overlap
    # Impulse (wall is fixed, so only body changes)
    ra_x, ra_y = _contact_offset(body, -ux, -uy)
    omega = math.radians(body.angular_velocity)
    inv_I = (1 / body.moment_of_inertia) if body.moment_of_inertia > 0 else 0
    inv_m = 1 / body.mass
    # Velocity of contact point
    va_cx = body.vx + (-omega * ra_y)
    va_cy = body.vy + (omega * ra_x)
    # Normal velocity (toward wall = negative of push direction)
    dvn = -(va_cx * ux + va_cy * uy)
    if dvn < 0:
        return
    ra_cross_n = ra_x * (-uy) - ra_y * (-ux)
    denom = inv_m + ra_cross_n * ra_cross_n * inv_I
    if denom == 0:
        return
    e = min(body.restitution, wall.restitution)
    jn = (1 + e) * dvn / denom
    body.vx += jn * inv_m * ux
    body.vy += jn * inv_m * uy
    if inv_I > 0:
        body.angular_velocity -= math.degrees(jn * ra_cross_n * inv_I)
    # Tangential friction
    fric = min(body.friction, wall.friction)
    if fric > 0:
        tx, ty = uy, -ux
        dvt = va_cx * tx + va_cy * ty
        ra_cross_t = ra_x * ty - ra_y * tx
        denom_t = inv_m + ra_cross_t * ra_cross_t * inv_I
        if denom_t > 0:
            jt = -fric * dvt / denom_t
            max_jt = abs(jn) * fric
            jt = max(-max_jt, min(max_jt, jt))
            body.vx += jt * inv_m * tx
            body.vy += jt * inv_m * ty
            if inv_I > 0:
                body.angular_velocity += math.degrees(jt * ra_cross_t * inv_I)


def _separate_wall(wall, body):
    """Position-only wall separation (no impulse)."""
    result = _overlap_wall_body(wall, body)
    if result is None:
        return
    overlap, ux, uy = result
    body.x += ux * overlap
    body.y += uy * overlap


# ── Body-body collision ─────────────────────────────────────────────


def _collide_bodies(a, b):
    """Resolve elastic collision between two non-wall bodies using SAT."""
    # Quick bounding-radius rejection
    dx, dy = b.x - a.x, b.y - a.y
    if dx * dx + dy * dy > (a.radius + b.radius + 1) ** 2:
        return
    sa, sb = a.shape, b.shape
    if sa == 'circle' and sb == 'circle':
        result = _overlap_circle_circle(a, b)
    elif sa == 'polygon' and sb == 'polygon':
        result = _overlap_polygon_polygon(a, b)
    elif sa == 'circle' and sb == 'polygon':
        result = _overlap_circle_polygon(a, b)
    elif sa == 'polygon' and sb == 'circle':
        result = _overlap_circle_polygon(b, a)
        if result:
            overlap, nx, ny = result
            result = (overlap, -nx, -ny)
    else:
        return
    if result is None:
        return
    overlap, ux, uy = result

    # Separate bodies along MTV
    if a.fixed:
        b.x += ux * overlap
        b.y += uy * overlap
    elif b.fixed:
        a.x -= ux * overlap
        a.y -= uy * overlap
    else:
        total_inv = 1 / a.mass + 1 / b.mass
        wa = (1 / a.mass) / total_inv
        wb = (1 / b.mass) / total_inv
        a.x -= ux * overlap * wa
        a.y -= uy * overlap * wa
        b.x += ux * overlap * wb
        b.y += uy * overlap * wb

    # Contact offsets from each body's center (toward the other body)
    ra_x, ra_y = _contact_offset(a, ux, uy)
    rb_x, rb_y = _contact_offset(b, -ux, -uy)

    omega_a = math.radians(a.angular_velocity) if not a.fixed else 0
    omega_b = math.radians(b.angular_velocity) if not b.fixed else 0
    inv_Ia = (1 / a.moment_of_inertia) if (not a.fixed and a.moment_of_inertia > 0) else 0
    inv_Ib = (1 / b.moment_of_inertia) if (not b.fixed and b.moment_of_inertia > 0) else 0

    # Velocity of each contact point
    va_cx = a.vx + (-omega_a * ra_y)
    va_cy = a.vy + (omega_a * ra_x)
    vb_cx = b.vx + (-omega_b * rb_y)
    vb_cy = b.vy + (omega_b * rb_x)

    # Relative velocity at contact point
    dvx, dvy = va_cx - vb_cx, va_cy - vb_cy
    dvn = dvx * ux + dvy * uy
    if dvn < 0:  # already separating
        return

    inv_ma = 0 if a.fixed else 1 / a.mass
    inv_mb = 0 if b.fixed else 1 / b.mass

    # Effective mass with rotational contribution: 1/ma + 1/mb + (ra×n)²/Ia + (rb×n)²/Ib
    ra_cross_n = ra_x * uy - ra_y * ux
    rb_cross_n = rb_x * uy - rb_y * ux
    denom = inv_ma + inv_mb + ra_cross_n * ra_cross_n * inv_Ia + rb_cross_n * rb_cross_n * inv_Ib
    if denom == 0:
        return

    e = min(a.restitution, b.restitution)
    jn = -(1 + e) * dvn / denom

    if not a.fixed:
        a.vx += jn * inv_ma * ux
        a.vy += jn * inv_ma * uy
        if inv_Ia > 0:
            a.angular_velocity += math.degrees(jn * ra_cross_n * inv_Ia)
    if not b.fixed:
        b.vx -= jn * inv_mb * ux
        b.vy -= jn * inv_mb * uy
        if inv_Ib > 0:
            b.angular_velocity -= math.degrees(jn * rb_cross_n * inv_Ib)

    # Tangential friction impulse
    fric = min(a.friction, b.friction)
    if fric > 0:
        tx, ty = -uy, ux
        dvt = dvx * tx + dvy * ty
        ra_cross_t = ra_x * ty - ra_y * tx
        rb_cross_t = rb_x * ty - rb_y * tx
        denom_t = inv_ma + inv_mb + ra_cross_t * ra_cross_t * inv_Ia + rb_cross_t * rb_cross_t * inv_Ib
        if denom_t > 0:
            jt = -fric * dvt / denom_t
            max_jt = abs(jn) * fric
            jt = max(-max_jt, min(max_jt, jt))
            if not a.fixed:
                a.vx += jt * inv_ma * tx
                a.vy += jt * inv_ma * ty
                if inv_Ia > 0:
                    a.angular_velocity += math.degrees(jt * ra_cross_t * inv_Ia)
            if not b.fixed:
                b.vx -= jt * inv_mb * tx
                b.vy -= jt * inv_mb * ty
                if inv_Ib > 0:
                    b.angular_velocity -= math.degrees(jt * rb_cross_t * inv_Ib)


def _separate_bodies(a, b):
    """Position-only separation pass for non-wall body pairs."""
    dx, dy = b.x - a.x, b.y - a.y
    if dx * dx + dy * dy > (a.radius + b.radius + 1) ** 2:
        return
    sa, sb = a.shape, b.shape
    if sa == 'circle' and sb == 'circle':
        result = _overlap_circle_circle(a, b)
    elif sa == 'polygon' and sb == 'polygon':
        result = _overlap_polygon_polygon(a, b)
    elif sa == 'circle' and sb == 'polygon':
        result = _overlap_circle_polygon(a, b)
    elif sa == 'polygon' and sb == 'circle':
        result = _overlap_circle_polygon(b, a)
        if result:
            overlap, nx, ny = result
            result = (overlap, -nx, -ny)
    else:
        return
    if result is None:
        return
    overlap, ux, uy = result
    if a.fixed:
        b.x += ux * overlap
        b.y += uy * overlap
    elif b.fixed:
        a.x -= ux * overlap
        a.y -= uy * overlap
    else:
        total_inv = 1 / a.mass + 1 / b.mass
        wa = (1 / a.mass) / total_inv
        wb = (1 / b.mass) / total_inv
        a.x -= ux * overlap * wa
        a.y -= uy * overlap * wa
        b.x += ux * overlap * wb
        b.y += uy * overlap * wb


def _traj_at(traj, start, dt, t):
    """Interpolate a trajectory at time *t*. Works for (x,y) tuples and scalars."""
    elapsed = t - start
    if elapsed <= 0:
        return traj[0]
    idx = elapsed / dt
    i = int(idx)
    if i >= len(traj) - 1:
        return traj[-1]
    frac = idx - i
    a, b = traj[i], traj[i + 1]
    if isinstance(a, tuple):
        return (a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac)
    return a + (b - a) * frac


def _bake_trajectory(body, start, dt):
    """Set a body's VObject position and rotation as time functions."""
    traj = body._trajectory
    if not traj or body.fixed:
        return
    obj = body.obj
    end_time = start + (len(traj) - 1) * dt
    pos_at = lambda t, _tr=traj: _traj_at(_tr, start, dt, t)

    # Set position via the appropriate attribute
    if hasattr(obj, 'cx') and hasattr(obj, 'cy'):
        # Circle / Ellipse / Dot — set center directly
        obj.cx.set_onward(start, lambda t: pos_at(t)[0])
        obj.cy.set_onward(start, lambda t: pos_at(t)[1])
        obj.cx.last_change = max(obj.cx.last_change, end_time)
        obj.cy.last_change = max(obj.cy.last_change, end_time)
    else:
        # Generic VObject (Polygon, Rectangle, …) — apply delta via add_onward
        x0, y0 = traj[0]  # initial simulated center
        def _delta(t, _x0=x0, _y0=y0):
            px, py = pos_at(t)
            return (px - _x0, py - _y0)
        def _dx(t, _x0=x0):
            return pos_at(t)[0] - _x0
        def _dy(t, _y0=y0):
            return pos_at(t)[1] - _y0
        for coor in obj._shift_coors():
            coor.add_onward(start, _delta, last_change=end_time)
        for xa, ya in obj._shift_reals():
            xa.add_onward(start, _dx, last_change=end_time)
            ya.add_onward(start, _dy, last_change=end_time)

    # Bake rotation if any angular motion was recorded
    ang_traj = body._angle_trajectory
    if ang_traj and hasattr(obj, 'styling'):
        # Check if there is any actual rotation to bake
        if any(a != ang_traj[0] for a in ang_traj):
            def _rot_at(t, _atr=ang_traj, _ptr=traj):
                angle = _traj_at(_atr, start, dt, t)
                px, py = _traj_at(_ptr, start, dt, t)
                # Negate: styling convention is positive=CCW, physics uses CW
                return (-angle, px, py)
            obj.styling.rotation.set_onward(start, _rot_at)
            obj.styling.rotation.last_change = max(obj.styling.rotation.last_change, end_time)


def _bake_line_to_bodies(line, ba, bb, start, dt):
    """Set a Line's endpoints to track two body trajectories."""
    pos_a = lambda t, _tr=ba._trajectory: _traj_at(_tr, start, dt, t)
    pos_b = lambda t, _tr=bb._trajectory: _traj_at(_tr, start, dt, t)
    line.p1.set_onward(start, pos_a)
    line.p2.set_onward(start, pos_b)
    end_time = start + max(len(ba._trajectory), len(bb._trajectory), 1) * dt
    line.p1.last_change = max(line.p1.last_change, end_time)
    line.p2.last_change = max(line.p2.last_change, end_time)
