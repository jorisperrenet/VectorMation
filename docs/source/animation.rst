Animation & Playback
====================

Browser Viewer
--------------

VectorMation displays animations in a browser via WebSocket:

.. code-block:: python

   canvas.browser_display(start=0, end=None, fps=60, port=8765, hot_reload=False)

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Parameter
     - Description
   * - ``start``
     - Animation start time (seconds)
   * - ``end``
     - Animation end time (``None`` = auto-detect, ``0`` = static picture)
   * - ``fps``
     - Frames per second
   * - ``port``
     - WebSocket server port
   * - ``hot_reload``
     - Re-run script on file save

Keyboard Shortcuts
------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Key
     - Action
   * - **P**
     - Pause / Resume
   * - **R**
     - Restart from beginning
   * - **Arrow Right**
     - Jump to next section
   * - **Arrow Left**
     - Step backward
   * - **S**
     - Save current frame as SVG
   * - **F**
     - Reset zoom to fit
   * - **Q**
     - Quit
   * - **D**
     - Toggle debug panel
   * - **N**
     - Toggle snap mode
   * - **+** / **=**
     - Increase playback speed by 0.25x
   * - **-** / **_**
     - Decrease playback speed by 0.25x
   * - **1**--**9**
     - Jump to 10%--90% of the animation
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

Playback Speed
--------------

Speed can be adjusted during playback with **+** / **-** keys, or via the toolbar buttons. The current speed and FPS are shown in the toolbar.

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

----

Hot Reload
----------

Enable hot reload to automatically re-run the script when you save changes:

.. code-block:: python

   canvas.browser_display(hot_reload=True)

The browser stays open and updates live -- useful during development.
