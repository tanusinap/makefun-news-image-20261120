#!/usr/bin/env python3
"""Draw the news-image entry: a one-page newspaper summing up the world news
of Friday 20 November 2026. 35 stories: 3 illustrated leads, 8 illustrated
secondaries, 24 numbered briefs, a UTC timeline and a DATE CHECK box.

Output: entry.png in this directory (PNG, at most 1 MiB, 1024x1024).
Run: python3 draw_news.py
"""
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 233)
INK = (24, 22, 18)
NAVY = (30, 58, 95)
RED = (176, 32, 32)
GOLD = (200, 150, 40)
MUTED = (110, 105, 95)
LINE = (200, 192, 172)
WHITE = (255, 255, 255)
BLUE = (43, 108, 176)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONT_DIR + name, size)
    return _cache[key]


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"

REGION_COLORS = {
    "ASIA": (190, 90, 30), "EUROPE": (43, 108, 176), "AMERICAS": (60, 140, 90),
    "AFRICA": (150, 110, 30), "MIDDLE EAST": (150, 60, 120), "OCEANIA": (60, 130, 150),
    "GLOBAL": (120, 60, 160),
}

# (region, topic, headline, summary, source)
LEADS = [
    ("EUROPE", "UKRAINE WAR", "Russia's biggest barrage yet kills eight in Kyiv",
     "More than 400 drones and 110 missiles hit three Dnipro bridges; two missiles land in Poland.",
     "REUTERS \u00b7 AP"),
    ("ASIA", "WEATHER", "Cyclone Akvan makes landfall in Odisha",
     "Comes ashore near Gopalpur after weakening; 370,000 evacuated, no major damage reported.",
     "IMD \u00b7 PTI"),
    ("MIDDLE EAST", "GULF", "Tanker ablaze in Hormuz as Gulf attacks surge",
     "Outbound tanker hit near Khasab, the fourth in three days; an ADNOC vessel is attacked too.",
     "REUTERS"),
]

SECONDARIES = [
    ("GLOBAL", "CLIMATE", "COP31 slips into overtime with no deal",
     "Draft drops fossil fuels and the $120bn fund; plenary suspended, COP32 goes to Addis Ababa.", "UNFCCC"),
    ("ASIA", "SUMMIT", "Trump, Xi and Putin sign four-point peace declaration",
     "Issued after Thursday's first three-way talks in Shenzhen; silent on Ukraine.", "REUTERS"),
    ("AMERICAS", "MARKETS", "Anthropic slides 6% on day two after record IPO",
     "Shares fall after a 17% debut jump to $97.17; the S&P 500 falls a sixth straight day.", "REUTERS"),
    ("ASIA", "SPORT", "Pakistan seal first Test series win in two years",
     "Eight-wicket win over Sri Lanka in Rawalpindi; Amir Jamal stars with bat and ball.", "AP"),
    ("EUROPE", "EU", "Hungary lifts veto on Ukraine's EU accession talks",
     "Budapest drops its block on opening negotiating clusters with Kyiv.", "AP"),
    ("AMERICAS", "POLITICS", "Senate rejects bid to end the Iran war, 51-48",
     "Trump says no decision on new strikes until next year; war cost put at $48.3bn.", "AP"),
    ("AFRICA", "HEALTH", "Kenya starts 42-day countdown to Ebola-free status",
     "Last patient discharged 11 Nov, 37 days after the first case; declaration due 23 Dec.", "WHO"),
    ("EUROPE", "UKRAINE WAR", "Kerch Bridge rail traffic resumes on one track",
     "Trains return after Ukraine's strikes; Putin promises a harsh response.", "REUTERS"),
]

BRIEFS = [
    ("Berlin", "Zelensky joins Coalition of the Willing"),
    ("Warsaw", "Two Russian missiles fell in Poland"),
    ("Kharkiv", "Ukraine retakes 14 settlements, 200 sq km"),
    ("Brussels", "EU to summon Russian envoy over Kyiv strikes"),
    ("Washington", "Trump floats penalties for US AI firms abroad"),
    ("Washington", "US, China: humans must oversee military AI"),
    ("Washington", "Trump keeps China on older AI chips"),
    ("Mexico City", "US: Chinese chemicals fuel Sinaloa cartel"),
    ("Bras\u00edlia", "Brazil sells $1bn reserves to slow dollar"),
    ("Bogot\u00e1", "Colombia warns of state action on blockade"),
    ("Wellington", "NZ court: pay equity reform broke rights"),
    ("Canberra", "Xi hails 'full turnaround' with Albanese"),
    ("Wellington", "Nicholls 175*, Phillips 118 lift NZ to 368"),
    ("Doha", "India A thrash Nepal by 306 runs"),
    ("Abu Dhabi", "UAE Bulls win T10 title by 24 runs"),
    ("Madrid", "Real Madrid extend Courtois to 2028"),
    ("Balochistan", "Bus-tanker crash kills 10, injures 27"),
    ("Paris", "L'Or\u00e9al to buy 10% of Armani"),
    ("Gaza", "22,000+ Palestinian children killed"),
    ("Kinshasa", "Attacks hold back DR Congo Ebola fight"),
    ("Sanaa", "Yemen's children face worsening crisis"),
    ("London", "Britain seeks EU food, carbon, mobility deals"),
    ("Vienna", "West urges Iran to restart IAEA inspections"),
    ("Boston", "Keck traces Europa's sodium cloud"),
]

BRIEF_REGIONS = [
    "EUROPE", "EUROPE", "EUROPE", "EUROPE",
    "AMERICAS", "GLOBAL", "AMERICAS", "AMERICAS",
    "AMERICAS", "AMERICAS", "OCEANIA", "OCEANIA",
    "OCEANIA", "ASIA", "MIDDLE EAST", "EUROPE",
    "ASIA", "EUROPE", "MIDDLE EAST", "AFRICA",
    "MIDDLE EAST", "EUROPE", "EUROPE", "AMERICAS",
]

TIMELINE = [
    ("OVERNIGHT", "Russia's barrage hits Kyiv bridges"),
    ("MORNING", "Akvan makes landfall near Gopalpur"),
    ("10:00 UTC", "COP31 draft drops fossil fuels"),
    ("MIDDAY", "Anthropic slides"),
    ("AFTERNOON", "Senate rejects Iran war resolution"),
    ("14:30 UTC", "Pakistan seal Test series win"),
    ("EVENING", "COP31 plenary suspended"),
    ("LATE", "Kerch Bridge rail traffic resumes"),
]


def region_counts():
    counts = {}
    for region, *_ in LEADS + SECONDARIES:
        counts[region] = counts.get(region, 0) + 1
    for r in BRIEF_REGIONS:
        counts[r] = counts.get(r, 0) + 1
    return counts


def text_block(draw, x, y, text, fnt, fill, max_w, line_h, max_lines):
    """Draw wrapped text, return the y just below the last line."""
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=1000) or [""])
    wrapped = []
    for ln in lines:
        while draw.textlength(ln, font=fnt) > max_w and len(ln) > 1:
            cut = len(ln) - 1
            while cut > 0 and draw.textlength(ln[:cut], font=fnt) > max_w:
                cut -= 1
            while cut > 0 and ln[cut] != " ":
                cut -= 1
            wrapped.append(ln[:cut].rstrip())
            ln = ln[cut:].strip()
        wrapped.append(ln)
    wrapped = wrapped[:max_lines]
    for i, ln in enumerate(wrapped):
        draw.text((x, y + i * line_h), ln, font=fnt, fill=fill)
    return y + len(wrapped) * line_h


# ---------- illustrations (all drawn in code) ----------

def illo_kyiv(draw, x, y, w, h):
    # night barrage over Kyiv: dark sky, missile trails, bridge, explosions
    draw.rectangle([x, y, x + w, y + h], fill=(18, 22, 40))
    for sx, sy in [(30, 18), (90, 10), (150, 24), (210, 12), (270, 20), (310, 30)]:
        draw.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(200, 200, 220))
    # missile trails arcing down
    for mx, my, mlen in [(40, 8, 44), (120, 4, 58), (200, 10, 50), (280, 6, 62)]:
        draw.line([(x + mx, y + my), (x + mx + 14, y + my + mlen)], fill=(255, 200, 90), width=2)
        draw.ellipse([x + mx + 10, y + my + mlen - 4, x + mx + 18, y + my + mlen + 4],
                     fill=(255, 220, 130))
    # river + bridge
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=(30, 60, 110))
    draw.line([(x, y + h - 30), (x + w, y + h - 30)], fill=(150, 160, 190), width=4)
    for px in (60, 150, 240):
        draw.line([(x + px, y + h - 30), (x + px, y + h - 52)], fill=(150, 160, 190), width=3)
        draw.line([(x + px, y + h - 52), (x + px - 24, y + h - 30)], fill=(150, 160, 190), width=2)
        draw.line([(x + px, y + h - 52), (x + px + 24, y + h - 30)], fill=(150, 160, 190), width=2)
    # explosions on the bridge
    for ex, ey, r in [(100, h - 34, 12), (220, h - 36, 10)]:
        draw.ellipse([x + ex - r, y + ey - r, x + ex + r, y + ey + r], fill=(255, 150, 40))
        draw.ellipse([x + ex - r // 2, y + ey - r // 2, x + ex + r // 2, y + ey + r // 2],
                     fill=(255, 230, 150))
    draw.rectangle([x + 8, y + 6, x + 150, y + 24], fill=RED)
    draw.text((x + 12, y + 8), "400+ DRONES \u00b7 110 MISSILES", font=font(SANS_B, 9), fill=WHITE)
    draw.text((x + 8, y + h - 22), "3 BRIDGES HIT \u00b7 2 MISSILES LAND IN POLAND",
              font=font(SANS_B, 9), fill=WHITE)


def illo_akvan(draw, x, y, w, h):
    # cyclone spiral over the Odisha coast
    draw.rectangle([x, y, x + w, y + h], fill=(25, 55, 85))
    cx, cy = x + 90, y + h // 2
    for r in (52, 42, 32, 22, 12):
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=140, end=500, fill=WHITE, width=4)
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=GOLD)
    # coastline + rain (kept to the far right so the AKVAN label stays clear)
    draw.polygon([(x + 250, y + h), (x + 270, y + 50), (x + 290, y + 80), (x + 310, y + 30),
                  (x + w, y + 60), (x + w, y + h)], fill=(60, 120, 70))
    for rx in (280, 300, 315):
        draw.line([(x + rx, y + 8), (x + rx - 6, y + 26)], fill=(170, 200, 235), width=2)
    draw.text((x + 170, y + 8), "AKVAN", font=font(SANS_B, 22), fill=WHITE)
    draw.text((x + 170, y + 34), "LANDFALL \u00b7 GOPALPUR", font=font(SANS_B, 10), fill=GOLD)
    draw.text((x + 170, y + h - 20), "370,000 EVACUATED", font=font(SANS_B, 10), fill=WHITE)


def illo_hormuz(draw, x, y, w, h):
    # tanker on fire in the strait
    draw.rectangle([x, y, x + w, y + h], fill=(35, 55, 85))
    draw.rectangle([x, y + h - 34, x + w, y + h], fill=(25, 80, 120))
    # tanker hull (brighter red so it reads against the dark sea)
    draw.rectangle([x + 30, y + h - 62, x + 260, y + h - 34], fill=(180, 60, 50))
    draw.rectangle([x + 210, y + h - 84, x + 250, y + h - 62], fill=(200, 200, 200))
    draw.rectangle([x + 30, y + h - 62, x + 260, y + h - 56], fill=(90, 90, 100))
    # flames
    for fx, fh in [(60, 34), (90, 46), (120, 38), (150, 30)]:
        draw.polygon([(x + fx, y + h - 62), (x + fx + 12, y + h - 62 - fh),
                      (x + fx + 24, y + h - 62)], fill=(255, 150, 30))
        draw.polygon([(x + fx + 6, y + h - 62), (x + fx + 12, y + h - 62 - fh + 14),
                      (x + fx + 18, y + h - 62)], fill=(255, 220, 120))
    # smoke (moved right, clear of the STRAIT OF HORMUZ label)
    for sx, sy, r in [(180, 18, 12), (205, 10, 14), (230, 16, 11)]:
        draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(90, 90, 100))
    draw.text((x + 8, y + 6), "STRAIT OF HORMUZ", font=font(SANS_B, 11), fill=WHITE)
    draw.text((x + 8, y + h - 22), "4TH TANKER HIT IN 3 DAYS", font=font(SANS_B, 10), fill=GOLD)


def illo_cop31(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 90, 80))
    draw.ellipse([x + 12, y + 8, x + 52, y + 48], fill=(60, 160, 220))
    draw.ellipse([x + 22, y + 14, x + 40, y + 30], fill=(90, 180, 90))
    draw.text((x + 66, y + 6), "NO DEAL", font=font(SANS_B, 20), fill=WHITE)
    draw.text((x + 66, y + 30), "DRAFT DROPS FOSSIL FUELS", font=font(SANS_B, 9), fill=(160, 230, 210))
    draw.text((x + 66, y + h - 16), "ANTALYA \u00b7 OVERTIME", font=font(SANS_B, 9), fill=(160, 230, 210))


def illo_declaration(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(230, 235, 245))
    draw.rectangle([x + 12, y + 6, x + 76, y + h - 6], fill=WHITE, outline=(150, 160, 180))
    for i in range(4):
        draw.line([(x + 18, y + 12 + i * 9), (x + 70, y + 12 + i * 9)], fill=(170, 175, 185), width=2)
    draw.rectangle([x + 18, y + 48, x + 44, y + 52], fill=RED)
    draw.text((x + 88, y + 6), "4-POINT", font=font(SANS_B, 18), fill=NAVY)
    draw.text((x + 88, y + 28), "PEACE DECLARATION", font=font(SANS_B, 10), fill=NAVY)
    draw.text((x + 88, y + h - 16), "SHENZHEN \u00b7 NO UKRAINE", font=font(SANS_B, 9), fill=MUTED)


def illo_ant_slide(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 20, 20))
    draw.rectangle([x, y, x + w, y + 20], fill=(40, 12, 12))
    draw.text((x + 8, y + 4), "NASDAQ \u00b7 DAY TWO", font=font(SANS_B, 10), fill=(230, 160, 160))
    pts = [(x + 16, y + 28), (x + 46, y + 26), (x + 76, y + 32), (x + 106, y + 40),
           (x + 136, y + 48)]
    draw.line(pts, fill=RED, width=3)
    for px, py in pts:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 120, 120))
    draw.text((x + 145, y + 24), "ANT -6%", font=font(SANS_B, 17), fill=WHITE)
    draw.text((x + 145, y + h - 16), "DAY 1: +17%", font=font(SANS_B, 9), fill=(230, 160, 160))


def illo_pakistan(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 90, 50))
    # cricket bat + ball
    draw.rounded_rectangle([x + 14, y + 8, x + 40, y + 40], radius=4, fill=(220, 190, 130))
    draw.rectangle([x + 24, y + 40, x + 30, y + 52], fill=(180, 150, 100))
    draw.ellipse([x + 52, y + 14, x + 68, y + 30], fill=RED)
    draw.arc([x + 54, y + 16, x + 66, y + 28], start=90, end=270, fill=WHITE, width=1)
    draw.text((x + 82, y + 6), "SERIES WIN", font=font(SANS_B, 18), fill=WHITE)
    draw.text((x + 82, y + 28), "PAKISTAN WIN BY 8 WKTS", font=font(SANS_B, 9), fill=(170, 230, 190))
    draw.text((x + 82, y + h - 16), "FIRST IN TWO YEARS", font=font(SANS_B, 9), fill=(170, 230, 190))


def illo_hungary(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 58, 95))
    # circle of EU stars
    cx, cy = x + 40, y + h // 2
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx = cx + int(18 * math.cos(a))
        sy = cy + int(18 * math.sin(a))
        draw.text((sx - 4, sy - 6), "\u2605", font=font(SANS_B, 8), fill=GOLD)
    draw.text((x + 72, y + 6), "VETO LIFTED", font=font(SANS_B, 18), fill=WHITE)
    draw.text((x + 72, y + 28), "HUNGARY OPENS EU TALKS", font=font(SANS_B, 10), fill=(170, 200, 240))
    draw.text((x + 72, y + h - 16), "UKRAINE ACCESSION", font=font(SANS_B, 9), fill=(170, 200, 240))


def illo_senate(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(235, 230, 215))
    # capitol dome
    cx = x + 40
    draw.arc([cx - 22, y + 6, cx + 22, y + 40], start=180, end=360, fill=NAVY, width=3)
    draw.rectangle([cx - 24, y + 24, cx + 24, y + 28], fill=NAVY)
    for i in range(4):
        px = cx - 20 + i * 12
        draw.rectangle([px, y + 30, px + 5, y + 46], fill=NAVY)
    draw.rectangle([cx - 26, y + 48, cx + 26, y + 52], fill=NAVY)
    draw.text((x + 78, y + 6), "51-48", font=font(SANS_B, 22), fill=RED)
    draw.text((x + 78, y + 32), "WAR POWERS VOTE FAILS", font=font(SANS_B, 9), fill=INK)
    draw.text((x + 78, y + h - 16), "IRAN WAR GOES ON", font=font(SANS_B, 9), fill=MUTED)


def illo_ebola(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 240, 220))
    draw.rectangle([x + 12, y + 6, x + 58, y + h - 6], fill=WHITE, outline=RED, width=2)
    draw.text((x + 35, y + 8), "42", font=font(SANS_B, 22), fill=RED, anchor="ma")
    draw.text((x + 35, y + 34), "DAYS", font=font(SANS_B, 9), fill=RED, anchor="ma")
    draw.text((x + 70, y + 6), "EBOLA-FREE", font=font(SANS_B, 16), fill=NAVY)
    draw.text((x + 70, y + 26), "COUNTDOWN STARTS", font=font(SANS_B, 11), fill=NAVY)
    draw.text((x + 70, y + h - 16), "KENYA \u00b7 DECLARATION 23 DEC", font=font(SANS_B, 9), fill=MUTED)


def illo_kerch(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(70, 85, 110))
    draw.rectangle([x, y + h - 14, x + w, y + h], fill=(60, 130, 200))
    draw.line([(x + 8, y + h - 18), (x + w - 8, y + h - 18)], fill=(200, 200, 210), width=3)
    for px in (50, 110, 170):
        draw.line([(x + px, y + h - 18), (x + px, y + h - 34)], fill=(200, 200, 210), width=2)
    # train on the bridge
    draw.rectangle([x + 60, y + h - 30, x + 180, y + h - 20], fill=(220, 60, 60))
    for wx in (80, 110, 140, 165):
        draw.ellipse([x + wx, y + h - 22, x + wx + 8, y + h - 14], fill=(40, 40, 50))
    draw.text((x + 8, y + 6), "RAIL RESUMES", font=font(SANS_B, 14), fill=WHITE)
    draw.text((x + 8, y + 24), "ONE TRACK OPEN", font=font(SANS_B, 9), fill=(200, 220, 240))


LEAD_ILLOS = [illo_kyiv, illo_akvan, illo_hormuz]
SEC_ILLOS = [illo_cop31, illo_declaration, illo_ant_slide, illo_pakistan,
             illo_hungary, illo_senate, illo_ebola, illo_kerch]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.text((8, 6), "THE WORLD IN ONE DAY", font=font(SANS_B, 12), fill=RED)
    d.text((W - 8, 6), "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 35 STORIES",
           font=font(SANS_B, 11), fill=MUTED, anchor="ra")
    d.line([(8, 26), (W - 8, 26)], fill=INK, width=2)
    d.text((8, 30), "Friday 20 November 2026", font=font(SERIF_B, 54), fill=INK)
    # calendar badge
    d.rectangle([W - 66, 30, W - 8, 84], outline=RED, width=2)
    d.text((W - 37, 32), "20", font=font(SANS_B, 26), fill=RED, anchor="ma")
    d.text((W - 37, 62), "NOV", font=font(SANS_B, 12), fill=RED, anchor="ma")
    d.text((8, 92), "Russia's biggest barrage yet hits Kyiv \u00b7 Akvan makes landfall \u00b7 COP31 slips into overtime",
           font=font(SERIF, 15), fill=RED)
    d.line([(8, 116), (W - 8, 116)], fill=INK, width=2)

    # ---- region bar
    counts = region_counts()
    total = sum(counts.values())
    assert total == 35, f"story count {total} != 35"
    order = ["ASIA", "EUROPE", "AMERICAS", "AFRICA", "MIDDLE EAST", "OCEANIA", "GLOBAL"]
    x = 8
    for region in order:
        label = f"{region} {counts[region]}"
        tw = d.textlength(label, font=font(SANS_B, 10)) + 16
        d.rectangle([x, 118, x + tw, 132], fill=REGION_COLORS[region])
        d.text((x + 8, 119), label, font=font(SANS_B, 10), fill=WHITE)
        x += tw + 2

    # ---- timeline strip (two rows of four)
    d.rectangle([0, 126, W, 164], fill=(235, 230, 215))
    d.text((14, 130), "THE DAY IN UTC", font=font(SANS_B, 11), fill=RED)
    for row_i in range(2):
        tx = 130 if row_i == 0 else 14
        ty = 130 if row_i == 0 else 147
        for time, label in TIMELINE[row_i * 4:(row_i + 1) * 4]:
            d.text((tx, ty), time, font=font(SANS_B, 10), fill=RED)
            tw = d.textlength(time, font=font(SANS_B, 10))
            d.text((tx + tw + 5, ty), label, font=font(SANS, 10), fill=INK)
            tx += tw + 5 + d.textlength(label, font=font(SANS, 10)) + 22
    d.line([(0, 164), (W, 164)], fill=LINE, width=1)

    # ---- three leads
    lw = 330
    for i, (region, topic, head, summ, src) in enumerate(LEADS):
        lx = 8 + i * (lw + 4)
        ly = 168
        LEAD_ILLOS[i](d, lx, ly, lw, 120)
        d.text((lx, ly + 124), f"{i + 1}  {region} \u00b7 {topic}",
               font=font(SANS_B, 10), fill=REGION_COLORS[region])
        y = text_block(d, lx, ly + 140, head, font(SERIF_B, 20), INK, lw, 23, max_lines=2)
        text_block(d, lx, y + 2, summ, font(SANS, 12), INK, lw, 15, max_lines=2)
        d.text((lx, 452), src, font=font(SANS_B, 9), fill=MUTED)

    d.line([(8, 460), (W - 8, 460)], fill=INK, width=2)

    # ---- eight secondaries, two rows of four (124px pitch, one-line summaries)
    sw = 248
    for row in range(2):
        for col in range(4):
            i = row * 4 + col
            region, topic, head, summ, src = SECONDARIES[i]
            sx = 8 + col * (sw + 4)
            sy = 464 + row * 124
            SEC_ILLOS[i](d, sx, sy, sw, 58)
            d.text((sx, sy + 62), f"{i + 4}  {region} \u00b7 {topic}",
                   font=font(SANS_B, 9), fill=REGION_COLORS[region])
            y = text_block(d, sx, sy + 76, head, font(SERIF_B, 14), INK, sw, 16, max_lines=2)
            text_block(d, sx, y + 1, summ, font(SANS, 10), MUTED, sw, 13, max_lines=1)

    d.line([(8, 716), (W - 8, 716)], fill=INK, width=2)

    # ---- briefs
    d.text((8, 722), "ALSO ON FRIDAY 20 NOVEMBER", font=font(SANS_B, 12), fill=NAVY)
    bw = 330
    for col in range(3):
        bx = 8 + col * (bw + 6)
        for r in range(8):
            i = col * 8 + r
            place, brief = BRIEFS[i]
            by = 742 + r * 25
            d.text((bx, by), str(12 + i), font=font(SANS_B, 11), fill=REGION_COLORS[BRIEF_REGIONS[i]])
            d.text((bx + 24, by), f"{place}: ", font=font(SANS_B, 11), fill=INK)
            pw = d.textlength(f"{place}: ", font=font(SANS_B, 11))
            text_block(d, bx + 24 + pw, by, brief, font(SANS, 11), INK, bw - 24 - pw, 14, max_lines=1)

    # ---- date check box
    d.rectangle([8, 934, W - 8, 980], outline=RED, width=2)
    d.text((16, 938), "DATE CHECK", font=font(SANS_B, 11), fill=RED)
    dc = ("Left out, first reported on Thursday 19 November: the three-way summit itself \u00b7 Anthropic's IPO debut at $83 \u00b7 "
          "the ICJ Rohingya judgment \u00b7 GTA VI's launch \u00b7 the Houthi strike on Riyadh's PIF Tower. "
          "Wednesday 18 November: Van Gogh's $190.4m sale \u00b7 the US strike on Qeshm. "
          "Not yet news on Friday: COP31's third draft (Sat) \u00b7 Kenya's Ebola-free declaration (23 Dec).")
    text_block(d, 16, 954, dc, font(SANS, 10), INK, W - 32, 13, max_lines=2)

    # ---- footer
    d.text((8, 988), "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 DW \u00b7 IANS \u00b7 PTI \u00b7 IMD \u00b7 WHO \u00b7 UNFCCC \u00b7 ICJ \u00b7 Keck \u00b7 MIT",
           font=font(SANS, 9), fill=MUTED)
    d.text((W - 8, 988), "Reads at three sizes: date and leads at thumbnail size \u00b7 all stories at full size.",
           font=font(SANS, 9), fill=MUTED, anchor="ra")

    img.save("entry.png", "PNG", optimize=True)
    print(f"wrote entry.png, size {img.size}, region counts {counts}")


if __name__ == "__main__":
    main()
