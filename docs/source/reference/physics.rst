Physics Engine
==============

Pre-computed 2D physics simulation that maps trajectories onto time-varying
VObject attributes. Physics bodies are stepped via semi-implicit Euler
integration at a configurable ``dt``, then positions are baked as time
functions so the SVG renderer can sample any frame.

.. admonition:: Example: Basic bouncing ball
   :class: example

   .. code-block:: python

      from vectormation.objects import *
      from vectormation._physics import PhysicsSpace

      canvas = VectorMathAnim()
      canvas.set_background()

      space = PhysicsSpace(gravity=(0, 980), dt=1/120)
      ball = Circle(r=20, cx=960, cy=100, fill='#58C4DD')
      b = space.add_body(ball, mass=1, restitution=0.7)
      space.add_wall(y=900)     # floor
      space.simulate(duration=5)

      canvas.add_objects(ball)
      canvas.browser_display(fps=60)

----

PhysicsSpace
------------

.. py:class:: PhysicsSpace(gravity=(0, 980), dt=1/120, start=0.0)

   The simulation container. Manages bodies, walls, springs, and forces.

   :param tuple gravity: Gravity vector in px/s\ :sup:`2`. Default ``(0, 980)``
      points downward in SVG coordinates.
   :param float dt: Simulation timestep in seconds.
   :param float start: Animation start time (offsets baked trajectories).

   .. py:method:: add_body(obj, mass=1.0, restitution=0.8, friction=0.0, radius=None, vx=0.0, vy=0.0, fixed=False, angle=0.0, angular_velocity=0.0, moment_of_inertia=None) -> Body

      Register a VObject as a physics body and return a :py:class:`Body` handle.
      If *radius* is ``None`` it is auto-detected from the object (e.g. ``Circle.r``).
      Set *fixed=True* for immovable obstacles.

      :param float angle: Initial rotation angle in radians.
      :param float angular_velocity: Initial angular velocity (rad/s).
      :param float moment_of_inertia: Rotational inertia (auto-computed if ``None``).

   .. py:method:: add_wall(x=None, y=None, restitution=0.9, friction=1.0) -> Wall

      Add an infinite axis-aligned wall. Specify *x* for a vertical wall or
      *y* for a horizontal wall.

   .. py:method:: add_walls(left=40, right=1880, top=40, bottom=1040, restitution=0.9)

      Convenience method: add four walls forming a bounding box.

   .. py:method:: add_spring(a, b, stiffness=0.5, rest_length=None, damping=0.02) -> Spring

      Add a spring constraint between two bodies, or between a body and a
      fixed ``(x, y)`` anchor point.

   .. py:method:: add_force(func)

      Add a global force function ``func(body, t) -> (fx, fy)`` that is
      evaluated every timestep for every non-fixed body.

   .. py:method:: simulate(duration=5.0)

      Run the simulation for *duration* seconds and bake trajectories
      onto each body's VObject. After calling this, each VObject will
      have its position attributes set as time functions.

   .. py:method:: add_drag(coefficient=0.01)

      Add velocity-proportional drag to all bodies.

   .. py:method:: add_attraction(target, strength=50000)

      Add gravitational attraction towards a :py:class:`Body` or ``(x, y)`` point.

   .. py:method:: add_repulsion(target, strength=50000, max_dist=500)

      Add repulsion away from a :py:class:`Body` or ``(x, y)`` point.

   .. py:method:: add_mutual_repulsion(strength=5000, max_dist=300)

      Add pairwise repulsion between all bodies.

----

Body
----

.. py:class:: Body(obj, mass=1.0, restitution=0.8, friction=0.0, radius=None, vx=0.0, vy=0.0, fixed=False, angle=0.0, angular_velocity=0.0, moment_of_inertia=None)

   A physics body wrapping a VObject. Created via
   :py:meth:`PhysicsSpace.add_body`.

   :param VObject obj: The visual object to move.
   :param float mass: Mass in kg. Use ``math.inf`` for static bodies.
   :param float restitution: Bounciness coefficient (0--1).
   :param float friction: Friction coefficient applied during collisions.
   :param float radius: Collision radius (auto-detected from ``Circle``/``Dot`` if ``None``).
   :param float vx: Initial horizontal velocity (px/s).
   :param float vy: Initial vertical velocity (px/s).
   :param bool fixed: If ``True``, the body does not move.

   .. py:attribute:: obj

      The wrapped VObject.

   .. py:attribute:: x
      :type: float

      Current x position (updated during simulation).

   .. py:attribute:: y
      :type: float

      Current y position.

   .. py:method:: apply_force(fx, fy)

      Accumulate a force for the current simulation step.

   .. py:method:: apply_torque(torque)

      Accumulate a torque for the current simulation step.

----

Wall
----

.. py:class:: Wall(x=None, y=None, restitution=0.9)

   An infinite axis-aligned wall for collision. Specify *x* for a vertical
   wall or *y* for a horizontal wall.

   :param float x: X-coordinate of a vertical wall.
   :param float y: Y-coordinate of a horizontal wall.
   :param float restitution: Bounciness coefficient.

----

Spring
------

.. py:class:: Spring(a, b, stiffness=0.5, rest_length=None, damping=0.02)

   A spring constraint between two :py:class:`Body` instances or between a
   body and a fixed ``(x, y)`` anchor.

   :param a: First body or ``(x, y)`` anchor.
   :param b: Second body or ``(x, y)`` anchor.
   :param float stiffness: Spring constant *k* (N/px).
   :param float rest_length: Natural length in pixels (uses initial distance if ``None``).
   :param float damping: Damping coefficient.

----

Cloth
-----

.. py:class:: Cloth(x=560, y=200, width=800, height=500, cols=15, rows=10, pin_top=True, stiffness=2.0, color='#58C4DD', creation=0)

   A 2D cloth simulation using a grid of particles connected by springs.
   The top row can be pinned (fixed) to create a hanging curtain effect.

   :param float x: Top-left x position.
   :param float y: Top-left y position.
   :param float width: Cloth width in pixels.
   :param float height: Cloth height in pixels.
   :param int cols: Number of columns in the particle grid.
   :param int rows: Number of rows in the particle grid.
   :param bool pin_top: Pin the top row of particles.
   :param float stiffness: Spring constant for structural springs.

   .. py:method:: simulate(duration=5.0)

      Run the cloth simulation and bake all particle and line trajectories.

   .. py:method:: objects()

      Return a list of all VObjects (lines and dots) for adding to the canvas.

   .. admonition:: Example: Cloth simulation
      :class: example

      .. code-block:: python

         from vectormation.objects import *
         from vectormation._physics import Cloth

         canvas = VectorMathAnim()
         canvas.set_background()

         cloth = Cloth(cols=20, rows=12, stiffness=3.0)
         cloth.simulate(duration=4)

         canvas.add_objects(*cloth.objects())
         canvas.browser_display(fps=60)

.. admonition:: Example: Bouncing balls
   :class: example

   .. raw:: html

      <video src="../_static/videos/physics_bounce.mp4" controls autoplay loop muted></video>

   Balls bouncing with walls.

   .. literalinclude:: ../../../examples/reference/physics_bounce.py
      :language: python
      :start-after: parse_args()
      :end-before: v.browser_display
