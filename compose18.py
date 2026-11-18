#!/usr/bin/env python3
"""Front-page composer: news-image-20261118 (world news of 18 November 2026).

Draws a broadsheet front page with PIL: masthead, lead headline, a self-drawn
world-map hero panel (Natural Earth 110m coastlines, public domain) marking the
day's hotspots, two columns of secondary headlines, an "also today" strip and
a footer. Output: entry.png (1024x1024, < 1 MiB).

Layout: masthead band with red rule, lead block, world-map hero panel with
numbered hotspots and legend, secondary headline columns, "also today" strip,
footer.
"""
from PIL import Image, ImageDraw, ImageFont
import json, math, os

W, H = 1024, 1024
WHITE = (255, 255, 255); INK = (18, 18, 18); GREY = (78, 78, 78)
RED = (170, 22, 22); PAPER = (246, 244, 238); GOLD = (196, 150, 20)
NAVY = (17, 38, 66); LAND = (226, 222, 208); LGREY = (196, 196, 192)
MASTHEAD_VOL = (200, 200, 200); MASTHEAD_DATE = (225, 225, 225)
GRATICULE_LINE = (28, 52, 84); LEGEND_BG = (10, 26, 46); LEGEND_EDGE = (80, 100, 130)
LEGEND_INK = (235, 235, 235); MAP_SOURCE = (150, 150, 150); STORM = (150, 200, 235)
MARGIN_X = 30; HERO_W = W - 2 * MARGIN_X; HERO_H = 344; LEGEND_H = 76; LEAD_TOP = 138
COL_GAP = (W - 2 * MARGIN_X) // 2; COL_W = COL_GAP - 44; COL_X0 = MARGIN_X; COL_X1 = MARGIN_X + COL_GAP

def font(sz, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try: return ImageFont.truetype(p, sz)
    except Exception: return ImageFont.load_default()

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------- Masthead ----------
d.rectangle([0, 0, W, 106], fill=INK)
d.text((30, 16), "THE WORLD LEDGER", font=font(40, True), fill=WHITE)
d.text((W-330, 28), "Vol. I — No. 329", font=font(22), fill=MASTHEAD_VOL)
d.text((W-424, 62), "Wednesday, 18 November 2026", font=font(21), fill=MASTHEAD_DATE)
d.rectangle([0, 106, W, 114], fill=RED)

# ---------- Lead headline ----------
def wrap(text, f, maxw):
    words = text.split(); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) > maxw and cur:
            lines.append(cur); cur = w_
        else:
            cur = t
    lines.append(cur)
    return lines

y = LEAD_TOP
lead = "US STRIKES IRGC SITE IN GULF AS WAR WITH IRAN FLARES ANEW"
f_lead = font(39, True)
for l in wrap(lead, f_lead, W - 64):
    d.text((30, y), l, font=f_lead, fill=INK); y += 47
d.text((30, y + 2), "Qeshm Island hit; Tehran fires at Kuwait — regional exchanges widen", font=font(23), fill=GREY)
y += 46

# ---------- Hero: world map with the day's hotspots ----------
MW, MH = HERO_W, HERO_H
mx, my = MARGIN_X, y
d.rectangle([mx, my, mx + MW, my + MH], fill=NAVY)

def proj(lon, lat):
    # equirectangular, lon -168..190, lat -58..80 mapped to map area above the legend
    mh = MH - LEGEND_H
    px = mx + 8 + (lon + 168) / 358 * (MW - 16)
    py = my + 8 + (80 - lat) / 138 * (mh - 16)
    x0, y0, x1, y1 = mx + 1, my + 1, mx + MW - 1, my + mh - 1
    return min(max(px, x0), x1), min(max(py, y0), y1)

gj = json.load(open("world110m.geojson"))
for feat in gj["features"]:
    g = feat["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        ring = poly[0]
        pts = [proj(lo, la) for lo, la in ring]
        if len(pts) > 2:
            d.polygon(pts, fill=LAND)

# graticule
for lon in range(-150, 181, 30):
    a, b = proj(lon, 78), proj(lon, -56)
    d.line([a, b], fill=GRATICULE_LINE, width=1)
for lat in range(-40, 81, 20):
    a, b = proj(-166, lat), proj(188, lat)
    d.line([a, b], fill=GRATICULE_LINE, width=1)

def dot(lon, lat, r, col, ring=WHITE):
    px, py = proj(lon, lat)
    d.ellipse([px - r - 3, py - r - 3, px + r + 3, py + r + 3], outline=ring, width=2)
    d.ellipse([px - r, py - r, px + r, py + r], fill=col)
    return px, py

def star(px, py, r, col):
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((px + rr * math.cos(ang), py - rr * math.sin(ang)))
    d.polygon(pts, fill=col, outline=WHITE)

def lab(px, py, text, f, col=WHITE, dx=12, dy=-6):
    d.text((px + dx, py + dy), text, font=f, fill=col)

f_m = font(19, True)
f_s = font(15)

def marker(lon, lat, n, col, r=12):
    px, py = proj(lon, lat)
    d.ellipse([px - r - 3, py - r - 3, px + r + 3, py + r + 3], outline=WHITE, width=2)
    d.ellipse([px - r, py - r, px + r, py + r], fill=col)
    f = font(17, True)
    tw = d.textlength(str(n), font=f)
    d.text((px - tw / 2, py - 10), str(n), font=f, fill=WHITE)
    return px, py

# 1 Manila, 2 Shenzhen, 3 Kerch, 4 Gulf/Qeshm, 5 Cyclone Akvan
marker(121.0, 14.6, 1, GOLD)
marker(114.1, 22.5, 2, GOLD)
marker(36.5, 45.3, 3, RED)
marker(56.3, 26.7, 4, RED)
ax_c, ay_c = proj(85.4, 13.1)
for rr, wdt in ((27, 3), (18, 3), (9, 2)):
    d.arc([ax_c - rr, ay_c - rr, ax_c + rr, ay_c + rr], start=200, end=80, fill=STORM, width=wdt)
marker(85.4, 13.1, 5, (52, 110, 160), r=11)

# ---------- legend bar ----------
ly = my + MH - LEGEND_H
d.rectangle([mx, ly, mx + MW, my + MH], fill=LEGEND_BG)
d.line([mx, ly, mx + MW, ly], fill=LEGEND_EDGE, width=2)
f_l = font(17, True); f_ls = font(16)

def legend_item(x, y_, n, col, text):
    r = 10
    d.ellipse([x, y_, x + 2 * r, y_ + 2 * r], fill=col)
    f = font(14, True)
    tw = d.textlength(str(n), font=f)
    d.text((x + r - tw / 2, y_ + 3), str(n), font=f, fill=WHITE)
    d.text((x + 2 * r + 9, y_ + 1), text, font=f_ls, fill=LEGEND_INK)

legend_item(mx + 14, ly + 12, 1, GOLD, "Trump in Manila — ASEAN/Quad")
legend_item(mx + 330, ly + 12, 2, GOLD, "Shenzhen: Xi, Trump, Putin Thu")
legend_item(mx + 646, ly + 12, 3, RED, "Kerch Bridge struck again")
legend_item(mx + 14, ly + 44, 4, RED, "US–Iran strikes widen in Gulf")
legend_item(mx + 330, ly + 44, 5, (52, 110, 160), "Cyclone Akvan nears India")
d.text((mx + 646 + 29, ly + 46), "Map: Natural Earth (PD)", font=font(15), fill=MAP_SOURCE)

# Small GREY edition mark for the map caption row.
# It tags the broadcast number and GMT reference beside the caption.
# The thin GREY bar under it separates stamp from caption.
def edition_stamp(d):
    def stamp_box():
        return [W - 30 - 220, my + MH + 2, W - 30, my + MH + 6]

    label = "EDITION 329 / GMT — WED"
    f = font(15)
    w = d.textlength(label, font=f)
    d.rectangle(stamp_box(), fill=GREY)
    d.text((W - 30 - w, my + MH + 6), label, font=f, fill=GREY)

# map caption
d.text((mx, my + MH + 6), "MAP: Where the day happened — 18 November 2026", font=font(17), fill=GREY)
edition_stamp(d)
d.rectangle([mx, my, mx + MW, my + MH], outline=INK, width=2)
y = my + MH + 42

# ---------- Secondary headlines ----------
col2 = [
    ("Trump lands in Manila, then Shenzhen",
     "Xi greets him in China ahead of three-way talks with Putin at APEC"),
    ("Ukraine hits Kerch Bridge for second day running",
     "Road span damaged in missile-and-drone strike; rail service resumes"),
]
col3 = [
    ("Canada and China cut tariffs in trade thaw",
     "Carney clinches reset as leaders gather for summits across Asia"),
    ("Cyber outages rattle Apple, NSA and airlines",
     "White House denies attacks after week of banking and tech failures"),
]
def draw_story(x, y, headline, dek, width):
    lines = wrap(headline, font(24, True), width)
    d.rectangle([x, y, x + 5, y + 8 + len(lines) * 29], fill=RED)
    yy = y
    for l in lines:
        d.text((x + 13, yy), l, font=font(24, True), fill=INK); yy += 29
    for sl in wrap(dek, font(16), width - 22):
        d.text((x + 13, yy + 3), sl, font=font(16), fill=GREY); yy += 21
    return yy + 16

def draw_col(x, items, width, y0):
    yy = y0
    for h, s in items:
        yy = draw_story(x, yy, h, s, width)
    return yy

e1 = draw_col(COL_X0, col2, COL_W, y)
e2 = draw_col(COL_X1, col3, COL_W, y)
end = max(e1, e2)

# ---------- "Also today" strip ----------
yy2 = end + 14
d.rectangle([30, yy2, W - 30, yy2 + 2], fill=GREY)
also_lines = [
    "ALSO TODAY — US loses measles elimination status · World Court moves on Rohingya case · Voyager 1 now one light-day from Earth",
    "Peltola wins Alaska Senate race · Rio Tinto pays $250m over PNG mine damage · 'human' is Cambridge Dictionary word of the year",
]
for i, t in enumerate(also_lines):
    col = INK if i == 0 else GREY
    f = font(15)
    while d.textlength(t, font=f) > W - 70:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", f.size - 1)
    d.text((30, yy2 + 12 + i * 22), t, font=f, fill=col)

# ---------- Footer ----------
d.rectangle([0, H - 58, W, H], fill=INK)
d.text((30, H - 44), "ONE DAY. ONE PAGE. — world news of 18 November 2026", font=font(20, True), fill=WHITE)

img.save("entry.png")
print("saved", img.size, os.path.getsize("entry.png"), "bytes")
