"""Typeset the edition. Only the checked-in PNG is needed at runtime."""
from collections import Counter
from functools import cache
from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen
import json
import math

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/"
LAND_HASH = "9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9"
PAPER, INK, RED, GREEN, GOLD, RULE = "#f5efe2", "#182b30", "#9e3d30", "#166765", "#eabc7c", "#c6bba3"
canvas = Image.new("RGB", (2048, 2048), PAPER)
pen = ImageDraw.Draw(canvas)


@cache
def font(face, size):
    family = {"h": "Serif-Bold", "s": "Sans", "b": "Sans-Bold", "m": "SansMono-Bold"}[face]
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVu{family}.ttf", size * 2)


def px(*positions):
    return tuple(round(p * 2) for p in positions)


def measure(label, face, size):
    return pen.textlength(label, font=font(face, size)) / 2


def label(x, y, value, face, size, color=INK, anchor="lt", limit=1024):
    while measure(value, face, size) > limit:
        size -= 1
    pen.text(px(x, y), value, fill=color, font=font(face, size), anchor=anchor)


def box(x, y, w, h, color):
    pen.rectangle(px(x, y, x+w, y+h), fill=color)


def stroke(points, color, weight=1):
    pen.line([px(*p) for p in points], fill=color, width=max(1, round(weight*2)))


def disc(x, y, radius, color):
    pen.ellipse(px(x-radius, y-radius, x+radius, y+radius), fill=color)


def copy(x, y, message, size, limit, leading):
    lines = [""]
    for word in message.split():
        next_line = (lines[-1] + " " + word).strip()
        if measure(next_line, "s", size) <= limit:
            lines[-1] = next_line
        else:
            lines.append(word)
    assert len(lines) <= 3, (message, lines)
    for i, row in enumerate(lines):
        label(x, y + i * leading, row, "s", size)


def items():
    rows = []
    for row in (ROOT / "SOURCES.md").read_text().splitlines():
        if row.startswith("| ") and row[2:4].isdigit():
            num, region, place, status, title, detail, _ = map(str.strip, row.strip("|").split("|"))
            rows.append((int(num), region, place, status, title, detail))
    assert [r[0] for r in rows] == list(range(1, 43))
    return rows


COLORS = (
    "#244852 #69988e", "#563841 #a96866", "#274943 #7ca684",
    "#455362 #9caaad", "#365c50 #8fb38c", "#225a65 #88b9b4",
    "#3c4c59 #7a9aa2", "#245950 #85aa8a", "#2c596c #81b4c0",
    "#71473b #bc8067", "#504f65 #a294ac", "#63423e #c58270", "#43584f #86a691",
)

# Original line drawings, each expressed on a 100 by 48 artboard.
GLYPHS = {
    4: "24,18 50,5 76,18 24,18;30,23 30,37;43,23 43,37;57,23 57,37;70,23 70,37;23,40 77,40;18,44 82,44",
    5: "18,34 34,34 34,24 48,24 48,29 63,29 63,15 82,15;22,39 77,39",
    7: "8,36 92,36;20,43 20,14 50,33 80,14 80,43;50,8 50,28;50,8 62,8 62,16 50,16",
    8: "18,26 34,13 50,26 66,13 83,26 66,39 50,26 34,39 18,26",
    9: "23,30 23,17 36,9 49,17 49,30;61,31 61,23 71,15 82,23 82,31;5,34 17,37 29,34 40,37 52,34 64,37 76,34 88,37 98,34",
    11: "18,41 85,41;25,37 25,19 33,19 33,37;45,37 45,13 53,13 53,37;65,37 65,26 73,26 73,37",
    13: "9,29 91,29 78,42 21,42 9,29;25,29 25,18 37,18 37,29;44,29 44,18 56,18 56,29;63,29 63,18 75,18 75,29",
}


def sketch(n, x, y, w, h):
    bg, mid = COLORS[n-1].split()
    box(x, y, w, h, bg)
    sx, sy = w/100, h/48

    def path(pairs, color=GOLD, weight=1.5):
        stroke([(x+a*sx, y+b*sy) for a, b in pairs], color, weight)

    for a in range(4, 100, 5):
        for b in range(4, 48, 7):
            disc(x+a*sx, y+b*sy, .55, mid)
    if n in GLYPHS:
        for segment in GLYPHS[n].split(";"):
            pairs = [tuple(map(int, packet.split(","))) for packet in segment.split()]
            path(pairs, weight=2)
    elif n in (1, 2, 12):
        disc(x+78*sx, y+15*sy, 9*sy, mid)
        for a, b, span in [(8,30,10),(21,26,7),(31,18,9),(43,27,8),(54,11,8),(64,23,7),(73,27,8),(85,30,9)]:
            box(x+a*sx, y+b*sy, span*sx, (40-b)*sy, GOLD if a % 2 else mid)
            for unit in range(b+4, 39, 4):
                path([(a+2, unit), (a+span-2, unit)], bg, .7)
        path([(1,40),(99,40)])
        if n == 2:
            path([(38,47),(47,40),(54,40),(69,47)], weight=2.2)
            for a in (14, 85):
                path([(a,40),(a+3,18),(a-4,22),(a+3,18),(a+8,22)])
        elif n == 1:
            for a in (24, 48, 72):
                disc(x+a*sx, y+37*sy, 2.6*sy, GOLD)
    elif n == 3:
        values = [(15,34),(28,28),(41,22),(54,25),(67,14),(80,7)]
        for a, b in values:
            box(x+a*sx, y+b*sy, 7*sx, (42-b)*sy, mid)
        path([(10,41), *values, (91,6)], weight=2)
        path([(85,4),(91,6),(87,12)])
    elif n == 6:
        for phase in (0, math.pi):
            path([(50+(3+t*.29)*1.6*math.cos(t/10+phase),
                   24+(3+t*.29)*math.sin(t/10+phase)) for t in range(64)], weight=2.2)
        disc(x+50*sx, y+24*sy, 1.9, GOLD)
    elif n == 10:
        for b in (9,17,25,34,42):
            path([(0,b),(20,b-4),(40,b+2),(62,b-2),(81,b+3),(100,b)],
                 GOLD if b == 25 else mid, 2.2)


# Coordinates are followed by the callout's offset from the plotted point.
PLACES = [
    (114.06,22.54,-24,-11), (-74.01,40.71,3,-19), (-74.01,40.71,21,-5),
    (4.30,52.08,-14,-17), (30.71,36.90,9,12), (85.53,19.81,-10,16),
    (30.52,50.45,10,-16), (114.06,22.54,17,12), (-80.14,26.12,11,13),
    (-112.11,36.06,-7,11), (2.35,48.86,-24,8), (46.68,24.71,12,14),
    (22.64,32.76,-9,19),
]


def world_map(x, y):
    box(x, y, 486, 190, "#e4eae0")
    scale = 462 / 360

    def project(lon, lat):
        return (x+12+(lon+180)*scale, y+9+(83-lat)*scale)

    with urlopen(BASE + "ne_110m_land.geojson", timeout=20) as reply:
        land = reply.read()
    assert sha256(land).hexdigest() == LAND_HASH
    mask = Image.new("1", canvas.size)
    geometry_pen = ImageDraw.Draw(mask)
    for part in json.loads(land)["features"]:
        geometry = part["geometry"]
        polygons = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            polygons = [polygons]
        for outer, *holes in polygons:
            if max(lat for _, lat in outer) < -55:
                continue
            for boundary, color in [(outer, 1), *((hole, 0) for hole in holes)]:
                geometry_pen.polygon([px(*project(*p)) for p in boundary], fill=color)
    for lon in range(-150, 180, 30):
        stroke([project(lon,83), project(lon,-55)], "#c2cec1", .5)
    for lat in range(-30, 75, 30):
        stroke([project(-180,lat), project(180,lat)], "#c2cec1", .5)
    for a in range(x+10, x+478, 3):
        for b in range(y+7, y+185, 3):
            if mask.getpixel(px(a,b)):
                disc(a,b,.68,"#5b8d7e")
    for lon, lat, name in [(-139,62,"N. AMERICA"),(-77,-18,"S. AMERICA"),(-13,71,"EUROPE"),
                           (-7,0,"AFRICA"),(86,61,"ASIA"),(122,-45,"OCEANIA")]:
        label(*project(lon,lat), name, "m", 8, GREEN)
    for n, (lon, lat, dx, dy) in enumerate(PLACES, 1):
        a, b = project(lon,lat)
        stroke([(a,b),(a+dx,b+dy)], RED, .8)
        disc(a,b,1.7,RED)
        disc(a+dx,b+dy,7,RED)
        label(a+dx,b+dy,f"{n:02}","m",8,PAPER,"mm")


FIGURES = (
    ("$81.3bn","Anthropic IPO priced 18 Nov"),
    ("17.1m","GTA VI pre-orders · Sensor Tower est."),
    ("204,070","Odisha identified for possible evacuation"),
    ("$120bn","COP31 draft proposal · no deal yet"),
    ("13 years","Since GTA V first launched"),
    ("15.3 in","Broward rain · 24h to 18 Nov"),
)


def front_page():
    rows = items()
    counts = Counter(row[1] for row in rows)
    box(0,0,1024,8,RED)
    label(23,20,"T H E   D A I L Y   A T L A S","m",11,RED)
    label(1001,20,"THURSDAY 19 NOVEMBER 2026","m",12,RED,"rt")
    label(512,38,"THE WORLD IN ONE PICTURE","h",61,INK,"mt",978)
    label(512,103,"Shenzhen summit  /  GTA VI launches  /  Record Anthropic IPO  /  Rohingya genocide case  /  Cyclone Akvan","b",14,INK,"mt",980)
    stroke([(22,126),(1002,126)], INK, 1.6)
    regions = ("Europe","Americas","Asia-Pacific","Middle East","Africa","Oceania","World")
    for i, region in enumerate(regions):
        label(92+i*140,132,f"{region.upper()}  {counts[region]:02}","m",11,INK,"mt")
    box(22,152,980,60,INK)
    for i, (amount, caption) in enumerate(FIGURES):
        x = 22+i*980/6
        if i:
            stroke([(x,163),(x,201)], "#637171", .7)
        label(x+9,159,amount,"h",27,GOLD)
        label(x+9,193,caption,"s",9,PAPER,limit=146)

    for n, _, place, date, title, detail in rows[:13]:
        hero = n <= 3
        index = n-1 if hero else n-4
        x = 22 + (index*329 if hero else index%5*197)
        y = 225 if hero else 421+index//5*114
        w = 322 if hero else 192
        h = 91 if hero else 33
        if not hero:
            stroke([(x,y-3),(x+w,y-3)], RULE)
        sketch(n,x,y,w,h)
        label(x+8,y+7,f"{n:02}","m",17 if hero else 14,PAPER)
        label(x,y+h+7,f"{place.upper()}  /  {date.upper()}","m",10 if hero else 8,RED,limit=w)
        label(x,y+h+(25 if hero else 19),title,"h",23 if hero else 15,limit=w-1)
        copy(x,y+h+(56 if hero else 38),detail,12 if hero else 10,w-1,14 if hero else 12)

    stroke([(22,655),(1002,655)], INK, 1.6)
    label(22,662,"WHERE IT HAPPENED","h",21)
    label(508,670,"01–13  /  LEAD STORIES","m",9,GREEN,"rt")
    world_map(22,687)
    label(523,662,"AROUND THE WORLD","h",21)
    label(1002,670,"14–42  /  CITY DESK","m",9,GREEN,"rt")
    for n, _, place, date, title, _ in rows[13:]:
        i = n-14
        if i < 20:
            x, y, w = 523+i//10*243, 688+i%10*19, 235
        else:
            j = i-20
            x, y, w = 22+j//3*329, 891+j%3*22, 322
        marker = " ◇" if "agenda" in date else " †" if "18 Nov" in date else " ~" if "forecast" in date else ""
        stroke([(x,y-3),(x+w,y-3)], RULE, .5)
        label(x,y+1,f"{n:02}","m",10,RED)
        label(x+20,y+1,f"{place.upper()}{marker}  ·  {title}","s",11,limit=w-21)
    label(22,955,"◇  Agenda or scheduled action     †  18 Nov development, carried in 19 Nov editions     ~  Forecast","m",9,GREEN)
    box(0,974,1024,50,INK)
    label(22,984,"DATE CHECK","h",14,GOLD)
    label(140,983,"18 NOV OR EARLIER  /  Derna seizure 17 Nov, reported 18 Nov. Florida deluge and Anthropic pricing 18 Nov.","s",11,PAPER)
    label(140,1001,"EARLIER CONTEXT  /  COP31 draft 16 Nov. Paris polling 9–13 Nov. Geology paper 4 Nov. See † for 18 Nov reports.","s",11,PAPER)

    destination = ROOT / "assets" / "entry.png"
    canvas.resize((1024,1024), Image.Resampling.LANCZOS).save(destination, format="PNG", optimize=True)
    raw = destination.read_bytes()
    assert len(raw) <= 1_048_576
    print(dict(counts), len(raw), sha256(raw).hexdigest())


if __name__ == "__main__":
    front_page()
