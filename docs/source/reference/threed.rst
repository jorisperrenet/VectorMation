3D Objects
==========

VectorMation includes a lightweight 3D module for rendering three-dimensional
scenes as SVG. Objects are projected orthographically and depth-sorted each
frame, so surfaces, primitives, and axis lines correctly occlude one another.

All 3D content lives inside a :py:class:`ThreeDAxes` instance, which acts as
both the coordinate system and the renderer. Surfaces are registered with
:py:meth:`~ThreeDAxes.add_surface`, primitives with
:py:meth:`~ThreeDAxes.add_3d`.

.. code-block:: python

   from vectormation.objects import *
   import math

   canvas = VectorMathAnim()
   canvas.set_background()

   axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-3, 3))
   canvas.add_objects(axes)

----

ThreeDAxes
----------

.. py:class:: ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-3, 3), cx=960, cy=540, scale=160, phi=75deg, theta=-30deg, show_ticks=True, show_labels=True, show_grid=False, x_label='x', y_label='y', z_label='z', **styling)

   Three-dimensional coordinate axes with camera control, ticks, labels, and
   depth-sorted rendering.

   Bases: :py:class:`VCollection`

   :param tuple x_range: ``(min, max)`` for the x-axis.
   :param tuple y_range: ``(min, max)`` for the y-axis.
   :param tuple z_range: ``(min, max)`` for the z-axis.
   :param float cx: Screen centre x (default ``960``).
   :param float cy: Screen centre y (default ``540``).
   :param float scale: Pixels per math unit (default ``160``).
   :param float phi: Camera elevation in radians (default ``math.radians(75)``).
   :param float theta: Camera azimuth in radians (default ``math.radians(-30)``).
   :param bool show_ticks: Draw tick marks on axes (default ``True``).
   :param bool show_labels: Draw numeric tick labels (default ``True``).
   :param bool show_grid: Draw ground-plane grid lines (default ``False``).
   :param str x_label: Label for x-axis, or ``None`` to hide.
   :param str y_label: Label for y-axis, or ``None`` to hide.
   :param str z_label: Label for z-axis, or ``None`` to hide.

   .. py:attribute:: phi
      :type: Real

      Camera elevation angle in radians (animatable).

   .. py:attribute:: theta
      :type: Real

      Camera azimuth angle in radians (animatable).

   .. rubric:: Camera Methods

   .. py:method:: set_camera_orientation(start, end, phi=None, theta=None, easing=smooth)

      Animate camera elevation and/or azimuth over ``[start, end]``.

      :param float phi: Target elevation in radians, or ``None`` to keep current.
      :param float theta: Target azimuth in radians, or ``None`` to keep current.

      .. code-block:: python

         # Rotate camera to a top-down view over 3 seconds
         axes.set_camera_orientation(0, 3, phi=0, theta=0)

   .. py:method:: begin_ambient_camera_rotation(start=0, end=None, rate=0.1)

      Continuously rotate the camera theta at *rate* radians per second.
      If *end* is ``None``, the rotation continues indefinitely.

      :param float rate: Angular velocity in radians/second.

      .. code-block:: python

         # Slowly orbit the scene for the entire animation
         axes.begin_ambient_camera_rotation(start=0, rate=0.15)

   .. py:method:: set_camera_preset(name, start=0, end=0.5, easing=smooth)

      Animate camera to a named preset orientation.

      :param str name: One of ``'default'``, ``'isometric'``, ``'front'``,
                       ``'top'``, ``'side'``.

      Preset values:

      =============== ============ ==============
      Name            phi          theta
      =============== ============ ==============
      ``default``     75 deg       -30 deg
      ``isometric``   54.7 deg     -45 deg
      ``front``       90 deg       0 deg
      ``top``         0 deg        0 deg
      ``side``        90 deg       -90 deg
      =============== ============ ==============

   .. py:method:: set_camera_zoom(factor, start=0, end=1, easing=smooth)

      Animate the 3D camera zoom (scale multiplier) over ``[start, end]``.

      :param float factor: Multiply the current scale by this factor.

      .. code-block:: python

         # Zoom in 2x over 2 seconds
         axes.set_camera_zoom(2.0, start=0, end=2)

   .. rubric:: Projection

   .. py:method:: project_point(x, y, z, time=0)

      Project a 3D point to screen coordinates using the current camera.

      :returns: ``(svg_x, svg_y, depth)``

   .. py:method:: coords_to_point(x, y, z=0, time=0)

      Convert 3D math coordinates to 2D SVG pixel coordinates.

      :returns: ``(svg_x, svg_y)``

   .. rubric:: Lighting

   .. py:method:: set_light_direction(x, y, z)

      Set the light direction vector for Lambertian shading on surfaces.
      The vector is normalized internally.

      :param float x: Light direction x-component.
      :param float y: Light direction y-component.
      :param float z: Light direction z-component.

      The default light direction is ``(0.5, -0.5, 0.7071)``.

      .. code-block:: python

         # Light from directly above
         axes.set_light_direction(0, 0, 1)

   .. rubric:: Adding Surfaces

   .. py:method:: add_surface(surface)

      Register a :py:class:`Surface` for depth-sorted rendering.

      :param Surface surface: The surface to add.

      .. code-block:: python

         sphere = Sphere3D(radius=1.5)
         axes.add_surface(sphere)

   .. py:method:: plot_surface(func, u_range=None, v_range=None, resolution=(20, 20), fill_color='#4488ff', checkerboard_colors=None, stroke_color='#333', stroke_width=0.5, fill_opacity=0.8)

      Create and register a Surface. If *u_range* or *v_range* is ``None``,
      the corresponding axis range is used. Returns the :py:class:`Surface`.

      :param callable func: ``z = func(x, y)`` or ``(x, y, z) = func(u, v)``.
      :param tuple resolution: ``(u_steps, v_steps)`` grid resolution.
      :param str fill_color: Base fill colour.
      :param tuple checkerboard_colors: Optional ``(color_a, color_b)`` pair.

      .. code-block:: python

         import math

         def gaussian(x, y):
             return math.exp(-(x**2 + y**2) / 0.32)

         axes.plot_surface(gaussian, resolution=(24, 24),
                           checkerboard_colors=('#FF862F', '#4488ff'))

   .. rubric:: Adding Primitives

   .. py:method:: add_3d(obj)

      Register a 3D primitive (:py:class:`Line3D`, :py:class:`Dot3D`,
      :py:class:`Arrow3D`, :py:class:`ParametricCurve3D`, :py:class:`Text3D`)
      for depth-sorted rendering.

      .. code-block:: python

         axes.add_3d(Dot3D((1, 0, 0), radius=6, fill='#FC6255'))
         axes.add_3d(Line3D((0, 0, 0), (2, 1, 3), stroke='#FFFF00'))

   .. rubric:: 3D Curves

   .. py:method:: get_graph_3d(func, x_range=None, plane='xz', num_points=100, stroke='#FFFF00', stroke_width=2)

      Plot a 2D function as a 3D curve in the specified plane.
      Returns a :py:class:`ParametricCurve3D`.

      :param callable func: ``y = func(x)`` or ``z = func(x)`` depending on plane.
      :param str plane: ``'xz'`` (default), ``'xy'``, or ``'yz'``.

      .. code-block:: python

         import math

         curve = axes.get_graph_3d(math.sin, plane='xz',
                                   stroke='#83C167')

   .. rubric:: Wireframe Surfaces

   .. py:method:: plot_surface_wireframe(func, x_steps=20, y_steps=20, **styling)

      Render a ``z = func(x, y)`` surface as a wireframe mesh.

      :param int x_steps: Grid resolution along x.
      :param int y_steps: Grid resolution along y.

   .. py:method:: plot_parametric_surface(func, u_range=(0, tau), v_range=(0, pi), u_steps=32, v_steps=16, **styling)

      Plot a parametric surface ``(x, y, z) = func(u, v)`` as a wireframe.

   .. rubric:: Grid Planes

   .. py:method:: add_grid_plane(plane='xz', step=1, color='#444444', opacity=0.3, stroke_width=0.5)

      Add a grid plane to the 3D axes.

      :param str plane: ``'xz'``, ``'xy'``, or ``'yz'``.
      :param float step: Grid line spacing in math units.

----

Surface
-------

.. py:class:: Surface(func, u_range=(-3, 3), v_range=(-3, 3), resolution=(20, 20), fill_color='#4488ff', checkerboard_colors=None, stroke_color='#333', stroke_width=0.5, fill_opacity=0.8)

   Filled quad surface with Lambertian shading and depth sorting.

   Surfaces auto-detect whether the given function is a height-map or
   parametric form:

   **Height-map** -- ``func(x, y) -> z``:

   .. code-block:: python

      def paraboloid(x, y):
          return x**2 + y**2

      surface = Surface(paraboloid, u_range=(-2, 2), v_range=(-2, 2))
      axes.add_surface(surface)

   **Parametric** -- ``func(u, v) -> (x, y, z)``:

   .. code-block:: python

      import math

      def mobius(u, v):
          x = (1 + v/2 * math.cos(u/2)) * math.cos(u)
          y = (1 + v/2 * math.cos(u/2)) * math.sin(u)
          z = v/2 * math.sin(u/2)
          return (x, y, z)

      surface = Surface(mobius,
                         u_range=(0, math.tau),
                         v_range=(-0.5, 0.5),
                         resolution=(40, 8),
                         fill_color='#58C4DD')
      axes.add_surface(surface)

   :param callable func: Height-map or parametric function.
   :param tuple u_range: ``(min, max)`` for the u parameter.
   :param tuple v_range: ``(min, max)`` for the v parameter.
   :param tuple resolution: ``(u_steps, v_steps)`` -- number of quad subdivisions.
   :param str fill_color: Base fill colour (hex).
   :param tuple checkerboard_colors: Optional ``(color_a, color_b)`` pair for
      alternating face colours.
   :param str stroke_color: Quad edge colour.
   :param float stroke_width: Quad edge width (set to ``0`` for no edges).
   :param float fill_opacity: Fill opacity (0--1).

   .. py:method:: set_checkerboard(color_a, color_b)

      Update the checkerboard colours for this surface. Returns self.

      .. code-block:: python

         surface.set_checkerboard('#FC6255', '#c44030')

----

SurfaceMesh
-----------

.. py:class:: SurfaceMesh(surface, resolution=None, stroke_color='#ffffff', stroke_width=1, stroke_opacity=0.4, creation=0, z=0)

   Wireframe mesh overlay for a :py:class:`Surface`, showing grid lines without
   fill. Inherits from :py:class:`Surface` but renders only line segments along
   the U and V directions of the parameter grid.

   :param Surface surface: The surface to overlay with a mesh.
   :param tuple resolution: ``(u_steps, v_steps)`` grid resolution, or ``None``
      to match the underlying surface's resolution.
   :param str stroke_color: Line colour (default ``'#ffffff'``).
   :param float stroke_width: Line width (default ``1``).
   :param float stroke_opacity: Line opacity (default ``0.4``).

   .. code-block:: python

      import math

      def saddle(x, y):
          return (x**2 - y**2) / 4

      surface = Surface(saddle, resolution=(20, 20),
                         fill_color='#58C4DD', fill_opacity=0.8)
      mesh = SurfaceMesh(surface, stroke_color='#ffffff',
                          stroke_opacity=0.3)
      axes.add_surface(surface)
      axes.add_surface(mesh)

----

3D Primitives
-------------

All primitives support ``show``, ``z``, ``copy()``, ``shift(dx, dy, dz)``,
``move_to(x, y, z)``, and ``set_color(color)``.

Line3D
^^^^^^

.. py:class:: Line3D(start, end, stroke='#fff', stroke_width=2)

   Line segment in 3D space.

   :param tuple start: ``(x, y, z)`` start point.
   :param tuple end: ``(x, y, z)`` end point.
   :param str stroke: Stroke colour.
   :param float stroke_width: Stroke width.

   .. py:method:: get_midpoint()

      Return the 3D midpoint as ``(x, y, z)``.

   .. py:method:: get_length()

      Return the Euclidean length.

   .. code-block:: python

      line = Line3D((0, 0, 0), (2, 1, 3), stroke='#FFFF00')
      axes.add_3d(line)

Arrow3D
^^^^^^^

.. py:class:: Arrow3D(start, end, stroke='#fff', stroke_width=2, tip_length=12, tip_radius=4)

   Arrow in 3D space with a triangular tip.

   :param tuple start: ``(x, y, z)`` tail point.
   :param tuple end: ``(x, y, z)`` tip point.
   :param str stroke: Shaft and tip colour.
   :param float tip_length: Length of the arrowhead in pixels.
   :param float tip_radius: Half-width of the arrowhead in pixels.

   .. py:method:: get_midpoint()

      Return the 3D midpoint as ``(x, y, z)``.

   .. py:method:: get_length()

      Return the Euclidean length of the shaft.

   .. code-block:: python

      arrow = Arrow3D((0, 0, 0), (1, 1, 2), stroke='#FC6255',
                       tip_length=14, tip_radius=5)
      axes.add_3d(arrow)

Dot3D
^^^^^

.. py:class:: Dot3D(point=(0, 0, 0), radius=5, fill='#fff')

   Filled circle in 3D space.

   :param tuple point: ``(x, y, z)`` position.
   :param float radius: Circle radius in pixels.
   :param str fill: Fill colour.

   .. py:method:: get_position()

      Return the 3D position as ``(x, y, z)``.

   .. py:method:: set_radius(radius)

      Set the dot radius. Returns self.

   .. code-block:: python

      dot = Dot3D((1, 0, 0), radius=6, fill='#83C167')
      axes.add_3d(dot)

ParametricCurve3D
^^^^^^^^^^^^^^^^^

.. py:class:: ParametricCurve3D(func, t_range=(0, 1), num_points=100, stroke='#fff', stroke_width=2)

   Parametric curve ``func(t) -> (x, y, z)`` sampled at *num_points* points.

   :param callable func: Function mapping ``t`` to ``(x, y, z)``.
   :param tuple t_range: ``(t_min, t_max)`` parameter range.
   :param int num_points: Number of sample points.
   :param str stroke: Stroke colour.
   :param float stroke_width: Stroke width.

   .. code-block:: python

      import math

      def helix(t):
          return (math.cos(t), math.sin(t), t / (2 * math.pi))

      curve = ParametricCurve3D(helix,
                                 t_range=(0, 4 * math.pi),
                                 num_points=200,
                                 stroke='#FFFF00',
                                 stroke_width=3)
      axes.add_3d(curve)

Text3D
^^^^^^

.. py:class:: Text3D(text, point=(0, 0, 0), font_size=20, fill='#fff')

   Text label placed at a 3D position. The label always faces the camera
   (billboard style).

   :param str text: Displayed text string.
   :param tuple point: ``(x, y, z)`` position.
   :param float font_size: Font size in pixels.
   :param str fill: Text fill colour.

   .. py:method:: get_position()

      Return the 3D position as ``(x, y, z)``.

   .. py:method:: set_text(text)

      Update the displayed text. Returns self.

   .. code-block:: python

      label = Text3D('Origin', point=(0, 0, 0), font_size=18)
      axes.add_3d(label)

----

3D Factory Functions
--------------------

Factory functions create pre-built :py:class:`Surface` objects (or lists of
them) for common shapes. They all accept ``fill_color``, ``stroke_color``,
``stroke_width``, ``fill_opacity``, ``checkerboard_colors``, ``creation``,
and ``z`` keyword arguments.

Sphere3D
^^^^^^^^

.. py:function:: Sphere3D(radius=1.5, center=(0, 0, 0), resolution=(16, 32), **kwargs)

   Create a sphere :py:class:`Surface`.

   :param float radius: Sphere radius in math units.
   :param tuple center: ``(x, y, z)`` centre.
   :param tuple resolution: ``(lat_steps, lon_steps)`` grid resolution.
   :returns: :py:class:`Surface`

   Default fill: ``#FC6255``.

   .. code-block:: python

      sphere = Sphere3D(radius=1.5,
                         checkerboard_colors=('#FC6255', '#c44030'))
      axes.add_surface(sphere)

Cube
^^^^

.. py:function:: Cube(side_length=2, center=(0, 0, 0), **kwargs)

   Create a cube as a list of 6 flat :py:class:`Surface` objects (one per face).

   :param float side_length: Edge length in math units.
   :param tuple center: ``(x, y, z)`` centre.
   :returns: ``list[Surface]``

   Default fill: ``#58C4DD``.

   .. code-block:: python

      faces = Cube(side_length=2)
      for face in faces:
          axes.add_surface(face)

Cylinder3D
^^^^^^^^^^

.. py:function:: Cylinder3D(radius=1, height=2, center=(0, 0, 0), resolution=(16, 16), **kwargs)

   Create an open-ended cylinder (side surface only) as a :py:class:`Surface`.

   :param float radius: Cylinder radius.
   :param float height: Cylinder height.
   :param tuple center: ``(x, y, z)`` centre.
   :param tuple resolution: ``(angular_steps, height_steps)`` grid resolution.
   :returns: :py:class:`Surface`

   Default fill: ``#58C4DD``.

Cone3D
^^^^^^

.. py:function:: Cone3D(radius=1, height=2, center=(0, 0, 0), resolution=(16, 16), **kwargs)

   Create an open-ended cone (side surface only) as a :py:class:`Surface`.

   :param float radius: Base radius.
   :param float height: Cone height.
   :param tuple center: ``(x, y, z)`` centre.
   :param tuple resolution: ``(angular_steps, height_steps)`` grid resolution.
   :returns: :py:class:`Surface`

   Default fill: ``#58C4DD``.

Torus3D
^^^^^^^

.. py:function:: Torus3D(major_radius=2, minor_radius=0.5, center=(0, 0, 0), resolution=(24, 12), **kwargs)

   Create a torus :py:class:`Surface`.

   :param float major_radius: Distance from torus centre to tube centre.
   :param float minor_radius: Tube radius.
   :param tuple center: ``(x, y, z)`` centre.
   :param tuple resolution: ``(major_steps, minor_steps)`` grid resolution.
   :returns: :py:class:`Surface`

   Default fill: ``#58C4DD``.

Prism3D
^^^^^^^

.. py:function:: Prism3D(n_sides=6, radius=1, height=2, center=(0, 0, 0), **kwargs)

   Create a prism with an n-sided polygon cross-section.
   Returns a list of :py:class:`Surface` objects (side faces + top and bottom
   caps).

   :param int n_sides: Number of sides of the polygon base.
   :param float radius: Circumscribed radius of the polygon.
   :param float height: Prism height.
   :param tuple center: ``(x, y, z)`` centre.
   :returns: ``list[Surface]``

   Default fill: ``#58C4DD``.

----

Platonic Solids
---------------

The Platonic solid factories create lists of flat :py:class:`Surface` objects
(one per face). They all accept ``fill_color``, ``stroke_color``,
``stroke_width``, ``fill_opacity``, ``creation``, and ``z`` keyword arguments.

Tetrahedron
^^^^^^^^^^^

.. py:function:: Tetrahedron(cx=0, cy=0, cz=0, size=1.0, **kwargs)

   Regular tetrahedron (4 triangular faces).

   :param float cx: Centre x.
   :param float cy: Centre y.
   :param float cz: Centre z.
   :param float size: Scale factor applied to vertex coordinates.
   :returns: ``list[Surface]``

   Default fill: ``#58C4DD``, default stroke: ``#FFFFFF``.

   .. code-block:: python

      faces = Tetrahedron(size=1.2, fill_color='#FC6255')
      for face in faces:
          axes.add_surface(face)

Octahedron
^^^^^^^^^^

.. py:function:: Octahedron(cx=0, cy=0, cz=0, size=1.0, **kwargs)

   Regular octahedron (8 triangular faces).

   :param float cx: Centre x.
   :param float cy: Centre y.
   :param float cz: Centre z.
   :param float size: Scale factor applied to vertex coordinates.
   :returns: ``list[Surface]``

Icosahedron
^^^^^^^^^^^

.. py:function:: Icosahedron(cx=0, cy=0, cz=0, size=1.0, **kwargs)

   Regular icosahedron (20 triangular faces).

   :param float cx: Centre x.
   :param float cy: Centre y.
   :param float cz: Centre z.
   :param float size: Scale factor applied to vertex coordinates.
   :returns: ``list[Surface]``

Dodecahedron
^^^^^^^^^^^^

.. py:function:: Dodecahedron(cx=0, cy=0, cz=0, size=1.0, **kwargs)

   Regular dodecahedron (12 pentagonal faces).

   :param float cx: Centre x.
   :param float cy: Centre y.
   :param float cz: Centre z.
   :param float size: Scale factor applied to vertex coordinates.
   :returns: ``list[Surface]``

----

Full Example
------------

The following example creates a 3D scene with a surface, a helix curve, and
an animated camera:

.. code-block:: python

   from vectormation.objects import *
   import math

   canvas = VectorMathAnim()
   canvas.set_background()

   axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-1, 3))

   # Height-map surface
   def saddle(x, y):
       return (x**2 - y**2) / 6

   axes.plot_surface(saddle, resolution=(20, 20),
                     fill_color='#58C4DD', fill_opacity=0.8)

   # Parametric helix curve
   def helix(t):
       return (math.cos(t), math.sin(t), t / (2 * math.pi))

   curve = ParametricCurve3D(helix,
                              t_range=(0, 4 * math.pi),
                              num_points=200,
                              stroke='#FFFF00', stroke_width=3)
   axes.add_3d(curve)

   # Dot at the helix start
   axes.add_3d(Dot3D((1, 0, 0), radius=6, fill='#FC6255'))

   # Animate the camera: full 360-degree rotation over 6 seconds
   axes.begin_ambient_camera_rotation(start=0, rate=math.tau / 6)

   # Adjust lighting
   axes.set_light_direction(0, 0, 1)

   canvas.add_objects(axes)
   canvas.browser_display(start=0, end=6, fps=30)

----

3D Primitive Factory Functions
------------------------------

These factory functions create common 3D shapes as collections of patches
that can be added to a :py:class:`ThreeDAxes` with ``axes.add_3d()``.

.. py:function:: Sphere3D(cx=0, cy=0, cz=0, radius=1, resolution=(20, 20), fill_color='#58C4DD', fill_opacity=0.8, stroke_width=0.5)
   :no-index:

   Create a sphere at ``(cx, cy, cz)`` with the given radius.

.. py:function:: Cube(cx=0, cy=0, cz=0, side=2, fill_color='#58C4DD', fill_opacity=0.8)
   :no-index:

   Create an axis-aligned cube centered at ``(cx, cy, cz)``.

.. py:function:: Cylinder3D(cx=0, cy=0, cz=0, radius=1, height=2, resolution=(20, 2), fill_color='#58C4DD', fill_opacity=0.8)
   :no-index:

   Create a cylinder along the z-axis.

.. py:function:: Cone3D(cx=0, cy=0, cz=0, radius=1, height=2, resolution=(20, 1), fill_color='#58C4DD', fill_opacity=0.8)
   :no-index:

   Create a cone with its apex pointing up the z-axis.

.. py:function:: Torus3D(cx=0, cy=0, cz=0, major_radius=2, minor_radius=0.5, resolution=(30, 15), fill_color='#58C4DD', fill_opacity=0.8)
   :no-index:

   Create a torus (donut) in the xy-plane.

.. py:function:: Prism3D(cx=0, cy=0, cz=0, sides=6, radius=1, height=2, fill_color='#58C4DD', fill_opacity=0.8)
   :no-index:

   Create a regular prism (hexagonal by default).

.. py:function:: Tetrahedron(cx=0, cy=0, cz=0, side=2, fill_color='#58C4DD', fill_opacity=0.8)
   :no-index:

   Create a regular tetrahedron (4 equilateral triangle faces).

.. py:function:: Octahedron(cx=0, cy=0, cz=0, side=2, fill_color='#58C4DD', fill_opacity=0.8)
   :no-index:

   Create a regular octahedron (8 equilateral triangle faces).

.. py:function:: Icosahedron(cx=0, cy=0, cz=0, side=2, fill_color='#58C4DD', fill_opacity=0.8)
   :no-index:

   Create a regular icosahedron (20 equilateral triangle faces).

.. py:function:: Dodecahedron(cx=0, cy=0, cz=0, side=2, fill_color='#58C4DD', fill_opacity=0.8)
   :no-index:

   Create a regular dodecahedron (12 pentagonal faces).

.. code-block:: python

   from vectormation.objects import *

   canvas = VectorMathAnim()
   canvas.set_background()

   axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-3, 3))
   axes.add_3d(Sphere3D(cx=-1.5, cy=0, cz=0, radius=0.8, fill_color='#FF6B6B'))
   axes.add_3d(Cube(cx=1.5, cy=0, cz=0, side=1.2, fill_color='#58C4DD'))
   axes.add_3d(Torus3D(cy=2, major_radius=1, minor_radius=0.3, fill_color='#83C167'))

   axes.begin_ambient_camera_rotation(start=0, rate=1)
   canvas.add_objects(axes)
   canvas.browser_display(start=0, end=6, fps=30)
