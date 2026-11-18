from PIL import Image, ImageDraw, ImageFont, ImageChops
import io, json, math, urllib.parse, urllib.request

W, H = 1024, 1024
BG = (245, 241, 232)
RED = (176, 34, 34)
INK = (26, 24, 22)
GRAY = (140, 134, 120)
FDIR = "/usr/share/fonts/truetype/dejavu"
HERO_PROMPT = "Dramatic photojournalistic news photograph, military fighter jet flying low over calm gulf sea at golden hour, contrail, aircraft carrier silhouette on horizon, telephoto press photography, cinematic"
CAPTION = "US strikes IRGC site in the Gulf — regional exchanges widen"
LEAD = "US STRIKES IRGC SITE IN GULF AS WAR WITH IRAN FLARES"
DECK = "Qeshm Island hit; Tehran fires at Kuwait; oil jumps 4%"

def _font(size, bold=False, italic=False):
    if italic:
        c = [FDIR + "/DejaVuSans-Oblique.ttf", FDIR + "/DejaVuSans.ttf", FDIR + "/DejaVuSans-Bold.ttf"]
    elif bold:
        c = [FDIR + "/DejaVuSans-Bold.ttf", FDIR + "/DejaVuSans.ttf", FDIR + "/DejaVuSans-BoldOblique.ttf"]
    else:
        c = [FDIR + "/DejaVuSans.ttf", FDIR + "/DejaVuSans-Bold.ttf", FDIR + "/DejaVuSansOblique.ttf"]
    for p in c:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

def fetch_hero():
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(HERO_PROMPT) + "?width=1280&height=720&nologo=true&seed=19"
    img = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                img = Image.open(io.BytesIO(r.read())).convert("RGB")
            break
        except Exception:
            img = None
    if img is None:
        img = Image.new("RGB", (1280, 720), (26, 29, 36))
        img.paste(Image.new("RGB", (1280, 360), (40, 44, 54)), (0, 0))
        img.paste(Image.new("RGB", (1280, 360), (18, 20, 26)), (0, 360))
    w, h = img.size
    img = img.crop((0, 0, w, int(h * 0.94)))
    tw, th = 944, 560
    scale = max(tw / w, th / h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = int((nw - tw) / 2), int((nh - th) / 2)
    return img.crop((left, top, left + tw, top + th))

def vignette(img, factor=0.92):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    px = mask.load()
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    maxd = math.hypot(w, h)
    for y in range(h):
        for x in range(w):
            dd = math.hypot(x - cx, y - cy) / maxd
            px[x, y] = int(255 * (factor + (1 - factor) * max(0.0, 1 - dd * dd)))
    r, g, b = img.split()
    return Image.merge("RGB", (ImageChops.multiply(r, mask), ImageChops.multiply(g, mask), ImageChops.multiply(b, mask)))

def wrap(d, text, f, max_w, max_lines=2):
    words = text.split()
    lines, cur = [], words[0]
    for wd in words[1:]:
        cand = cur + " " + wd
        if d.textlength(cand, font=f) <= max_w:
            cur = cand
        else:
            lines.append(cur); cur = wd
    lines.append(cur)
    return lines[:max_lines]

def load_secondary():
    try:
        with open("news17-dense.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else None
        if items is None and isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list) and v:
                    items = v; break
        out = []
        if items:
            for it in items[:3]:
                hl = it.get("headline") or it.get("title") if isinstance(it, dict) else str(it)
                gl = it.get("summary") or it.get("deck") if isinstance(it, dict) else ""
                out.append((hl, gl))
        if len(out) == 3 and all(hl for hl, _ in out):
            return out
    except Exception:
        pass
    return [
        ("Trump lands in Manila, then Shenzhen", "Manila summit steers toward Shenzhen trade talks"),
        ("Ukraine hits Kerch Bridge again", "Fresh assault follows bridge reinforcement"),
        ("Canada and China cut tariffs", "Truce holds after weekend talks"),
    ]

def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 48], fill=(0, 0, 0))
    d.text((40, 8), "THE WORLD LEDGER", font=_font(30, bold=True), fill=(255, 255, 255))
    d.text((W - 40 - d.textlength("Wednesday, 18 November 2026 · Vol. I — No. 330", font=_font(12)), 10), "Wednesday, 18 November 2026 · Vol. I — No. 330", font=_font(12), fill=(255, 255, 255))
    d.line([0, 46, W, 46], fill=RED, width=2)
    hero = vignette(fetch_hero())
    img.paste(hero, (40, 52))
    region = img.crop((40, 572, 984, 612)).convert("RGBA")
    region = Image.alpha_composite(region, Image.new("RGBA", (944, 40), (0, 0, 0, 170))).convert("RGB")
    img.paste(region, (40, 572))
    d.text((271, 580), CAPTION, font=_font(16, italic=True), fill=(255, 255, 255))
    d.text((944 - d.textlength("Photo: Ledger / AI wire", font=_font(10)), 592), "Photo: Ledger / AI wire", font=_font(10), fill=(255, 255, 255))
    f = _font(30, bold=True)
    y = 630
    for ln in wrap(d, LEAD, f, 904):
        d.text((40, y), ln, font=f, fill=INK); y += 42
    d.text((40, 718), DECK, font=_font(20), fill=GRAY)
    d.line([40, 746, 984, 746], fill=RED, width=2)
    d.text((40, 764), "MEASLES STATUS LOST · VOYAGER 1 ONE LIGHT-DAY OUT · WORLD COURT ON ROHINGYA · RIO TINTO PAYS $250M", font=_font(12), fill=RED)
    stories = load_secondary()
    ry = 854
    x = 40
    for hl, gl in stories:
        size, f = 22, _font(22, bold=True)
        while d.textlength(hl, font=f) > 278 and size > 9:
            size -= 1; f = _font(size, bold=True)
        lines = wrap(d, hl, f, 278)
        d.line([x + 6, ry, x + 296, ry], fill=(150, 60, 60), width=2)
        y = ry + 18
        for ln in lines:
            d.text((x, y), ln, font=f, fill=INK); y += 32
        d.text((x, y + 12), gl, font=_font(11), fill=GRAY)
        x = x + 314
    d.rectangle([0, 968, W, H], fill=(0, 0, 0))
    fb = _font(12)
    d.text((40, 984), "ONE DAY. ONE PAGE. — 18 November 2026", font=fb, fill=(255, 255, 255))
    d.text((W - 40 - d.textlength("Ledger wire reports", font=fb), 984), "Ledger wire reports", font=fb, fill=(255, 255, 255))
    img.save("/root/makefun/news-image-20261118/entry19.png"); print("/root/makefun/news-image-20261118/entry19.png")


main()
