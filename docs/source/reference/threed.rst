3D Objects
==========

VectorMation includes a lightweight 3D module for rendering three-dimensional
scenes as SVG. Objects are projected orthographically and depth-sorted.

----

ThreeDAxes
----------

.. py:class:: ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-3, 3), cx=960, cy=540, scale=160, phi=75°, theta=-30°, **styling)

   Three-dimensional coordinate axes with camera control.

   :param tuple x_range: ``(min, max)`` for x-axis.
   :param tuple y_range: ``(min, max)`` for y-axis.
   :param tuple z_range: ``(min, max)`` for z-axis.
   :param float cx: Screen centre x.
   :param float cy: Screen centre y.
   :param float scale: Pixels per unit.
   :param float phi: Camera elevation in radians.
   :param float theta: Camera azimuth in radians.

   .. py:method:: set_camera_orientation(start, end, phi=None, theta=None, easing=smooth)

      Animate camera elevation (phi) and azimuth (theta) in radians.

   .. py:method:: begin_ambient_camera_rotation(start=0, end=None, rate=0.1)

      Continuously rotate the camera at *rate* radians per second.

   .. py:method:: set_light_direction(x, y, z)

      Set the light direction for Lambertian shading on surfaces.

   .. py:method:: project_point(x, y, z, time=0)

      Project a 3D point to screen coordinates.

      :returns: ``(svg_x, svg_y, depth)``

   .. py:method:: coords_to_point(x, y, z=0, time=0)

      Convert 3D coordinates to 2D screen coordinates.

      :returns: ``(svg_x, svg_y)``

   .. py:method:: plot_surface(func, u_range=None, v_range=None, resolution=(20, 20), **kwargs)

      Plot a surface ``z = func(x, y)`` or parametric surface.

   .. py:method:: add_3d(obj)

      Register a 3D primitive for depth-sorted rendering.

   .. py:method:: get_graph_3d(func, x_range=None, plane='xz', num_points=100, **kwargs)

      Plot a 2D function as a 3D curve in the specified plane.

   .. py:method:: plot_surface_wireframe(func, x_steps=20, y_steps=20, **kwargs)

      Render a surface as a wireframe mesh.

   .. py:method:: plot_parametric_surface(func, u_range=(0, tau), v_range=(0, pi), resolution=20, **kwargs)

      Plot a parametric surface ``(x, y, z) = func(u, v)``.

----

Surface
-------

.. py:class:: Surface(func, u_range=(-3, 3), v_range=(-3, 3), resolution=(20, 20), **styling)

   Filled quad surface with Lambertian shading.

   Supports both height-map (``func(x, y) -> z``) and parametric
   (``func(u, v) -> (x, y, z)``) forms.

----

3D Primitives
-------------

.. py:class:: Line3D(start, end, stroke='#fff', stroke_width=2)

   Line segment in 3D space.

.. py:class:: Arrow3D(start, end, stroke='#fff', stroke_width=2, tip_length=12, tip_radius=4)

   Arrow in 3D space with a conical tip.

.. py:class:: Dot3D(point=(0, 0, 0), radius=5, fill='#fff')

   Dot (filled circle) in 3D space.

.. py:class:: ParametricCurve3D(func, t_range=(0, 1), num_points=100, **kwargs)

   Parametric curve ``func(t) -> (x, y, z)``.

.. py:class:: Text3D(text, point=(0, 0, 0), font_size=20, fill='#fff')

   Text label in 3D space.

----

3D Factory Functions
--------------------

.. py:function:: Sphere3D(radius=1.5, center=(0, 0, 0), resolution=(16, 32), **kwargs)

   Create a sphere surface.

.. py:function:: Cube(side_length=2, center=(0, 0, 0), **kwargs)

   Create a cube (list of 6 Surface objects).

.. py:function:: Cylinder3D(radius=1, height=2, center=(0, 0, 0), resolution=(16, 16), **kwargs)

   Create a cylinder surface.

.. py:function:: Cone3D(radius=1, height=2, center=(0, 0, 0), resolution=(16, 16), **kwargs)

   Create a cone surface.

.. py:function:: Torus3D(major_radius=2, minor_radius=0.5, center=(0, 0, 0), resolution=(24, 12), **kwargs)

   Create a torus surface.

.. py:function:: Prism3D(n_sides=6, radius=1, height=2, center=(0, 0, 0), **kwargs)

   Create a prism with n-sided polygon cross-section (list of Surface objects).
