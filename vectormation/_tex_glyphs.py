"""Shared TeX glyph cache and assembly functions.

Built-in Computer Modern glyphs for common characters (digits, letters, signs,
Greek letters, etc.) are embedded as SVG path data in ``_tex_glyphs_data.py``
— no LaTeX installation required for these.  Additional glyphs are compiled
on-demand via LaTeX and cached.

Built-in glyph format: ``(advance_width, y_offset, [(svg_d, transform), ...])``
All built-in glyphs share a consistent baseline (compiled together in LaTeX).
"""
import tempfile

from vectormation._tex_glyphs_data import BUILTIN_GLYPHS, BUILTIN_TEXT_GLYPHS

# Glyph cache for on-demand LaTeX-compiled glyphs: {tex_dir: {token: (vb, [Tags])}}
_latex_glyph_cache: dict[str, dict[str, tuple[list, list] | None]] = {}

_fallback_tex_dir: str | None = None

# Reference height: digit '0' advance width is used for scaling.
# Pre-compute from the viewBox height of the digit group (9.9626 TeX points).
# This is the height of the shared viewBox when digits are compiled together.
_REF_HEIGHT = 6.420368  # abs(viewBox[3]) for standalone digit '0'


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


# Characters that cause errors in math mode (e.g. \spacefactor).
# These are compiled via \mbox{} instead of $...$
_TEXT_MODE_TOKENS = {'!', '?', '$'}


def _ensure_glyph(token, tex_dir=None, text_mode=False):
    """Ensure a single token is available (built-in or LaTeX-compiled).

    Returns True if the glyph is available, False if LaTeX is not installed.
    When *text_mode* is True, ASCII letters use upright (text-mode) glyphs.
    """
    if text_mode and token in BUILTIN_TEXT_GLYPHS:
        return True
    if token in BUILTIN_GLYPHS:
        return True
    tex_dir = _resolve_tex_dir(tex_dir)
    cache = _latex_glyph_cache.setdefault(tex_dir, {})
    if token in cache:
        return cache[token] is not None
    try:
        from vectormation.tex_file_writing import get_characters
        import sys
        if text_mode or token in _TEXT_MODE_TOKENS:
            tex_token = token.replace('$', '\\$')
            expr = f'$\\mbox{{{tex_token}}}$'
        else:
            expr = f'${token}$'
        print(f'[tex_glyphs] Compiling glyph for {expr} via LaTeX...', file=sys.stderr)
        cache[token] = get_characters(tex_dir, expr, 'latex', '')
        return True
    except ImportError:
        import sys
        print(f'[tex_glyphs] LaTeX not available \u2014 cannot render ${token}$', file=sys.stderr)
        return False
    except Exception as exc:
        import sys
        print(f'[tex_glyphs] LaTeX compilation failed for ${token}$: {exc}', file=sys.stderr)
        cache[token] = None  # cache the failure so we don't retry
        return False


def _get_glyph(token, tex_dir, text_mode=False):
    """Look up a glyph: built-in first, then LaTeX cache.

    Built-in: ``(advance_width, y_offset, [(d, transform), ...])``
    LaTeX-compiled: ``(viewbox, [bs4_Tags])`` (legacy format from get_characters)

    When *text_mode* is True, ASCII letters use upright (text-mode) glyphs.
    """
    if text_mode and token in BUILTIN_TEXT_GLYPHS:
        return BUILTIN_TEXT_GLYPHS[token]
    if token in BUILTIN_GLYPHS:
        return BUILTIN_GLYPHS[token]
    cache = _latex_glyph_cache.get(tex_dir, {})
    return cache.get(token)


def _is_builtin(glyph_data):
    """Check whether glyph_data is built-in format vs LaTeX-compiled format."""
    # Built-in: (float, float, list)  — advance_width, y_offset, paths
    # LaTeX:    (list, list)          — viewbox, tags
    return len(glyph_data) == 3


def _char_width(glyph_data, font_size):
    """Return the advance width for a glyph at the given font_size."""
    base_scale = font_size / _REF_HEIGHT
    if _is_builtin(glyph_data):
        return glyph_data[0] * base_scale + font_size * 0.05
    # LaTeX-compiled: viewbox format [x, y, w, h]
    vb = glyph_data[0]
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


def _assemble(tokens, x, y, font_size, creation, tex_dir, anchor, styles,
              v_anchor='baseline', text_mode=False):
    """Core assembly: lay out a sequence of glyph tokens into a VCollection.

    Returns VCollection, or None if any token is missing from both
    built-in and LaTeX caches.

    *v_anchor* controls vertical alignment of the assembled glyphs:
    ``'baseline'`` (default) places glyphs at *y* on the text baseline,
    ``'center'`` vertically centers them on *y*.
    """
    from vectormation._base import VCollection
    from vectormation._svg_utils import from_svg

    # Look up all glyphs, auto-compiling via LaTeX if needed.
    # Spaces produce a cursor gap (no glyph lookup).
    glyph_list = []  # parallel to tokens: glyph_data or None for spaces
    for tok in tokens:
        if tok == ' ':
            glyph_list.append(None)
            continue
        # ('space', multiplier) tuples from spacing commands (\quad, etc.)
        if isinstance(tok, tuple) and tok[0] == 'space':
            glyph_list.append(tok)
            continue
        # ('text', char) forces text-mode; ('math', char) forces math-mode
        if isinstance(tok, tuple) and tok[0] == 'text':
            lookup_tok, lookup_tm = tok[1], True
        elif isinstance(tok, tuple) and tok[0] == 'math':
            lookup_tok, lookup_tm = tok[1], False
        else:
            lookup_tok, lookup_tm = tok, text_mode
        g = _get_glyph(lookup_tok, tex_dir, text_mode=lookup_tm)
        if g is None:
            # Try to compile on-demand
            if not _ensure_glyph(lookup_tok, tex_dir, text_mode=lookup_tm):
                return None
            g = _get_glyph(lookup_tok, tex_dir, text_mode=lookup_tm)
            if g is None:
                return None
        glyph_list.append(g)

    # Normalize anchor
    if anchor in ('middle', None):
        anchor = 'center'
    elif anchor == 'end':
        anchor = 'right'

    base_scale = font_size / _REF_HEIGHT
    space_width = font_size * 0.45

    def _glyph_width(g):
        if g is None:
            return space_width
        if isinstance(g, tuple) and len(g) == 2 and g[0] == 'space':
            return space_width * g[1]
        return _char_width(g, font_size)

    total_w = sum(_glyph_width(g) for g in glyph_list)
    if anchor == 'center':
        offset_x = -total_w / 2
    elif anchor == 'right':
        offset_x = -total_w
    else:
        offset_x = 0

    # Vertical centering: compute visual extent from glyph bounding boxes
    offset_y = 0.0
    if v_anchor == 'center':
        min_top = 0.0  # most negative y in scaled glyph coords (ascent)
        max_bot = 0.0  # most positive y in scaled glyph coords (descent)
        for g in glyph_list:
            if g is None:
                continue
            if _is_builtin(g):
                _adv, y_off, paths = g
                # Built-in paths are in glyph units; y_off shifts baseline
                min_top = min(min_top, y_off * base_scale - font_size)
                max_bot = max(max_bot, y_off * base_scale)
            else:
                vb = g[0]
                # vb[1] is top edge (negative = above baseline), vb[3] is height
                glyph_top = vb[1] * base_scale
                glyph_bot = (vb[1] + vb[3]) * base_scale
                min_top = min(min_top, glyph_top)
                max_bot = max(max_bot, glyph_bot)
        # Shift so the visual center sits at y
        offset_y = -(min_top + max_bot) / 2

    default_styles = {'stroke_width': 0, 'fill': '#fff'}
    merged = {**default_styles, **styles}

    objects = []
    cursor_x = x + offset_x
    y_adjusted = y + offset_y
    for tok, glyph_data in zip(tokens, glyph_list):
        if glyph_data is None:
            cursor_x += space_width
            continue
        # Spacing commands (\quad, etc.)
        if isinstance(glyph_data, tuple) and len(glyph_data) == 2 and glyph_data[0] == 'space':
            cursor_x += space_width * glyph_data[1]
            continue

        builtin = _is_builtin(glyph_data)

        if builtin:
            advance, y_off, paths = glyph_data
            char_width = advance * base_scale
            dy_offset = y_off * base_scale
            st = {**merged,
                  'scale_x': base_scale * merged.get('scale_x', 1),
                  'scale_y': base_scale * merged.get('scale_y', 1)}
            for d, transform in paths:
                obj = _make_path_obj(d, transform, **st)
                obj.styling.dx.set_onward(creation, cursor_x)
                obj.styling.dy.set_onward(creation, y_adjusted + dy_offset)
                objects.append(obj)
        else:
            # LaTeX-compiled: glyph_data = (viewbox, [bs4_Tags])
            vb = glyph_data[0]
            char_width = (abs(vb[2]) if vb[2] else 1) * base_scale
            st = {**merged,
                  'scale_x': base_scale * merged.get('scale_x', 1),
                  'scale_y': base_scale * merged.get('scale_y', 1)}
            for char_svg in glyph_data[1]:
                obj = from_svg(char_svg, **st)
                obj.styling.dx.set_onward(creation, cursor_x)
                obj.styling.dy.set_onward(creation, y_adjusted)
                objects.append(obj)

        cursor_x += char_width + font_size * 0.05

    return VCollection(*objects, creation=creation)


def assemble_tex_glyphs(text, x, y, font_size, creation=0, tex_dir=None,
                         anchor='center', v_anchor='baseline',
                         text_mode=False, **styles):
    """Assemble a string from cached glyphs.

    Plain characters are treated as individual tokens.  Backslash commands
    like ``\\degree`` or ``\\pi`` are resolved via aliases or the glyph cache.
    Returns None only if a character cannot be resolved at all
    (e.g. LaTeX not installed and character not built-in).

    When *text_mode* is True, letters outside ``$...$`` use upright (Roman)
    glyphs.  Sections wrapped in ``$...$`` switch to math (italic) mode.
    ``\\text{}``, ``\\mathrm{}``, etc. switch back to text mode within math.

    *v_anchor*: ``'baseline'`` (default) or ``'center'`` for vertical alignment.
    """
    tex_dir = _resolve_tex_dir(tex_dir)
    tokens = _tokenize_with_modes(text, text_mode)
    if tokens is None:
        return None
    return _assemble(tokens, x, y, font_size, creation, tex_dir, anchor, styles,
                     v_anchor=v_anchor, text_mode=text_mode)


def _tokenize_with_modes(text, text_mode):
    """Tokenize text with ``$...$`` mode switching.

    In *text_mode*, plain characters are emitted as ``('text', ch)`` tuples
    and ``$...$`` sections emit plain strings (math-mode).  Outside text_mode,
    plain characters are emitted as plain strings and ``$...$`` would be
    unusual but still handled.  ``\\text{}``, ``\\mathrm{}`` etc. always
    force text-mode for their brace contents (handled by ``_tokenize_tex``).
    """
    if '$' not in text:
        # No mode switching — use simple tokenizer
        if '\\' in text or any(c in text for c in '^_{}'):
            return _tokenize_tex(text)
        return list(text)

    parts = text.split('$')
    if len(parts) % 2 == 0:
        # Unmatched dollar sign
        return None

    tokens = []
    for i, part in enumerate(parts):
        if not part:
            continue
        is_math = (i % 2 == 1)
        # Determine the effective mode for this segment
        if text_mode:
            seg_is_text = not is_math
        else:
            seg_is_text = is_math  # in math-mode default, $...$ would toggle to text

        if '\\' in part or any(c in part for c in '^_{}'):
            seg_tokens = _tokenize_tex(part)
            if seg_tokens is None:
                return None
        else:
            seg_tokens = list(part)

        if seg_is_text:
            for tok in seg_tokens:
                if tok == ' ' or isinstance(tok, tuple):
                    tokens.append(tok)
                else:
                    tokens.append(('text', tok))
        else:
            for tok in seg_tokens:
                if tok == ' ' or isinstance(tok, tuple):
                    tokens.append(tok)
                else:
                    tokens.append(('math', tok))

    return tokens




# Command aliases: \degree → °, etc.
_COMMAND_ALIASES = {
    '\\degree': '°',
    '\\circ': '°',
    '\\cdot': '·',
    '\\times': '×',
    '\\leq': '≤',
    '\\geq': '≥',
    '\\neq': '≠',
    '\\pm': '±',
    '\\infty': '∞',
    '\\partial': '∂',
    '\\nabla': '∇',
}

# LaTeX operator names rendered as upright (text-mode) letters.
# Tokens are emitted as ('text', char) tuples so _assemble uses text-mode glyphs.
# LaTeX spacing commands mapped to space multipliers (relative to space_width).
_TEX_SPACES = {
    '\\quad': 2.0,
    '\\qquad': 4.0,
    '\\,': 0.5,
    '\\;': 0.7,
    '\\:': 0.6,
    '\\!': -0.25,
    '\\enspace': 1.0,
    '\\hspace': 1.0,
}

_TEX_OPERATORS = {
    '\\sin', '\\cos', '\\tan', '\\cot', '\\sec', '\\csc',
    '\\arcsin', '\\arccos', '\\arctan',
    '\\sinh', '\\cosh', '\\tanh', '\\coth',
    '\\log', '\\ln', '\\exp', '\\lg',
    '\\lim', '\\min', '\\max', '\\sup', '\\inf',
    '\\det', '\\dim', '\\gcd', '\\hom', '\\ker',
    '\\deg', '\\arg', '\\mod',
}


# Commands that switch to text (upright) mode for their brace argument.
_TEXT_MODE_COMMANDS = {'\\text', '\\mathrm', '\\textrm', '\\textbf', '\\textit',
                       '\\mbox', '\\hbox'}


def _tokenize_tex(inner):
    """Split a TeX inner string into tokens for glyph assembly.

    Handles backslash commands (``\\pi``, ``\\alpha``) and single characters.
    Command aliases like ``\\degree`` are resolved to their Unicode equivalents.
    ``\\text{}``, ``\\mathrm{}`` etc. emit their contents as ``('text', ch)``
    tuples (upright glyphs).
    Returns None for complex expressions that can't be tokenized (e.g.
    commands with brace arguments like ``\\frac{1}{2}``).
    """
    tokens = []
    i = 0

    while i < len(inner):
        if inner[i] == '\\':
            j = i + 1
            while j < len(inner) and inner[j].isalpha():
                j += 1
            cmd = inner[i:j]
            # Text/mathrm commands: extract brace content as text-mode tokens
            if cmd in _TEXT_MODE_COMMANDS:
                if j >= len(inner) or inner[j] != '{':
                    return None
                # Find matching closing brace
                depth = 1
                k = j + 1
                while k < len(inner) and depth > 0:
                    if inner[k] == '{':
                        depth += 1
                    elif inner[k] == '}':
                        depth -= 1
                    k += 1
                brace_content = inner[j + 1:k - 1]
                for ch in brace_content:
                    if ch in ' \t':
                        tokens.append(' ')
                    else:
                        tokens.append(('text', ch))
                i = k
                continue
            # Other commands with brace args — too complex
            if j < len(inner) and inner[j] == '{':
                return None
            # Spacing commands
            if cmd in _TEX_SPACES:
                tokens.append(('space', _TEX_SPACES[cmd]))
                i = j
                continue
            # Operator names (\sin, \cos, …) — always upright
            if cmd in _TEX_OPERATORS:
                for ch in cmd[1:]:
                    tokens.append(('text', ch))
                i = j
                continue
            # Resolve aliases or keep as-is
            tokens.append(_COMMAND_ALIASES.get(cmd, cmd))
            i = j
        elif inner[i] in ' \t':
            tokens.append(' ')
            i += 1
        elif inner[i] in '{}^_':
            return None
        else:
            tokens.append(inner[i])
            i += 1
    return tokens
