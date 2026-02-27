Text & LaTeX
============

Text
----

.. py:class:: Text(text='', x=960, y=540, font_size=48, text_anchor=None, font_family=None, **styling)

   Plain SVG ``<text>`` element.

   :param str text: Text content.
   :param float x: X position.
   :param float y: Y position (baseline).
   :param float font_size: Font size in pixels.
   :param str text_anchor: SVG ``text-anchor`` (``'start'``, ``'middle'``, ``'end'``).

   .. py:attribute:: text
      :type: String

      Text content (time-varying).

   .. py:attribute:: x
      :type: Real

   .. py:attribute:: y
      :type: Real

   .. py:attribute:: font_size
      :type: Real

   .. py:method:: typing(start=0, end=1, change_existence=True)

      Typewriter effect: reveal characters one by one over ``[start, end]``.

   .. py:method:: set_text(start, end, new_text, easing=smooth)

      Cross-fade to *new_text*: opacity drops to 0, text changes, opacity returns.

----

CountAnimation
--------------

.. py:class:: CountAnimation(start_val=0, end_val=100, start=0, end=1, fmt='{:.0f}', easing=smooth, x=960, y=540, font_size=60, **styling)

   Bases: :py:class:`Text`

   Animated number counter from *start_val* to *end_val*.

   :param float start_val: Starting number.
   :param float end_val: Ending number.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param str fmt: Format string (e.g. ``'{:.2f}'``).

----

TexObject
---------

.. py:class:: TexObject(to_render, x=0, y=0, font_size=30, **styles)

   Bases: :py:class:`VCollection`

   Renders a LaTeX string as SVG paths. Requires ``latex`` and ``dvisvgm``
   on the system. Paths are auto-scaled so the rendered height matches
   ``font_size`` in pixels.

   :param str to_render: LaTeX source (e.g. ``r'$$E = mc^2$$'``).
   :param float x: X offset.
   :param float y: Y offset.
   :param float font_size: Target height in pixels (default 30).

   The result is a :py:class:`VCollection` of :py:class:`Path` objects, one
   per glyph. All VCollection and VObject methods work on it.

   ``scale_x`` / ``scale_y`` in styles act as multipliers on the
   font-size-derived scale.

   .. code-block:: python

      formula = TexObject(r'$$\sum_{n=1}^{\infty} \frac{1}{n^2}$$',
                          font_size=60)
      formula.write(0, 1.5)   # handwriting reveal
      formula.center_to_pos()  # centre on canvas

----

SplitTexObject
--------------

.. py:class:: SplitTexObject(*lines, x=0, y=0, line_spacing=60, **styles)

   Renders multiple LaTeX lines, each as a separate :py:class:`TexObject`.
   Supports indexing (``split[i]``), iteration, and ``len()``.

   :param lines: LaTeX strings, one per line.
   :param float line_spacing: Vertical distance between lines.
