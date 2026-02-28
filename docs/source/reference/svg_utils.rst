SVG Utilities
=============

SVG filter definitions, geometric annotations, boolean shape operations,
vector field visualizations, and SVG import helpers. All visual classes
inherit from :doc:`VObject <vobject>` or :py:class:`VCollection` and support
the full set of animation methods.

----

Filters & Clip Paths
---------------------

ClipPath
~~~~~~~~

.. py:class:: ClipPath(*objects)

   SVG clip path definition containing one or more shape objects. Register
   with ``canvas.add_def()`` and apply via the ``clip_path`` styling attribute.

   :param objects: One or more VObject shapes that define the clip region.

   .. py:method:: clip_ref()

      Returns the ``url(#...)`` reference string for use in ``clip_path``.

   .. py:method:: to_svg_def(time)

      Returns the ``<clipPath>`` SVG element string.

   .. code-block:: python

      clip = ClipPath(Circle(r=120, cx=960, cy=540))
      canvas.add_def(clip)
      rect = Rectangle(400, 400, clip_path=clip.clip_ref())

----

BlurFilter
~~~~~~~~~~

.. py:class:: BlurFilter(std_deviation=4)

   SVG Gaussian blur filter definition. Register with ``canvas.add_def()``
   and apply to objects via styling: ``obj.styling.filter = blur.filter_ref()``.

   :param float std_deviation: Blur radius.

   .. py:method:: filter_ref()

      Returns the ``url(#...)`` reference string.

   .. code-block:: python

      blur = BlurFilter(std_deviation=8)
      canvas.add_def(blur)
      text = Text('Blurred', filter=blur.filter_ref())

----

DropShadowFilter
~~~~~~~~~~~~~~~~

.. py:class:: DropShadowFilter(dx=4, dy=4, std_deviation=4, color='#000', opacity=0.5)

   SVG drop shadow filter definition. Register with ``canvas.add_def()``.

   :param float dx: Horizontal shadow offset.
   :param float dy: Vertical shadow offset.
   :param float std_deviation: Blur radius.
   :param str color: Shadow colour.
   :param float opacity: Shadow opacity.

   .. py:method:: filter_ref()

      Returns the ``url(#...)`` reference string.

   .. code-block:: python

      shadow = DropShadowFilter(dx=6, dy=6, std_deviation=4, color='#000')
      canvas.add_def(shadow)
      rect = Rectangle(200, 100, filter=shadow.filter_ref())

----

Geometric Annotations
---------------------

Angle
~~~~~

.. py:class:: Angle(vertex, p1, p2, radius=36, label=None, label_radius=None, label_font_size=36, **styling)

   Bases: :py:class:`VCollection`

   Angle indicator arc between two rays meeting at a vertex. All three
   position parameters accept ``(x, y)`` tuples or :py:class:`Coor` objects
   for time-varying angles.

   :param vertex: Vertex point ``(x, y)`` or ``Coor``.
   :param p1: First ray endpoint ``(x, y)`` or ``Coor``.
   :param p2: Second ray endpoint ``(x, y)`` or ``Coor``.
   :param float radius: Arc radius in pixels.
   :param label: ``None`` for no label, ``True`` for a dynamic degree label,
      or a string (e.g. ``r'\theta'``) for a static TeX label.
   :param float label_radius: Distance from vertex to label (defaults to
      ``radius * 1.75``).
   :param float label_font_size: Font size for the label.

   .. py:attribute:: arc
      :type: Arc

      The underlying arc object.

   .. py:method:: set_radius(new_radius, start=0, end=None, easing=smooth)

      Animate the angle arc radius to *new_radius*.

   .. code-block:: python

      v = (960, 540)
      a = (1100, 540)
      b = (1060, 400)
      angle = Angle(v, a, b, radius=50, label=True)

----

RightAngle
~~~~~~~~~~

.. py:class:: RightAngle(vertex, p1, p2, size=18, **styling)

   Bases: :py:class:`VCollection`

   Right angle indicator (small square) at a vertex between two
   perpendicular lines.

   :param tuple vertex: Vertex point ``(x, y)``.
   :param tuple p1: First ray endpoint.
   :param tuple p2: Second ray endpoint.
   :param float size: Side length of the square indicator.

   .. code-block:: python

      right = RightAngle((500, 500), (600, 500), (500, 400), size=20)

----

Cross
~~~~~

.. py:class:: Cross(size=36, cx=960, cy=540, **styling)

   Bases: :py:class:`VCollection`

   X-mark shape (two crossing lines), useful for indicating errors or
   crossing out elements.

   :param float size: Full width/height of the cross.
   :param float cx: Centre x.
   :param float cy: Centre y.

   .. code-block:: python

      x_mark = Cross(size=50, cx=400, cy=300, stroke='#FF0000')

----

Zoomed Inset & Overlays
------------------------

ZoomedInset
~~~~~~~~~~~

.. py:class:: ZoomedInset(canvas, source, display, frame_color='#FFFF00', display_color='#FFFF00', frame_width=2, creation=0, z=999)

   Bases: :py:class:`VObject`

   Magnified inset view of a region on the canvas. Renders a nested SVG
   ``<svg>`` element with a viewBox matching the source region, displayed
   at the display region's position and size.

   :param canvas: The :py:class:`VectorMathAnim` canvas.
   :param tuple source: ``(x, y, width, height)`` of the region to magnify.
   :param tuple display: ``(x, y, width, height)`` of the display viewport.
   :param str frame_color: Colour of the source frame rectangle.
   :param str display_color: Colour of the display border.
   :param float frame_width: Stroke width of the frame and border.

   .. py:attribute:: src_x
      :type: Real

   .. py:attribute:: src_y
      :type: Real

   .. py:attribute:: src_w
      :type: Real

   .. py:attribute:: src_h
      :type: Real

   .. py:attribute:: dst_x
      :type: Real

   .. py:attribute:: dst_y
      :type: Real

   .. py:attribute:: dst_w
      :type: Real

   .. py:attribute:: dst_h
      :type: Real

   .. py:method:: move_source(x, y, start, end=None, easing=smooth)

      Animate the source region position to ``(x, y)``.

   .. code-block:: python

      inset = ZoomedInset(
          canvas,
          source=(800, 400, 200, 200),
          display=(1400, 100, 400, 400),
      )
      canvas.add(inset)
      inset.move_source(900, 450, start=0, end=2)

----

Spotlight
~~~~~~~~~

.. py:class:: Spotlight(target=(960, 540), radius=120, color='#000000', opacity=0.7, creation=0, z=10)

   Bases: :py:class:`VObject`

   Dark overlay with a circular cutout -- draws attention to a point or
   object. The overlay covers the entire canvas and uses an even-odd fill
   rule to create the bright area.

   :param target: Centre of the spotlight. An ``(x, y)`` tuple or a VObject
      (uses its centre).
   :param float radius: Radius of the bright area.
   :param str color: Overlay colour (usually dark).
   :param float opacity: Overlay opacity (0 = invisible, 1 = fully opaque).

   .. py:method:: set_target(target, start=0, end=None, easing=smooth)

      Move the spotlight to a new target (point or VObject).

   .. py:method:: set_radius(value, start=0, end=None, easing=smooth)

      Animate the spotlight radius.

   .. code-block:: python

      dot = Dot(cx=400, cy=300)
      spot = Spotlight(target=dot, radius=80, opacity=0.8)
      spot.set_target((960, 540), start=1, end=3)
      spot.set_radius(200, start=1, end=3)

----

Cutout
~~~~~~

.. py:class:: Cutout(hole_x=660, hole_y=340, hole_w=600, hole_h=400, color='#000', opacity=0.7, rx=0, ry=0, creation=0, z=99)

   Bases: :py:class:`VObject`

   Full-screen overlay with a rectangular cutout (spotlight effect). Unlike
   :py:class:`Spotlight`, the cutout is rectangular and supports rounded
   corners via ``rx``/``ry``.

   :param float hole_x: Hole top-left x.
   :param float hole_y: Hole top-left y.
   :param float hole_w: Hole width.
   :param float hole_h: Hole height.
   :param str color: Overlay colour.
   :param float opacity: Overlay opacity.
   :param float rx: Hole corner radius x (for rounded cutouts).
   :param float ry: Hole corner radius y.

   .. py:attribute:: hole_x
      :type: Real

   .. py:attribute:: hole_y
      :type: Real

   .. py:attribute:: hole_w
      :type: Real

   .. py:attribute:: hole_h
      :type: Real

   .. py:method:: set_hole(x=None, y=None, w=None, h=None, start=0, end=None, easing=smooth)

      Animate hole position and/or size. Pass only the parameters you want
      to change.

   .. py:method:: surround(obj, buff=20, start=0, end=None, easing=smooth)

      Move the cutout hole to surround a VObject's bounding box with
      *buff* pixels of padding.

   .. code-block:: python

      title = Text('Important', x=960, y=300, font_size=72)
      cutout = Cutout(opacity=0.8, rx=12, ry=12)
      cutout.surround(title, buff=30)
      # Animate the cutout to a new position
      cutout.set_hole(x=200, y=200, w=400, h=200, start=1, end=3)

----

AnimatedBoundary
~~~~~~~~~~~~~~~~

.. py:class:: AnimatedBoundary(target, colors=None, cycle_rate=1.0, buff=8, stroke_width=3, creation=0, z=0)

   Bases: :py:class:`VObject`

   Animated colour-cycling dashed border around another VObject. The border
   colour smoothly cycles through the given colours and the dash pattern
   scrolls along the perimeter.

   :param VObject target: The object to surround with an animated border.
   :param list colors: Colours to cycle through (defaults to
      ``['#58C4DD', '#FF6B6B', '#83C167', '#FFFF00']``).
   :param float cycle_rate: Full colour cycles per second.
   :param float buff: Extra padding around the target's bounding box.
   :param float stroke_width: Border stroke width.

   .. code-block:: python

      rect = Rectangle(300, 200)
      border = AnimatedBoundary(rect, cycle_rate=0.5, buff=12)

----

Boolean Shape Operations
------------------------

Boolean operations combine two shapes using SVG clip paths. All four
classes inherit from a common ``_BooleanOp`` base (itself a
:py:class:`VObject`) and support the standard animation methods.

Union
~~~~~

.. py:class:: Union(shape_a, shape_b, **styling)

   Bases: :py:class:`VObject`

   Boolean union -- combined area of both shapes.

   :param VObject shape_a: First shape.
   :param VObject shape_b: Second shape.

   .. code-block:: python

      c1 = Circle(r=100, cx=900, cy=540, fill='#58C4DD')
      c2 = Circle(r=100, cx=1020, cy=540, fill='#FC6255')
      u = Union(c1, c2, fill='#83C167', fill_opacity=0.8)

----

Difference
~~~~~~~~~~

.. py:class:: Difference(shape_a, shape_b, **styling)

   Bases: :py:class:`VObject`

   Boolean difference -- ``shape_a`` minus ``shape_b``. The resulting shape
   is the area of *shape_a* that does not overlap with *shape_b*.

   :param VObject shape_a: Shape to subtract from.
   :param VObject shape_b: Shape to subtract.

   .. code-block:: python

      rect = Rectangle(200, 200, x=860, y=440)
      circle = Circle(r=80, cx=960, cy=540)
      diff = Difference(rect, circle, fill='#FF8C00')

----

Intersection
~~~~~~~~~~~~

.. py:class:: Intersection(shape_a, shape_b, **styling)

   Bases: :py:class:`VObject`

   Boolean intersection -- only the area where both shapes overlap.

   :param VObject shape_a: First shape.
   :param VObject shape_b: Second shape.

   .. code-block:: python

      c1 = Circle(r=100, cx=900, cy=540)
      c2 = Circle(r=100, cx=1020, cy=540)
      inter = Intersection(c1, c2, fill='#FFFF00', fill_opacity=0.9)

----

Exclusion
~~~~~~~~~

.. py:class:: Exclusion(shape_a, shape_b, **styling)

   Bases: :py:class:`VObject`

   Boolean exclusion (XOR) -- the non-overlapping areas of both shapes.
   Uses the ``evenodd`` fill rule.

   :param VObject shape_a: First shape.
   :param VObject shape_b: Second shape.

   .. code-block:: python

      c1 = Circle(r=100, cx=900, cy=540)
      c2 = Circle(r=100, cx=1020, cy=540)
      xor = Exclusion(c1, c2, fill='#A855F7')

----

Vector Field Visualizations
---------------------------

ArrowVectorField
~~~~~~~~~~~~~~~~

.. py:class:: ArrowVectorField(func, x_range=(60, 1860, 120), y_range=(60, 1020, 120), max_length=80, creation=0, z=0, **styling)

   Bases: :py:class:`VCollection`

   Vector field visualization using arrows. Arrows are placed on a grid and
   normalized so the longest arrow has length *max_length*.

   :param callable func: ``f(x, y) -> (vx, vy)`` vector function.
   :param tuple x_range: ``(min, max, step)`` for horizontal sampling.
   :param tuple y_range: ``(min, max, step)`` for vertical sampling.
   :param float max_length: Maximum arrow length in pixels.

   .. code-block:: python

      def field(x, y):
          return (y - 540, -(x - 960))

      vf = ArrowVectorField(field, x_range=(100, 1820, 150),
                            y_range=(100, 980, 150))

----

StreamLines
~~~~~~~~~~~

.. py:class:: StreamLines(func, x_range=(60, 1860, 200), y_range=(60, 1020, 200), n_steps=40, step_size=5, creation=0, z=0, **styling)

   Bases: :py:class:`VCollection`

   Flow lines for a vector field. Each seed point on the grid is integrated
   forward through the field to produce a polyline.

   :param callable func: ``f(x, y) -> (vx, vy)`` vector function.
   :param tuple x_range: ``(min, max, step)`` for seed grid.
   :param tuple y_range: ``(min, max, step)`` for seed grid.
   :param int n_steps: Number of integration steps per stream line.
   :param float step_size: Step size per integration step.

   .. code-block:: python

      def swirl(x, y):
          dx, dy = x - 960, y - 540
          return (-dy, dx)

      streams = StreamLines(swirl, n_steps=60, step_size=8,
                            stroke='#83C167')

----

Geometry Helpers
----------------

ConvexHull
~~~~~~~~~~

.. py:class:: ConvexHull(*items, **styling)

   Bases: :py:class:`Polygon`

   Convex hull polygon around a set of points or VObjects. Uses Andrew's
   monotone chain algorithm.

   :param items: ``(x, y)`` tuples or VObject instances (their centres are
      used).

   .. code-block:: python

      d1 = Dot(cx=300, cy=300)
      d2 = Dot(cx=600, cy=200)
      d3 = Dot(cx=500, cy=500)
      hull = ConvexHull(d1, d2, d3, (400, 450),
                        stroke='#58C4DD', fill_opacity=0.1)

----

brace_between_points
~~~~~~~~~~~~~~~~~~~~

.. py:function:: brace_between_points(p1, p2, direction=None, label=None, buff=0, depth=18, creation=0, z=0, **styling)

   Create a :py:class:`Brace` between two arbitrary points. If *direction*
   is ``None``, the brace points perpendicular to the line from *p1* to
   *p2*.

   :param tuple p1: Start point ``(x, y)``.
   :param tuple p2: End point ``(x, y)``.
   :param direction: ``'up'``, ``'down'``, ``'left'``, ``'right'``, or
      ``None`` for automatic.
   :param str label: Optional label text.
   :param float buff: Buffer distance from the line.
   :param float depth: Depth of the brace curve.
   :returns: A :py:class:`Brace` object.

   .. code-block:: python

      brace = brace_between_points((400, 500), (800, 500),
                                   direction='down', label='width')

----

SVG Import
----------

from_svg
~~~~~~~~

.. py:function:: from_svg(element, **styles)

   Convert a single BeautifulSoup SVG element into a VObject. Handles
   presentation attributes and inline CSS style attributes.

   Supported SVG tags: ``path``, ``rect``, ``circle``, ``ellipse``,
   ``line``, ``polygon``, ``polyline``, ``text``, ``g`` (group).

   The ``transform="translate(...)"`` attribute is applied automatically.

   :param element: A BeautifulSoup element.
   :param styles: Extra styling keyword arguments merged into the result.
   :returns: A VObject corresponding to the SVG element.
   :raises NotImplementedError: For unsupported SVG tags.

   .. code-block:: python

      from bs4 import BeautifulSoup
      from vectormation.objects import from_svg

      soup = BeautifulSoup('<circle cx="100" cy="100" r="50"/>', 'xml')
      circle = from_svg(soup.find('circle'), fill='#FF0000')

----

from_svg_file
~~~~~~~~~~~~~

.. py:function:: from_svg_file(filepath, creation=0, z=0, **styles)

   Load an SVG file and return a :py:class:`VCollection` of all parseable
   elements. Elements inside ``<g>`` groups are handled recursively.

   :param str filepath: Path to the SVG file.
   :param float creation: Creation time for all loaded objects.
   :param float z: Z-index for all loaded objects.
   :param styles: Extra styling keyword arguments.
   :returns: A :py:class:`VCollection` containing the parsed shapes.

   .. note::

      Requires the ``beautifulsoup4`` and ``lxml`` packages (lazy-imported).

   .. code-block:: python

      from vectormation.objects import from_svg_file

      logo = from_svg_file('logo.svg', creation=0)
      logo.center_to_pos(posx=960, posy=540)
      logo.scale(factor=0.5, start=0)
