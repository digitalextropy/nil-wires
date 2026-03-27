import os, re, glob

html_files = glob.glob("*.html")

# ── CHANGE 1: Text replacements ──
replacements = [
    ("Good morning, Your University", "Good morning, Blue Mountain State"),
    ("Your University", "Blue Mountain State"),
    ("State University", "Blue Mountain State"),
    ("Non-compliant", "Needs Review"),
    ("In Violation", "Needs Review"),
    ("Compliance Officer", "Reviewer"),
    ("Compliance Review", "Verification Review"),
]

def replace_certified(text):
    # Replace standalone "Certified" but not certificate/certification
    return re.sub(r'(?<![a-zA-Z])Certified(?!ion|e[sd]?|ing)', 'Verified', text)

def replace_compliant(text):
    # Replace standalone "Compliant" but not "Non-compliant" (already handled above)
    return re.sub(r'(?<!Non-)Compliant', 'Verified', text)

def replace_flagged(text):
    return re.sub(r'(?<![a-zA-Z])Flagged(?![a-zA-Z])', 'Needs Review', text)

# ── CHANGE 2: Search bar CSS + HTML ──
search_css = """
.nav-search-wrap{flex:1;max-width:280px;margin:0 16px;position:relative;}
.nav-search{width:100%;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);border-radius:6px;padding:5px 10px 5px 30px;font-family:'Outfit',sans-serif;font-size:12px;color:#fff;outline:none;}
.nav-search::placeholder{color:rgba(255,255,255,.35);}
.nav-search:focus{background:rgba(255,255,255,.15);border-color:rgba(255,255,255,.3);}
.nav-search-icon{position:absolute;left:9px;top:50%;transform:translateY(-50%);color:rgba(255,255,255,.35);font-size:13px;pointer-events:none;}
"""

search_html = """<div class="nav-search-wrap">
    <span class="nav-search-icon">\u2315</span>
    <input class="nav-search" type="text" placeholder="Search athlete or deal #\u2026"
      oninput="if(this.value.length>=3)window.location.href='nil-search.html?q='+encodeURIComponent(this.value)" />
  </div>"""

for f in html_files:
    if f == "index.html":
        continue  # index has no nav, handle separately

    with open(f, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Change 1: ordered replacements
    for old, new in replacements:
        content = content.replace(old, new)
    content = replace_compliant(content)
    content = replace_flagged(content)
    content = replace_certified(content)

    # Change 2a: inject CSS before </style>
    if ".nav-search-wrap" not in content:
        content = content.replace("</style>", search_css + "</style>")

    # Change 2b: inject search bar HTML after closing </div> of div.nav-links
    if "nav-search-wrap" not in content.split("</style>")[-1]:
        # Find the nav-links div and its closing tag
        # Pattern: </div>\n    <div class="nav-user"> — inject search widget before nav-user
        # Actually, spec says: after closing </div> of div.nav-links
        # Looking at the HTML, nav-links div closes, then nav-user div starts
        # We insert between them
        content = re.sub(
            r'(class="nav-link[^"]*">Benchmarks\s*<span class="nav-premium-tag">Premium</span></a>\s*</div>)',
            r'\1\n    ' + search_html,
            content
        )

    with open(f, "w", encoding="utf-8") as fh:
        fh.write(content)

print("Done processing", len(html_files)-1, "files (excluding index.html)")

# Show summary of changes
for f in sorted(html_files):
    if f == "index.html":
        continue
    with open(f, "r", encoding="utf-8") as fh:
        c = fh.read()
    has_search = "nav-search-wrap" in c
    has_bms = "Blue Mountain State" in c
    print(f"  {f}: search={has_search}, BMS={has_bms}")
