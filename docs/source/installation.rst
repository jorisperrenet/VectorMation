Installation
============

Python Package
--------------

.. code-block:: bash

   pip install vectormation

Or install from source:

.. code-block:: bash

   git clone https://github.com/jorisperrenet/VectorMation.git
   cd VectorMation
   pip install -e .

To run examples without installing, set ``PYTHONPATH``:

.. code-block:: bash

   git clone https://github.com/jorisperrenet/VectorMation.git
   cd VectorMation
   pip install numpy svgpathtools beautifulsoup4 lxml websockets
   PYTHONPATH=. python examples/showcase/spiral.py

**Requires Python 3.10 or later.**

.. tip::

   It is recommended to install VectorMation inside a virtual environment:

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate   # Linux / macOS
      pip install vectormation

Verify Installation
-------------------

After installing, verify everything works by running:

.. code-block:: bash

   python -c "from vectormation.objects import *; print('VectorMation is ready!')"

Or create a quick test script:

.. code-block:: python

   from vectormation.objects import *
   v = VectorMathAnim()
   v.set_background()
   c = Circle(r=100, cx=960, cy=540, fill='#58C4DD')
   v.add(c)
   v.show(end=0)

Python Dependencies
-------------------

These are installed automatically with ``pip install vectormation``:

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Package
     - Purpose
   * - ``numpy``
     - Path morphing interpolation
   * - ``svgpathtools``
     - SVG path parsing and morphing
   * - ``beautifulsoup4``
     - SVG/HTML parsing
   * - ``lxml``
     - XML backend for BeautifulSoup
   * - ``websockets``
     - Browser-based viewer

Optional Dependencies
---------------------

These are only needed for specific export formats:

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Package
     - Required for
   * - ``cairosvg``
     - PNG export (``export_png``) and video/GIF export
   * - ``Pillow``
     - GIF export (``export_gif``)
   * - ``ffmpeg`` (system package)
     - Video export (``export_video``)

Install the optional Python packages with:

.. code-block:: bash

   pip install vectormation[export]   # installs cairosvg and Pillow

.. note::

   **ffmpeg** is a system package, not a Python package. Install it with your
   system package manager:

   - Debian/Ubuntu: ``sudo apt install ffmpeg``
   - Arch Linux: ``sudo pacman -S ffmpeg``
   - macOS: ``brew install ffmpeg``
   - Windows: download from `ffmpeg.org <https://ffmpeg.org/download.html>`_

LaTeX (optional)
----------------

LaTeX is required only if you use ``TexObject`` or ``SplitTexObject`` to render LaTeX expressions. Install a full TeX distribution:

.. list-table::
   :header-rows: 1
   :widths: auto

   * - OS
     - Package
   * - Linux (Debian/Ubuntu)
     - ``sudo apt install texlive-full``
   * - Linux (Arch)
     - ``sudo pacman -S texlive``
   * - macOS
     - `MacTeX <https://tug.org/mactex/>`_
   * - Windows
     - `MiKTeX <https://miktex.org/>`_

.. tip::

   If you see an error like ``LaTeX not found`` or ``dvisvgm not found``,
   it means a TeX distribution is not installed. VectorMation's built-in
   ``TexObject`` will fall back to pre-built Computer Modern glyphs for
   common math symbols, but a full TeX installation gives access to
   arbitrary LaTeX expressions.

Documentation (optional)
------------------------

To build and serve the documentation locally:

.. code-block:: bash

   pip install -r docs/requirements.txt
   cd docs
   sphinx-build -b html source build
   python -m http.server -d build

Then open ``http://localhost:8000`` in your browser.
