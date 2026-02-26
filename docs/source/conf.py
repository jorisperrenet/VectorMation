project = 'VectorMation'
author = 'Joris Perrenet'
copyright = '2023-2025 Joris Perrenet'

extensions = [
    'sphinx_design',
    'sphinx_copybutton',
    'sphinx.ext.mathjax',
]

exclude_patterns = ['_build']
html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_logo = '_static/logo.svg'
html_favicon = '_static/logo.svg'
html_title = 'VectorMation'

html_theme_options = {
    'light_css_variables': {
        'color-brand-primary': '#000000',
        'color-brand-content': '#000000',
    },
}
mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'
