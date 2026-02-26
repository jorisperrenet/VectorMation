"""
MIT License

Copyright (c) 2018 3Blue1Brown LLC
Copyright (c) 2021, the Manim Community Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import re
import hashlib
import logging
from copy import copy
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger('vectormation.tex')


def hash_string(string: str) -> str:
    # Truncating at 16 bytes for cleanliness
    hasher = hashlib.sha256(string.encode())
    return hasher.hexdigest()[:16]

def tex_content_to_svg_file(
    dir_name: str, content: str, compiler: str, preamble: str,
) -> str:

    full_tex = "\n\n".join((
        "\\documentclass[preview]{standalone}",
        "\\usepackage{amsmath}",
        "\\usepackage{amsfonts}",
        preamble,
        "\\begin{document}",
        content,
        "\\end{document}"
    )) + "\n"

    svg_file = os.path.join(
        dir_name, hash_string(full_tex) + ".svg"
    )
    if not os.path.exists(svg_file):
        logger.info('Generating LaTeX for "%s"...', content[:50])
        os.makedirs(dir_name, exist_ok=True)
        create_tex_svg(full_tex, svg_file, compiler)
    else:
        logger.log(5, 'Using cached SVG: %s', svg_file)
    return svg_file


def create_tex_svg(full_tex: str, svg_file: str, compiler: str) -> None:
    logger.debug('Compiling %s -> SVG', compiler)
    if compiler == "latex":
        program = "latex"
        dvi_ext = ".dvi"
    elif compiler == "xelatex":
        program = "xelatex -no-pdf"
        dvi_ext = ".xdv"
    else:
        raise NotImplementedError(
            f"Compiler '{compiler}' is not implemented"
        )

    # Write tex file
    root, _ = os.path.splitext(svg_file)
    with open(root + ".tex", "w", encoding="utf-8") as tex_file:
        tex_file.write(full_tex)

    # tex to dvi
    if os.system(" ".join((
        program,
        "-interaction=batchmode",
        "-halt-on-error",
        f"-output-directory=\"{os.path.dirname(svg_file)}\"",
        f"\"{root}.tex\"",
        ">",
        os.devnull
    ))):
        error_str = "LaTeX compilation failed."
        log_file_path = root + ".log"
        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r", encoding="utf-8") as log_file:
                    log_content = log_file.read()
                    error_match = re.search(r"(?<=\n! ).*\n.*\n", log_content)
                    if error_match:
                        error_str += f"\n{error_match.group().strip()}"
                    else:
                        # Try to find lines starting with '!'
                        bang_lines = re.findall(r"^!.*$", log_content, re.MULTILINE)
                        if bang_lines:
                            error_str += "\n" + "\n".join(bang_lines[:5])
            except Exception:
                pass
        logger.error(error_str)
        raise RuntimeError(error_str)

    # dvi to svg
    os.system(" ".join((
        "dvisvgm",
        f"\"{root}{dvi_ext}\"",
        "-n",
        "-v",
        "0",
        "-o",
        f"\"{svg_file}\"",
        ">",
        os.devnull
    )))

    # Cleanup superfluous documents
    for ext in (".tex", dvi_ext, ".log", ".aux"):
        try:
            os.remove(root + ext)
        except FileNotFoundError:
            pass

def get_characters(tex_dir, to_render, compiler='latex', preamble=''):
    """Parse LaTeX content into individual character SVG elements."""
    filename = tex_content_to_svg_file(tex_dir, content=to_render, compiler=compiler, preamble=preamble)

    with open(filename, 'r') as f:
        svg_contents = BeautifulSoup(f.read(), features='xml').svg
        assert isinstance(svg_contents, Tag)
        viewbox = [float(i) for i in str(svg_contents['viewBox']).split(' ')]
        assert isinstance(svg_contents.g, Tag)
        chars: list[Tag] = [c for c in svg_contents.g if isinstance(c, Tag)]

        # Resolve <use xlink:href="#id"> references by inlining the definition
        uses = [(str(ref_id)[1:], c, idx) for idx, c in enumerate(chars)
                if (ref_id := c.get('xlink:href', None)) is not None]
        assert isinstance(svg_contents.defs, Tag)
        defs = {str(i.get('id', '')): i for i in svg_contents.defs if isinstance(i, Tag)}
        for def_id, use, idx in uses:
            d = copy(defs[def_id])
            del use['xlink:href']
            del d['id']
            for name, val in use.attrs.items():
                if d.get(name, None) is not None:
                    d[name] = str(float(str(d[name])) + float(str(val)))
                else:
                    d[name] = val
            chars[idx] = d

    return viewbox, chars

