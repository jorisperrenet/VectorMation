Text & LaTeX
============

All text classes inherit from :doc:`VObject <vobject>` and share its full set
of animation methods (movement, styling, effects, etc.).

Text
----

.. py:class:: Text(text='', x=960, y=540, font_size=48, text_anchor=None, font_family=None, **styling)

   Plain SVG ``<text>`` element. Default fill is white (``#fff``) with no
   stroke.

   :param str text: Text content.
   :param float x: X position.
   :param float y: Y position (baseline).
   :param float font_size: Font size in pixels (default ``48``).
   :param str text_anchor: SVG ``text-anchor`` -- ``'start'``, ``'middle'``, or ``'end'``.
   :param str font_family: CSS font family name.

   .. py:attribute:: text
      :type: String

      Text content (time-varying).

   .. py:attribute:: x
      :type: Real

   .. py:attribute:: y
      :type: Real

   .. py:attribute:: font_size
      :type: Real

   .. rubric:: Querying

   .. py:method:: get_text(time=0)

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

      Return ``True`` if the text starts with *prefix*.

   .. py:method:: ends_with(suffix, time=0)

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

      Typewriter effect: reveal characters one by one over ``[start, end]``.

      :param float start: Animation start time.
      :param float end: Animation end time.
      :param bool change_existence: If ``True``, the object appears at *start*.

   .. py:method:: typewrite(start=0, end=1, cursor='|', change_existence=True)

      Reveal text character by character with a blinking cursor. Similar to
      :py:meth:`typing` but appends a *cursor* character (e.g. ``'|'``) after
      the revealed portion. The cursor is removed once all characters are shown.

      :param str cursor: Cursor character displayed during reveal.

   .. py:method:: untype(start=0, end=1, change_existence=True)

      Reverse typewriter: remove characters right-to-left over
      ``[start, end]``. Text becomes empty at the end. If
      *change_existence* is ``True``, the object is hidden after completion.

   .. py:method:: reveal_by_word(start=0, end=1, change_existence=True, easing=None)

      Reveal text word by word over ``[start, end]``. Words appear in order,
      separated by spaces. ``word_by_word`` is an alias.

      :param easing: Easing function for word timing (default: ``linear``).

   .. py:method:: scramble(start=0, end=1, charset=None, change_existence=True)

      Decode/reveal effect: characters settle left-to-right from random
      characters to the final text. Un-settled positions cycle through random
      characters from *charset* (defaults to alphanumeric + symbols). Uses a
      deterministic seed for reproducibility.

      :param str charset: Character set for scrambled characters.

   .. py:method:: set_text(start, end, new_text, easing=smooth)

      Cross-fade to *new_text*: opacity drops to 0 at the midpoint, the text
      content changes, then opacity returns to 1.

      :param str new_text: The replacement text.

   .. py:method:: highlight(start=0, end=1, color='#FFFF00', opacity=0.3, padding=4, easing=there_and_back)

      Highlight the text with a colored background rectangle that fades in and
      out. Returns the highlight :py:class:`Rectangle` (must be added to the
      canvas separately).

      :param str color: Highlight fill color.
      :param float opacity: Peak fill opacity.
      :param float padding: Padding around the text bounding box.

   .. py:method:: highlight_substring(substring, color='#FFFF00', start=0, end=1, opacity=0.3, easing=there_and_back)

      Highlight a specific substring within the text. The highlight rectangle
      is positioned over the approximate location of *substring*. Returns the
      highlight :py:class:`Rectangle` (must be added to the canvas separately).

      :param str substring: The substring to highlight.

   .. rubric:: Examples

   .. code-block:: python

      from vectormation.objects import *

      v = VectorMathAnim()

      # Basic text with typewriter reveal
      title = Text('Hello, World!', font_size=72, text_anchor='middle')
      title.center_to_pos()
      title.typing(0, 1.5)
      v.add(title)

      # Word-by-word reveal
      msg = Text('This appears word by word', y=640, text_anchor='middle')
      msg.center_to_pos()
      msg.reveal_by_word(1.5, 3)
      v.add(msg)

      # Cross-fade text change
      label = Text('Before', font_size=60, text_anchor='middle')
      label.center_to_pos()
      label.fadein(0, 0.5)
      label.set_text(2, 3, 'After')
      v.add(label)

   .. code-block:: python

      # Scramble decode effect
      code = Text('ACCESS GRANTED', font_size=48, fill='#0f0')
      code.center_to_pos()
      code.scramble(0, 2)
      v.add(code)

      # Typewriter with cursor
      terminal = Text('$ pip install vectormation', x=100, y=300,
                       font_size=32, font_family='monospace')
      terminal.typewrite(0, 2, cursor='_')
      v.add(terminal)

      # Highlight a substring
      sentence = Text('The quick brown fox', font_size=48)
      sentence.center_to_pos()
      sentence.fadein(0, 0.5)
      highlight_rect = sentence.highlight_substring('quick', start=1, end=3)
      v.add(sentence, highlight_rect)

----

CountAnimation
--------------

.. py:class:: CountAnimation(start_val=0, end_val=100, start=0, end=1, fmt='{:.0f}', easing=smooth, x=960, y=540, font_size=60, **styling)

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

   .. code-block:: python

      # Count from 0 to 100 over the first two seconds
      counter = CountAnimation(0, 100, start=0, end=2, fmt='{:.0f}')
      counter.center_to_pos()
      v.add(counter)

      # Chain: count 0 -> 50, then 50 -> 200
      counter = CountAnimation(0, 50, start=0, end=1)
      counter.count_to(200, start=1.5, end=3)
      counter.center_to_pos()
      v.add(counter)

----

DecimalNumber
-------------

.. py:class:: DecimalNumber(value=0, fmt='{:.2f}', x=960, y=540, font_size=48, **styling)

   Bases: :py:class:`Text`

   Text that dynamically displays a numeric value, updating each frame.
   Can track a :py:class:`Real` attribute or a :py:class:`ValueTracker` so the
   displayed number follows an animated value automatically.

   :param value: Initial value, or a :py:class:`Real` / :py:class:`ValueTracker` to track.
   :param str fmt: Format string for display (default ``'{:.2f}'``).

   .. py:attribute:: tracker
      :type: Real

      The underlying tracked value.

   .. py:method:: set_value(val, start=0)

      Set the tracked value from *start* onward.

   .. py:method:: animate_value(target, start, end, easing=smooth)

      Animate the tracked value to *target* over ``[start, end]``.

   .. code-block:: python

      # DecimalNumber tracking a ValueTracker
      vt = ValueTracker(0)
      vt.animate_value(3.14159, start=0, end=2)
      label = DecimalNumber(vt, fmt='{:.4f}', font_size=60)
      label.center_to_pos()
      v.add(label)

      # Standalone DecimalNumber
      dn = DecimalNumber(0, fmt='{:.1f}')
      dn.center_to_pos()
      dn.animate_value(99.9, start=0, end=3)
      v.add(dn)

----

Integer
-------

.. py:class:: Integer(value=0, x=960, y=540, font_size=48, **styling)

   Bases: :py:class:`DecimalNumber`

   :py:class:`DecimalNumber` pre-configured with ``fmt='{:.0f}'`` to display
   whole numbers only.

   :param value: Initial value, or a :py:class:`Real` / :py:class:`ValueTracker` to track.

   .. code-block:: python

      n = Integer(0)
      n.center_to_pos()
      n.animate_value(42, start=0, end=2)
      v.add(n)

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

   .. rubric:: Examples

   .. code-block:: python

      # Basic formula with handwriting reveal
      formula = TexObject(r'$$\sum_{n=1}^{\infty} \frac{1}{n^2}$$',
                          font_size=60)
      formula.center_to_pos()
      formula.write(0, 1.5)
      v.add(formula)

   .. code-block:: python

      # Color specific parts using t2c in the constructor
      eq = TexObject(r'$$E = mc^2$$', font_size=80,
                     t2c={'E': '#FF6666', 'm': '#66FF66', 'c': '#6666FF'})
      eq.center_to_pos()
      eq.fadein(0, 1)
      v.add(eq)

   .. code-block:: python

      # Color parts after construction
      integral = TexObject(r'$$\int_0^1 x^2 \, dx$$', font_size=60)
      integral.center_to_pos()

      # Highlight the integrand
      integrand = integral.get_part_by_tex('x')
      integrand.set_color('#FFCC00', start=0)

      integral.write(0, 2)
      v.add(integral)

   .. code-block:: python

      # Animate individual glyphs
      tex = TexObject(r'$$a^2 + b^2 = c^2$$', font_size=60)
      tex.center_to_pos()
      tex.stagger('fadein', delay=0.1)  # each glyph fades in sequentially
      v.add(tex)

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

   .. code-block:: python

      equations = SplitTexObject(
          r'$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$',
          r'$$\Delta = b^2 - 4ac$$',
          line_spacing=80, font_size=48,
      )
      for i, line in enumerate(equations):
          line.center_to_pos()
          line.shift(0, 0, 0, i * 80 - 40)
          line.write(i * 0.8, i * 0.8 + 1.5)
          v.add(line)

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

   .. code-block:: python

      # LaTeX-styled counter
      counter = TexCountAnimation(0, 100, start=0, end=3, font_size=72)
      counter.center_to_pos()
      v.add(counter)

----

Paragraph
---------

.. py:class:: Paragraph(*lines, x=960, y=540, font_size=36, alignment='left', line_spacing=1.4, **styling)

   Multi-line text with alignment and line spacing. Each line is rendered as
   a separate SVG ``<text>`` element.

   :param lines: Text strings, one per line.
   :param str alignment: ``'left'``, ``'center'``, or ``'right'``.
   :param float line_spacing: Multiplier for vertical spacing between lines (default ``1.4``).
   :param float font_size: Font size in pixels.

   .. py:attribute:: lines

      List of line strings (alias for ``items``).

   .. code-block:: python

      p = Paragraph(
          'First line of text.',
          'Second line continues here.',
          'Third and final line.',
          alignment='center', font_size=40,
      )
      p.center_to_pos()
      p.fadein(0, 1)
      v.add(p)

----

BulletedList
------------

.. py:class:: BulletedList(*items, x=200, y=200, font_size=36, bullet='\u2022', indent=40, line_spacing=1.6, **styling)

   List of items with bullet points.

   :param items: Text strings.
   :param str bullet: Bullet character (default ``'\u2022'``).
   :param float indent: Pixel indentation for each item (default ``40``).
   :param float line_spacing: Multiplier for vertical spacing (default ``1.6``).

   .. code-block:: python

      bl = BulletedList(
          'Install dependencies',
          'Configure settings',
          'Run the application',
          font_size=36,
      )
      bl.fadein(0, 1)
      v.add(bl)

----

NumberedList
------------

.. py:class:: NumberedList(*items, x=200, y=200, font_size=36, indent=50, line_spacing=1.6, start_number=1, **styling)

   List of items with numeric labels (1. 2. 3. ...).

   :param items: Text strings.
   :param float indent: Pixel indentation after the number (default ``50``).
   :param float line_spacing: Multiplier for vertical spacing (default ``1.6``).
   :param int start_number: First number in the sequence (default ``1``).

   .. code-block:: python

      nl = NumberedList(
          'Define the problem',
          'Gather data',
          'Build a model',
          'Evaluate results',
          font_size=36,
      )
      nl.fadein(0, 1)
      v.add(nl)

----

Common Patterns
---------------

.. rubric:: Animated Label Following a Graph Point

.. code-block:: python

   from vectormation.objects import *

   v = VectorMathAnim()

   axes = Axes(x_range=(-2, 5), y_range=(-1, 10))
   f = lambda x: x ** 2
   curve = axes.plot(f, stroke='#58C4DD')

   # Dot that moves along the curve
   dot = Dot()
   x_val = ValueTracker(0)
   x_val.animate_value(4, start=0, end=3)
   dot.c.set_onward(0, axes.graph_position(f, x_val.value))

   # Label that shows the current y-value
   label = DecimalNumber(x_val, fmt='y = {:.1f}', font_size=32)
   label.add_updater(lambda obj, t: obj.next_to(dot, 'up', buff=20, time=t))

   v.add(axes, curve, dot, label)

.. rubric:: Equation Derivation with SplitTexObject

.. code-block:: python

   steps = SplitTexObject(
       r'$$F = ma$$',
       r'$$a = \frac{F}{m}$$',
       r'$$a = \frac{10}{2} = 5 \; \text{m/s}^2$$',
       line_spacing=80, font_size=48,
   )

   for i, eq in enumerate(steps):
       eq.center_to_pos()
       eq.shift(0, 0, 0, (i - 1) * 80)
       eq.write(i, i + 1.2)
       v.add(eq)

.. rubric:: Typewriter Terminal Effect

.. code-block:: python

   lines = [
       '$ python train.py --epochs 100',
       'Loading dataset...',
       'Epoch 1/100: loss=2.341',
       'Epoch 100/100: loss=0.023',
       'Training complete.',
   ]

   y_pos = 200
   for i, line in enumerate(lines):
       t = Text(line, x=100, y=y_pos + i * 50, font_size=28,
                font_family='monospace', fill='#0f0')
       t.typewrite(start=i * 0.8, end=i * 0.8 + 0.6, cursor='_')
       v.add(t)
