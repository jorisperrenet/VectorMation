project = 'VectorMation'
author = 'Joris Perrenet'
copyright = '2023-2025 Joris Perrenet'

extensions = [
    'sphinx_design',
    'sphinx_copybutton',
    'sphinx.ext.mathjax',
    'sphinx_sitemap',
]

exclude_patterns = ['_build']
html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_logo = '_static/logo.svg'
html_favicon = '_static/logo.svg'
html_title = 'VectorMation'

# Canonical URL for every page (and required by sphinx-sitemap).
html_baseurl = 'https://jorisperrenet.com/VectorMation/'

# Default <meta name="description"> applied to every page (per-page descriptions
# can override via `:description:` in the page's docinfo).
html_meta = {
    'description': 'VectorMation: a vector-based math animation engine in Python. An SVG-driven alternative to manim — render mathematical animations as small, scalable SVGs.',
    'keywords': 'VectorMation, math animation, SVG animation, manim alternative, Python animation library, mathematical visualization, Joris Perrenet',
    'author': 'Joris Perrenet',
}

html_theme_options = {
    'light_css_variables': {
        'color-brand-primary': '#000000',
        'color-brand-content': '#000000',
    },
}
mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'

# sphinx-sitemap settings — emits sitemap.xml at the docs root.
sitemap_url_scheme = '{link}'
