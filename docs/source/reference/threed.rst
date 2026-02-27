3D Objects
==========

VectorMation includes a lightweight 3D module for rendering three-dimensional
scenes as SVG. Objects are projected orthographically and depth-sorted.

----

ThreeDAxes
----------

.. py:class:: ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-3, 3), cx=960, cy=540, scale=100, creation=0, z=0)

   Three-dimensional coordinate axes with camera control.

   :param tuple x_range: ``(min, max)`` for x-axis.
   :param tuple y_range: ``(min, max)`` for y-axis.
   :param tuple z_range: ``(min, max)`` for z-axis.
   :param float cx: Screen centre x.
   :param float cy: Screen centre y.
   :param float scale: Pixels per unit.

   .. py:method:: set_camera_orientation(start=0, end=None, phi=None, theta=None)

      Animate camera elevation (phi) and azimuth (theta) in degrees.

   .. py:method:: begin_ambient_camera_rotation(start=0, end=None, rate=20)

      Continuously rotate the camera.

   .. py:method:: set_light_direction(x, y, z)

      Set the light direction for Lambertian shading on surfaces.

   .. py:method:: project_point(x, y, z, time=0)

      Project a 3D point to screen coordinates.

      :returns: ``(svg_x, svg_y, depth)``

   .. py:method:: coords_to_point(x, y, z=0, time=0)

      Convert 3D coordinates to 2D screen coordinates.

      :returns: ``(svg_x, svg_y)``

   .. py:method:: plot_surface(func, u_range=(-3, 3), v_range=(-3, 3), resolution=20, **kwargs)

      Plot a surface ``z = func(x, y)`` or parametric surface.

   .. py:method:: add_3d(obj)

      Register a 3D primitive for depth-sorted rendering.

----

Surface
-------

.. py:class:: Surface(func, u_range=(-3, 3), v_range=(-3, 3), resolution=20, **styling)

   Filled quad surface with Lambertian shading.

   Supports both height-map (``func(x, y) -> z``) and parametric
   (``func(u, v) -> (x, y, z)``) forms.

----

3D Primitives
-------------

.. py:class:: Line3D(start, end, **kwargs)

   Line segment in 3D space.

.. py:class:: Arrow3D(start, end, **kwargs)

   Arrow in 3D space with a conical tip.

.. py:class:: Dot3D(x, y, z, r=5, **kwargs)

   Dot (filled circle) in 3D space.

.. py:class:: ParametricCurve3D(func, t_range=(0, 1), num_points=100, **kwargs)

   Parametric curve ``func(t) -> (x, y, z)``.

.. py:class:: Text3D(text, x, y, z, font_size=24, **kwargs)

   Text label in 3D space.

----

3D Factory Functions
--------------------

.. py:function:: Sphere3D(cx=0, cy=0, cz=0, radius=1, resolution=20, **kwargs)

   Create a sphere surface.

.. py:function:: Cube(cx=0, cy=0, cz=0, size=1, **kwargs)

   Create a cube surface.

.. py:function:: Cylinder3D(cx=0, cy=0, cz=0, radius=1, height=2, resolution=20, **kwargs)

   Create a cylinder surface.

.. py:function:: Cone3D(cx=0, cy=0, cz=0, radius=1, height=2, resolution=20, **kwargs)

   Create a cone surface.

.. py:function:: Torus3D(cx=0, cy=0, cz=0, R=2, r=0.5, resolution=20, **kwargs)

   Create a torus surface.

.. py:function:: Prism3D(cx=0, cy=0, cz=0, n=6, radius=1, height=2, **kwargs)

   Create a prism with n-sided polygon cross-section.
