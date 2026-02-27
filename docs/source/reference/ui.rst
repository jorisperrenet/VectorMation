UI Components
=============

User interface and annotation classes. All inherit from :py:class:`VCollection`
(unless noted) and support the full set of animation methods.

----

Title
-----

.. py:class:: Title(text, creation=0, z=0, **kwargs)

   Centered title text at the top of the canvas with an underline.
   Passes extra keyword arguments through to ``Text`` (e.g. ``font_size``,
   ``fill``).

   :param str text: Title string.

   .. code-block:: python

      title = Title('Introduction to Calculus')

----

Variable
--------

.. py:class:: Variable(label='x', value=0, fmt='{:.2f}', x=960, y=540, font_size=48, creation=0, z=0, **styling)

   Display a variable label with an animated numeric value
   (e.g. ``x = 3.14``).

   :param str label: Variable name.
   :param float value: Initial numeric value.
   :param str fmt: Format string for the displayed number.

   .. py:attribute:: tracker
      :type: Real

      The underlying ``DecimalNumber`` tracker.

   .. py:method:: set_value(val, start=0)

      Set the displayed value from *start* onward.

   .. py:method:: animate_value(target, start, end, easing=smooth)

      Animate the value to *target* over ``[start, end]``.

----

Underline
---------

.. py:class:: Underline(target, buff=4, follow=True, creation=0, z=0, **styling)

   Underline beneath a target object. Tracks the target's bounding box if
   ``follow=True``.

   :param VObject target: Object to underline.
   :param float buff: Gap below the target.
   :param bool follow: Dynamically follow the target.

----

Code
----

.. py:class:: Code(text, language='python', x=120, y=120, font_size=24, line_height=1.5, tab_width=4, creation=0, z=0, **styling)

   Syntax-highlighted code block with line numbers and a dark background.
   Supports Python, JavaScript, C, Java, Rust, and Go keyword highlighting.

   :param str text: Source code string.
   :param str language: Programming language for keyword coloring.
   :param float line_height: Multiplier for vertical spacing.

   .. py:method:: highlight_lines(line_nums, start=0, end=1, color='#FFFF00', opacity=0.2, easing=there_and_back)

      Highlight specific lines with a colored overlay. Returns a
      ``VCollection`` of overlay rectangles.

   .. py:method:: reveal_lines(start=0, end=1, overlap=0.5)

      Reveal code lines sequentially with staggered fade-in.

   .. code-block:: python

      code = Code('''
      def greet(name):
          return f"Hello, {name}!"
      ''', language='python')

----

Label
-----

.. py:class:: Label(text, x=960, y=540, font_size=36, padding=10, corner_radius=4, creation=0, z=0, **styling)

   Text label with a surrounding rounded-rectangle background.

   :param str text: Label content.
   :param float padding: Padding around the text.

----

LabeledLine
-----------

.. py:class:: LabeledLine(x1=860, y1=540, x2=1060, y2=540, label='', font_size=24, label_buff=10, creation=0, z=0, **styling)

   Line with a text label placed at its midpoint, offset perpendicular to
   the line direction.

   :param str label: Midpoint label text.
   :param float label_buff: Perpendicular offset distance.

----

LabeledArrow
-------------

.. py:class:: LabeledArrow(x1=860, y1=540, x2=1060, y2=540, label='', font_size=24, label_buff=10, creation=0, z=0, **styling)

   Arrow with a text label placed at its midpoint.

   :param str label: Midpoint label text.
   :param float label_buff: Perpendicular offset distance.

----

Callout
-------

.. py:class:: Callout(text, target, direction='up', distance=80, font_size=24, padding=8, corner_radius=4, creation=0, z=0, **styling)

   Text callout with a pointer line to a target position.

   :param str text: Callout message.
   :param target: A VObject (uses its center) or an ``(x, y)`` tuple.
   :param str direction: ``'up'``, ``'down'``, ``'left'``, or ``'right'``.
   :param float distance: Distance from the target to the callout box.

----

DimensionLine
-------------

.. py:class:: DimensionLine(p1, p2, label=None, offset=30, font_size=20, tick_size=10, creation=0, z=0, **styling)

   Technical dimension line between two points with extension lines, tick
   marks, and a measurement label.

   :param tuple p1: Start point ``(x, y)``.
   :param tuple p2: End point ``(x, y)``.
   :param str label: Measurement text (auto-computed from distance if ``None``).
   :param float offset: Perpendicular offset from the measured line.

----

Tooltip
-------

.. py:class:: Tooltip(text, target, start=0, duration=1.5, font_size=18, padding=6, creation=0, z=10, **styling)

   Small tooltip that automatically fades in, holds, and fades out near a
   target object.

   :param str text: Tooltip message.
   :param target: A VObject or ``(x, y)`` tuple.
   :param float start: Time to begin the tooltip.
   :param float duration: Total visible duration (fade-in + hold + fade-out).

----

TextBox
-------

.. py:class:: TextBox(text, x=100, y=100, font_size=20, padding=12, width=None, height=None, corner_radius=6, box_fill='#333', box_opacity=0.9, text_color='#fff', creation=0, z=0, **styling)

   Text with a surrounding rounded rectangle. Auto-sizes from the text
   length if *width*/*height* are ``None``.

   :param str text: Displayed text.
   :param str box_fill: Background color.
   :param str text_color: Text fill color.

----

Bracket
-------

.. py:class:: Bracket(x=100, y=100, width=100, height=20, direction='down', stroke='#fff', stroke_width=2, text='', font_size=16, text_color='#aaa', creation=0, z=0)

   Square bracket decoration pointing at a range, with an optional text label.

   :param str direction: ``'down'``, ``'up'``, ``'left'``, or ``'right'``.
   :param str text: Label placed outside the bracket.

----

IconGrid
--------

.. py:class:: IconGrid(data, x=100, y=100, cols=10, size=15, gap=3, shape='circle', creation=0, z=0)

   Grid of colored shapes for infographic-style visualizations.

   :param list data: List of ``(count, color)`` tuples.
   :param int cols: Number of columns.
   :param str shape: ``'circle'`` or ``'square'``.

----

SpeechBubble
------------

.. py:class:: SpeechBubble(text='', x=100, y=100, font_size=20, padding=14, width=None, height=None, corner_radius=10, box_fill='#1e1e2e', box_opacity=0.95, text_color='#fff', tail_direction='down', tail_width=20, tail_height=18, creation=0, z=0, **styling)

   Rounded rectangle with a triangular tail, useful for dialogue and
   annotations.

   :param str text: Bubble content.
   :param str tail_direction: ``'down'``, ``'up'``, ``'left'``, or ``'right'``.
   :param float tail_width: Width of the triangular tail.
   :param float tail_height: Height of the triangular tail.

----

Badge
-----

.. py:class:: Badge(text='Label', x=100, y=100, font_size=16, padding_x=14, padding_y=6, bg_color='#58C4DD', text_color='#000', creation=0, z=0, **styling)

   Pill-shaped label with fully rounded corners, similar to GitHub badges.

   :param str text: Badge text.
   :param str bg_color: Background fill color.

----

Divider
-------

.. py:class:: Divider(x=100, y=300, length=400, direction='horizontal', label=None, font_size=16, gap=12, creation=0, z=0, **styling)

   Horizontal or vertical line with an optional centered text label.
   When a label is provided, the line splits into two segments with the label
   in between.

   :param str direction: ``'horizontal'`` or ``'vertical'``.
   :param str label: Optional centered label text.

----

Checklist
---------

.. py:class:: Checklist(*items, x=100, y=100, font_size=24, spacing=1.6, box_size=None, check_color='#83C167', uncheck_color='#555', text_color='#fff', creation=0, z=0)

   List of items with checkbox indicators. Each item is either a plain
   string (unchecked) or a ``(text, checked)`` tuple.

   :param items: Strings or ``(text, bool)`` tuples.

   .. py:method:: check_item(index, start=0, end=0.3)

      Animate checking the item at *index*.

   .. py:method:: reveal_items(start=0, end=1, overlap=0.5)

      Cascade items into view sequentially.

   .. code-block:: python

      cl = Checklist('Buy groceries',
                     ('Walk the dog', True),
                     'Write docs')
      cl.check_item(0, start=1, end=1.5)

----

Stepper
-------

.. py:class:: Stepper(steps, x=100, y=300, spacing=150, radius=20, active=0, direction='horizontal', font_size=16, active_color='#58C4DD', inactive_color='#555', text_color='#fff', creation=0, z=0)

   Step indicator: numbered circles connected by lines, with active step
   highlighting. *steps* can be an ``int`` (auto-numbered) or a list of
   label strings.

   :param steps: Number of steps or list of label strings.
   :param int active: Initially active step index.
   :param str direction: ``'horizontal'`` or ``'vertical'``.

   .. py:method:: advance(from_step, to_step, start=0, end=0.5)

      Animate transitioning the active highlight from one step to another.

----

TagCloud
--------

.. py:class:: TagCloud(data, x=100, y=100, width=500, min_font=14, max_font=48, colors=None, creation=0, z=0)

   Word/tag cloud with font sizes proportional to weights.

   :param list data: List of ``(text, weight)`` tuples.
   :param float min_font: Minimum font size.
   :param float max_font: Maximum font size.

----

StatusIndicator
---------------

.. py:class:: StatusIndicator(label, status='online', x=100, y=100, font_size=18, dot_radius=6, gap=10, creation=0, z=0)

   Colored dot with a text label, like a service status indicator.

   :param str label: Indicator label.
   :param str status: One of ``'online'``, ``'offline'``, ``'warning'``, ``'pending'``,
      ``'ok'``, ``'error'``, ``'success'``, ``'fail'``, ``'warn'``, ``'unknown'``,
      or a raw hex color string.

----

Meter
-----

.. py:class:: Meter(value=0.5, x=100, y=100, width=30, height=150, direction='vertical', fill_color='#58C4DD', bg_color='#333', border_color='#888', creation=0, z=0)

   Vertical or horizontal bar meter (battery level, VU meter, etc.).

   :param float value: Initial fill level (0--1).
   :param str direction: ``'vertical'`` or ``'horizontal'``.

----

Breadcrumb
----------

.. py:class:: Breadcrumb(*items, x=100, y=100, font_size=18, separator='\u203a', gap=8, active_index=None, active_color='#58C4DD', inactive_color='#888', creation=0, z=0)

   Navigation breadcrumb trail (e.g. Home > Products > Details).

   :param items: Breadcrumb label strings.
   :param int active_index: Highlighted item (defaults to the last item).
   :param str separator: Character between items.

----

Countdown
---------

.. py:class:: Countdown(start_value=10, end_value=0, x=960, y=540, font_size=120, start=0, end=3, creation=0, z=0, **styling)

   Animated countdown timer that updates the displayed number each frame.

   :param int start_value: Starting number.
   :param int end_value: Ending number.
   :param float start: Animation start time.
   :param float end: Animation end time.

----

Filmstrip
---------

.. py:class:: Filmstrip(labels, x=100, y=400, frame_width=200, frame_height=130, spacing=20, font_size=16, creation=0, z=0, **styling)

   Horizontal row of labeled thumbnail boxes, like a storyboard.

   :param list labels: Label for each frame.
   :param float frame_width: Width of each frame rectangle.
   :param float spacing: Horizontal gap between frames.

   .. py:method:: highlight_frame(index, start=0, end=1, color='#58C4DD', easing=there_and_back)

      Flash-highlight a frame by index.

----

RoundedCornerPolygon
--------------------

.. py:class:: RoundedCornerPolygon(*vertices, radius=20, creation=0, z=0, **styling)

   Bases: :py:class:`VObject`

   Polygon with rounded (filleted) corners. Each corner is replaced by a
   circular arc of the given *radius*.

   :param vertices: ``(x, y)`` tuples for each vertex.
   :param float radius: Corner rounding radius (clamped to half the shortest edge).
