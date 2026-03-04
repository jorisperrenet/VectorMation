Text & LaTeX
============

All text classes inherit from :doc:`VObject <vobject>` and share its full set
of animation methods (movement, styling, effects, etc.).

Text
----

.. admonition:: Text
   :class: example

   .. raw:: html

      <img src="../_static/videos/ref_text.svg" style="width:100%;max-width:800px;display:block;margin:auto;" />

   .. literalinclude:: ../../../examples/reference/ref_text.py
      :language: python

.. py:class:: Text(text='', x=960, y=540, font_size=48, text_anchor=None, font_family=None, **styling)
   :no-index:

   Plain SVG ``<text>`` element. Default fill is white (``#fff``) with no
   stroke.

   :param str text: Text content.
   :param float x: X position.
   :param float y: Y position (baseline).
   :param float font_size: Font size in pixels (default ``48``).
   :param str text_anchor: SVG ``text-anchor`` -- ``'start'``, ``'middle'``, or ``'end'``.
   :param str font_family: CSS font family name.

   .. py:attribute:: text
      :no-index:
      :type: String

      Text content (time-varying).

   .. py:attribute:: x
      :type: Real

   .. py:attribute:: y
      :type: Real

   .. py:attribute:: font_size
      :no-index:
      :type: Real

   .. rubric:: Querying

   .. py:method:: get_text(time=0)
      :no-index:

      Return the text string at the given time.

   .. py:method:: char_count(time=0)

      Return the number of characters.

   .. py:method:: word_count(time=0)

      Return the number of whitespace-separated words.

   .. py:method:: word_at(index, time=0)

      Return the word at the given index.

   .. py:method:: char_at(index, time=0)

      Return the character at the given index.

   .. py:method:: starts_with(prefix, time=0)
      :no-index:

      Return ``True`` if the text starts with *prefix*.

   .. py:method:: ends_with(suffix, time=0)
      :no-index:

      Return ``True`` if the text ends with *suffix*.

   .. rubric:: Styling

   .. py:method:: bold(weight='bold')

      Set the font weight to bold. Returns *self* for chaining.

   .. py:method:: italic(style='italic')

      Set the font style to italic. Returns *self* for chaining.

   .. py:method:: set_font_family(family, start=0)

      Set the CSS font family. Returns *self*.

   .. py:method:: set_font_size(size, start=0, end=None, easing=smooth)

      Animate font size to a new value over ``[start, end]``.

   .. rubric:: Text Manipulation

   .. py:method:: update_text(new_text, start=0)

      Instantly change the displayed text from *start* onward (no animation).

   .. py:method:: to_upper(time=0)

      Change the text to uppercase at the given time.

   .. py:method:: to_lower(time=0)

      Change the text to lowercase at the given time.

   .. py:method:: reverse_text(time=0)

      Reverse the text content in-place at the given time.

   .. py:method:: truncate(n, ellipsis='...', time=0)

      Truncate the text to at most *n* characters, appending *ellipsis* if
      trimmed.

   .. py:method:: fit_to_box(max_width, max_height=None, time=0)

      Adjust ``font_size`` so the text fits within the given pixel dimensions.

   .. rubric:: Splitting

   .. py:method:: split_words(time=0)

      Split text into a :py:class:`VCollection` of individual word
      :py:class:`Text` objects, positioned to match the original layout.

   .. py:method:: split_chars(time=0)

      Split text into a :py:class:`VCollection` of individual character
      :py:class:`Text` objects (spaces are excluded).

   .. py:method:: split_lines(time=0, line_spacing=1.4)

      Split multi-line text (containing newline characters) into separate
      :py:class:`Text` objects.

   .. py:method:: split_into_words(time=0, **kwargs)

      Like :py:meth:`split_words` but accounts for ``text_anchor`` when
      positioning. Extra keyword arguments are forwarded to each child
      :py:class:`Text`.

   .. py:method:: wrap(max_width, time=0)

      Word-wrap the text to fit within *max_width* pixels. Returns a
      :py:class:`VCollection` of line :py:class:`Text` objects.

   .. rubric:: Background

   .. py:method:: add_background_rectangle(color='#000000', opacity=0.5, padding=10, time=0)

      Create a semi-transparent :py:class:`Rectangle` behind the text. Returns
      a :py:class:`VCollection` containing the rectangle and the text.

   .. rubric:: Text Animations

   .. py:method:: typing(start=0, end=1, change_existence=True)
      :no-index:

      Typewriter effect: reveal characters one by one over ``[start, end]``.

      :param float start: Animation start time.
      :param float end: Animation end time.
      :param bool change_existence: If ``True``, the object appears at *start*.

   .. py:method:: typewrite(start=0, end=1, cursor='|', change_existence=True)
      :no-index:

      Reveal text character by character with a blinking cursor. Similar to
      :py:meth:`typing` but appends a *cursor* character (e.g. ``'|'``) after
      the revealed portion. The cursor is removed once all characters are shown.

      :param str cursor: Cursor character displayed during reveal.

   .. py:method:: untype(start=0, end=1, change_existence=True)
      :no-index:

      Reverse typewriter: remove characters right-to-left over
      ``[start, end]``. Text becomes empty at the end. If
      *change_existence* is ``True``, the object is hidden after completion.

   .. py:method:: reveal_by_word(start=0, end=1, change_existence=True, easing=None)
      :no-index:

      Reveal text word by word over ``[start, end]``. Words appear in order,
      separated by spaces. ``word_by_word`` is an alias.

      :param easing: Easing function for word timing (default: ``linear``).

   .. py:method:: scramble(start=0, end=1, charset=None, change_existence=True)
      :no-index:

      Decode/reveal effect: characters settle left-to-right from random
      characters to the final text. Un-settled positions cycle through random
      characters from *charset* (defaults to alphanumeric + symbols). Uses a
      deterministic seed for reproducibility.

      :param str charset: Character set for scrambled characters.

   .. admonition:: Example: Typewrite
      :class: example

      .. raw:: html

         <video src="../_static/videos/typewrite.mp4" controls autoplay loop muted></video>

      Typewriter effect with blinking cursor.

      .. literalinclude:: ../../../examples/reference/typewrite.py
         :language: python

   .. py:method:: set_text(start, end, new_text, easing=smooth)
      :no-index:

      Cross-fade to *new_text*: opacity drops to 0 at the midpoint, the text
      content changes, then opacity returns to 1.

      :param str new_text: The replacement text.

   .. py:method:: highlight(start=0, end=1, color='#FFFF00', opacity=0.3, padding=4, easing=there_and_back)
      :no-index:

      Highlight the text with a colored background rectangle that fades in and
      out. Returns the highlight :py:class:`Rectangle` (must be added to the
      canvas separately).

      :param str color: Highlight fill color.
      :param float opacity: Peak fill opacity.
      :param float padding: Padding around the text bounding box.

   .. py:method:: highlight_substring(substring, color='#FFFF00', start=0, end=1, opacity=0.3, easing=there_and_back)
      :no-index:

      Highlight a specific substring within the text. The highlight rectangle
      is positioned over the approximate location of *substring*. Returns the
      highlight :py:class:`Rectangle` (must be added to the canvas separately).

      :param str substring: The substring to highlight.


----

CountAnimation
--------------

.. py:class:: CountAnimation(start_val=0, end_val=100, start=0, end=1, fmt='{:.0f}', easing=smooth, x=960, y=540, font_size=60, **styling)
   :no-index:

   Bases: :py:class:`Text`

   Animated number counter that displays a number transitioning from
   *start_val* to *end_val* over ``[start, end]``.

   :param float start_val: Starting number.
   :param float end_val: Ending number.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param str fmt: Format string (e.g. ``'{:.2f}'`` for two decimal places).
   :param easing: Easing function for the count progression.

   .. py:method:: count_to(target, start, end, easing=smooth)

      Animate counting from the current value to a new *target*. Can be
      chained for multi-step counting sequences.

      :param float target: Target number.
      :param float start: Animation start time.
      :param float end: Animation end time.

   .. admonition:: Example: Counting animations
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_count_anim.mp4" controls autoplay loop muted></video>

      .. literalinclude:: ../../../examples/reference/ref_count_anim.py
         :language: python

----

DecimalNumber
-------------

.. py:class:: DecimalNumber(value=0, fmt='{:.2f}', x=960, y=540, font_size=48, **styling)
   :no-index:

   Bases: :py:class:`Text`

   Text that dynamically displays a numeric value, updating each frame.
   Can track a :py:class:`Real` attribute or a :py:class:`ValueTracker` so the
   displayed number follows an animated value automatically.

   :param value: Initial value, or a :py:class:`Real` / :py:class:`ValueTracker` to track.
   :param str fmt: Format string for display (default ``'{:.2f}'``).

   .. py:attribute:: tracker
      :no-index:
      :type: Real

      The underlying tracked value.

   .. py:method:: set_value(val, start=0)

      Set the tracked value from *start* onward.

   .. py:method:: animate_value(target, start, end, easing=smooth)

      Animate the tracked value to *target* over ``[start, end]``.

   .. admonition:: Example: Tracking a ValueTracker
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_value_tracker.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_value_tracker.py
         :language: python

----

Integer
-------

.. py:class:: Integer(value=0, x=960, y=540, font_size=48, **styling)
   :no-index:

   Bases: :py:class:`DecimalNumber`

   :py:class:`DecimalNumber` pre-configured with ``fmt='{:.0f}'`` to display
   whole numbers only.

   :param value: Initial value, or a :py:class:`Real` / :py:class:`ValueTracker` to track.

   .. admonition:: Example: Animated integer display
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_animated_integer.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_animated_integer.py
         :language: python

----

TexObject
---------

.. py:class:: TexObject(to_render, x=0, y=0, font_size=48, **styles)

   Bases: :py:class:`VCollection`

   Renders a LaTeX string as SVG paths via ``dvisvgm``. Requires ``latex``
   and ``dvisvgm`` on the system. Paths are auto-scaled so the rendered
   height matches ``font_size`` in pixels.

   :param str to_render: LaTeX source (e.g. ``r'$$E = mc^2$$'``).
   :param float x: X offset.
   :param float y: Y offset.
   :param float font_size: Target height in pixels (default ``48``).

   The result is a :py:class:`VCollection` of :py:class:`Path` objects, one
   per glyph. All :py:class:`VCollection` and :py:class:`VObject` methods
   work on it.

   ``scale_x`` / ``scale_y`` in *styles* act as multipliers on the
   font-size-derived scale.

   .. rubric:: Text-to-Color Mapping

   .. py:attribute:: t2c

      Pass a ``t2c`` dictionary in the constructor to color specific parts of
      the LaTeX expression. Keys are TeX substrings, values are fill colors.
      This calls :py:meth:`set_color_by_tex` automatically.

   .. rubric:: Part Selection

   .. py:method:: get_part_by_tex(substring)

      Return a :py:class:`VCollection` of glyph :py:class:`Path` objects
      whose source LaTeX matches *substring*. LaTeX commands are stripped from
      both the full TeX string and the query before matching.

      Returns an empty :py:class:`VCollection` when no match is found.

      :param str substring: TeX substring to find.

   .. py:method:: set_color_by_tex(tex_to_color_map, start=0)

      Color glyph objects by matching TeX substrings. For each key in
      *tex_to_color_map*, calls :py:meth:`get_part_by_tex` and sets the fill
      color of the matched glyphs to the corresponding value. Returns *self*.

      :param dict tex_to_color_map: ``{tex_substring: color}`` mapping.

   .. admonition:: Example: TexObject
      :class: example

      .. raw:: html

         <video src="../_static/videos/tex.mp4" controls autoplay loop muted></video>

      TeX formula with colored parts via ``t2c``.

      .. literalinclude:: ../../../examples/reference/tex.py
         :language: python

----

SplitTexObject
--------------

.. py:class:: SplitTexObject(*lines, x=0, y=0, line_spacing=60, **styles)

   Renders multiple LaTeX lines, each as a separate :py:class:`TexObject`.
   Supports indexing (``split[i]``), iteration, and ``len()``.

   :param lines: LaTeX strings, one per line.
   :param float x: X offset for all lines.
   :param float y: Y offset for the first line.
   :param float line_spacing: Vertical distance between lines (default ``60``).

   Each line is a full :py:class:`TexObject` and can be animated
   independently.

   .. admonition:: Example: Multi-line LaTeX derivation
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_multiline_latex.svg" style="width:100%;max-width:800px;display:block;margin:auto;" />

      .. literalinclude:: ../../../examples/reference/ref_multiline_latex.py
         :language: python

----

TexCountAnimation
-----------------

.. py:class:: TexCountAnimation(start_val=0, end_val=100, start=0, end=1, fmt='{:.0f}', easing=smooth, x=960, y=540, font_size=48, **styles)

   Bases: :py:class:`DynamicObject`

   Animated number display using pre-rendered LaTeX digit glyphs. Unlike
   :py:class:`CountAnimation` (which uses plain SVG text),
   ``TexCountAnimation`` renders each digit as a LaTeX glyph path, giving a
   typographically consistent look that matches :py:class:`TexObject` output.

   Digit glyphs are cached at the class level, so creating multiple
   ``TexCountAnimation`` instances is efficient.

   :param float start_val: Starting number.
   :param float end_val: Ending number.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param str fmt: Format string (e.g. ``'{:.2f}'``).
   :param easing: Easing function for the count progression.

   .. py:method:: count_to(target, start, end, easing=smooth)

      Animate counting from the current value to a new *target*. Can be
      chained for multi-step counting sequences.

   .. admonition:: Example: LaTeX-styled counter
      :class: example

      .. raw:: html

         <video src="../_static/videos/ref_tex_counter.mp4" controls autoplay loop muted style="width:100%;max-width:800px;display:block;margin:auto;"></video>

      .. literalinclude:: ../../../examples/reference/ref_tex_counter.py
         :language: python

----

Paragraph
---------

.. py:class:: Paragraph(*lines, x=960, y=540, font_size=36, alignment='left', line_spacing=1.4, **styling)
   :no-index:

   Multi-line text with alignment and line spacing. Each line is rendered as
   a separate SVG ``<text>`` element.

   :param lines: Text strings, one per line.
   :param str alignment: ``'left'``, ``'center'``, or ``'right'``.
   :param float line_spacing: Multiplier for vertical spacing between lines (default ``1.4``).
   :param float font_size: Font size in pixels.

   .. py:attribute:: lines

      List of line strings (alias for ``items``).

   .. admonition:: Example: Paragraph
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_paragraph.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_paragraph.py
         :language: python

----

BulletedList
------------

.. py:class:: BulletedList(*items, x=200, y=200, font_size=36, bullet='\u2022', indent=40, line_spacing=1.6, **styling)
   :no-index:

   List of items with bullet points.

   :param items: Text strings.
   :param str bullet: Bullet character (default ``'\u2022'``).
   :param float indent: Pixel indentation for each item (default ``40``).
   :param float line_spacing: Multiplier for vertical spacing (default ``1.6``).

   .. admonition:: Example: BulletedList
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_bulleted_list.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_bulleted_list.py
         :language: python

----

NumberedList
------------

.. py:class:: NumberedList(*items, x=200, y=200, font_size=36, indent=50, line_spacing=1.6, start_number=1, **styling)
   :no-index:

   List of items with numeric labels (1. 2. 3. ...).

   :param items: Text strings.
   :param float indent: Pixel indentation after the number (default ``50``).
   :param float line_spacing: Multiplier for vertical spacing (default ``1.6``).
   :param int start_number: First number in the sequence (default ``1``).

   .. admonition:: Example: NumberedList
      :class: example

      .. raw:: html

         <img src="../_static/videos/ref_numbered_list.svg" style="width:100%; max-width:800px;" />

      .. literalinclude:: ../../../examples/reference/ref_numbered_list.py
         :language: python

