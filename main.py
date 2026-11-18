#!/usr/bin/env python3
"""news-image-20261117 v2 agent-B — one-page newspaper, genuinely different
from the kept Aa entry: navy inverted header (no serif masthead), ONE full-width
hero lead (Quad Manila), ranked TOP STORIES list + map in the right column,
two-column ALSO list. Sans typography throughout, white background.
Deterministic: no dates from system clock, no randomness.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
NAVY = (15, 42, 74)
RED = (200, 16, 46)
WHITE = (255, 255, 255)
PANEL = (239, 243, 248)
INK = (26, 26, 26)
GREY = (90, 90, 90)
SEA = (207, 227, 238)
LAND = (232, 217, 176)
RULE = (200, 200, 200)

FD = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FDB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FDB if bold else FD, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(draw, text, fnt, max_w, min_size=None):
    """Shorten with ellipsis until it fits one line."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while len(text) > 4 and draw.textlength(text + "…", font=fnt) > max_w:
        text = text[:-1].rstrip()
    return text + "…"


# ---------------- story data (43 stories, new order) ----------------
HERO = {
    "kicker": "ASIA · DIPLOMACY",
    "headline": "Trump holds his first Quad summit in Manila",
    "dek": "The four unveil critical-minerals deals; Putin reaches Shenzhen "
           "for Thursday's talks with Trump and Xi.",
    "flags": ["US", "INDIA", "JAPAN", "AUSTRALIA"],
}

NUMBERS = [
    ("$115.8BN", "Nvidia quarterly sales double"),
    ("11,000+", "Ebola cases in DR Congo"),
    ("1,441", "Russian drones in one night"),
    ("M6.6", "Quake felt off Darwin"),
]

# top stories 02-09: (number, headline, dek)
TOP = [
    ("02", "Ukraine says a Crimean Bridge road span fell into the sea",
     "Second strike in two days; Zelensky hails an “unprecedented operation”."),
    ("03", "Iran sends drones at a US radar in Bahrain; US hits back",
     "Bahrain and the US say all were downed; US jets then strike Qeshm."),
    ("04", "Gaza truce at risk of collapse, UN is told",
     "Board of Peace report; UN agencies say 1.4m face acute hunger."),
    ("05", "Nvidia's quarterly sales double to $115.8bn",
     "Reported after the close. Earlier the Dow fell 849 points (-1.6%)."),
    ("06", "Ebola cases in DR Congo top 11,000, WHO says",
     "Cases more than doubled in three months; about 5,400 have died."),
    ("07", "COP31 divided over a fossil-fuel phase-out",
     "Nations weigh the first draft; the Antalya talks end Friday."),
    ("08", "US, Mexico and Bolivia lose measles-free status",
     "PAHO cites a year of spread; the US has 5,700 cases in 2026."),
    ("09", "Serbia's student-led majority takes its seats",
     "Student List holds 140 of 250; Vučić's party goes into opposition."),
]

# also list 10-43: single-line items (kept short on purpose)
ALSO = [
    "Mongolia's president says he will resign",
    "Bangladesh police tear-gas garment workers",
    "Russian An-12 crash in Siberia kills all 19",
    "Mozambique puts opposition leader on trial",
    "Russia: says it downed a record 1,441 drones overnight",
    "Kyiv: missiles hit North and South Dnipro bridges",
    "UN: Ukraine's civilian deaths top all of 2025",
    "Prague: two trains collide; 46 people injured",
    "France: public-sector strike; 146,000 march",
    "Poland: Tusk's government survives no-confidence vote",
    "Germany: Deutsche Bank shares fall after huge data leak",
    "Moldova: shuts its airspace as drone nears Chișinău",
    "Turkey: police seize opposition broadcaster Sözcü TV",
    "Football: Norway win 3-2 in Denmark; Haaland scores twice",
    "Vatican: Pope Leo XIV returns from South America tour",
    "UK: sanctions 8 settlement firms and Tzav 9",
    "Israel: Eisenkot ally Matan Kahana elected speaker, 66-52",
    "West Bank: settlers kill a woman, 72, near Jericho",
    "Oman: Iran's Aragchi holds shipping-safety talks",
    "India: Cyclone Akvan strengthens; Odisha evacuates",
    "India: bus falls into an Uttarakhand gorge, 8 dead",
    "Japan: protests a Russian airspace intrusion near Fukuoka",
    "China-Canada: more tariff cuts after Carney-Xi talks",
    "Malaysia: Macron visit seals a strategic partnership",
    "Thailand: pledges to scrap tariffs on US goods",
    "South Korea: IMF lifts 2026 growth forecast to 3.9%",
    "Football: India beat Pakistan 2-1 in SAFF final",
    "Kenya: WFP aids 30,000 who fled Ethiopia clashes",
    "Football: Togo beat Algeria 3-0 in AFCON qualifier",
    "Haiti: Aristide's party will field no candidates",
    "US Senate: Van Hollen challenges Schumer for leader",
    "Australia: eases planned backpacker visa curbs",
    "Darwin: M6.6 quake off Indonesia felt; no tsunami",
    "Apple: Pay, iCloud and App Store outage; not a hack",
]

# ---------------- world map: land spans per row (60 cols x 20 rows) ----------------
# Explicit spans (col_start, col_end inclusive) — no ASCII-art drift.
MAP_SPANS = {
    2: [(3, 9), (19, 22), (38, 57)],
    3: [(2, 15), (19, 22), (29, 31), (32, 57)],
    4: [(2, 14), (28, 33), (34, 56)],
    5: [(3, 14), (27, 33), (34, 55)],
    6: [(4, 13), (28, 32), (34, 38), (36, 53)],
    7: [(6, 11), (11, 13), (34, 40), (41, 43), (46, 49)],
    8: [(12, 14), (28, 37), (41, 43), (46, 50)],
    9: [(13, 18), (28, 37), (41, 42), (47, 50), (48, 52)],
    10: [(13, 19), (29, 37), (48, 50)],
    11: [(13, 19), (29, 36)],
    12: [(14, 19), (30, 36)],
    13: [(14, 18), (30, 35)],
    14: [(15, 18), (31, 34)],
    15: [(15, 17), (31, 33), (48, 55)],
    16: [(16, 17), (48, 55)],
    17: [(16, 17), (49, 54)],
    18: [(16, 16), (50, 53)],
}
# pin (col, row) on the 60x20 grid for stories 1-9
PINS = {
    1: (50, 8),   # Manila
    2: (36, 5),   # Kerch / Crimea
    3: (38, 7),   # Bahrain / Hormuz
    4: (36, 7),   # Gaza
    5: (10, 6),   # Nvidia / California
    6: (34, 10),  # DR Congo
    7: (36, 6),   # Antalya / COP31
    8: (13, 6),   # measles / eastern US
    9: (33, 5),   # Belgrade / Serbia
}


# ---------------- flag drawing (primitives only) ----------------
def draw_flag(d, code, x, y, w, h):
    """Draw a simplified flag of `code` in box (x, y, w, h)."""
    if code == "US":
        for i in range(13):
            c = RED if i % 2 == 0 else WHITE
            d.rectangle([x, y + i * h // 13, x + w, y + (i + 1) * h // 13], fill=c)
        d.rectangle([x, y, x + int(w * 0.4), y + int(h * 7 / 13)], fill=NAVY)
        for r in range(4):
            for c in range(5):
                px = x + 6 + c * (int(w * 0.4) - 10) // 4
                py = y + 5 + r * (int(h * 7 / 13) - 10) // 3
                d.ellipse([px, py, px + 2, py + 2], fill=WHITE)
    elif code == "INDIA":
        d.rectangle([x, y, x + w, y + h // 3], fill=(255, 153, 51))
        d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=WHITE)
        d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(19, 136, 8))
        cx, cy, r = x + w // 2, y + h // 2, h // 6
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=2)
    elif code == "JAPAN":
        d.rectangle([x, y, x + w, y + h], fill=WHITE)
        cx, cy, r = x + w // 2, y + h // 2, h // 3
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(188, 0, 45))
    elif code == "AUSTRALIA":
        d.rectangle([x, y, x + w, y + h], fill=(0, 0, 139))
        d.rectangle([x, y, x + w // 2, y + h // 2], fill=(0, 0, 139))
        d.line([x, y, x + w // 2, y + h // 2], fill=WHITE, width=2)
        d.line([x + w // 2, y, x, y + h // 2], fill=WHITE, width=2)
        for sx, sy in [(0.72, 0.25), (0.85, 0.45), (0.72, 0.65), (0.85, 0.8), (0.62, 0.5)]:
            px, py = x + int(w * sx), y + int(h * sy)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=WHITE)
    d.rectangle([x, y, x + w, y + h], outline=(120, 120, 120))


# ---- PART 2: RENDERING ----

# ---------------- rendering ----------------
CLUSTER = {2: (20, -16), 3: (22, -12), 4: (16, 14), 7: (-22, 16), 9: (-24, -14)}


def draw_map(d, x0, y0, cell=6):
    d.rectangle([x0, y0, x0 + 60 * cell, y0 + 20 * cell], fill=SEA,
                outline=(150, 170, 185), width=1)
    for r, spans in MAP_SPANS.items():
        for c0, c1 in spans:
            d.rectangle([x0 + c0 * cell, y0 + r * cell,
                         x0 + (c1 + 1) * cell - 1, y0 + (r + 1) * cell - 1],
                        fill=LAND)
    for num, (col, row) in PINS.items():
        cx, cy = x0 + col * cell + cell // 2, y0 + row * cell + cell // 2
        if num in CLUSTER:
            ox, oy = CLUSTER[num]
            px, py = cx + ox, cy + oy
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=NAVY)
            d.line([cx, cy, px, py], fill=NAVY, width=1)
        else:
            px, py = cx, cy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=NAVY, outline=WHITE, width=1)
        f = font(10, bold=True)
        tw = d.textlength(str(num), font=f)
        d.text((px - tw / 2, py - 6), str(num), font=f, fill=WHITE)


def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    MX = 28  # margin

    # ---- 1. navy header band (no serif masthead) ----
    d.rectangle([0, 0, W, 64], fill=NAVY)
    d.text((MX, 17), "THE WORLD IN ONE DAY", font=font(26, bold=True), fill=WHITE)
    f_date = font(16, bold=True)
    t = "TUESDAY 17 NOVEMBER 2026"
    d.text((W - MX - d.textlength(t, font=f_date), 12), t, font=f_date, fill=WHITE)
    f_sub = font(12)
    s = "43 STORIES · 6 CONTINENTS"
    d.text((W - MX - d.textlength(s, font=f_sub), 34), s, font=f_sub, fill=(200, 210, 225))
    d.rectangle([0, 64, W, 68], fill=RED)

    # ---- 2. hero: ONE full-width lead (Quad Manila) ----
    hy, hh = 76, 224
    d.rectangle([MX, hy, W - MX, hy + hh], fill=PANEL)
    d.rectangle([MX, hy, MX + 6, hy + hh], fill=RED)
    tx = MX + 22
    d.text((tx, hy + 10), HERO["kicker"], font=font(15, bold=True), fill=RED)
    lines = wrap(d, HERO["headline"], font(40, bold=True), 560)
    y = hy + 34
    for ln in lines[:3]:
        d.text((tx, y), ln, font=font(40, bold=True), fill=NAVY)
        y += 46
    dl = wrap(d, HERO["dek"], font(16), 560)
    y += 2
    for ln in dl[:2]:
        d.text((tx, y), ln, font=font(16), fill=INK)
        y += 22
    # flag chips under the dek
    cy = hy + hh - 46
    fx = tx
    for code in HERO["flags"]:
        draw_flag(d, code, fx, cy, 46, 30)
        d.text((fx, cy + 32), code, font=font(10, bold=True), fill=GREY)
        fx += 62
    # right card: 4 flags 2x2
    cx0, cx1 = 640, W - MX
    d.rectangle([cx0, hy, cx1, hy + hh], fill=WHITE, outline=RULE, width=1)
    d.text((cx0 + 16, hy + 8), "QUAD LEADERS' SUMMIT · MANILA",
           font=font(13, bold=True), fill=NAVY)
    fw, fh = 156, 72
    for i, code in enumerate(HERO["flags"]):
        gx = cx0 + 16 + (i % 2) * (fw + 12)
        gy = hy + 34 + (i // 2) * (fh + 26)
        draw_flag(d, code, gx, gy, fw, fh)
        d.text((gx, gy + fh + 4), code, font=font(12, bold=True), fill=INK)

    # ---- 3. numbers strip ----
    ny = 308
    d.line([MX, ny, W - MX, ny], fill=RULE, width=1)
    d.line([MX, ny + 52, W - MX, ny + 52], fill=RULE, width=1)
    cw = (W - 2 * MX) // 4
    for i, (num, lab) in enumerate(NUMBERS):
        x = MX + i * cw
        if i:
            d.line([x, ny + 8, x, ny + 44], fill=RULE, width=1)
        d.text((x + 12, ny + 6), num, font=font(22, bold=True), fill=NAVY)
        d.text((x + 12, ny + 32), lab, font=font(12), fill=GREY)

    # ---- 4. middle: TOP STORIES (left) + map (right) ----
    my = 372
    d.text((MX, my), "TOP STORIES", font=font(18, bold=True), fill=NAVY)
    d.rectangle([MX, my + 26, 600, my + 29], fill=RED)
    d.line([608, my, 608, 700], fill=RULE, width=1)
    ry = my + 38
    for num, head, dek in TOP:
        d.text((MX, ry), num, font=font(16, bold=True), fill=RED)
        hh1 = fit_one_line(d, head, font(15, bold=True), 600 - 62)
        d.text((62, ry), hh1, font=font(15, bold=True), fill=INK)
        dd = fit_one_line(d, dek, font(12), 600 - 62)
        d.text((62, ry + 19), dd, font=font(12), fill=GREY)
        ry += 37
    # map panel
    d.text((616, my), "WHERE IT HAPPENED", font=font(16, bold=True), fill=NAVY)
    d.rectangle([616, my + 26, W - MX, my + 29], fill=RED)
    draw_map(d, 626, my + 40, cell=6)
    ly = my + 40 + 20 * 6 + 12
    d.ellipse([626, ly, 636, ly + 10], fill=NAVY)
    d.text((640, ly - 1), "numbered pin = story 1–9", font=font(12), fill=GREY)
    d.rectangle([820, ly, 830, ly + 10], fill=LAND, outline=GREY)
    d.text((834, ly - 1), "land", font=font(12), fill=GREY)
    # one-line summary box
    by = ly + 26
    d.rectangle([616, by, W - MX, by + 74], fill=PANEL)
    d.text((628, by + 8), "TUESDAY IN ONE LINE", font=font(12, bold=True), fill=RED)
    summ = ("Summits in Manila, strikes on the Kerch Bridge and in the Gulf, "
            "and a truce in Gaza under strain — while Nvidia doubles its sales.")
    for i, ln in enumerate(wrap(d, summ, font(13), 380 - 24)):
        d.text((628, by + 28 + i * 17), ln, font=font(13), fill=INK)

    # ---- 5. ALSO ON — two columns ----
    ay = 712
    d.text((MX, ay), "ALSO ON TUESDAY 17 NOVEMBER", font=font(16, bold=True), fill=RED)
    d.rectangle([MX, ay + 24, W - MX, ay + 27], fill=NAVY)
    iy = ay + 34
    col_w = (W - 2 * MX - 24) // 2
    for idx, item in enumerate(ALSO):
        col = idx // 17
        row = idx % 17
        x = MX if col == 0 else MX + col_w + 24
        y = iy + row * 14
        num = str(10 + idx)
        d.text((x, y), num, font=font(12, bold=True), fill=RED)
        txt = fit_one_line(d, item, font(12), col_w - 28)
        d.text((x + 28, y), txt, font=font(12), fill=INK)

    # ---- 6. footer ----
    d.line([MX, 990, W - MX, 990], fill=RULE, width=1)
    d.text((MX, 997),
           "Every story here happened or was first reported on Tuesday 17 November 2026. "
           "Disputed claims are attributed. Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN.",
           font=font(11), fill=GREY)

    img.save("entry.png", "PNG")
    print("saved entry.png", img.size, img.mode)


if __name__ == "__main__":
    main()
