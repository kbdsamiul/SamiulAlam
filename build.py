"""
build.py — Samiul Alam Academic Website Builder
================================================
Reads data.json (exported from admin.html) and injects
all dynamic content into index.html.

Run automatically by GitHub Actions when data.json changes.
You never need to run this manually.
"""

import json
import re
from datetime import datetime

# ── Load data ────────────────────────────────────────────────
try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✓ Loaded data.json")
except FileNotFoundError:
    print("✗ data.json not found — nothing to do")
    exit(0)
except json.JSONDecodeError as e:
    print(f"✗ data.json is invalid: {e}")
    exit(1)

# ── Load base index.html ─────────────────────────────────────
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
print(f"✓ Loaded index.html ({len(html):,} chars)")

# ── Helper functions ─────────────────────────────────────────
def fmt_authors(text):
    """Convert **Name** to <span class="me">Name</span>"""
    return re.sub(r'\*\*(.+?)\*\*', r'<span class="me">\1</span>', text or '')

def safe(text):
    """Basic HTML safety for user input"""
    return (text or '').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def type_label(t):
    return {'oral':'Oral','poster':'Poster','invited':'Invited Talk','keynote':'Keynote'}.get(t, t or 'Oral')

# ── Build HTML blocks ────────────────────────────────────────

def build_publications(pubs):
    if not pubs:
        return ''
    items = []
    for p in pubs:
        doi_tag = f'<a href="{safe(p.get("doi",""))}" class="tag tag-doi" target="_blank" rel="noopener">DOI ↗</a>' if p.get('doi') else ''
        review_tag = '<span class="tag tag-review">Under Review</span>' if p.get('status') == 'review' else ''
        accepted_tag = '<span class="tag tag-doi">Accepted</span>' if p.get('status') == 'accepted' else ''
        book_tag = '<span class="tag tag-bookchapter">Book Chapter</span>' if p.get('type') == 'book' else ''
        conf_tag = '<span class="tag tag-bookchapter">Conference</span>' if p.get('type') == 'conference' else ''
        items.append(f'''
      <div class="pub-card" style="border-left-color:var(--accent-mid)">
        <div class="pub-number">NEW · {safe(p.get("year","TBD"))}</div>
        <div class="pub-authors">{fmt_authors(p.get("authors",""))}</div>
        <div class="pub-title">{safe(p.get("title",""))}</div>
        <div class="pub-venue">{safe(p.get("venue",""))}</div>
        <div class="pub-tags">{doi_tag}{review_tag}{accepted_tag}{book_tag}{conf_tag}</div>
      </div>''')
    return '\n'.join(items)


def build_talks(talks):
    if not talks:
        return ''
    items = []
    for t in talks:
        ptype = 'poster' if t.get('type') == 'poster' else 'oral'
        img_html = f'<img src="{t["img"]}" style="width:100px;height:65px;object-fit:cover;border-radius:6px;margin-bottom:.4rem;display:block"/>' if t.get('img') else ''
        meta_parts = [p for p in [t.get('date',''), t.get('loc','')] if p]
        items.append(f'''
      <div class="pres-item">
        <span class="pres-type {ptype}">{type_label(t.get("type","oral"))}</span>
        <div class="pres-body">
          {img_html}
          <div class="pres-conf">{safe(t.get("conf",""))}</div>
          <div class="pres-meta">{" · ".join(meta_parts)}</div>
        </div>
      </div>''')
    return '\n'.join(items)


def build_gallery(gallery):
    if not gallery:
        return ''
    items = []
    for g in gallery:
        cap = f'<div style="font-size:.75rem;color:var(--text-muted);padding:.5rem .75rem">{safe(g.get("caption",""))}</div>' if g.get('caption') else ''
        items.append(f'''
        <div style="border-radius:10px;overflow:hidden;background:var(--bg-subtle);border:1px solid var(--border)">
          <img src="{g["src"]}" alt="{safe(g.get("caption",""))}" style="width:100%;height:150px;object-fit:cover;display:block"/>
          {cap}
        </div>''')
    return f'''
<section id="gallery-section">
  <div class="container">
    <div class="section-label">Gallery</div>
    <h2 class="section-title">Photos</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem">
      {''.join(items)}
    </div>
  </div>
</section>'''


def build_awards(awards):
    if not awards:
        return ''
    items = []
    for a in awards:
        logo_html = f'<img src="{a["logo"]}" style="height:32px;border-radius:5px;object-fit:contain;flex-shrink:0"/>' if a.get('logo') else ''
        org_text = f' — {safe(a.get("org",""))}' if a.get('org') else ''
        items.append(f'''
      <div class="workshop-item">
        {logo_html}
        <div class="workshop-text"><strong>{safe(a.get("title",""))}</strong>{org_text}</div>
        <div class="workshop-year">{safe(a.get("year",""))}</div>
      </div>''')
    return '\n'.join(items)


def build_memberships(mems):
    if not mems:
        return ''
    items = []
    for m in mems:
        items.append(f'''
      <div class="member-item">
        <div class="member-name">{safe(m.get("name",""))}</div>
        <div class="member-period">{safe(m.get("period",""))}</div>
      </div>''')
    return '\n'.join(items)


def build_experience(exps):
    if not exps:
        return ''
    items = []
    for e in exps:
        period_html = f'<div class="exp-period">{safe(e.get("period",""))}</div>' if e.get('period') else ''
        project_html = f'<div class="exp-project">{safe(e.get("project",""))}</div>' if e.get('project') else ''
        duties = e.get('duties', [])
        if isinstance(duties, str):
            duties = [d.strip() for d in duties.split('\n') if d.strip()]
        duties_html = f'<ul class="exp-bullets">{"".join(f"<li>{safe(d)}</li>" for d in duties)}</ul>' if duties else ''
        ref_html = ''
        if e.get('refName'):
            email_part = f' — <a href="mailto:{safe(e.get("refEmail",""))}">{safe(e.get("refEmail",""))}</a>' if e.get('refEmail') else ''
            ref_html = f'<div class="exp-ref"><strong>Reference:</strong> {safe(e.get("refName",""))}{email_part}</div>'
        items.append(f'''
      <div class="exp-card">
        <div class="exp-header">
          <div class="exp-title">{safe(e.get("role",""))}</div>
          {period_html}
        </div>
        <div class="exp-org">{safe(e.get("org",""))}</div>
        {project_html}
        {duties_html}
        {ref_html}
      </div>''')
    return '\n'.join(items)


def build_workshops(workshops):
    if not workshops:
        return ''
    items = []
    for w in workshops:
        org_text = f' — {safe(w.get("org",""))}' if w.get('org') else ''
        items.append(f'''
      <div class="workshop-item">
        <div class="workshop-text"><strong>{safe(w.get("title",""))}</strong>{org_text}</div>
        <div class="workshop-year">{safe(w.get("date",""))}</div>
      </div>''')
    return '\n'.join(items)


# ── Inject into HTML ─────────────────────────────────────────

def inject(html, marker, content):
    """Insert content right before the marker comment"""
    if marker not in html:
        print(f"  ⚠ Marker not found: {marker}")
        return html
    return html.replace(marker, content + '\n    ' + marker)

def replace_marker(html, marker, content):
    """Replace marker entirely with content"""
    if marker not in html:
        print(f"  ⚠ Marker not found: {marker}")
        return html
    return html.replace(marker, content)

pubs      = data.get('publications', [])
talks     = data.get('talks', [])
gallery   = data.get('gallery', [])
awards    = data.get('awards', [])
mems      = data.get('memberships', [])
exps      = data.get('experience', [])
workshops = data.get('workshops', [])

print(f"\n📊 Content to inject:")
print(f"   Publications : {len(pubs)}")
print(f"   Talks        : {len(talks)}")
print(f"   Gallery      : {len(gallery)}")
print(f"   Awards       : {len(awards)}")
print(f"   Memberships  : {len(mems)}")
print(f"   Experience   : {len(exps)}")
print(f"   Workshops    : {len(workshops)}")

# Inject each section
html = inject(html, '<!-- DYNAMIC_PUBS_END -->',    build_publications(pubs))
html = inject(html, '<!-- DYNAMIC_TALKS_END -->',   build_talks(talks))
html = inject(html, '<!-- DYNAMIC_AWARDS_END -->',  build_awards(awards))
html = inject(html, '<!-- DYNAMIC_MEMS_END -->',    build_memberships(mems))
html = inject(html, '<!-- DYNAMIC_EXP_END -->',     build_experience(exps))
html = inject(html, '<!-- DYNAMIC_WS_END -->',      build_workshops(workshops))

# Gallery replaces its own section marker
html = replace_marker(html, '<!-- DYNAMIC_GALLERY -->', build_gallery(gallery))

# Update hero stats
pub_count  = 12 + len(pubs)
talk_count = 5  + len(talks)
html = re.sub(r'id="pub-count">[^<]+<',  f'id="pub-count">{pub_count}<',  html)
html = re.sub(r'id="talk-count">[^<]+<', f'id="talk-count">{talk_count}<', html)

# Stamp build date in footer
build_time = datetime.utcnow().strftime('%d %b %Y %H:%M UTC')
html = html.replace(
    '<!-- BUILD_TIMESTAMP -->',
    f'<span style="color:var(--text-faint);font-size:.72rem"> · Last updated {build_time}</span>'
)

# ── Write output ─────────────────────────────────────────────
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ index.html rebuilt successfully ({len(html):,} chars)")
print(f"   Build time: {build_time}")
