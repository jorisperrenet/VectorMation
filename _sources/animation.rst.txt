Animation & Playback
====================

Browser Viewer
--------------

The simplest way to display an animation is ``canvas.show()``, which
automatically parses CLI arguments and either opens the browser viewer or
exports to a file:

.. code-block:: python

   canvas.show(end=5)

.. list-table::
   :header-rows: 1
   :widths: auto

   * - CLI Flag
     - Default
     - Description
   * - ``-v``, ``--verbose``
     - off
     - Enable debug logging
   * - ``--fps FPS``
     - 60
     - Frames per second
   * - ``--port PORT``
     - 8765
     - WebSocket server port
   * - ``-o``, ``--output PATH``
     - none
     - Export to file (format inferred from extension: ``.mp4``, ``.gif``, ``.svg``, ``.png``)
   * - ``-d``, ``--duration SECS``
     - none
     - Animation duration in seconds
   * - ``--start SECS``
     - 0
     - Start time
   * - ``--end SECS``
     - none
     - End time
   * - ``--hot-reload``
     - off
     - Re-run script on file save

.. tip::

   Examples:

   .. code-block:: bash

      python my_scene.py              # open browser viewer
      python my_scene.py -v           # verbose logging
      python my_scene.py --fps 30     # set frame rate
      python my_scene.py --port 9000  # custom port
      python my_scene.py -o out.mp4   # export to video
      python my_scene.py -o frame.svg # export single SVG frame
      python my_scene.py -d 5         # set duration to 5 seconds

You can also call ``browser_display()`` directly for more control:

.. code-block:: python

   canvas.browser_display(start=0, end=None, fps=60, port=8765, hot_reload=False)

Keyboard Shortcuts
------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Key
     - Action
   * - **Space** / **P**
     - Pause / Resume
   * - **R**
     - Restart from beginning
   * - **,** / **.**
     - Step backward / forward one frame
   * - **Left** / **Right**
     - Previous / next section
   * - **-** / **+** / **Up** / **Down**
     - Slower / faster (0.25x increments)
   * - **0**--**9**
     - Jump to 0%--90% of the animation
   * - **Home** / **End**
     - Jump to start / end
   * - **F**
     - Reset zoom to fit
   * - **S**
     - Save current frame as SVG
   * - **Shift+S**
     - Save current frame as PNG
   * - **C**
     - Copy SVG to clipboard
   * - **L**
     - Toggle loop
   * - **B**
     - Cycle background (dark / white / checker)
   * - **Ctrl+B**
     - Add / remove bookmark
   * - **[** / **]**
     - Previous / next bookmark
   * - **H**
     - Hide / show toolbars
   * - **G**
     - Toggle grid overlay
   * - **I**
     - Inspect mode (nearest object)
   * - **M**
     - Measure tool (click two points)
   * - **N**
     - Toggle snap mode
   * - **D**
     - Toggle debug panel
   * - **?**
     - Help overlay
   * - **Q**
     - Quit
   * - **Scroll wheel**
     - Zoom in/out at cursor position

Debug Panel
-----------

Press **D** to toggle the debug panel. It shows:

- Current time and frame number
- Total frames
- List of visible objects at the current time

Snap Mode
---------

Press **N** to toggle snap mode. When enabled, moving the mouse over the SVG canvas snaps the cursor to nearby object points (centres, corners, etc.), shown with a visual indicator.

Sections
--------

Sections let you pause the animation at specific times, useful for presentations:

.. code-block:: python

   canvas.add_section(3)   # pause at t=3
   canvas.add_section(6)   # pause at t=6

During playback, the animation pauses at each section boundary. Press **Arrow Right** to continue to the next section.

.. admonition:: Example: sections demo
   :class: example

   .. raw:: html

      <video src="_static/videos/anim_sections.mp4" controls autoplay loop muted></video>

   Objects appear in phases separated by section breaks. During playback
   the animation pauses at each ``add_section`` time.

   .. literalinclude:: ../../examples/reference/anim_sections.py
      :language: python

Playback Speed
--------------

Speed can be adjusted during playback with **+** / **-** keys, or via the toolbar buttons. The current speed and FPS are shown in the toolbar.

.. admonition:: Example: animation timing
   :class: example

   .. raw:: html

      <video src="_static/videos/anim_speed.mp4" controls autoplay loop muted></video>

   The same shift animation with different ``start``/``end`` durations.
   Shorter intervals mean faster motion.

   .. literalinclude:: ../../examples/reference/anim_speed.py
      :language: python

Static Pictures
---------------

Pass ``end=0`` to display a single static frame with no animation:

.. code-block:: python

   canvas.browser_display(end=0)

----

Exporting
---------

SVG Frame
^^^^^^^^^

.. code-block:: python

   canvas.write_frame(time=2.5, filename='frame.svg')

All Sections as SVG
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   canvas.export_sections(prefix='slide')
   # Writes slide_000.svg, slide_001.svg, ... for each section boundary

PNG
^^^

Export a single frame as PNG (requires ``cairosvg``):

.. code-block:: python

   canvas.export_png(time=0, filename='frame.png', width=None, height=None)

``width`` and ``height`` control the output resolution. If omitted, the canvas dimensions are used.

Video (MP4)
^^^^^^^^^^^

Export the animation as an MP4 video (requires ``cairosvg`` and ``ffmpeg``):

.. code-block:: python

   canvas.export_video(filename='animation.mp4', start=0, end=None, fps=60)

.. note::

   Video export requires **ffmpeg** to be installed and available on your
   ``PATH``. On Debian/Ubuntu: ``sudo apt install ffmpeg``. On macOS:
   ``brew install ffmpeg``. On Arch: ``sudo pacman -S ffmpeg``.

Animated GIF
^^^^^^^^^^^^

Export the animation as a GIF (requires ``cairosvg`` and ``Pillow``):

.. code-block:: python

   canvas.export_gif(filename='animation.gif', start=0, end=None, fps=30, scale=1.0, loop=0)

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Parameter
     - Description
   * - ``scale``
     - Scale factor for output dimensions (e.g. ``0.5`` for half size)
   * - ``loop``
     - Number of loops (``0`` = infinite)

.. admonition:: Example: static frame export
   :class: example

   .. raw:: html

      <img src="_static/videos/anim_export.svg" style="width:100%; max-width:800px;" />

   A composed scene exported as a single SVG frame with ``write_frame``.

   .. literalinclude:: ../../examples/reference/anim_export.py
      :language: python

----

Hot Reload
----------

Enable hot reload to automatically re-run the script when you save changes:

.. code-block:: python

   canvas.browser_display(hot_reload=True)

The browser stays open and updates live -- useful during development.
