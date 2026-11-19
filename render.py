"""Build the print edition. The contest runner is main.py."""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen
import json
import math

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
LAND = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_110m_land.geojson"
LAND_SHA = "9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9"
S = 2
INK, PAPER, RULE = "#182b30", "#f5efe2", "#c6bba3"
RED, TEAL, GOLD = "#9e3d30", "#166765", "#eabc7c"
FONTS = {
    "serif": "DejaVuSerif-Bold.ttf", "sans": "DejaVuSans.ttf",
    "bold": "DejaVuSans-Bold.ttf", "mono": "DejaVuSansMono-Bold.ttf",
}

image = Image.new("RGB", (1024 * S, 1024 * S), PAPER)
draw = ImageDraw.Draw(image)


@lru_cache
def font(style, size):
    return ImageFont.truetype(str(FONT_DIR / FONTS[style]), size * S)


def coords(values):
    return tuple(round(value * S) for value in values)


def rect(x, y, w, h, color):
    draw.rectangle(coords((x, y, x + w, y + h)), fill=color)


def line(points, color, width=1):
    draw.line([coords(p) for p in points], fill=color, width=max(1, round(width * S)))


def dot(x, y, r, color):
    draw.ellipse(coords((x-r, y-r, x+r, y+r)), fill=color)


def width(value, style, size):
    return draw.textlength(value, font=font(style, size)) / S


def text(x, y, value, style, size, color=INK, anchor="lt"):
    draw.text(coords((x, y)), value, font=font(style, size), fill=color, anchor=anchor)


def fit(x, y, value, style, size, available, color=INK, anchor="lt"):
    while width(value, style, size) > available:
        size -= 1
    text(x, y, value, style, size, color, anchor)


def paragraph(x, y, value, style, size, available, leading, max_lines, color=INK):
    rows = []
    current = ""
    for word in value.split():
        combined = f"{current} {word}".strip()
        if width(combined, style, size) <= available:
            current = combined
        else:
            rows.append(current)
            current = word
    rows.append(current)
    if len(rows) > max_lines:
        raise ValueError(f"Text exceeds {max_lines} lines: {value} ({rows})")
    for index, row in enumerate(rows):
        text(x, y + index * leading, row, style, size, color)


def ledger():
    result = []
    for row in (ROOT / "SOURCES.md").read_text().splitlines():
        if row.startswith("| ") and row[2:4].isdigit():
            number, region, place, status, headline, summary, _ = (
                value.strip() for value in row.strip("|").split("|")
            )
            result.append((int(number), region, place, status, headline, summary))
    assert [row[0] for row in result] == list(range(1, 43))
    return result


PALETTES = [
    ("#244852", "#f0bd80", "#69988e"),
    ("#563841", "#ffc396", "#a96866"),
    ("#274943", "#fcdb97", "#7ca684"),
    ("#455362", "#f5d495", "#9caaad"),
    ("#365c50", "#f2daa5", "#8fb38c"),
    ("#225a65", "#f9d799", "#88b9b4"),
    ("#3c4c59", "#f4ca85", "#7a9aa2"),
    ("#245950", "#f2d397", "#85aa8a"),
    ("#2c596c", "#fbd394", "#81b4c0"),
    ("#71473b", "#f4ce95", "#bc8067"),
    ("#504f65", "#f1c691", "#a294ac"),
    ("#63423e", "#fed292", "#c58270"),
    ("#43584f", "#f4d098", "#86a691"),
]


def illustration(number, x, y, w, h):
    back, light, shade = PALETTES[number - 1]
    rect(x, y, w, h, back)

    def path(points, color=light, weight=1.5):
        line([(x + u / 100 * w, y + v / 48 * h) for u, v in points], color, weight)

    def block(u, v, a, b, color=light):
        rect(x + u / 100 * w, y + v / 48 * h, a / 100 * w, b / 48 * h, color)

    def circle(u, v, r, color=light):
        dot(x + u / 100 * w, y + v / 48 * h, r * min(h / 48, w / 100), color)

    for u in range(3, 100, 5):
        for v in range(4, 48, 7):
            circle(u, v, .42, shade)

    if number in (1, 2, 12):
        circle(77, 17, 11, shade)
        for u, roof, span in [(7,30,8),(17,25,7),(26,17,9),(37,28,7),
                             (46,12,7),(55,21,8),(65,27,7),(74,20,9),(86,29,8)]:
            if number == 12 and u == 46:
                roof = 5
            block(u, roof, span, 40 - roof, shade if u % 2 else light)
            for v in range(roof + 4, 39, 4):
                block(u + 2, v, span - 4, .45, back)
        path([(0,40),(100,40)])
        if number == 1:
            for u in (25, 50, 75):
                circle(u, 34, 3)
            path([(15,39),(85,39)], light, 2.5)
        if number == 2:
            path([(41,48),(48,40),(54,40),(69,48)], light, 2.3)
            for u in (12, 87):
                path([(u,41),(u+2,17),(u-4,21),(u+2,17),(u+8,20),(u+2,17),(u,13)])
    elif number in (3, 11):
        for u, v in [(16,32),(29,27),(42,22),(55,24),(68,13),(81,8)]:
            block(u, v, 7, 42 - v, shade)
        path([(12,41),(29,31),(42,23),(56,27),(70,13),(88,8)], light, 2.5)
        path([(82,5),(88,8),(85,14)])
        path([(10,42),(94,42)], shade)
    elif number == 4:
        path([(24,18),(50,5),(76,18),(24,18)], light, 2)
        for u in (30, 41, 53, 65):
            block(u, 22, 5, 15, shade)
        for v, a in [(38,48),(42,60)]:
            block(50 - a/2, v, a, 1.6)
    elif number in (5, 8):
        for u in (27, 50, 73):
            circle(u, 24, 14, shade)
            for v in (17, 24, 31):
                path([(u-10,v),(u+10,v)], back, .7)
            path([(u,10),(u,38)], back, 1)
        path([(13,36),(29,18),(52,27),(75,11),(88,17)], light, 1.8)
    elif number in (6, 9):
        if number == 6:
            for offset in (0, math.pi):
                points = []
                for step in range(65):
                    angle = offset + step / 11
                    radius = 2 + step * .29
                    points.append((50 + radius * 1.65 * math.cos(angle),
                                   24 + radius * math.sin(angle)))
                path(points, light, 2.3)
            circle(50, 24, 2.4)
        else:
            for u, v in [(23,22),(43,15),(64,23)]:
                path([(u,v),(u+8,v-6),(u+16,v),(u+16,34),(u,34),(u,v)], light, 2)
            for v in (33, 39, 45):
                path([(u, v + (2 if u % 12 == 6 else 0)) for u in range(0, 101, 6)], shade)
    elif number == 7:
        path([(8,36),(92,36)], shade, 3)
        for u in (20, 80):
            path([(u,14),(u,42)], light, 2.5)
        path([(8,35),(20,14),(50,33),(80,14),(92,35)], light, 1.8)
        path([(49,7),(49,28)], light, 2)
        block(49, 8, 13, 5, "#e8bb71")
        block(49, 13, 13, 5, "#769fb1")
    elif number == 10:
        for v in (13, 21, 32, 39):
            path([(0,v),(19,v-5),(42,v+3),(62,v-2),(80,v+4),(100,v)], shade, 3)
        path([(0,25),(19,20),(42,28),(62,23),(80,29),(100,25)], light, 2.5)
    else:
        path([(9,31),(90,31),(78,42),(21,42),(9,31)], light, 2)
        for u in (22, 39, 56, 73):
            block(u, 20, 14, 9, shade)
            path([(u+3,22),(u+3,27)], back, .8)
        path([(7,45),(29,44),(64,46),(94,44)], shade)


FIGURES = [
    ("$81.3bn", "Anthropic IPO priced 18 Nov"),
    ("17.1m", "GTA VI pre-orders · Sensor Tower est."),
    ("204,070", "Odisha identified for possible evacuation"),
    ("$120bn", "COP31 draft proposal · no deal yet"),
    ("13 years", "Since GTA V first launched"),
    ("15.3 in", "Broward rain · 24h to 18 Nov"),
]

# Longitude, latitude and callout offset in print pixels.
LOCATIONS = [
    (114.06, 22.54, -24, -11), (-74.01, 40.71, 3, -19),
    (-74.01, 40.71, 21, -5), (4.30, 52.08, -14, -17),
    (30.71, 36.90, 9, 12), (85.53, 19.81, -10, 16),
    (30.52, 50.45, 10, -16), (114.06, 22.54, 17, 12),
    (-80.14, 26.12, 11, 13), (-112.11, 36.06, -7, 11),
    (2.35, 48.86, -24, 8), (46.68, 24.71, 12, 14),
    (22.64, 32.76, -9, 19),
]


def atlas(x, y):
    w, h = 486, 190
    rect(x, y, w, h, "#e4eae0")
    left, top, scale = x + 12, y + 9, 462 / 360

    def project(lon, lat):
        return left + (lon + 180) * scale, top + (83 - lat) * scale

    with urlopen(LAND, timeout=20) as response:
        raw = response.read()
    if sha256(raw).hexdigest() != LAND_SHA:
        raise ValueError("Natural Earth land layer checksum mismatch")
    mask = Image.new("1", image.size)
    mask_draw = ImageDraw.Draw(mask)
    for item in json.loads(raw)["features"]:
        geometry = item["geometry"]
        polygons = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            polygons = [polygons]
        for polygon in polygons:
            if max(lat for _, lat in polygon[0]) < -55:
                continue
            for i, ring in enumerate(polygon):
                mask_draw.polygon([coords(project(lon, lat)) for lon, lat in ring], fill=int(i == 0))

    for lon in range(-150, 180, 30):
        line([project(lon, 83), project(lon, -55)], "#c2cec1", .5)
    for lat in range(-30, 75, 30):
        line([project(-180, lat), project(180, lat)], "#c2cec1", .5)
    for a in range(x + 10, x + w - 8, 3):
        for b in range(y + 7, y + h - 5, 3):
            if mask.getpixel(coords((a, b))):
                dot(a, b, .68, "#5b8d7e")

    for lon, lat, label in [
        (-139, 62, "N. AMERICA"), (-77, -18, "S. AMERICA"),
        (-13, 71, "EUROPE"), (-7, 0, "AFRICA"), (86, 61, "ASIA"),
        (122, -45, "OCEANIA"),
    ]:
        text(*project(lon, lat), label, "mono", 8, TEAL)

    for number, (lon, lat, dx, dy) in enumerate(LOCATIONS, 1):
        a, b = project(lon, lat)
        line([(a, b), (a+dx, b+dy)], RED, .8)
        dot(a, b, 1.7, RED)
        dot(a+dx, b+dy, 7, RED)
        text(a+dx, b+dy, f"{number:02}", "mono", 8, PAPER, "mm")


def cover():
    stories = ledger()
    counts = Counter(row[1] for row in stories)
    rect(0, 0, 1024, 8, RED)
    text(23, 20, "T H E   D A I L Y   A T L A S", "mono", 11, RED)
    text(1001, 20, "THURSDAY 19 NOVEMBER 2026", "mono", 12, RED, "rt")
    fit(512, 38, "THE WORLD IN ONE PICTURE", "serif", 61, 978, anchor="mt")
    text(512, 103, "Shenzhen summit  /  GTA VI launches  /  Record Anthropic IPO  /  Rohingya genocide case  /  Cyclone Akvan",
         "bold", 14, INK, "mt")
    line([(22,126),(1002,126)], INK, 1.6)
    regions = ["Europe", "Americas", "Asia-Pacific", "Middle East", "Africa", "Oceania", "World"]
    for i, region in enumerate(regions):
        text(92 + i * 140, 132, f"{region.upper()}  {counts[region]:02}", "mono", 11, INK, "mt")

    rect(22, 152, 980, 60, INK)
    for i, (value, label) in enumerate(FIGURES):
        x = 22 + i * 980 / 6
        if i:
            line([(x,163),(x,201)], "#637171", .7)
        text(x + 9, 159, value, "serif", 27, GOLD)
        fit(x + 9, 193, label, "sans", 9, 146, PAPER)

    for i, story in enumerate(stories[:3]):
        number, _, place, status, headline, summary = story
        x = 22 + i * 329
        illustration(number, x, 225, 322, 91)
        text(x+9, 234, f"{number:02}", "mono", 17, PAPER)
        text(x, 324, f"{place.upper()}  /  {status.upper()}", "mono", 10, RED)
        fit(x, 341, headline, "serif", 23, 321)
        paragraph(x, 372, summary, "sans", 12, 320, 14, 3)

    for i, story in enumerate(stories[3:13]):
        number, _, place, status, headline, summary = story
        x = 22 + (i % 5) * 197
        y = 421 + (i // 5) * 114
        line([(x,y-3),(x+192,y-3)], RULE)
        illustration(number, x, y, 192, 33)
        text(x+7, y+6, f"{number:02}", "mono", 14, PAPER)
        fit(x, y+39, f"{place.upper()}  /  {status.upper()}", "mono", 8, 192, RED)
        fit(x, y+52, headline, "serif", 15, 192)
        paragraph(x, y+72, summary, "sans", 10, 192, 12, 3)

    line([(22,655),(1002,655)], INK, 1.6)
    text(22, 662, "WHERE IT HAPPENED", "serif", 21)
    text(508, 670, "01–13  /  LEAD STORIES", "mono", 9, TEAL, "rt")
    atlas(22, 687)
    text(523, 662, "AROUND THE WORLD", "serif", 21)
    text(1002, 670, "14–42  /  CITY DESK", "mono", 9, TEAL, "rt")
    for i, story in enumerate(stories[13:]):
        number, _, place, status, headline, _ = story
        if i < 20:
            x = 523 + (i // 10) * 243
            y = 688 + (i % 10) * 19
            available = 235
        else:
            j = i - 20
            x = 22 + (j // 3) * 329
            y = 891 + (j % 3) * 22
            available = 322
        line([(x, y-3), (x+available, y-3)], RULE, .5)
        text(x, y+1, f"{number:02}", "mono", 10, RED)
        tag = ""
        if "agenda" in status:
            tag = " ◇"
        elif "18 Nov" in status:
            tag = " †"
        elif "forecast" in status:
            tag = " ~"
        label = f"{place.upper()}{tag}  ·  {headline}"
        fit(x+20, y+1, label, "sans", 11, available-21)

    text(22, 955, "◇  Agenda or scheduled action     †  18 Nov development, carried in 19 Nov editions     ~  Forecast", "mono", 9, TEAL)
    rect(0, 974, 1024, 50, INK)
    text(22, 984, "DATE CHECK", "serif", 14, GOLD)
    text(140, 983, "18 NOV OR EARLIER  /  Derna seizure 17 Nov, reported 18 Nov. Florida deluge and Anthropic pricing 18 Nov.", "sans", 11, PAPER)
    text(140, 1001, "EARLIER CONTEXT  /  COP31 draft 16 Nov. Paris polling 9–13 Nov. Geology paper 4 Nov. See † for 18 Nov reports.", "sans", 11, PAPER)

    final = image.resize((1024, 1024), Image.Resampling.LANCZOS)
    destination = ROOT / "assets" / "entry.png"
    final.save(destination, format="PNG", optimize=True)
    assert destination.stat().st_size <= 1_048_576
    print(dict(counts), destination.stat().st_size, sha256(destination.read_bytes()).hexdigest())


if __name__ == "__main__":
    cover()
