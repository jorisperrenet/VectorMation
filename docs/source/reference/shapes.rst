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

----

FunctionGraph
-------------

.. py:class:: FunctionGraph(func, x_range=(-5, 5), y_range=None, x=360, y=140, width=1200, height=800, num_points=200, **styling)

   Bases: :py:class:`Lines`

   Plot a function as a polyline (no axes, ticks, or labels).

   :param callable func: ``f(x) → y`` function.
   :param tuple x_range: ``(start, end)`` in math coordinates.
   :param tuple y_range: ``(min, max)`` or ``None`` for auto.
   :param int num_points: Sampling resolution.

----

CubicBezier
-----------

.. py:class:: CubicBezier(p0=(860,540), p1=(910,440), p2=(1010,440), p3=(1060,540), **styling)

   Cubic Bezier curve from four control points.

   .. py:attribute:: p0
      :type: Coor

   .. py:attribute:: p1
      :type: Coor

   .. py:attribute:: p2
      :type: Coor

   .. py:attribute:: p3
      :type: Coor

----

ArcBetweenPoints
----------------

.. py:class:: ArcBetweenPoints(start, end, angle=60, **styling)

   Bases: :py:class:`Arc`

   Arc connecting two points, bulging by a given angle.

   :param tuple start: Start ``(x, y)`` point.
   :param tuple end: End ``(x, y)`` point.
   :param float angle: Bulge angle in degrees (positive = left of start→end).

----

Elbow
-----

.. py:class:: Elbow(cx=960, cy=540, width=40, height=40, **styling)

   Bases: :py:class:`Lines`

   Right-angle connector (L-shape).

   :param float width: Horizontal arm size.
   :param float height: Vertical arm size.

----

AnnularSector
-------------

.. py:class:: AnnularSector(inner_radius=60, outer_radius=120, cx=960, cy=540, start_angle=0, end_angle=90, **styling)

   Bases: :py:class:`Arc`

   Sector of an annulus (ring wedge). Like a Wedge but with an inner radius cut out.

   :param float inner_radius: Inner radius.
   :param float outer_radius: Outer radius.

----

Paragraph
---------

.. py:class:: Paragraph(*lines, x=960, y=540, font_size=36, alignment='left', line_spacing=1.4, **styling)

   Multi-line text with alignment and line spacing.

   :param lines: Text strings, one per line.
   :param str alignment: ``'left'``, ``'center'``, or ``'right'``.
   :param float line_spacing: Multiplier for vertical spacing between lines.

----

BulletedList
------------

.. py:class:: BulletedList(*items, bullet='•', indent=30, x=960, y=540, font_size=36, **styling)

   List of items with bullet points.

   :param items: Text strings.
   :param str bullet: Bullet character.
   :param float indent: Pixel indentation for each item.

----

NumberedList
------------

.. py:class:: NumberedList(*items, indent=30, start_number=1, x=960, y=540, font_size=36, **styling)

   Bases: similar to :py:class:`BulletedList`

   List of items with numeric labels (1. 2. 3. …).

   :param items: Text strings.
   :param float indent: Pixel indentation after the number.
   :param int start_number: First number in the sequence.

----

SurroundingRectangle
--------------------

.. py:class:: SurroundingRectangle(target, buff=14, corner_radius=6, follow=True, **styling)

   Bases: :py:class:`RoundedRectangle`

   Rectangle that surrounds a target object with padding.
   If ``follow=True`` (default), tracks the target as it moves.

   :param VObject target: Object to surround.
   :param float buff: Padding around the target.
   :param bool follow: Track target position dynamically.

----

SurroundingCircle
-----------------

.. py:class:: SurroundingCircle(target, buff=14, follow=True, **styling)

   Bases: :py:class:`Circle`

   Circle that surrounds a target object with padding.

   :param VObject target: Object to surround.
   :param float buff: Padding around the target.
   :param bool follow: Track target position dynamically.

----

BackgroundRectangle
-------------------

.. py:class:: BackgroundRectangle(target, buff=14, z=-1, **styling)

   Bases: :py:class:`Rectangle`

   Semi-transparent rectangle behind a target object (useful for text backgrounds).
   Default fill is black at 75% opacity.

   :param VObject target: Object to put background behind.
   :param float buff: Padding around the target.

----

ScreenRectangle
---------------

.. py:class:: ScreenRectangle(width=480, **styling)

   Bases: :py:class:`Rectangle`

   Rectangle with the canvas aspect ratio (16:9). Height is derived from width.

   :param float width: Width in pixels.

----

ValueTracker
------------

.. py:class:: ValueTracker(value=0, creation=0)

   Convenience wrapper around a time-varying Real attribute. Use to drive
   reactive animations (e.g. link a label's position to a value).

   :param float value: Initial value.

   .. py:method:: set_value(start, end, value, **kwargs)

      Animate to a new value over ``[start, end]``.

   .. py:method:: at_time(time)

      Return the value at a given time.

----

DecimalNumber
-------------

.. py:class:: DecimalNumber(value=0, fmt='{:.2f}', x=960, y=540, font_size=48, **styling)

   Bases: :py:class:`Text`

   Text that dynamically displays a numeric value, updating each frame.

   :param value: Initial value, or a :py:class:`Real` / :py:class:`ValueTracker` to track.
   :param str fmt: Format string for display.

   .. py:attribute:: tracker
      :type: Real

      The underlying tracked value.
