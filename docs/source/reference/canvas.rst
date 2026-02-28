VectorMathAnim
==============

The canvas is the top-level object that manages all visual objects, camera
controls, frame generation, and export. Every VectorMation script creates
exactly one ``VectorMathAnim`` instance.

----

Constructor
-----------

.. py:class:: VectorMathAnim(save_dir, width=1920, height=1080, scale=1, verbose=False)

   Create a new canvas with a given save directory and viewport size.

   :param str save_dir: Directory where SVG frames are saved. Created
      automatically if it does not exist.
   :param int width: ViewBox width in pixels (default ``1920``).
   :param int height: ViewBox height in pixels (default ``1080``).
   :param int scale: Pixel scale factor applied to the output ``<svg>``
      element. ``1`` gives native resolution; ``2`` doubles it.
   :param bool verbose: When ``True``, enable ``DEBUG``-level logging.

   The canvas creates a default viewBox of ``0 0 width height`` and
   maintains an internal clock (``canvas.time``) used by
   :py:meth:`generate_frame_svg` when no explicit time is given.

   .. py:attribute:: duration
      :type: float

      Read-only property. Returns the total animation duration in seconds,
      auto-detected from the latest animation end time across all registered
      objects and camera keyframes.

   .. py:attribute:: viewbox
      :type: tuple

      The current ``(x, y, width, height)`` viewBox. Readable and writable.
      Writing sets all four viewBox attributes from the current canvas time
      onward.

   .. code-block:: python

      from vectormation.objects import *

      canvas = VectorMathAnim(save_dir='svgs/my_animation', verbose=True)

----

Scene Setup
-----------

.. py:method:: VectorMathAnim.set_background(creation=0, z=-1, grid=False, grid_spacing=60, grid_color='#333', **styling)

   Add a full-canvas background rectangle. Optional grid lines can be
   overlaid for alignment or debugging.

   :param float creation: Time at which the background appears.
   :param int z: Z-order (default ``-1``, behind everything).
   :param bool grid: Draw grid lines over the background.
   :param float grid_spacing: Distance (pixels) between grid lines.
   :param str grid_color: Grid line colour.
   :param styling: Any additional SVG styling (``fill``, ``fill_opacity``, etc.).
      When no fill is given the Styling defaults apply.
   :returns: ``self`` (for chaining).

   Calling ``set_background`` again replaces the previous background.

   .. code-block:: python

      canvas.set_background(fill='#1a1a2e')
      canvas.set_background(fill='#0d1b2a', grid=True, grid_spacing=135)

----

Adding and Removing Objects
---------------------------

.. py:method:: VectorMathAnim.add_objects(*args)

   Register one or more objects for rendering. Objects are drawn each frame
   sorted by z-order.

   :param args: VObject or VCollection instances.
   :returns: ``self`` (for chaining).

   ``add`` is an alias for ``add_objects``.

   .. code-block:: python

      circle = Circle(r=80, fill='#58C4DD')
      label  = Text(text='Hello', x=960, y=540)
      canvas.add_objects(circle, label)
      # or equivalently:
      canvas.add(circle, label)

.. py:method:: VectorMathAnim.remove(*args)

   Remove objects from the canvas so they are no longer rendered.

   :param args: Objects previously added via :py:meth:`add_objects`.
   :returns: ``self`` (for chaining).

.. py:method:: VectorMathAnim.clear()

   Remove all objects from the canvas except the background and defs.
   Useful for multi-scene scripts that rebuild the scene between segments.

   :returns: ``self`` (for chaining).

.. py:method:: VectorMathAnim.add_def(def_obj)

   Register a gradient, clip path, or filter for the ``<defs>`` block.
   The object must have an ``id`` attribute and a ``to_svg_def(time)`` method.

   Aliases: ``add_gradient``, ``add_clip_path``.

   :returns: ``self`` (for chaining).

.. py:method:: VectorMathAnim.add_section(time)

   Add a section break at the given time. Sections allow pausing playback
   in the browser viewer (press ``N`` to jump to the next section). They are
   also used by :py:meth:`export_sections`.

   :param float time: Section boundary time in seconds.
   :returns: ``self`` (for chaining).

----

Frame Generation
----------------

.. py:method:: VectorMathAnim.generate_frame_svg(time=None)

   Return the complete SVG string for a single frame at the given time.

   :param float time: Timestamp to render. Defaults to ``canvas.time``.
   :returns: SVG string (including XML declaration and ``<svg>`` wrapper).
   :rtype: str

   This is the core rendering method. It:

   1. Evaluates the animated viewBox at *time*.
   2. Emits any ``<defs>`` (gradients, clip paths).
   3. Collects all objects whose ``show`` attribute is ``True`` at *time*.
   4. Sorts them by z-order.
   5. Runs updaters on each object.
   6. Calls ``to_svg(time)`` on each object and concatenates the result.
   7. Rounds floating-point numbers for compact output.

.. py:method:: VectorMathAnim.write_frame(time=None, filename=None)

   Write an SVG frame to disk.

   :param float time: Timestamp (defaults to ``canvas.time``).
   :param str filename: Output path. Defaults to ``<save_dir>/gen.svg``.

----

Camera Controls
---------------

All camera methods animate the SVG viewBox, which effectively pans and zooms
the visible region. They return ``self`` for chaining.

.. py:method:: VectorMathAnim.camera_shift(dx, dy, start, end, easing=smooth)

   Pan the camera by ``(dx, dy)`` pixels over ``[start, end]``.

   :param float dx: Horizontal shift in pixels.
   :param float dy: Vertical shift in pixels.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param easing: Easing function (default ``smooth``).

   .. code-block:: python

      # Slowly pan 400px to the right over 2 seconds
      canvas.camera_shift(400, 0, start=1, end=3)

.. py:method:: VectorMathAnim.camera_zoom(factor, start, end, cx=None, cy=None, easing=smooth)

   Zoom the camera by *factor* around the point ``(cx, cy)`` over
   ``[start, end]``. ``factor > 1`` zooms in; ``factor < 1`` zooms out.

   :param float factor: Zoom factor.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param float cx: Zoom centre x (default: canvas centre).
   :param float cy: Zoom centre y (default: canvas centre).
   :param easing: Easing function (default ``smooth``).

   .. code-block:: python

      # Zoom 2x into the upper-left quadrant
      canvas.camera_zoom(2, start=0, end=2, cx=480, cy=270)

.. py:method:: VectorMathAnim.camera_follow(obj, start, end=None)

   Make the camera continuously track an object, keeping it centred in the
   viewport. If *end* is given, the camera freezes at its position at that
   time.

   :param VObject obj: Object to follow.
   :param float start: When tracking begins.
   :param float end: When tracking ends (``None`` = track indefinitely).

   .. code-block:: python

      dot = Dot(cx=100, cy=540)
      dot.shift(dx=1600, start=0, end=5)
      canvas.camera_follow(dot, start=0, end=5)

.. py:method:: VectorMathAnim.camera_reset(start, end, easing=smooth)

   Reset the camera to the default full-canvas viewBox (``0 0 width height``)
   over ``[start, end]``.

   :param float start: Animation start time.
   :param float end: Animation end time.
   :param easing: Easing function (default ``smooth``).

.. py:method:: VectorMathAnim.focus_on(*objects, start, end, padding=100, easing=smooth)

   Pan and zoom the camera to tightly frame the given objects (with padding),
   maintaining the canvas aspect ratio.

   :param objects: One or more VObject/VCollection instances to frame.
   :param float start: Animation start time.
   :param float end: Animation end time.
   :param float padding: Extra padding (pixels) around the bounding box.
   :param easing: Easing function (default ``smooth``).

   .. code-block:: python

      canvas.focus_on(circle, label, start=1, end=2, padding=80)
      # ... inspect detail ...
      canvas.camera_reset(3, 4)

----

Display
-------

.. py:method:: VectorMathAnim.browser_display(start=0, end=None, fps=60, port=8765, hot_reload=False)

   Open a browser-based viewer with real-time playback over WebSocket.
   The viewer supports zoom (scroll wheel), playback speed control,
   keyboard shortcuts, and a timeline scrubber.

   :param float start: Playback start time. Negative values are relative to
      the end (e.g. ``-3`` starts 3 seconds before the end).
   :param float end: Playback end time. ``None`` auto-detects from the last
      animation. ``0`` displays a single static frame at *start* (no
      animation).
   :param int fps: Frames per second.
   :param int port: WebSocket server port.
   :param bool hot_reload: When ``True``, watches the calling script for
      file changes and automatically re-runs it, allowing a live development
      workflow.

   **Keyboard shortcuts in the browser viewer:**

   .. list-table::
      :widths: 20 50
      :header-rows: 1

      * - Key
        - Action
      * - ``Space``
        - Pause / resume playback
      * - ``R``
        - Restart from the beginning
      * - ``N``
        - Jump to next section break
      * - ``F``
        - Fit the view to the full canvas
      * - ``Q``
        - Quit the server
      * - ``Right``
        - Step forward one frame (while paused)
      * - ``Left``
        - Step backward one frame (while paused)

   **Single-picture mode:**

   Pass ``end=0`` to display a static frame without animation. This is
   useful for debugging layouts.

   .. code-block:: python

      # Static preview at t=0
      canvas.browser_display(start=0, end=0)

----

Export
------

.. py:method:: VectorMathAnim.export_png(time=0, filename='frame.png', scale=None)

   Export a single frame as a PNG image.

   :param float time: Timestamp to render.
   :param str filename: Output file path.
   :param int scale: Pixel scale factor. ``None`` uses the canvas ``scale``.

   Requires ``cairosvg`` (``pip install cairosvg``).

.. py:method:: VectorMathAnim.export_video(filename='animation.mp4', start=0, end=None, fps=60, scale=None)

   Export the animation as an MP4 video.

   :param str filename: Output file path.
   :param float start: Start time.
   :param float end: End time (``None`` = auto-detect).
   :param int fps: Frames per second.
   :param int scale: Pixel scale factor (``1`` = 1920x1080,
      ``2`` = 3840x2160).

   Requires ``cairosvg`` and ``ffmpeg``.

   .. code-block:: python

      canvas.export_video('output.mp4', fps=30, end=10)

.. py:method:: VectorMathAnim.export_gif(filename='animation.gif', start=0, end=None, fps=30, scale=None, loop=0)

   Export the animation as an animated GIF.

   :param str filename: Output file path.
   :param float start: Start time.
   :param float end: End time (``None`` = auto-detect).
   :param int fps: Frames per second.
   :param int scale: Pixel scale factor.
   :param int loop: Number of loops (``0`` = infinite).

   Requires ``cairosvg`` and ``Pillow``.

.. py:method:: VectorMathAnim.export_sections(prefix='section')

   Export each section boundary as a standalone SVG file. Files are written
   to the canvas save directory as ``<prefix>_000.svg``, ``<prefix>_001.svg``,
   etc.

   :param str prefix: Filename prefix.

----

Inspection
----------

.. py:method:: VectorMathAnim.get_all_objects()

   Return a list of all registered objects (excluding the background).

   :rtype: list[VObject]

.. py:method:: VectorMathAnim.find_by_type(cls)

   Return all objects matching a given class (including subclasses).

   :param type cls: The class to filter by (e.g. ``Circle``, ``Text``).
   :rtype: list[VObject]

.. py:method:: VectorMathAnim.find(predicate)

   Return all objects where ``predicate(obj)`` returns ``True``.

   :param callable predicate: Filter function.
   :rtype: list[VObject]

.. py:method:: VectorMathAnim.get_object_count(time=None)

   Return the number of visible objects at the given time (excludes
   the background).

   :param float time: Timestamp (default ``0``).
   :rtype: int

.. py:method:: VectorMathAnim.list_objects_by_type(time=None)

   Return a dict mapping class names to lists of visible objects of that
   type at the given time.

   :param float time: Timestamp (default ``0``).
   :rtype: dict[str, list[VObject]]

.. py:method:: VectorMathAnim.get_visible_objects_info(time=None)

   Return a list of dicts with ``'class'`` and ``'id'`` keys for each
   visible object at the given time.

   :param float time: Timestamp (defaults to canvas time).
   :rtype: list[dict]

.. py:method:: VectorMathAnim.get_snap_points(time=None)

   Extract snappable points (vertices, endpoints, centres) from all
   visible objects at the given time. Used internally by the browser
   viewer's snap-to-grid feature.

   :param float time: Timestamp (defaults to canvas time).
   :rtype: list[tuple]

----

CLI Utility
-----------

.. py:function:: parse_args()

   Parse common command-line arguments for VectorMation scripts. Returns
   an ``argparse.Namespace`` with the following fields:

   .. list-table::
      :widths: 20 15 15 50
      :header-rows: 1

      * - Flag
        - Type
        - Default
        - Description
      * - ``-v`` / ``--verbose``
        - bool
        - ``False``
        - Enable verbose (debug) logging
      * - ``--port``
        - int
        - ``8765``
        - Browser viewer WebSocket port
      * - ``--fps``
        - int
        - ``60``
        - Frames per second
      * - ``--no-display``
        - bool
        - ``False``
        - Skip browser display (useful for export-only runs)
      * - ``-o`` / ``--output``
        - str
        - ``None``
        - Output file path (e.g. ``out.mp4``, ``frame.png``)
      * - ``-d`` / ``--duration``
        - float
        - ``None``
        - Animation duration override (seconds)
      * - ``--start``
        - float
        - ``None``
        - Playback start time
      * - ``--end``
        - float
        - ``None``
        - Playback end time
      * - ``--hot-reload``
        - bool
        - ``False``
        - Re-run script on file change in browser viewer

   .. code-block:: python

      from vectormation.objects import *

      args = parse_args()
      canvas = VectorMathAnim(save_dir='svgs/demo', verbose=args.verbose)

   From the command line::

      python my_script.py -v --fps 30 --hot-reload
      python my_script.py --no-display -o animation.mp4

----

Workflow Examples
-----------------

Basic setup
~~~~~~~~~~~

A minimal script that creates a canvas, adds an object with an animation,
and opens the browser viewer.

.. code-block:: python

   from vectormation.objects import *

   args = parse_args()
   canvas = VectorMathAnim(save_dir='svgs/basic', verbose=args.verbose)
   canvas.set_background(fill='#1a1a2e')

   circle = Circle(r=100, fill='#58C4DD', fill_opacity=0.8)
   circle.fadein(0, 1)
   circle.shift(dx=400, start=1, end=3)

   canvas.add(circle)

   if not args.no_display:
       canvas.browser_display(fps=args.fps, port=args.port, hot_reload=args.hot_reload)

Camera animation
~~~~~~~~~~~~~~~~

Combine camera methods to guide the viewer's attention through a scene.

.. code-block:: python

   from vectormation.objects import *

   args = parse_args()
   canvas = VectorMathAnim(save_dir='svgs/camera', verbose=args.verbose)
   canvas.set_background()

   c1 = Circle(r=50, cx=300, cy=300, fill='#58C4DD')
   c2 = Circle(r=50, cx=1600, cy=700, fill='#83C167')
   c1.fadein(0, 0.5)
   c2.fadein(0, 0.5)

   # Focus on the first circle
   canvas.focus_on(c1, start=1, end=2, padding=80)

   # Reset to full view
   canvas.camera_reset(3, 4)

   # Zoom into the second circle
   canvas.camera_zoom(3, start=5, end=6, cx=1600, cy=700)

   # Reset again
   canvas.camera_reset(7, 8)

   canvas.add(c1, c2)
   if not args.no_display:
       canvas.browser_display(fps=args.fps, port=args.port)

Browser preview with hot reload
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Hot reload watches the script file for changes and re-runs it
automatically, enabling a rapid edit-save-preview loop.

.. code-block:: python

   from vectormation.objects import *

   args = parse_args()
   canvas = VectorMathAnim(save_dir='svgs/dev', verbose=args.verbose)
   canvas.set_background(fill='#0d1b2a')

   t = Text(text='Edit me!', x=960, y=540, font_size=72,
            fill='#fff', stroke_width=0, text_anchor='middle')
   t.write(0, 1)

   canvas.add(t)
   canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)

Run with::

   python my_script.py --hot-reload

Export video
~~~~~~~~~~~~

Use ``export_video`` for MP4 output or ``export_gif`` for animated GIFs.
Combine with ``--no-display`` for headless render pipelines.

.. code-block:: python

   from vectormation.objects import *

   args = parse_args()
   canvas = VectorMathAnim(save_dir='svgs/export', verbose=args.verbose)
   canvas.set_background(fill='#1a1a2e')

   rect = Rectangle(200, 200, fill='#E76F51')
   rect.fadein(0, 1)
   rect.rotate_by(1, 4, degrees=360)

   canvas.add(rect)

   # Export a video
   canvas.export_video('spinning_rect.mp4', fps=30, end=5)

   # Export a single PNG frame
   canvas.export_png(time=2.5, filename='frame_at_2.5s.png')

   # Export an animated GIF
   canvas.export_gif('spinning_rect.gif', fps=15, end=5)

Sections for structured playback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sections create pause points in the browser viewer, useful for
presentation-style animations.

.. code-block:: python

   from vectormation.objects import *

   args = parse_args()
   canvas = VectorMathAnim(save_dir='svgs/sections', verbose=args.verbose)
   canvas.set_background()

   title = Text(text='Part 1', x=960, y=540, font_size=72,
                fill='#fff', stroke_width=0, text_anchor='middle')
   title.write(0, 1)
   canvas.add_section(2)  # pause here

   subtitle = Text(text='Part 2', x=960, y=640, font_size=48,
                   fill='#aaa', stroke_width=0, text_anchor='middle')
   subtitle.write(2, 3)
   canvas.add_section(4)  # pause here again

   canvas.add(title, subtitle)
   if not args.no_display:
       canvas.browser_display(fps=args.fps, port=args.port)

----

Tips and Best Practices
-----------------------

**One canvas per script.** Each script should create a single
``VectorMathAnim`` instance. The canvas manages a global save directory
used by TeX caching and frame output.

**Use parse_args() for flexibility.** Wrapping ``browser_display`` and
``export_video`` calls behind ``args.no_display`` and ``args.output``
makes your script usable both interactively and in CI pipelines.

**Add objects before displaying.** All objects must be registered with
``add_objects`` (or ``add``) before calling ``browser_display`` or
``export_video``. Objects added after display starts will not appear.

**Auto-detected end time.** When ``end=None``, the canvas scans every
registered object's ``last_change`` attribute plus its own camera
keyframes to determine the animation duration. This means objects
created but not added to the canvas do not contribute to the end time.

**Z-ordering.** Objects are drawn sorted by their ``z`` attribute.
Lower values render first (behind); higher values render on top. The
background defaults to ``z=-1``. Use ``obj.to_front()`` or
``obj.to_back()`` for quick adjustments, or ``obj.set_z(value)`` for
precise control.

**Static previews.** Use ``browser_display(end=0)`` to display a
single frame at ``start`` without animation. This is handy for
checking layouts and positioning before adding animations.

**Camera methods chain.** All camera methods return ``self``, so you
can chain them:

.. code-block:: python

   (canvas
       .camera_zoom(2, start=0, end=1)
       .camera_shift(200, 0, start=1, end=2)
       .camera_reset(3, 4))

**Scale for high-DPI export.** Pass ``scale=2`` to the constructor or
to ``export_video`` / ``export_png`` to render at 2x resolution
(3840x2160 for the default 1920x1080 canvas).

**Hot reload workflow.** Run your script with ``--hot-reload``, keep
the browser tab open, and edit your script in a separate editor. On
each file save the animation restarts with your changes.
