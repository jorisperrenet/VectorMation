"""SEO presentation helpers for the VectorMation documentation."""

import json
from pathlib import Path
from xml.etree import ElementTree

BASE_URL = 'https://jorisperrenet.com/VectorMation/'

PAGE_TITLES = {
    'index': 'VectorMation: SVG Math Animation in Python',
    'installation': 'Install VectorMation: Python Math Animation Setup',
    'tutorial': 'VectorMation Tutorial: Create SVG Math Animations in Python',
    'reference': 'VectorMation API Reference: Shapes, Graphs, Charts and 3D',
    'attributes': 'Time-Varying Attributes in VectorMation',
    'animation': 'Preview and Export VectorMation SVG Animations',
    'graphing': 'Plot Mathematical Functions with VectorMation',
    'examples': 'VectorMation Examples: Math, Geometry and Physics',
    'advanced_examples': 'Advanced VectorMation Math and Physics Examples',
    'vs_manim': 'VectorMation vs Manim: SVG Output, Workflow and Examples',
}


def _page_url(pagename):
    return BASE_URL if pagename == 'index' else f'{BASE_URL}{pagename}.html'


def _label(title):
    """Turn a Sphinx title into a concise, plain-text breadcrumb label."""
    return title.split(' — ', 1)[0].split(' - ', 1)[0]


def _breadcrumbs(app, pagename, context):
    if pagename in {'index', 'search', 'genindex'}:
        return []

    title = _label(context.get('title', pagename.rsplit('/', 1)[-1].replace('_', ' ').title()))
    crumbs = [{'name': 'VectorMation', 'url': BASE_URL}]

    if pagename == 'reference':
        crumbs.append({'name': 'API Reference', 'url': None})
    elif pagename.startswith('reference/'):
        crumbs.append({'name': 'API Reference', 'url': f'{BASE_URL}reference.html'})
        crumbs.append({'name': title, 'url': None})
    else:
        crumbs.append({'name': title, 'url': None})

    return crumbs


def add_page_context(app, pagename, templatename, context, doctree):
    """Add canonical URLs, titles, and breadcrumb data to every content page."""
    context['pageurl'] = _page_url(pagename)
    context['seo_title'] = PAGE_TITLES.get(pagename)

    crumbs = _breadcrumbs(app, pagename, context)
    context['breadcrumbs'] = crumbs
    if crumbs:
        items = []
        for position, crumb in enumerate(crumbs, 1):
            item = {
                '@type': 'ListItem',
                'position': position,
                'name': crumb['name'],
            }
            if crumb['url']:
                item['item'] = crumb['url']
            items.append(item)
        context['breadcrumb_jsonld'] = json.dumps({
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': items,
        }, separators=(',', ':'))


def canonicalize_sitemap(app, exception):
    """Make the sitemap agree with the public canonical URL for the home page."""
    if exception or app.builder.name not in {'html', 'dirhtml'}:
        return

    sitemap = Path(app.outdir) / app.config.sitemap_filename
    if not sitemap.exists():
        return

    tree = ElementTree.parse(sitemap)
    namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    changed = False
    for location in tree.findall('.//sm:loc', namespace):
        if location.text == f'{BASE_URL}index.html':
            location.text = BASE_URL
            changed = True
    if changed:
        ElementTree.register_namespace('', namespace['sm'])
        tree.write(sitemap, xml_declaration=True, encoding='utf-8')


def setup(app):
    app.connect('html-page-context', add_page_context)
    app.connect('build-finished', canonicalize_sitemap)
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
