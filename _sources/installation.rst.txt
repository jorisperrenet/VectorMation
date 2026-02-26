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

**Requires Python 3.10 or later.**

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

Documentation (optional)
------------------------

To build and serve the documentation locally:

.. code-block:: bash

   pip install -r docs/requirements.txt
   cd docs
   sphinx-build -b html source build
   python -m http.server -d build

Then open ``http://localhost:8000`` in your browser.
