VectorMathAnim
==============

.. py:class:: VectorMathAnim(save_dir, width=1920, height=1080, verbose=False)

   The top-level canvas that manages all objects and controls rendering.
   Creates a 1920x1080 SVG viewBox by default.

   :param str save_dir: Directory for saved SVG frames.
   :param int width: ViewBox width (default ``1920``).
   :param int height: ViewBox height (default ``1080``).
   :param bool verbose: Enable debug logging.

   .. rubric:: Scene Setup

   .. py:method:: set_background(creation=0, z=-1, grid=False, grid_spacing=60, grid_color='#333', **styling)

      Add a background rectangle with optional grid lines.

      :param bool grid: Show grid lines.
      :param float grid_spacing: Distance between grid lines.
      :param str grid_color: Grid line colour.

   .. py:method:: add_objects(*args)

      Register one or more objects for rendering. Objects are drawn in z-order.

   .. py:method:: add_def(def_obj)

      Register a gradient, clip path, or filter definition.
      Aliases: ``add_gradient``, ``add_clip_path``.

   .. py:method:: add_section(time)

      Add a section break at *time* for paused playback.

   .. rubric:: Rendering

   .. py:method:: generate_frame_svg(time=None)

      Return the complete SVG string for a single frame.

      :param float time: Timestamp to render (defaults to canvas time).
      :returns: SVG string.

   .. py:method:: write_frame(time=None, filename=None)

      Write an SVG frame to disk.

   .. rubric:: Display

   .. py:method:: browser_display(start_time=0, end_time=None, fps=60, port=8765, hot_reload=False)

      Open a browser-based viewer with real-time playback, zoom, speed control, and keyboard shortcuts.

      :param float start_time: Playback start.
      :param float end_time: Playback end (``None`` = auto-detect from last animation).
      :param int fps: Frames per second.
      :param int port: WebSocket port.
      :param bool hot_reload: Re-run script on file change.

   .. rubric:: Export

   .. py:method:: export_png(time=0, filename='frame.png', width=None, height=None)

      Export a single PNG frame. Requires ``cairosvg``.

   .. py:method:: export_video(filename='animation.mp4', start_time=0, end_time=None, fps=60, scale=1)

      Export an MP4 video. Requires ``cairosvg`` and ``ffmpeg``.

      :param int scale: Pixel scale factor (1 = native 1920x1080, 2 = 3840x2160).

   .. py:method:: export_gif(filename='animation.gif', start_time=0, end_time=None, fps=30, scale=1, loop=0)

      Export an animated GIF. Requires ``cairosvg`` and ``Pillow``.

   .. py:method:: export_sections(prefix='section')

      Export each section as a separate SVG file.

   .. rubric:: Inspection

   .. py:method:: get_visible_objects_info(time=None)

      Return a list of visible objects and their bounding boxes at the given time.

   .. py:method:: get_snap_points(time=None)

      Extract snappable points (centers, corners, endpoints) from all visible objects.
