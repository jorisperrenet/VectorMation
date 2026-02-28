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

   **Geometry methods**

   .. py:method:: get_area(time=0)

      Return the area π·rx·ry.

   .. py:method:: get_perimeter(time=0)

      Approximate perimeter (Ramanujan's formula).

   .. py:method:: eccentricity(time=0)

      Return the eccentricity e = √(1 - (min/max)²).

   .. py:method:: get_foci(time=0)

      Return a list of two ``(x, y)`` foci points.

   .. py:method:: point_at_angle(degrees, time=0)

      Return ``(x, y)`` on the ellipse boundary at the given angle.

   .. py:method:: get_point_at_parameter(t, time=0)

      Return ``(x, y)`` at parametric value *t* ∈ [0, 1] (full revolution).

   .. py:method:: contains_point(px, py, time=0)

      Return ``True`` if the point lies inside the ellipse.

   **Mutation methods**

   .. py:method:: set_center(cx, cy, start=0, end=None, easing=smooth)

      Animate the centre to a new position.

   .. py:method:: set_rx(value, start=0, end=None, easing=smooth)
   .. py:method:: set_ry(value, start=0, end=None, easing=smooth)

      Animate radius changes.

   .. py:method:: get_rx(time=0)
   .. py:method:: get_ry(time=0)

      Return current radii values.

   **Tangent / Normal**

   .. py:method:: tangent_at_angle(angle_deg, length=200, time=0, **kwargs)

      Return a :py:class:`Line` tangent to the ellipse at the given angle.

   .. py:method:: normal_at_angle(angle_deg, length=200, time=0, **kwargs)

      Return a :py:class:`Line` normal to the ellipse at the given angle.

   .. py:method:: get_tangent_line(angle_deg, length=100, time=0, **kwargs)

      Alias for :py:meth:`tangent_at_angle`.

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

   **Geometry**

   .. py:method:: point_at_angle(degrees, time=0)

      Return ``(x, y)`` on the circumference at the given angle.

   .. py:method:: get_area(time=0)

      Return πr².

   .. py:method:: get_perimeter(time=0)

      Return 2πr.

   .. py:method:: get_radius(time=0)
   .. py:method:: set_radius(value, start=0, end=None, easing=smooth)

      Get / animate the radius.

   .. py:method:: contains_point(px, py, time=0)

      Return ``True`` if the point lies inside the circle.

   .. py:method:: sector_area(start_angle, end_angle, time=0)

      Area of the sector between two angles (degrees).

   .. py:method:: arc_length(start_angle, end_angle, time=0)

      Arc length between two angles (degrees).

   .. py:method:: segment_area(start_angle, end_angle, time=0)

      Area of the circular segment between two angles.

   .. py:method:: chord_length(distance, time=0)

      Chord length at given distance from center.

   .. py:method:: power_of_point(px, py, time=0)

      Return the power of a point with respect to the circle.

   **Construction**

   .. py:method:: chord(angle1, angle2, time=0, **kwargs)

      Return a :py:class:`Line` chord between two angles.

   .. py:method:: diameter_line(angle_deg=0, time=0, **kwargs)

      Return a :py:class:`Line` through the center at the given angle.

   .. py:method:: get_arc(start_angle=0, end_angle=180, time=0, **kwargs)

      Return an :py:class:`Arc` on this circle.

   .. py:method:: arc_between(start_angle, end_angle, time=0, **kwargs)

      Same as :py:meth:`get_arc`.

   .. py:method:: inscribed_polygon(n, angle=0, time=0, **kwargs)

      Return a :py:class:`RegularPolygon` inscribed in this circle.

   .. py:method:: circumscribed_polygon(n, angle=0, time=0, **kwargs)

      Return a :py:class:`RegularPolygon` circumscribed around this circle.

   .. py:method:: get_annulus(inner_ratio=0.5, time=0, **kwargs)

      Return an :py:class:`Annulus` with inner radius as a fraction of r.

   .. py:method:: annular_sector(inner_ratio=0.5, start_angle=0, end_angle=360, **kwargs)

      Return an :py:class:`AnnularSector` based on this circle.

   .. py:method:: get_sectors(n, **kwargs)

      Return a list of *n* equal :py:class:`Wedge` sectors.

   **Tangent lines**

   .. py:method:: tangent_line(angle_degrees, length=100, time=0, **kwargs)

      Return a :py:class:`Line` tangent at the given angle on the circle.

   .. py:method:: tangent_at_point(px, py, length=200, time=0, **kwargs)

      Return a tangent line at the closest point on the circle.

   .. py:method:: tangent_line_from_point(px, py, time=0, length=200, **kwargs)

      Return tangent lines from an external point.

   .. py:method:: get_tangent_lines(px, py, time=0, length=200, **kwargs)

      Return both tangent lines from external point as a list.

   .. py:method:: tangent_points(px, py, time=0)

      Return the two tangent contact points from an external point.

   **Intersections**

   .. py:method:: intersect_line(line, time=0)

      Return list of ``(x, y)`` intersection points with a :py:class:`Line`.

   .. py:method:: intersect_circle(other, time=0)

      Return list of ``(x, y)`` intersection points with another circle.

   **Class methods**

   .. py:classmethod:: from_diameter(p1, p2, **kwargs)

      Create a circle from two diameter endpoints.

   .. py:classmethod:: from_center_and_point(center, point, **kwargs)

      Create from center and a point on the circumference.

   .. py:classmethod:: from_bounding_box(vobject, padding=0, time=0, **kwargs)

      Create the smallest enclosing circle for a VObject's bounding box.

   .. py:classmethod:: from_three_points(p1, p2, p3, **kwargs)

      Create the unique circle through three non-collinear points.

   **Example — animated circle with tangent**

   .. code-block:: python

      c = Circle(r=100, cx=960, cy=540, stroke='#3498DB', fill_opacity=0.1)
      c.set_radius(200, start=1, end=3)

      # Tangent line that follows the circle
      tl = c.tangent_line(45, length=250, stroke='#E74C3C')
      tl.fadein(start=0.5, end=1.5)

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

AnnotationDot
-------------

.. py:class:: AnnotationDot(r=14, cx=960, cy=540, **styling)

   Bases: :py:class:`Dot`

   Slightly larger dot with an outline stroke, designed for annotations.
   Default styling: yellow fill (``#FFFF00``), black stroke, stroke_width=2.

----

Square
------

.. py:class:: Square(side=200, x=960, y=540, **styling)

   Bases: :py:class:`Rectangle`

   Square (rectangle with equal width and height).

   :param float side: Side length.

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

   **Geometry**

   .. py:method:: get_size(time=0)

      Return ``(width, height)`` tuple.

   .. py:method:: is_square(time=0, tol=1e-3)

      Return ``True`` if width ≈ height.

   .. py:method:: aspect_ratio(time=0)

      Return width / height.

   .. py:method:: contains_point(px, py, time=0)

      Return ``True`` if the point lies inside the rectangle.

   .. py:method:: sample_border(t, time=0)

      Return ``(x, y)`` at parameter *t* ∈ [0, 1] around the border.

   **Mutation**

   .. py:method:: set_size(width, height, start=0, end=None, easing=smooth)

      Animate to new dimensions.

   .. py:method:: grow_width(amount, start=0, end=1, easing=smooth)
   .. py:method:: grow_height(amount, start=0, end=1, easing=smooth)

      Add *amount* to width or height over the interval.

   .. py:method:: expand(amount=20, start=0, end=1, easing=smooth)

      Expand width and height by *amount* simultaneously.

   **Subdivision**

   .. py:method:: split(direction='horizontal', count=2, time=0, **kwargs)

      Split into *count* sub-rectangles. Direction is ``'horizontal'`` or ``'vertical'``.

   .. py:method:: split_horizontal(n=2, time=0, **kwargs)
   .. py:method:: split_vertical(n=2, time=0, **kwargs)

      Convenience methods for :py:meth:`split`.

   .. py:method:: quadrants(time=0, **kwargs)

      Split into 4 equal sub-rectangles.

   .. py:method:: subdivide(rows=2, cols=2, time=0, **kwargs)

      Split into a grid of *rows* × *cols* sub-rectangles.

   **Construction**

   .. py:method:: inset(amount, time=0, **kwargs)

      Return a smaller rectangle inset by *amount* on all sides.

   .. py:method:: round_corners(radius=10, time=0, **kwargs)

      Return a :py:class:`RoundedRectangle` copy with rounded corners.

   .. py:method:: to_polygon(time=0, **kwargs)

      Convert to a :py:class:`Polygon` with four vertices.

   .. py:method:: to_lines(time=0, **kwargs)

      Convert to four :py:class:`Line` objects (the edges).

   .. py:method:: diagonal_lines(time=0, **kwargs)

      Return the two diagonal :py:class:`Line` objects.

   .. py:method:: chamfer(size=10, time=0, **kwargs)

      Return a :py:class:`Polygon` with chamfered (cut) corners.

   .. py:method:: get_grid_lines(rows, cols, time=0, **kwargs)

      Return a list of :py:class:`Line` objects forming a grid.

   **Class methods**

   .. py:classmethod:: square(side, **kwargs)

      Create a square rectangle.

   .. py:classmethod:: from_center(cx, cy, width, height, **kwargs)

      Create a rectangle centered at ``(cx, cy)``.

   .. py:classmethod:: from_corners(x1, y1, x2, y2, **kwargs)

      Create from opposite corner coordinates.

   .. py:classmethod:: from_bounding_box(vobject, padding=0, time=0, **kwargs)

      Create the bounding rectangle for a VObject.

   .. py:classmethod:: from_two_objects(obj_a, obj_b, padding=0, **kwargs)

      Create the bounding rectangle that encloses two VObjects.

   **Example — animated subdivision**

   .. code-block:: python

      r = Rectangle(400, 300, x=780, y=390, fill='#2C3E50', stroke='#ECF0F1')
      r.fadein(start=0, end=1)

      # Split into a 3×3 grid
      cells = r.subdivide(rows=3, cols=3)
      for i, cell in enumerate(cells):
          cell.fadein(start=1 + i * 0.2, end=1.5 + i * 0.2)
          v.add(cell)

----

RoundedRectangle
----------------

.. py:class:: RoundedRectangle(width, height, x=960, y=540, corner_radius=12, **styling)

   Bases: :py:class:`Rectangle`

   Rectangle with rounded corners.

   .. py:method:: get_corner_radius(time=0)

      Return the corner radius.

   .. py:method:: set_corner_radius(value, start=0, end=None, easing=smooth)

      Animate the corner radius.

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

   **Query methods**

   .. py:method:: get_start(time=0)
   .. py:method:: get_end(time=0)

      Return ``(x, y)`` of start / end points.

   .. py:method:: get_midpoint(time=0)

      Return ``(x, y)`` midpoint.

   .. py:method:: get_length(time=0)

      Return the length of the line segment.

   .. py:method:: get_angle(time=0)

      Return the angle in degrees.

   .. py:method:: get_slope(time=0)

      Return the slope (dy/dx), or ``float('inf')`` for vertical lines.

   .. py:method:: get_direction(time=0)

      Return ``(dx, dy)`` unit direction vector.

   .. py:method:: get_vector(time=0)

      Return ``(dx, dy)`` (not normalized).

   .. py:method:: get_normal(time=0)

      Return ``(-dy, dx)`` unit normal vector.

   .. py:method:: lerp(t, time=0)

      Return ``(x, y)`` at parameter *t* ∈ [0, 1] along the line.

   **Boolean checks**

   .. py:method:: is_horizontal(time=0, tol=1e-3)
   .. py:method:: is_vertical(time=0, tol=1e-3)
   .. py:method:: is_parallel(other, time=0, tol=1e-6)
   .. py:method:: is_perpendicular(other, time=0, tol=1e-6)
   .. py:method:: contains_point(px, py, time=0, tol=2)

   **Mutation**

   .. py:method:: set_start(point, start=0, end=None, easing=smooth)
   .. py:method:: set_end(point, start=0, end=None, easing=smooth)

      Animate start or end point.

   .. py:method:: set_points(p1, p2, start=0)

      Set both points at once (instant).

   .. py:method:: set_length(length, start=0, end=None, easing=smooth)

      Animate to a new length, keeping the midpoint fixed.

   .. py:method:: set_angle(angle_deg, about='midpoint', start=0, end=None, easing=smooth)

      Animate to a new angle. ``about`` can be ``'midpoint'``, ``'start'``, or ``'end'``.

   .. py:method:: put_start_and_end_on(p1, p2, start=0, end=None, easing=smooth)

      Animate both endpoints simultaneously.

   .. py:method:: extend_to(length, anchor='start', start=0, end=None, easing=smooth)

      Extend to a given total length from an anchor.

   .. py:method:: extend(factor=1.5, start=0, end=None, easing=smooth)

      Multiply the length by *factor*.

   .. py:method:: scale_length(factor=2.0, time=0)

      Instantly scale the length by *factor*.

   .. py:method:: add_tip(end=True, start=False, tip_length=None, tip_width=None)

      Add arrowhead tips to one or both ends.

   **Construction**

   .. py:method:: split_at(t=0.5, time=0)

      Return two new :py:class:`Line` segments split at parameter *t*.

   .. py:method:: subdivide_into(n=2, time=0, **kwargs)

      Return *n* equal sub-segments as :py:class:`Line` objects.

   .. py:method:: divide(n=2, time=0)

      Return *n+1* evenly spaced points along the line.

   .. py:method:: perpendicular(at_proportion=0.5, length=None, time=0, **kwargs)

      Return a :py:class:`Line` perpendicular at the given proportion.

   .. py:method:: parallel(offset=50, time=0, **kwargs)

      Return a parallel :py:class:`Line` at given offset distance.

   .. py:method:: parallel_through(point, time=0, **kwargs)

      Return a parallel :py:class:`Line` through a point.

   .. py:method:: bisector(time=0, length=None, **kwargs)

      Return the perpendicular bisector line.

   **Intersections and projections**

   .. py:method:: intersect_line(other, time=0)

      Return ``(x, y)`` intersection with another infinite line, or ``None``.

   .. py:method:: intersect_segment(other, time=0)

      Return ``(x, y)`` only if both segments actually overlap.

   .. py:method:: intersection(other, time=0)

      Alias for :py:meth:`intersect_line`.

   .. py:method:: project_point(px, py, time=0)

      Orthogonal projection of a point onto the infinite line.

   .. py:method:: closest_point_on_segment(px, py, time=0)

      Closest point clamped to the segment.

   .. py:method:: distance_to_point(px, py, time=0)

      Shortest distance from a point to the segment.

   .. py:method:: angle_to(other, time=0)

      Angle between this line and another (degrees).

   .. py:method:: reflect_over(other, time=0, **kwargs)

      Return a :py:class:`Line` reflected over another line.

   .. py:method:: project_onto(other, time=0, **kwargs)

      Return the projection of this segment onto another line.

   **Class methods**

   .. py:classmethod:: between(p1, p2, **kwargs)

      Create a line between two ``(x, y)`` points.

   .. py:classmethod:: vertical(x, y1, y2, **kwargs)
   .. py:classmethod:: horizontal(y, x1, x2, **kwargs)

      Create vertical or horizontal lines.

   .. py:classmethod:: from_direction(origin, direction, length=100, **kwargs)

      Create from an origin point and direction tuple.

   .. py:classmethod:: from_angle(origin, angle_deg, length=100, **kwargs)

      Create from an origin point and angle.

   .. py:classmethod:: from_slope_point(slope, point, length=200, **kwargs)

      Create from a slope and a point on the line.

   .. py:classmethod:: from_objects(obj_a, obj_b, buff=0, **kwargs)

      Create a line connecting two VObjects' centres.

   **Example — line geometry**

   .. code-block:: python

      l1 = Line(200, 300, 800, 600, stroke='#3498DB')
      l2 = Line(200, 600, 800, 200, stroke='#E74C3C')

      # Find intersection
      pt = l1.intersect_line(l2)
      if pt:
          dot = Dot(cx=pt[0], cy=pt[1])
          dot.fadein(start=1, end=2)

      # Perpendicular bisector
      bisector = l1.bisector(length=300, stroke='#2ECC71')

----

DashedLine
----------

.. py:class:: DashedLine(x1=0, y1=0, x2=100, y2=100, dash='10,5', **styling)

   Bases: :py:class:`Line`

   Line with a dashed pattern.

   :param str dash: SVG dash-array string.

   .. py:method:: set_dash_pattern(dash, gap=None, start=0)

      Change the dash pattern.

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

   **Geometry**

   .. py:method:: get_vertices(time=0)

      Return list of ``(x, y)`` tuples.

   .. py:method:: get_center(time=0)

      Return the bounding-box center.

   .. py:method:: centroid(time=0)

      Return the geometric centroid (average of vertices).

   .. py:method:: area(time=0)

      Return the polygon area (shoelace formula, always positive).

   .. py:method:: signed_area(time=0)

      Return signed area (positive for counter-clockwise).

   .. py:method:: perimeter(time=0)

      Return the polygon perimeter.

   .. py:method:: edge_lengths(time=0)

      Return a list of edge lengths.

   .. py:method:: contains_point(px, py, time=0)

      Return ``True`` if the point lies inside (winding number algorithm).

   .. py:method:: winding_number(px, py, time=0)

      Return the winding number of a point with respect to the polygon.

   .. py:method:: is_convex(time=0)

      Return ``True`` if the polygon is convex.

   .. py:method:: is_clockwise(time=0)

      Return ``True`` if vertices are ordered clockwise.

   .. py:method:: is_regular(tol=1e-3, time=0)

      Return ``True`` if all edges and angles are equal.

   .. py:method:: interior_angles(time=0)

      Return a list of interior angles in degrees.

   **Edges and diagonals**

   .. py:method:: get_edges(time=0)

      Return a list of ``((x1,y1), (x2,y2))`` edge tuples.

   .. py:method:: get_edge_midpoints(time=0)

      Return list of ``(x, y)`` midpoints of each edge.

   .. py:method:: get_longest_edge(time=0)
   .. py:method:: get_shortest_edge(time=0)

      Return ``((x1,y1), (x2,y2))`` for the longest / shortest edge.

   .. py:method:: get_diagonals(time=0, **kwargs)

      Return all diagonals as :py:class:`Line` objects.

   **Mutation**

   .. py:method:: move_vertex(index, x, y, start=0, end=None, easing=smooth)

      Animate a single vertex to a new position.

   .. py:method:: translate(dx, dy)

      Translate all vertices by ``(dx, dy)`` instantly.

   .. py:method:: scale_vertices(factor, time=0)

      Scale all vertices relative to the centroid.

   .. py:method:: rotate_vertices(angle_deg, cx=None, cy=None, time=0)

      Rotate all vertices around a point (defaults to centroid).

   .. py:method:: mirror_x(cx=None, time=0)
   .. py:method:: mirror_y(cy=None, time=0)

      Mirror vertices across a vertical / horizontal axis.

   .. py:method:: apply_pointwise(func, time=0)

      Apply a function ``f(x, y) → (x', y')`` to each vertex.

   **Derived shapes**

   .. py:method:: offset(distance, time=0)

      Return a new :py:class:`Polygon` offset outward by *distance*.

   .. py:method:: buffer(distance, time=0)

      Alias for :py:meth:`offset`.

   .. py:method:: inset(distance, time=0, **kwargs)

      Return a new polygon inset by *distance*.

   .. py:method:: to_path(time=0)

      Convert to a :py:class:`Path`.

   .. py:method:: get_convex_hull(time=0, **kwargs)

      Return the convex hull as a new :py:class:`Polygon`.

   .. py:method:: bounding_circle(time=0, **kwargs)

      Return the smallest enclosing :py:class:`Circle`.

   .. py:method:: triangulate(time=0, **kwargs)

      Return a list of :py:class:`Polygon` triangles via ear clipping.

   .. py:method:: explode_edges(gap=10, **kwargs)

      Return individual :py:class:`Line` objects with a gap between each.

   .. py:method:: subdivide_edges(iterations=1, time=0, **kwargs)

      Subdivide each edge into two, refining the polygon.

   .. py:method:: smooth_corners(radius=10, time=0, **kwargs)

      Return a new polygon with rounded corners.

   .. py:method:: label_vertices(labels=None, offset=20, font_size=24, time=0, **kwargs)

      Return :py:class:`Text` labels positioned near each vertex.

   **Class methods**

   .. py:classmethod:: from_points(points, **kwargs)

      Create from a list of ``(x, y)`` points.

   .. py:classmethod:: convex_hull(*points, **kwargs)

      Create the convex hull of a set of points.

   .. py:classmethod:: from_svg_path(path_d, **kwargs)

      Create from an SVG path ``d`` string.

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

   .. py:method:: get_side_length(time=0)

      Return the side length.

   .. py:method:: get_inradius(time=0)
   .. py:method:: get_apothem(time=0)

      Return the inradius (distance from center to edge midpoint). Both are equivalent.

   .. py:method:: get_circumradius(time=0)

      Return the circumscribed radius.

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

   .. py:method:: get_outer_radius()
   .. py:method:: get_inner_radius()

      Return the stored radius values.

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

   **Methods**

   .. py:method:: get_start_point(time=0)
   .. py:method:: get_end_point(time=0)

      Return ``(x, y)`` at the start / end of the arc.

   .. py:method:: get_arc_length(time=0)

      Return the arc length.

   .. py:method:: point_at_angle(angle_deg, time=0)

      Return ``(x, y)`` at a specific angle on the arc's circle.

   .. py:method:: set_angles(start_angle, end_angle, start=0, end_time=None, easing=smooth)

      Animate the arc angles.

   .. py:method:: to_arc(time=0, **kwargs)

      Convert to a separate :py:class:`Arc` (useful for Wedge → Arc).

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

   .. py:method:: get_inner_radius(time=0)
   .. py:method:: get_outer_radius(time=0)
   .. py:method:: set_inner_radius(value, start=0, end=None, easing=smooth)
   .. py:method:: set_outer_radius(value, start=0, end=None, easing=smooth)
   .. py:method:: set_radii(inner=None, outer=None, start=0, end=None, easing=smooth)

      Get, set, or animate both radii at once.

   .. py:method:: get_area(time=0)

      Return π(R² - r²).

----

AnnularSector
-------------

.. py:class:: AnnularSector(inner_radius=60, outer_radius=120, cx=960, cy=540, start_angle=0, end_angle=90, **styling)

   Bases: :py:class:`Arc`

   Sector of an annulus (ring wedge). Like a Wedge but with an inner radius cut out.

   :param float inner_radius: Inner radius.
   :param float outer_radius: Outer radius.

   .. py:method:: set_inner_radius(value, start=0, end=None, easing=smooth)
   .. py:method:: get_area(time=0)

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

ArcPolygon
----------

.. py:class:: ArcPolygon(*vertices, arc_angles=30, **styling)

   Polygon whose edges are arcs instead of straight lines.

   :param vertices: At least 3 ``(x, y)`` tuples.
   :param arc_angles: Bulge angle for each edge (scalar for all, or list per edge).
      Positive = left of travel, negative = right, 0 = straight.

   **Example**

   .. code-block:: python

      # Triangle with curved edges
      ap = ArcPolygon((860, 400), (1060, 400), (960, 250),
                      arc_angles=30, fill='#3498DB', fill_opacity=0.3)

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

Text
----

.. py:class:: Text(text='', x=960, y=540, font_size=48, text_anchor=None, font_family=None, **styling)

   SVG ``<text>`` element with animation support.

   :param str text: Text content.
   :param float x: X position.
   :param float y: Y position.
   :param float font_size: Font size in pixels.
   :param str text_anchor: SVG text-anchor (``'start'``, ``'middle'``, ``'end'``).
   :param str font_family: Font family name.

   .. py:attribute:: text
      :type: String

      The text content (time-varying).

   .. py:attribute:: font_size
      :type: Real

      Font size (time-varying, animatable).

   **Query**

   .. py:method:: get_text(time=0)

      Return the current text string.

   .. py:method:: get_font_size(time=0)

      Return the current font size.

   .. py:method:: starts_with(prefix, time=0)
   .. py:method:: ends_with(suffix, time=0)

      String checks on the current text.

   **Text animations**

   .. py:method:: typing(start=0, end=1, change_existence=True)

      Typewriter effect — reveals the text character by character.

   .. py:method:: reveal_by_word(start=0, end=1, change_existence=True, easing=None)

      Reveal text word by word. Alias: ``word_by_word``.

   .. py:method:: typewrite(start=0, end=1, cursor='|', cursor_blink=0.5)

      Typewriter with a blinking cursor character.

   .. py:method:: untype(start=0, end=1)

      Reverse typewriter — removes characters one by one.

   .. py:method:: scramble(start=0, end=1, chars=None)

      Scramble text with random characters before settling to the final text.

   .. py:method:: set_text(start, end, new_text)

      Change the text content over the interval.

   .. py:method:: highlight(start=0, end=1, color='#FFFF00')

      Briefly highlight the text with a color flash.

   .. py:method:: highlight_substring(substring, color='#FFFF00', start=0, end=None)

      Highlight occurrences of a substring with a different color.

   **Example — typewriter effect**

   .. code-block:: python

      t = Text("Hello, World!", x=960, y=540, font_size=64, fill='#fff')
      t.typing(start=0, end=3)  # Reveals over 3 seconds

----

CountAnimation
--------------

.. py:class:: CountAnimation(start_value, end_value, fmt='{:.0f}', x=960, y=540, font_size=48, start=0, end=1, **styling)

   Bases: :py:class:`Text`

   Animated counter that interpolates between two numeric values.

   :param float start_value: Starting number.
   :param float end_value: Ending number.
   :param str fmt: Format string (e.g. ``'{:.2f}'`` or ``'${:,.0f}'``).
   :param float start: Animation start time.
   :param float end: Animation end time.

   **Example**

   .. code-block:: python

      counter = CountAnimation(0, 1000, fmt='${:,.0f}',
                               x=960, y=540, font_size=72, fill='#2ECC71')
      counter.fadein(start=0, end=0.5)
      # Counts from $0 to $1,000 over 3 seconds

----

Integer
-------

.. py:class:: Integer(value=0, x=960, y=540, font_size=48, **styling)

   Bases: :py:class:`DecimalNumber`

   Like DecimalNumber but formats as an integer (no decimal places).

----

ComplexValueTracker
-------------------

.. py:class:: ComplexValueTracker(value=0+0j, creation=0)

   Like :py:class:`ValueTracker` but tracks a complex number (two Reals for real/imaginary parts).

   .. py:method:: set_value(val, start=0)
   .. py:method:: animate_value(target, start, end, easing=smooth)
   .. py:method:: at_time(time)

      Get, set, or animate the complex value.

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

.. py:class:: FunctionGraph(func, x_range=(-5, 5), y_range=None, num_points=200, x=120, y=60, width=1440, height=840, **styling)

   Bases: :py:class:`Lines`

   Plot a function as a polyline (no axes, ticks, or labels).

   :param callable func: ``f(x) → y`` function.
   :param tuple x_range: ``(start, end)`` in math coordinates.
   :param tuple y_range: ``(min, max)`` or ``None`` for auto.
   :param int num_points: Sampling resolution.

   .. py:method:: get_point_from_x(math_x)

      Return ``(svg_x, svg_y)`` for a math x value.

   .. py:method:: get_slope_at(math_x, dx=1e-6)

      Return the numerical slope at a math x value.

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

   .. py:method:: point_at(t, time=0)

      Return ``(x, y)`` at parameter *t* ∈ [0, 1].

   .. py:method:: tangent_at(t, time=0)

      Return ``(dx, dy)`` tangent vector at parameter *t*.

----

Elbow
-----

.. py:class:: Elbow(cx=960, cy=540, width=40, height=40, **styling)

   Bases: :py:class:`Lines`

   Right-angle connector (L-shape).

   :param float width: Horizontal arm size.
   :param float height: Vertical arm size.

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

.. py:class:: BulletedList(*items, x=200, y=200, font_size=36, bullet='•', indent=40, **styling)

   List of items with bullet points.

   :param items: Text strings.
   :param str bullet: Bullet character.
   :param float indent: Pixel indentation for each item.

----

NumberedList
------------

.. py:class:: NumberedList(*items, x=200, y=200, font_size=36, indent=50, start_number=1, **styling)

   Bases: similar to :py:class:`BulletedList`

   List of items with numeric labels (1. 2. 3. …).

   :param items: Text strings.
   :param float indent: Pixel indentation after the number.
   :param int start_number: First number in the sequence.

----

Fractals & Spirals
------------------

.. py:class:: KochSnowflake(cx=960, cy=540, size=400, depth=3, **styling)

   Bases: :py:class:`Polygon`

   Koch snowflake fractal polygon. Each recursion depth subdivides edges
   with triangular bumps, creating the classic fractal boundary.

   :param float cx: Center x.
   :param float cy: Center y.
   :param float size: Side length of the initial equilateral triangle.
   :param int depth: Recursion depth (0 = triangle, 3 is typical).

.. py:class:: SierpinskiTriangle(cx=960, cy=540, size=500, depth=4, **styling)

   Bases: :py:class:`VCollection`

   Sierpinski triangle fractal composed of many small filled triangles.

   :param float cx: Center x.
   :param float cy: Center y.
   :param float size: Side length of the outer triangle.
   :param int depth: Recursion depth (0 = solid triangle, 4–5 is typical).

.. py:class:: Spiral(cx=960, cy=540, a=0, b=15, turns=5, num_points=500, log_spiral=False, **styling)

   Bases: :py:class:`Lines`

   Archimedean (``r = a + b·θ``) or logarithmic (``r = a·e^{b·θ}``) spiral.

   :param float a: Initial radius (distance from center at θ=0).
   :param float b: Growth rate per radian.
   :param float turns: Number of full turns.
   :param int num_points: Number of sample points.
   :param bool log_spiral: If True, use logarithmic spiral.

   **Example**

   .. code-block:: python

      # Archimedean spiral
      s = Spiral(a=0, b=12, turns=6, stroke='#3498DB', stroke_width=2)
      s.create(start=0, end=3)

      # Logarithmic spiral
      ls = Spiral(a=5, b=0.15, turns=4, log_spiral=True,
                  stroke='#E74C3C', stroke_width=2)

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

   .. py:method:: set_value(val, start=0)

      Set the value from *start* onward.

   .. py:method:: animate_value(target, start, end, easing=smooth)

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
