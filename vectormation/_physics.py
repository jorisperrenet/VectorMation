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
    """

    def __init__(self, obj, mass=1.0, restitution=0.8, friction=0.0,
                 radius=None, vx=0.0, vy=0.0, fixed=False):
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
        self.radius = float(radius) if radius is not None else _guess_radius(obj)
        # Trajectory (filled by simulate)
        self._trajectory: list[tuple[float, float]] = []

    def apply_force(self, fx, fy):
        """Accumulate a force for the current step."""
        self.fx += fx
        self.fy += fy


class Wall:
    """An axis-aligned infinite wall for collision."""

    def __init__(self, x=None, y=None, restitution=0.9):
        if x is None and y is None:
            raise ValueError("Wall needs at least x or y")
        self.x = x  # vertical wall at x
        self.y = y  # horizontal wall at y
        self.restitution = restitution


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

    def __init__(self, a, b, stiffness=0.5, rest_length=None, damping=0.02):
        self.a = a
        self.b = b
        self.stiffness = stiffness
        self.damping = damping
        ax, ay = _spring_pos(a)
        bx, by = _spring_pos(b)
        if rest_length is None:
            rest_length = math.hypot(bx - ax, by - ay)
        self.rest_length = rest_length


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

    def __init__(self, gravity=(0, 980), dt=1 / 120, start=0.0):
        self.gravity = gravity
        self.dt = dt
        self.start = start
        self.bodies: list[Body] = []
        self.walls: list[Wall] = []
        self.springs: list[Spring] = []
        self._forces: list = []  # (callable(body, t) -> (fx, fy))

    # ── Adding objects ──────────────────────────────────────────────

    def add_body(self, obj, mass=1.0, restitution=0.8, friction=0.0,
                 radius=None, vx=0.0, vy=0.0, fixed=False) -> Body:
        """Register a VObject as a physics body and return the Body handle."""
        b = Body(obj, mass=mass, restitution=restitution, friction=friction,
                 radius=radius, vx=vx, vy=vy, fixed=fixed)
        self.bodies.append(b)
        return b

    def add_wall(self, x=None, y=None, restitution=0.9) -> Wall:
        """Add an infinite axis-aligned wall."""
        w = Wall(x=x, y=y, restitution=restitution)
        self.walls.append(w)
        return w

    def add_spring(self, a, b, stiffness=0.5, rest_length=None,
                   damping=0.02) -> Spring:
        """Add a spring constraint between two bodies or a body and point."""
        s = Spring(a, b, stiffness=stiffness, rest_length=rest_length,
                   damping=damping)
        self.springs.append(s)
        return s

    def add(self, *bodies):
        """Add pre-constructed Body objects to the simulation."""
        for b in bodies:
            if isinstance(b, Body):
                self.bodies.append(b)
            elif isinstance(b, Spring):
                self.springs.append(b)
        return self

    def add_walls(self, left=None, right=None, top=None, bottom=None, restitution=0.9):
        """Add multiple axis-aligned walls at once."""
        for x in (left, right):
            if x is not None:
                self.add_wall(x=x, restitution=restitution)
        for y in (top, bottom):
            if y is not None:
                self.add_wall(y=y, restitution=restitution)
        return self

    def add_force(self, func):
        """Add a global force function ``func(body, t) -> (fx, fy)``."""
        self._forces.append(func)

    # ── Simulation ──────────────────────────────────────────────────

    def simulate(self, duration=5.0):
        """Run the simulation for *duration* seconds and bake trajectories.

        After calling this, each body's VObject will have its position
        attributes set as time functions that follow the computed path.
        """
        steps = int(math.ceil(duration / self.dt))
        gx, gy = self.gravity

        # Initialize trajectories
        for b in self.bodies:
            b._trajectory = [(b.x, b.y)]

        for step in range(steps):
            t = self.start + step * self.dt

            # Reset forces, apply gravity
            for b in self.bodies:
                if b.fixed:
                    continue
                b.fx, b.fy = gx * b.mass, gy * b.mass

            # Apply spring forces
            for s in self.springs:
                _apply_spring(s)

            # Apply custom forces
            for force_fn in self._forces:
                for b in self.bodies:
                    if b.fixed:
                        continue
                    fx, fy = force_fn(b, t)
                    b.fx += fx
                    b.fy += fy

            # Integrate (semi-implicit Euler for stability)
            for b in self.bodies:
                if b.fixed:
                    b._trajectory.append((b.x, b.y))
                    continue
                ax = b.fx / b.mass
                ay = b.fy / b.mass
                b.vx += ax * self.dt
                b.vy += ay * self.dt
                b.x += b.vx * self.dt
                b.y += b.vy * self.dt

            # Wall collisions
            for b in self.bodies:
                if b.fixed:
                    continue
                for w in self.walls:
                    _collide_wall(b, w)

            # Body-body collisions
            for i, a in enumerate(self.bodies):
                for b in self.bodies[i + 1:]:
                    if a.fixed and b.fixed:
                        continue
                    _collide_bodies(a, b)

            # Record positions
            for b in self.bodies:
                b._trajectory.append((b.x, b.y))

        # Bake trajectories onto VObjects
        for b in self.bodies:
            _bake_trajectory(b, self.start, self.dt)

    # ── Convenience forces ──────────────────────────────────────────

    def add_drag(self, coefficient=0.01):
        """Add velocity-proportional drag to all bodies."""
        c = coefficient
        self._forces.append(
            lambda b, t: (-b.vx * c * b.mass, -b.vy * c * b.mass))

    def add_attraction(self, target, strength=50000):
        """Add point attraction towards a Body or (x, y) point."""
        self._forces.append(_point_force(target, strength))

    def add_repulsion(self, target, strength=50000, max_dist=500):
        """Add point repulsion away from a Body or (x, y) point."""
        self._forces.append(_point_force(target, -strength, max_dist))

    def add_mutual_repulsion(self, strength=5000, max_dist=300):
        """Add pairwise repulsion between all bodies."""
        bodies = self.bodies
        s = strength
        md = max_dist
        def _mutual(b, t):
            fx, fy = 0.0, 0.0
            for other in bodies:
                if other is b or other.fixed:
                    continue
                dx, dy = b.x - other.x, b.y - other.y
                dist = math.hypot(dx, dy)
                if dist < 1 or dist > md:
                    continue
                f = s / (dist * dist)
                fx += dx / dist * f
                fy += dy / dist * f
            return (fx, fy)
        self._forces.append(_mutual)


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

    def __init__(self, x=560, y=200, width=800, height=500,
                 cols=15, rows=10, pin_top=True, stiffness=2.0,
                 color='#58C4DD', creation=0):
        from vectormation._shapes import Line, Dot  # noqa: F811
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

    def simulate(self, duration=5.0):
        """Run the cloth simulation and bake all trajectories."""
        self.space.simulate(duration)
        start, dt = self.space.start, self.space.dt
        for ln, ba, bb in self._line_pairs:
            _bake_line_to_bodies(ln, ba, bb, start, dt)

    def objects(self):
        """Return all VObjects for adding to the canvas."""
        return list(self._lines) + [b.obj for row in self._bodies for b in row]


# ── Internal helpers ────────────────────────────────────────────────

def _body_center(obj, time):
    """Extract the center position of a VObject."""
    for xa, ya in (('cx', 'cy'), ('x', 'y')):
        try:
            return (getattr(obj, xa).at_time(time),
                    getattr(obj, ya).at_time(time))
        except AttributeError:
            pass
    try:
        c = obj.c.at_time(time)
        return (c[0], c[1])
    except AttributeError:
        return (960, 540)  # fallback to center


def _guess_radius(obj):
    """Try to extract a collision radius from a VObject."""
    for attr in ('rx', 'r'):
        if hasattr(obj, attr):
            a = getattr(obj, attr)
            if hasattr(a, 'at_time'):
                return float(a.at_time(0))
            return float(a)
    # For rectangles, use half-diagonal
    try:
        w = obj.width.at_time(0)
        h = obj.height.at_time(0)
        return math.hypot(w, h) / 2
    except AttributeError:
        return 20.0  # default


def _spring_pos(thing):
    """Get (x, y) from a Body or a tuple."""
    if isinstance(thing, Body):
        return (thing.x, thing.y)
    return (float(thing[0]), float(thing[1]))


def _point_force(target, strength, max_dist=None):
    """Return a force function for attraction (strength>0) or repulsion (<0).

    The force magnitude is ``|strength| / dist^2``, directed toward or away
    from *target* depending on the sign of *strength*.
    """
    def _force(b, t):
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
    if dist < 0.001:
        return
    # Spring force: F = -k * (dist - rest) * direction
    stretch = dist - s.rest_length
    ux, uy = dx / dist, dy / dist
    force = s.stiffness * stretch

    # Damping: relative velocity along spring axis
    if isinstance(s.a, Body) and isinstance(s.b, Body):
        dvx, dvy = s.b.vx - s.a.vx, s.b.vy - s.a.vy
    elif isinstance(s.a, Body):
        dvx, dvy = -s.a.vx, -s.a.vy
    else:
        dvx, dvy = s.b.vx, s.b.vy
    rel_v = dvx * ux + dvy * uy
    force += s.damping * rel_v

    fx, fy = force * ux, force * uy
    if isinstance(s.a, Body) and not s.a.fixed:
        s.a.fx += fx
        s.a.fy += fy
    if isinstance(s.b, Body) and not s.b.fixed:
        s.b.fx -= fx
        s.b.fy -= fy


def _collide_wall(b, w):
    """Resolve wall collision for a body."""
    e = b.restitution * w.restitution
    fric = 1 - b.friction
    if w.y is not None:  # horizontal wall
        if b.y + b.radius > w.y and b.vy > 0:  # penetrating from above
            b.y = w.y - b.radius
            b.vy *= -e
            b.vx *= fric
        elif b.y - b.radius < w.y and b.vy < 0:  # penetrating from below
            b.y = w.y + b.radius
            b.vy *= -e
            b.vx *= fric
    if w.x is not None:  # vertical wall
        if b.x + b.radius > w.x and b.vx > 0:
            b.x = w.x - b.radius
            b.vx *= -e
            b.vy *= fric
        elif b.x - b.radius < w.x and b.vx < 0:
            b.x = w.x + b.radius
            b.vx *= -e
            b.vy *= fric


def _collide_bodies(a, b):
    """Resolve elastic collision between two circular bodies."""
    dx, dy = b.x - a.x, b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = a.radius + b.radius
    if dist >= min_dist or dist < 0.001:
        return

    # Separate bodies
    overlap = min_dist - dist
    ux, uy = dx / dist, dy / dist
    if a.fixed:
        b.x += ux * overlap
        b.y += uy * overlap
    elif b.fixed:
        a.x -= ux * overlap
        a.y -= uy * overlap
    else:
        a.x -= ux * overlap / 2
        a.y -= uy * overlap / 2
        b.x += ux * overlap / 2
        b.y += uy * overlap / 2

    # Impulse-based velocity resolution
    e = min(a.restitution, b.restitution)
    dvx, dvy = a.vx - b.vx, a.vy - b.vy
    dvn = dvx * ux + dvy * uy
    if dvn > 0:  # already separating
        return

    if a.fixed:
        j = -(1 + e) * dvn
        b.vx -= j * ux
        b.vy -= j * uy
    elif b.fixed:
        j = -(1 + e) * dvn
        a.vx += j * ux
        a.vy += j * uy
    else:
        j = -(1 + e) * dvn / (1 / a.mass + 1 / b.mass)
        a.vx += j / a.mass * ux
        a.vy += j / a.mass * uy
        b.vx -= j / b.mass * ux
        b.vy -= j / b.mass * uy


def _traj_at(traj, start, dt, t):
    """Interpolate a trajectory at time *t* and return (x, y)."""
    elapsed = t - start
    if elapsed <= 0:
        return traj[0]
    idx = elapsed / dt
    i = int(idx)
    if i >= len(traj) - 1:
        return traj[-1]
    frac = idx - i
    x1, y1 = traj[i]
    x2, y2 = traj[i + 1]
    return (x1 + (x2 - x1) * frac, y1 + (y2 - y1) * frac)


def _bake_trajectory(body, start, dt):
    """Set a body's VObject position as a time function from its trajectory."""
    traj = body._trajectory
    if not traj or body.fixed:
        return
    obj = body.obj
    pos_at = lambda t, _tr=traj: _traj_at(_tr, start, dt, t)

    # Set position via the appropriate attribute
    if hasattr(obj, 'c'):
        obj.c.set_onward(start, pos_at)
    elif hasattr(obj, 'cx') and hasattr(obj, 'cy'):
        obj.cx.set_onward(start, lambda t: pos_at(t)[0])
        obj.cy.set_onward(start, lambda t: pos_at(t)[1])
    elif hasattr(obj, 'x') and hasattr(obj, 'y'):
        obj.x.set_onward(start, lambda t: pos_at(t)[0])
        obj.y.set_onward(start, lambda t: pos_at(t)[1])


def _bake_line_to_bodies(line, ba, bb, start, dt):
    """Set a Line's endpoints to track two body trajectories."""
    pos_a = lambda t, _tr=ba._trajectory: _traj_at(_tr, start, dt, t)
    pos_b = lambda t, _tr=bb._trajectory: _traj_at(_tr, start, dt, t)
    line.p1.set_onward(start, pos_a)
    line.p2.set_onward(start, pos_b)
