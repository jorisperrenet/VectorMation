"""Shared TeX glyph cache and assembly functions.

Built-in Computer Modern glyphs for common characters (digits, letters, signs,
Greek letters, etc.) are embedded as SVG path data in ``_tex_glyphs_data.py``
— no LaTeX installation required for these.  Additional glyphs are compiled
on-demand via LaTeX and cached.
"""
import tempfile

from vectormation._tex_glyphs_data import BUILTIN_GLYPHS

# Glyph cache for on-demand LaTeX-compiled glyphs: {tex_dir: {token: (vb, [Tags])}}
_latex_glyph_cache: dict[str, dict[str, tuple[list, list]]] = {}

_fallback_tex_dir: str | None = None


def _resolve_tex_dir(tex_dir=None) -> str:
    """Resolve LaTeX cache directory."""
    global _fallback_tex_dir
    if tex_dir is not None:
        return tex_dir
    import vectormation._canvas as _cm
    if hasattr(_cm, 'save_directory'):
        return f'{_cm.save_directory}/tex'
    if _fallback_tex_dir is None:
        _fallback_tex_dir = tempfile.mkdtemp()
    return _fallback_tex_dir


def _ensure_glyph(token, tex_dir=None):
    """Ensure a single token is available (built-in or LaTeX-compiled).

    Returns True if the glyph is available, False if LaTeX is not installed.
    """
    if token in BUILTIN_GLYPHS:
        return True
    tex_dir = _resolve_tex_dir(tex_dir)
    cache = _latex_glyph_cache.setdefault(tex_dir, {})
    if token in cache:
        return True
    try:
        from vectormation.tex_file_writing import get_characters
        import sys
        print(f'[tex_glyphs] Compiling glyph for ${token}$ via LaTeX...', file=sys.stderr)
        cache[token] = get_characters(tex_dir, f'${token}$', 'latex', '')
        return True
    except ImportError:
        import sys
        print(f'[tex_glyphs] LaTeX not available \u2014 cannot render ${token}$', file=sys.stderr)
        return False
    except Exception as exc:
        import sys
        print(f'[tex_glyphs] LaTeX compilation failed for ${token}$: {exc}', file=sys.stderr)
        return False


def ensure_glyphs(tokens, tex_dir=None):
    """Ensure a list of tokens are available in the glyph cache.

    Built-in glyphs (digits, letters, signs, Greek, etc.) need no LaTeX.
    Other tokens are compiled via LaTeX on demand.
    """
    tex_dir = _resolve_tex_dir(tex_dir)
    for token in tokens:
        _ensure_glyph(token, tex_dir)


def _get_glyph(token, tex_dir):
    """Look up a glyph: built-in first, then LaTeX cache."""
    if token in BUILTIN_GLYPHS:
        return BUILTIN_GLYPHS[token]
    cache = _latex_glyph_cache.get(tex_dir, {})
    return cache.get(token)


def _ref_height():
    """Return the reference viewbox height (digit '0') for uniform scaling."""
    vb = BUILTIN_GLYPHS['0'][0]
    return abs(vb[3]) if vb[3] else 1


def _char_width(glyph_data, font_size):
    """Return the advance width for a glyph at the given font_size."""
    vb = glyph_data[0]
    base_scale = font_size / _ref_height()
    return (abs(vb[2]) if vb[2] else 1) * base_scale + font_size * 0.05


def _make_path_obj(d, transform, **styles):
    """Create a Path VObject from raw SVG path data."""
    from vectormation._shapes import Path
    import re
    obj = Path(d, **styles)
    if transform:
        m = re.search(r'translate\(\s*([-\d.]+)[\s,]+([-\d.]+)\s*\)', transform)
        if m:
            obj.shift(dx=float(m.group(1)), dy=float(m.group(2)), start=0)
    return obj


def _assemble(tokens, x, y, font_size, creation, tex_dir, anchor, styles):
    """Core assembly: lay out a sequence of glyph tokens into a VCollection.

    Returns VCollection, or None if any token is missing from both
    built-in and LaTeX caches.
    """
    from vectormation._base import VCollection
    from vectormation._svg_utils import from_svg

    # Look up all glyphs, auto-compiling via LaTeX if needed
    glyph_list = []
    for tok in tokens:
        g = _get_glyph(tok, tex_dir)
        if g is None:
            # Try to compile on-demand
            if not _ensure_glyph(tok, tex_dir):
                return None
            g = _get_glyph(tok, tex_dir)
            if g is None:
                return None
        glyph_list.append(g)

    # Normalize anchor
    if anchor in ('middle', None):
        anchor = 'center'
    elif anchor == 'end':
        anchor = 'right'

    total_w = sum(_char_width(g, font_size) for g in glyph_list)
    if anchor == 'center':
        offset_x = -total_w / 2
    elif anchor == 'right':
        offset_x = -total_w
    else:
        offset_x = 0

    default_styles = {'stroke_width': 0, 'fill': '#fff'}
    merged = {**default_styles, **styles}

    ref_h = _ref_height()
    objects = []
    cursor_x = x + offset_x
    for tok, glyph_data in zip(tokens, glyph_list):
        vb = glyph_data[0]
        base_scale = font_size / ref_h
        char_width = (abs(vb[2]) if vb[2] else 1) * base_scale
        st = {**merged,
              'scale_x': base_scale * merged.get('scale_x', 1),
              'scale_y': base_scale * merged.get('scale_y', 1)}

        if tok in BUILTIN_GLYPHS:
            # Built-in: create Path objects directly (no bs4 dependency)
            paths = glyph_data[1]
            for d, transform in paths:
                obj = _make_path_obj(d, transform, **st)
                obj.styling.dx.set_onward(creation, cursor_x)
                obj.styling.dy.set_onward(creation, y)
                objects.append(obj)
        else:
            # LaTeX-compiled: glyph_data[1] is list of bs4 Tags
            for char_svg in glyph_data[1]:
                obj = from_svg(char_svg, **st)
                obj.styling.dx.set_onward(creation, cursor_x)
                obj.styling.dy.set_onward(creation, y)
                objects.append(obj)
        cursor_x += char_width + font_size * 0.05

    return VCollection(*objects, creation=creation)


def assemble_tex_glyphs(text, x, y, font_size, creation=0, tex_dir=None,
                         anchor='center', **styles):
    """Assemble a plain string character-by-character from cached glyphs.

    Each character in *text* is treated as a single token.  Built-in glyphs
    are used when available; missing characters are compiled via LaTeX
    on-demand.  Returns None only if a character cannot be resolved at all
    (e.g. LaTeX not installed and character not built-in).
    """
    tex_dir = _resolve_tex_dir(tex_dir)
    return _assemble(list(text), x, y, font_size, creation, tex_dir, anchor, styles)


def assemble_tex_tokens(tokens, x, y, font_size, creation=0, tex_dir=None,
                         anchor='center', **styles):
    """Assemble a list of LaTeX tokens from cached glyphs.

    Like :func:`assemble_tex_glyphs` but takes a list of tokens (for
    multi-char commands like ``\\pi``).
    """
    tex_dir = _resolve_tex_dir(tex_dir)
    return _assemble(list(tokens), x, y, font_size, creation, tex_dir, anchor, styles)


def _tokenize_tex(inner):
    """Split a TeX inner string into tokens for glyph assembly.

    Handles backslash commands (``\\pi``, ``\\alpha``) and single characters.
    Returns None for complex expressions that can't be tokenized (e.g.
    commands with brace arguments like ``\\frac{1}{2}``).
    """
    tokens = []
    i = 0
    while i < len(inner):
        if inner[i] == '\\':
            # Collect the command name
            j = i + 1
            while j < len(inner) and inner[j].isalpha():
                j += 1
            cmd = inner[i:j]
            # If the command is followed by a brace, it takes arguments
            # and can't be rendered as a single glyph
            if j < len(inner) and inner[j] == '{':
                return None
            tokens.append(cmd)
            i = j
        elif inner[i] in ' \t':
            i += 1  # skip whitespace
        elif inner[i] in '{}^_':
            # Braces, superscript/subscript — too complex for glyph assembly
            return None
        else:
            tokens.append(inner[i])
            i += 1
    return tokens
