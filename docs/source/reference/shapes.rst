Shapes
======

All shapes inherit from :doc:`VObject <vobject>` and share its full set of
animation methods.

----

Ellipse
-------

.. image:: ../_static/images/ellipse_params.svg
   :width: 400
   :align: center

.. py:class:: Ellipse(rx=120, ry=60, cx=960, cy=540, **styling)

   Ellipse centred at ``(cx, cy)`` with radii ``rx`` and ``ry``.

   :param float rx: Horizontal radius.
   :param float ry: Vertical radius.
   :param float cx: Centre x.
   :param float cy: Centre y.

   .. py:attribute:: c
      :type: Coor

      Centre coordinate (time-varying).

   .. py:attribute:: rx
      :type: Real

   .. py:attribute:: ry
      :type: Real

----

Circle
------

.. image:: ../_static/images/circle_params.svg
   :width: 400
   :align: center

.. py:class:: Circle(r=120, cx=960, cy=540, **styling)

   Bases: :py:class:`Ellipse`

   Circle (Ellipse with ``rx == ry``).

   :param float r: Radius.
   :param float cx: Centre x.
   :param float cy: Centre y.

   .. py:attribute:: r
      :type: Real

      Radius (property that gets/sets both ``rx`` and ``ry``).

   .. py:method:: point_at_angle(degrees, time=0)

      Return ``(x, y)`` on the circumference at the given angle.

----

Dot
---

.. py:class:: Dot(r=11, cx=960, cy=540, **styling)

   Bases: :py:class:`Circle`

   Small circle with default green fill (``#83C167``).

   :param float r: Radius (default ``11``).

   .. py:attribute:: c
      :type: Coor

      Centre coordinate.

----

Rectangle
---------

.. image:: ../_static/images/rectangle_params.svg
   :width: 440
   :align: center

.. py:class:: Rectangle(width, height, x=960, y=540, rx=0, ry=0, **styling)

   Rectangle positioned at ``(x, y)`` (top-left corner).

   :param float width: Width.
   :param float height: Height.
   :param float x: Top-left x.
   :param float y: Top-left y.
   :param float rx: Corner radius x.
   :param float ry: Corner radius y.

   .. py:attribute:: x
      :type: Real

   .. py:attribute:: y
      :type: Real

   .. py:attribute:: width
      :type: Real

   .. py:attribute:: height
      :type: Real

----

RoundedRectangle
----------------

.. py:class:: RoundedRectangle(width, height, x=960, y=540, corner_radius=12, **styling)

   Bases: :py:class:`Rectangle`

   Rectangle with rounded corners.

----

Line
----

.. image:: ../_static/images/line_params.svg
   :width: 400
   :align: center

.. py:class:: Line(x1=0, y1=0, x2=100, y2=100, **styling)

   Line segment from ``(x1, y1)`` to ``(x2, y2)``.

   :param float x1: Start x.
   :param float y1: Start y.
   :param float x2: End x.
   :param float y2: End y.

   .. py:attribute:: p1
      :type: Coor

      Start point (time-varying).

   .. py:attribute:: p2
      :type: Coor

      End point (time-varying).

----

DashedLine
----------

.. py:class:: DashedLine(x1=0, y1=0, x2=100, y2=100, dash='10,5', **styling)

   Bases: :py:class:`Line`

   Line with a dashed pattern.

   :param str dash: SVG dash-array string.

----

Polygon
-------

.. py:class:: Polygon(*vertices, closed=True, **styling)

   Closed polygon from ``(x, y)`` vertex tuples.

   :param vertices: Sequence of ``(x, y)`` tuples.
   :param bool closed: ``False`` for an open polyline.

   .. py:attribute:: vertices
      :type: list[Coor]

      Vertex coordinates (time-varying).

----

Lines
-----

.. py:class:: Lines(*vertices, **styling)

   Bases: :py:class:`Polygon` (with ``closed=False``)

   Open polyline.

----

RegularPolygon
--------------

.. image:: ../_static/images/regular_polygon_params.svg
   :width: 400
   :align: center

.. py:class:: RegularPolygon(n, radius=120, cx=960, cy=540, angle=0, **styling)

   Bases: :py:class:`Polygon`

   N-sided regular polygon inscribed in a circle of given radius.

   :param int n: Number of sides.
   :param float radius: Circumscribed radius.
   :param float angle: Starting rotation angle in degrees.

----

EquilateralTriangle
-------------------

.. py:class:: EquilateralTriangle(side_length, angle=0, cx=960, cy=540, **styling)

   Bases: :py:class:`RegularPolygon` (n=3)

----

Star
----

.. image:: ../_static/images/star_params.svg
   :width: 400
   :align: center

.. py:class:: Star(n=5, outer_radius=120, inner_radius=None, cx=960, cy=540, angle=90, **styling)

   Bases: :py:class:`Polygon`

   N-pointed star.

   :param int n: Number of points.
   :param float outer_radius: Outer radius.
   :param float inner_radius: Inner radius (defaults to ``outer_radius / 2``, i.e. ``60``).

----

Arc
---

.. image:: ../_static/images/arc_params.svg
   :width: 400
   :align: center

.. py:class:: Arc(cx=960, cy=540, r=120, start_angle=0, end_angle=90, **styling)

   SVG arc from ``start_angle`` to ``end_angle`` (in degrees, counterclockwise).

   :param float cx: Centre x.
   :param float cy: Centre y.
   :param float r: Radius.
   :param float start_angle: Start angle in degrees.
   :param float end_angle: End angle in degrees.

   .. py:attribute:: cx
      :type: Real

   .. py:attribute:: cy
      :type: Real

   .. py:attribute:: r
      :type: Real

   .. py:attribute:: start_angle
      :type: Real

   .. py:attribute:: end_angle
      :type: Real

----

Wedge / Sector
--------------

.. image:: ../_static/images/wedge_params.svg
   :width: 400
   :align: center

.. py:class:: Wedge(cx=960, cy=540, r=120, start_angle=0, end_angle=90, **styling)

   Bases: :py:class:`Arc`

   Pie-wedge shape (arc closing through the centre). ``Sector`` is an alias.

----

Annulus
-------

.. image:: ../_static/images/annulus_params.svg
   :width: 400
   :align: center

.. py:class:: Annulus(inner_radius=60, outer_radius=120, cx=960, cy=540, **styling)

   Ring (donut) shape.

   :param float inner_radius: Inner radius.
   :param float outer_radius: Outer radius.

   .. py:attribute:: c
      :type: Coor

      Centre coordinate.

   .. py:attribute:: inner_r
      :type: Real

   .. py:attribute:: outer_r
      :type: Real

----

Angle
-----

.. image:: ../_static/images/angle_params.svg
   :width: 440
   :align: center

.. py:class:: Angle(vertex, p1, p2, radius=36, **styling)

   Bases: :py:class:`VCollection`

   Angle indicator arc between two points meeting at a vertex.
   All three position parameters accept ``(x, y)`` tuples or :py:class:`Coor`
   objects for time-varying angles.

   :param vertex: Vertex point.
   :param p1: First ray endpoint.
   :param p2: Second ray endpoint.
   :param float radius: Arc radius.

----

RightAngle
----------

.. py:class:: RightAngle(vertex, p1, p2, size=18, **styling)

   Right angle square indicator.

----

Cross
-----

.. py:class:: Cross(size=36, cx=960, cy=540, **styling)

   X-mark shape (two crossing lines).

----

Path
----

.. py:class:: Path(path, x=0, y=0, **styling)

   Raw SVG ``<path>`` element.

   :param str path: SVG path data (``d`` attribute).

   .. py:attribute:: d
      :type: String

      Path data (time-varying).

----

Image
-----

.. py:class:: Image(href, x=0, y=0, width=1, height=1, **styling)

   SVG ``<image>`` element.

   :param str href: Image URL or path.

   .. py:attribute:: x
      :type: Real

   .. py:attribute:: y
      :type: Real

   .. py:attribute:: width
      :type: Real

   .. py:attribute:: height
      :type: Real

----

Trace
-----

.. py:class:: Trace(point, start=0, end=None, dt=1/60, **styling)

   Follows a :py:class:`Coor` attribute and renders its trajectory as a polyline.

   :param Coor point: The coordinate to trace.
   :param float start: Start time.
   :param float end: End time.
   :param float dt: Time step between samples.

   .. py:method:: vertices(time)

      Return the list of ``(x, y)`` vertices traced up to *time*.

   .. py:method:: to_polygon(time)

      Convert the trace to a :py:class:`Polygon`.
