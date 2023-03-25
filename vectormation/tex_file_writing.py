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
import hashlib
from copy import copy
from bs4 import BeautifulSoup


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
        # If svg doesn't exist, create it
        # with display_during_execution("Writing " + short_tex):
        os.makedirs(dir_name, exist_ok=True)
        create_tex_svg(full_tex, svg_file, compiler)
    return svg_file


def create_tex_svg(full_tex: str, svg_file: str, compiler: str) -> None:
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
        log.error(
            "LaTeX Error!  Not a worry, it happens to the best of us."
        )
        error_str = ""
        with open(root + ".log", "r", encoding="utf-8") as log_file:
            error_match_obj = re.search(r"(?<=\n! ).*\n.*\n", log_file.read())
            if error_match_obj:
                error_str = error_match_obj.group()
                log.debug(
                    f"The error could be:\n`{error_str}`",
                )
        raise LatexError(error_str)

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

def get_characters(tex_dir, to_render, compiler, preamble):
    # Write the tex content to an svg file
    filename = tex_content_to_svg_file(tex_dir, content=to_render, compiler='latex', preamble='')

    with open(filename, 'r') as f:
        svg_contents = BeautifulSoup(f.read(), features='xml').svg
        surrounding_box = [float(i) for i in svg_contents['viewBox'].split(' ')]

        chars = [svg_char for svg_char in svg_contents.g if svg_char != '\n']

        # Some chars use definitions, we add the value of the 'use' to the definition
        uses = [(ref_id[1:], c, chard_idx) for chard_idx, c in enumerate(chars) if (ref_id := c.get('xlink:href', None)) != None]

        defs = {i.get('id', None): i for i in svg_contents.defs if i != '\n'}
        for def_id, use, char_idx in uses:
            # Find the corresponding def to the use
            d = copy(defs[def_id])
            # d = svg_contents.select(f'#{def_id}', )[0]
            del use['xlink:href']
            del d['id']
            for name, val in use.attrs.items():
                if d.get(name, None) != None:
                    # Add the two values
                    d[name] = str(float(d[name]) + float(val))
                else:
                    d[name] = val

            chars[char_idx] = d

    return surrounding_box, chars


if __name__ == '__main__':
    tex_content_to_svg_file('svgs/scene1/tex', '$$x^2$$', compiler='latex', preamble='')

