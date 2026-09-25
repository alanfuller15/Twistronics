"""Bundle the static guide into a single, offline-readable HTML file."""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
html = (HERE / "index.html").read_text()
html = html.replace('<link rel="stylesheet" href="style.css">',
                    '<style>'+ (HERE / "style.css").read_text() + '</style>')
html = re.sub(r'  <script src="(?:data|app)\.js" defer></script>\n', '', html)
for name in ("data.js", "app.js"):
    code = (HERE / name).read_text().replace('</script', '<\\/script')
    html = html.replace('</body>', '<script>'+code+'</script>\n</body>')
html = html.replace('href="favicon.svg"', 'href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 40 40\'%3E%3Crect width=\'40\' height=\'40\' fill=\'%2309151f\'/%3E%3Ctext x=\'10\' y=\'29\' fill=\'%2377e3ed\' font-size=\'26\'%3ET%3C/text%3E%3C/svg%3E"')
base = 'https://github.com/alanfuller15/Twistronics/blob/docs/interactive-learning-atlas/docs/interactive-guide/'
for name in ('sources.json', 'data.js'):
    html = html.replace('href="'+name+'"', 'href="'+base+name+'"')
(HERE / "explorer.html").write_text(html)
print(f'Wrote standalone explorer.html ({len(html.encode()):,} bytes).')
