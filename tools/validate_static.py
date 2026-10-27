from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1] / 'website'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.h1 = set(), [], 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'img':
            assert 'alt' in attrs, 'Image without alt text'
        self.links.extend(attrs[key] for key in ('href', 'src') if key in attrs)

pages = {}
for file in ROOT.glob('*.html'):
    if file.name.startswith('.'):
        continue
    content = file.read_text(encoding='utf-8')
    assert '{{' not in content, f'Unresolved placeholder: {file.name}'
    page = Page()
    page.feed(content)
    assert page.h1 == 1, f'Expected one h1: {file.name}'
    pages[file.name] = page
assert len(pages) >= 7, 'Missing website pages'
for name, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = unquote(url.path) or name
        assert (ROOT / target).is_file(), f'{name}: missing file {target}'
        if url.fragment and target in pages:
            assert url.fragment in pages[target].ids, f'{name}: missing anchor {link}'
print(f'PASS: {len(pages)} pages; local links, images, anchors and headings checked.')
