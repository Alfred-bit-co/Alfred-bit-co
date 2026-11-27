#!/usr/bin/env python3
"""Generate the self-hosted SVG assets for the Alfred-bit-co profile README.

Usage (from the repository root):
    python3 .github/assets-src/generate.py assets

Icon data: si.json (Simple Icons, CC0) and lucide.json (Lucide, ISC).

Every asset exists in a dark and a light variant so the README follows the
viewer's GitHub theme (via <picture> + prefers-color-scheme).
"""
import json
import os
import sys
from html import escape

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
os.makedirs(OUT, exist_ok=True)

SI = json.load(open(os.path.join(os.path.dirname(__file__), "si.json")))
LU = json.load(open(os.path.join(os.path.dirname(__file__), "lucide.json")))

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace"

THEMES = {
    "dark": {
        "bg1": "#0B1220", "bg2": "#0D1117", "surface": "#161B22", "surface2": "#1C2230",
        "border": "#30363D", "text": "#E6EDF3", "muted": "#8B949E", "faint": "#6E7681",
        "a1": "#2DD4BF", "a2": "#38BDF8", "chip": "#1F2937", "chipText": "#C9D1D9",
        "dot": "#8B949E", "ok": "#3FB950", "mono_logo": "#E6EDF3",
    },
    "light": {
        "bg1": "#FFFFFF", "bg2": "#F6F8FA", "surface": "#FFFFFF", "surface2": "#F6F8FA",
        "border": "#D0D7DE", "text": "#1F2328", "muted": "#59636E", "faint": "#818B98",
        "a1": "#0F766E", "a2": "#0369A1", "chip": "#EEF2F6", "chipText": "#31383F",
        "dot": "#8C959F", "ok": "#1A7F37", "mono_logo": "#1F2328",
    },
}


def text_w(s, size, mono=False, weight=400):
    """Rough text-width estimate, deliberately generous across system fonts."""
    k = 0.62 if mono else (0.55 if weight >= 600 else 0.52)
    return len(s) * size * k


def lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def mix(hexc, other, a):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    o = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * a):02X}" for x, y in zip(c, o))


def lucide(name, x, y, size, color, sw=2):
    s = size / 24
    return (f'<g transform="translate({x} {y}) scale({s})" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{LU[name]}</g>')


def icon_any(icon, x, y, size, color):
    if icon.startswith("si:"):
        return (f'<g transform="translate({x} {y}) scale({size / 24})">'
                f'<path d="{SI[icon[3:]]["path"]}" fill="{color}"/></g>')
    return lucide(icon, x, y, size, color)


def write(name, svg):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(svg.strip() + "\n")


# --------------------------------------------------------------------------- banner
def banner(t, mode):
    W, H = 1280, 360
    nodes = [(905, 95), (990, 60), (1080, 110), (1175, 70), (960, 175), (1060, 205),
             (1160, 170), (1225, 245), (920, 270), (1015, 295), (1120, 285), (1200, 320)]
    edges = [(0, 1), (1, 2), (2, 3), (0, 4), (1, 4), (2, 5), (4, 5), (5, 6), (3, 6), (6, 7),
             (4, 8), (8, 9), (5, 9), (9, 10), (10, 6), (10, 11), (7, 11), (2, 6)]
    lines = "".join(
        f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}"/>'
        for a, b in edges)
    circles = ""
    for i, (x, y) in enumerate(nodes):
        r = 6 if i in (2, 5, 9) else 3.5
        circles += f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#acc)"/>'
    pulses = ""
    for i, (idx, delay) in enumerate([(2, 0), (5, 1.2), (9, 2.4)]):
        x, y = nodes[idx]
        pulses += (f'<circle cx="{x}" cy="{y}" r="6" fill="none" stroke="{t["a1"]}" stroke-width="1.5">'
                   f'<animate attributeName="r" values="6;22" dur="3.6s" begin="{delay}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0.7;0" dur="3.6s" begin="{delay}s" repeatCount="indefinite"/>'
                   f'</circle>')

    # pills
    pills = []
    x = 72
    y = 290
    status = "Available for freelance projects"
    sw = text_w(status, 15, weight=600) + 46
    pills.append(
        f'<rect x="{x}" y="{y}" width="{sw:.0f}" height="36" rx="18" fill="{t["ok"]}" fill-opacity="0.12" '
        f'stroke="{t["ok"]}" stroke-opacity="0.45"/>'
        f'<circle cx="{x + 20}" cy="{y + 18}" r="5" fill="{t["ok"]}">'
        f'<animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></circle>'
        f'<text x="{x + 34}" y="{y + 23.5}" font-family="{SANS}" font-size="15" font-weight="600" fill="{t["ok"]}">{status}</text>')
    x += sw + 12
    for label in ["Full-Stack", "AI Integration", "Security"]:
        w = text_w(label, 15, weight=600) + 32
        pills.append(
            f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="36" rx="18" fill="{t["surface2"]}" stroke="{t["border"]}"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 23.5}" text-anchor="middle" font-family="{SANS}" font-size="15" '
            f'font-weight="600" fill="{t["chipText"]}">{label}</text>')
        x += w + 10

    glow_op = 0.22 if mode == "dark" else 0.12
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
  <title id="title">Alfred AYITOU — AI-Oriented Full-Stack Developer</title>
  <desc id="desc">Software engineer based in Lomé, Togo, building real-world web products and integrating AI into them.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/>
    </linearGradient>
    <linearGradient id="acc" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{t["a1"]}"/><stop offset="1" stop-color="{t["a2"]}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.82" cy="0.2" r="0.55">
      <stop offset="0" stop-color="{t["a1"]}" stop-opacity="{glow_op}"/>
      <stop offset="1" stop-color="{t["a1"]}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.1" fill="{t["dot"]}"/>
    </pattern>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0.35" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/>
    </linearGradient>
    <mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <clipPath id="clip"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24"/></clipPath>
  </defs>
  <g clip-path="url(#clip)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#dots)" opacity="0.28" mask="url(#m)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>
    <g stroke="url(#acc)" stroke-width="1.2" stroke-opacity="0.35">{lines}</g>
    {pulses}
    <g opacity="0.95">{circles}</g>
    <rect x="0" y="0" width="6" height="{H}" fill="url(#acc)"/>
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="none" stroke="{t["border"]}"/>

  <text x="72" y="84" font-family="{MONO}" font-size="15" font-weight="600" letter-spacing="3" fill="{t["a1"]}">SOFTWARE ENGINEER  ·  LOMÉ, TOGO</text>
  <text x="70" y="160" font-family="{SANS}" font-size="66" font-weight="700" letter-spacing="-1.5" fill="{t["text"]}">Alfred AYITOU</text>
  <text x="72" y="209" font-family="{SANS}" font-size="30" font-weight="600" fill="url(#acc)">AI-Oriented Full-Stack Developer</text>
  <text x="72" y="250" font-family="{SANS}" font-size="18" fill="{t["muted"]}">I build real-world web applications and integrate AI into products that solve practical problems.</text>
  {"".join(pills)}
</svg>'''


# --------------------------------------------------------------------------- project cards
PROJECTS = [
    {
        "file": "project-ucao-marketplace", "title": "UCAO Marketplace", "icon": "shopping-bag",
        "badge": "FLAGSHIP",
        "desc": ["Student-to-student marketplace for UCAO-UUT,", "with seller plans, payments and AI features."],
        "chips": ["Full-stack", "JWT auth", "PostgreSQL", "Payments", "AI"],
    },
    {
        "file": "project-dataanalys-ai", "title": "DataAnalys.AI", "icon": "chart-column",
        "badge": "AI",
        "desc": ["AI-oriented project that turns raw data", "into clear, useful insights."],
        "chips": ["AI", "Data analysis", "Insights"],
    },
    {
        "file": "project-panier-dor", "title": "Panier d'Or", "icon": "shopping-basket",
        "badge": "CLIENT",
        "desc": ["Digital commerce platform built around", "a real-world business use case in Lomé."],
        "chips": ["E-commerce", "Real business", "Web app"],
    },
    {
        "file": "project-portfolio", "title": "Portfolio", "icon": "panels-top-left",
        "badge": "WEB",
        "desc": ["My personal developer portfolio", "and project showcase."],
        "chips": ["Showcase", "Front-end", "Responsive"],
    },
]


def card(p, t):
    W, H = 600, 236
    chips = ""
    x = 28
    for c in p["chips"]:
        w = text_w(c, 14, mono=True) + 22
        chips += (f'<rect x="{x:.0f}" y="180" width="{w:.0f}" height="32" rx="9" fill="{t["chip"]}" stroke="{t["border"]}" stroke-opacity="0.6"/>'
                  f'<text x="{x + w / 2:.0f}" y="201" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{t["chipText"]}">{escape(c)}</text>')
        x += w + 8
    bw = text_w(p["badge"], 11, mono=True) + 20
    desc = "".join(
        f'<text x="28" y="{114 + i * 28}" font-family="{SANS}" font-size="20" fill="{t["muted"]}">{escape(line)}</text>'
        for i, line in enumerate(p["desc"]))
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(p["title"])} project">
  <defs>
    <linearGradient id="acc" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{t["a1"]}"/><stop offset="1" stop-color="{t["a2"]}"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t["surface"]}" stroke="{t["border"]}"/>
  <rect x="28" y="24" width="44" height="44" rx="11" fill="{t["a1"]}" fill-opacity="0.12" stroke="{t["a1"]}" stroke-opacity="0.35"/>
  {lucide(p["icon"], 39, 35, 22, t["a1"])}
  <text x="88" y="55" font-family="{SANS}" font-size="26" font-weight="700" fill="{t["text"]}">{escape(p["title"])}</text>
  <rect x="{W - 72 - bw:.0f}" y="31" width="{bw:.0f}" height="24" rx="12" fill="none" stroke="url(#acc)"/>
  <text x="{W - 72 - bw / 2:.0f}" y="47.5" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1" fill="{t["a1"]}">{p["badge"]}</text>
  {lucide("arrow-up-right", W - 52, 33, 22, t["muted"])}
  {desc}
  {chips}
</svg>'''


# --------------------------------------------------------------------------- tech stack
STACK = [
    ("Languages", [("si", "python", "Python"), ("si", "javascript", "JavaScript"), ("si", "typescript", "TypeScript"),
                   ("si", "openjdk", "Java"), ("si", "html5", "HTML"), ("si", "css", "CSS"), ("si", "php", "PHP")]),
    ("Frameworks", [("si", "flask", "Flask"), ("si", "nextdotjs", "Next.js"), ("si", "tailwindcss", "Tailwind")]),
    ("Data & Backend", [("si", "postgresql", "PostgreSQL"), ("si", "mysql", "MySQL"), ("si", "supabase", "Supabase"),
                        ("si", "firebase", "Firebase"), ("si", "sqlalchemy", "SQLAlchemy")]),
    ("AI & Security", [("lu", "sparkles", "LLM APIs"), ("lu", "webhook", "REST APIs"), ("si", "jsonwebtokens", "JWT"),
                       ("lu", "key-round", "OAuth"), ("lu", "smartphone", "Mobile Money")]),
    ("DevOps & Tools", [("si", "docker", "Docker"), ("si", "git", "Git"), ("si", "github", "GitHub"),
                        ("si", "prometheus", "Prometheus"), ("si", "grafana", "Grafana")]),
]
DARK_LOGOS = {"openjdk", "nextdotjs", "github", "jsonwebtokens", "flask", "sqlalchemy"}


def stack(t, mode):
    LABEL_W, TILE, GAP, ROW_H, PAD = 210, 60, 36, 112, 36
    W = PAD * 2 + LABEL_W + 7 * TILE + 6 * GAP
    H = PAD * 2 + len(STACK) * ROW_H - 12
    rows = ""
    for r, (label, items) in enumerate(STACK):
        y = PAD + r * ROW_H
        if r:
            rows += f'<line x1="{PAD}" y1="{y - 14}" x2="{W - PAD}" y2="{y - 14}" stroke="{t["border"]}" stroke-opacity="0.6"/>'
        rows += (f'<text x="{PAD}" y="{y + 36}" font-family="{MONO}" font-size="13" font-weight="700" '
                 f'letter-spacing="1.5" fill="{t["a1"]}">{escape(label.upper())}</text>')
        for i, (kind, key, name) in enumerate(items):
            x = PAD + LABEL_W + i * (TILE + GAP)
            rows += f'<rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="15" fill="{t["surface2"]}" stroke="{t["border"]}"/>'
            if kind == "si":
                ic = SI[key]
                color = t["mono_logo"] if (key in DARK_LOGOS and mode == "dark") or ic["hex"] in ("000000", "181717", "191919") else "#" + ic["hex"]
                if mode == "dark" and color.startswith("#") and lum(color) < 0.22:
                    color = mix(color, "#FFFFFF", 0.38)
                if key == "javascript" and mode == "light":
                    color = "#E2C400"
                s = 30 / 24
                rows += f'<g transform="translate({x + 15} {y + 15}) scale({s})"><path d="{ic["path"]}" fill="{color}"/></g>'
            else:
                rows += lucide(key, x + 15, y + 15, 30, t["a1"])
            rows += (f'<text x="{x + TILE / 2}" y="{y + TILE + 22}" text-anchor="middle" font-family="{SANS}" '
                     f'font-size="13" fill="{t["muted"]}">{escape(name)}</text>')
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack: Python, JavaScript, TypeScript, Java, HTML, CSS, PHP, Flask, Next.js, Tailwind CSS, PostgreSQL, MySQL, Supabase, Firebase, SQLAlchemy, LLM APIs, REST APIs, JWT, OAuth, Mobile Money, Docker, Git, GitHub, Prometheus, Grafana">
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{t["surface"]}" stroke="{t["border"]}"/>
  {rows}
</svg>'''


# --------------------------------------------------------------------------- buttons
BUTTONS = [
    ("btn-portfolio", "globe", "Portfolio", "alfred-bit-co.github.io"),
    ("btn-github", "si:github", "GitHub", "@Alfred-bit-co"),
    ("btn-location", "map-pin", "Based in", "Lomé, Togo"),
]


def button(icon, label, value, t):
    w = 60 + max(text_w(label, 12, mono=True), text_w(value, 16, weight=600)) + 28
    H = 56
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{H}" viewBox="0 0 {w:.0f} {H}" role="img" aria-label="{escape(label)}: {escape(value)}">
  <rect x="1" y="1" width="{w - 2:.0f}" height="{H - 2}" rx="14" fill="{t["surface"]}" stroke="{t["border"]}"/>
  {icon_any(icon, 18, 17, 22, t["a1"])}
  <text x="54" y="24" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.2" fill="{t["faint"]}">{escape(label.upper())}</text>
  <text x="54" y="43" font-family="{SANS}" font-size="16" font-weight="600" fill="{t["text"]}">{escape(value)}</text>
</svg>'''


for mode, t in THEMES.items():
    write(f"banner-{mode}.svg", banner(t, mode))
    write(f"stack-{mode}.svg", stack(t, mode))
    for p in PROJECTS:
        write(f'{p["file"]}-{mode}.svg', card(p, t))
    for f, icon, label, value in BUTTONS:
        write(f"{f}-{mode}.svg", button(icon, label, value, t))
print("ok", sorted(os.listdir(OUT)))
