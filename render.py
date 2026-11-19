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
PAPER, INK, RED, GREEN, GOLD, RULE = "#f5efe2", "#12213e", "#bc253f", "#166765", "#f4ca7d", "#c6bba3"
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


def headline(x, y, message, width):
    words = message.split()
    for size in range(23, 16, -1):
        if measure(message,"h",size) <= width:
            lines = [message]
        else:
            candidates = [(" ".join(words[:i])," ".join(words[i:])) for i in range(1,len(words))]
            candidates = [p for p in candidates if max(measure(v,"h",size) for v in p) <= width]
            if not candidates:
                continue
            lines = min(candidates,key=lambda p: abs(measure(p[0],"h",size)-measure(p[1],"h",size)))
        if lines:
            for i, line in enumerate(lines):
                label(x,y+i*24,line,"h",size)
            return
    raise ValueError(message)


def items():
    rows = []
    for row in (ROOT / "SOURCES.md").read_text().splitlines():
        if row.startswith("| ") and row[2:4].isdigit():
            num, region, place, status, title, detail, _ = map(str.strip, row.strip("|").split("|"))
            rows.append((int(num), region, place, status, title, detail))
    assert [r[0] for r in rows] == list(range(1, 43))
    return rows


def sketch(n, x, y, w, h):
    # Original editorial scenes on a shared artboard; no decorative dot texture.
    backgrounds = ["#cdddea", "#53215e", "#103f30", "#cadbe9", "#dfebce",
                   "#164e73", "#bdd4e2", "#cae8df", "#afd2e5", "#9ac4d8",
                   "#6da3be", "#edc78f", "#d5c8b1"]
    box(x, y, w, h, backgrounds[n-1])
    sx, sy = w/100, h/48
    def rect(a,b,c,d,color):
        box(x+a*sx,y+b*sy,c*sx,d*sy,color)
    def poly(points,color):
        pen.polygon([px(x+a*sx,y+b*sy) for a,b in points],fill=color)
    def oval(a,b,c,d,color):
        pen.ellipse(px(x+a*sx,y+b*sy,x+c*sx,y+d*sy),fill=color)
    def path(pairs, color=PAPER, weight=1.5):
        stroke([(x+a*sx, y+b*sy) for a, b in pairs], color, weight)
    if n == 1:
        for a,b in [(2,22),(12,16),(29,25),(42,12),(66,20),(82,10),(93,24)]:
            rect(a,b,7,42-b,"#a8bfce")
        rect(0,39,100,9,"#79553e")
        oval(9,36,92,46,"#b88550")
        for k,a in enumerate((24,49,74)):
            path([(a,39),(a,7)],INK,2)
            rect(a,7,18,14,"#f7f3e9")
            if k==0:
                for b in (7,11,15,19): rect(a,b,18,2,"#b72940")
                rect(a,7,7,8,"#234875")
            elif k==1:
                rect(a,7,18,14,"#dc302e")
                label(x+(a+2)*sx,y+9*sy,"★","s",10,"#ffdb5c")
                for da,db in ((8,2),(10,5),(10,8),(8,11)):
                    oval(a+da,7+db,a+da+1.3,8.3+db,"#ffdb5c")
            else:
                rect(a,12,18,4.5,"#2354b0"); rect(a,16.5,18,4.5,"#ce293e")
            rect(a-2,38,5,3,INK)
    elif n == 2:
        for b in range(48):
            t=b/47
            rect(0,b,100,1,tuple(round(u+(v-u)*t) for u,v in zip((54,22,92),(248,113,106))))
        oval(39,12,64,47,"#ffcf65")
        for a,b,ww in [(0,31,9),(9,23,7),(18,33,8),(28,27,7),(64,28,7),(73,22,7),(82,31,7),(91,19,9)]:
            rect(a,b,ww,48-b,"#261437")
        for a in (32,73):
            path([(a,47),(a+2,17)],"#241735",2)
            for da,db in ((-11,3),(-9,-5),(8,-6),(12,2)):
                poly([(a+2,17),(a+da*.55,15+db*.6),(a+da,17+db),
                      (a+da*.7,17+db*.4)],"#241735")
        pen.rounded_rectangle(px(x+42*sx,y+15*sy,x+61*sx,y+25*sy),radius=7,fill=INK)
        path([(46,18),(46,22)],PAPER,1.7)
        path([(44.5,20),(47.5,20)],PAPER,1.7)
        oval(55,18,57,21,"#ffcf65"); oval(58,20,60,23,"#f582b0")
        label(x+w/2,y+6,"VICE CITY","b",13,"#fff0cc","mt")
    elif n == 3:
        for b in (17,29,41): path([(5,b),(95,b)],"#2a6750",.6)
        for a,b in [(13,34),(27,29),(41,32),(55,22),(69,16),(83,8)]:
            path([(a,b-4),(a,b+10)],"#94e6b3",1.4)
            rect(a-2,b,4,7,"#53cd86" if a!=41 else "#ed7370")
        path([(8,42),(27,32),(41,35),(55,25),(69,19),(89,7)],GOLD,2)
        label(x+w-12,y+5,"ANT  $83","b",20,PAPER,"rt")
        label(x+12,y+h-5,"NASDAQ · PRICED 18 NOV","m",8,"#a3e7c2","lb")
    elif n == 4:
        poly([(17,16),(50,2),(84,16)],"#a4956d")
        rect(19,16,63,3,INK)
        for a in (23,38,56,71): rect(a,19,5,21,PAPER)
        path([(50,22),(50,34)],INK,1.2); path([(44,25),(56,25)],INK,1.2)
        rect(15,40,72,4,"#80785c"); rect(12,44,78,4,INK)
    elif n == 5:
        oval(35,3,52,43,"#2d92b2")
        poly([(38,7),(44,5),(47,16),(42,24),(44,36),(40,36),(38,24)],"#62ad61")
        path([(44,4),(41,23),(45,43)],"#acd6e2",.6)
        oval(68,28,76,44,RED); rect(70,9,4,26,RED)
        path([(68,29),(68,9),(72,5),(76,9),(76,29)],INK,1)
        oval(82,5,92,20,"#f7b839")
    elif n == 6:
        poly([(83,0),(100,0),(100,48),(67,48),(73,31),(70,18)],"#d3bd86")
        for phase in (0,math.pi):
            path([(44+(2+t*.22)*math.cos(t/8+phase),24+(2+t*.22)*math.sin(t/8+phase)) for t in range(77)],PAPER,2.7)
        oval(42,21,46,27,"#164e73")
        label(x+w-5,y+4,"RED ALERT","b",7,PAPER,"rt")
    elif n == 7:
        rect(22,3,65,20,"#2871b8"); rect(22,23,65,21,"#f4cd43")
        path([(22,46),(22,2)],INK,2)
        oval(43,19,64,44,INK); rect(34,41,39,5,INK)
        path([(53,20),(53,31)],GOLD,1.5)
    elif n == 8:
        poly([(32,3),(67,3),(67,44),(32,44)],PAPER)
        label(x+49*sx,y+8*sy,"APEC","b",9,GREEN,"mt")
        for b in (25,30,35): path([(37,b),(61,b)],"#86958c",.8)
        oval(57,33,64,44,RED)
        poly([(70,36),(83,5),(86,8),(73,39)],INK)
        poly([(70,36),(73,39),(69,43)],"#c49543")
    elif n == 9:
        for a in (25,63):
            poly([(a-4,27),(a+9,10),(a+23,27)],"#ad5f49")
            rect(a,27,19,17,PAPER); rect(a+7,32,5,12,INK)
        for b in (37,43):
            path([(0,b),(14,b+3),(29,b),(45,b+3),(62,b),(78,b+3),(100,b)],"#377fa0",2.5)
        for a in (31,47,71,85): path([(a,2),(a-3,12)],"#edf5fa",1)
    elif n == 10:
        rect(0,34,100,14,"#3d83a0")
        for a in (17,43,77): rect(a,22,4,22,"#64635a")
        path([(4,23),(96,23)],INK,3)
        path([(17,22),(30,8),(45,22),(60,8),(79,22)],"#e5dfc8",1.5)
        path([(56,23),(62,28),(68,23)],RED,2.7)
    elif n == 11:
        rect(0,35,100,13,"#246481")
        poly([(15,25),(89,25),(79,41),(28,41)],INK)
        rect(28,17,44,9,"#d6b66d"); rect(72,11,9,15,PAPER)
        rect(73,5,3,7,INK)
        for a in (31,46,61): rect(a,18,2,7,"#8e7246")
        path([(8,44),(27,44),(33,47),(63,47),(70,43),(96,43)],"#afd6de",1)
    elif n == 12:
        oval(76,2,91,25,"#ef9d42")
        for a,b,ww in [(13,23,13),(29,16,9),(42,29,11),(57,17,10),(71,27,8)]: rect(a,b,ww,44-b,"#a27f59")
        poly([(29,16),(33.5,4),(38,16)],"#a27f59")
        path([(33.5,8),(33.5,15)],GOLD,1)
        rect(0,44,100,4,"#654c39")
    elif n == 13:
        pen.rounded_rectangle(px(x+27*sx,y+8*sy,x+59*sx,y+24*sy),radius=8,fill=PAPER)
        pen.rounded_rectangle(px(x+43*sx,y+8*sy,x+59*sx,y+24*sy),radius=8,fill=RED)
        pen.rounded_rectangle(px(x+53*sx,y+28*sy,x+84*sx,y+42*sy),radius=7,fill=GREEN)
        for a,b in ((31,35),(41,40),(71,14),(82,20)): oval(a,b,a+4,b+6,"#f5d16e")


# Coordinates are followed by the callout's offset from the plotted point.
PLACES = [
    (114.06,22.54,-24,-11), (-74.01,40.71,3,-19), (-74.01,40.71,21,-5),
    (4.30,52.08,-14,-17), (30.71,36.90,9,12), (85.53,19.81,-10,16),
    (30.52,50.45,10,-16), (114.06,22.54,17,12), (-80.14,26.12,11,13),
    (36.5,45.3,21,-4), (56.25,26.2,42,15), (46.68,24.71,-8,30),
    (22.64,32.76,-9,19),
]


def world_map(x, y):
    box(x, y, 486, 190, INK)
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
    canvas.paste("#dcc58d", (0,0), mask)
    for lon, lat, name in [(-139,62,"N. AMERICA"),(-77,-18,"S. AMERICA"),(-13,71,"EUROPE"),
                           (-7,0,"AFRICA"),(86,61,"ASIA"),(122,-45,"OCEANIA")]:
        label(*project(lon,lat), name, "m", 7, "#7497b6")
    for n, (lon, lat, dx, dy) in enumerate(PLACES, 1):
        a, b = project(lon,lat)
        stroke([(a,b),(a+dx,b+dy)], RED, .8)
        disc(a,b,1.7,RED)
        disc(a+dx,b+dy,7,RED)
        label(a+dx,b+dy,f"{n:02}","m",8,PAPER,"mm")


FIGURES = (
    ("$81.3bn","Anthropic IPO priced 18 Nov"),
    ("17.1m","GTA VI pre-orders · Sensor Tower est."),
    ("72,000","Odisha evacuated · 19 Nov briefing"),
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
        y = 225 if hero else 438+index//5*108
        w = 322 if hero else 192
        h = 102 if hero else 38
        if not hero:
            stroke([(x,y-3),(x+w,y-3)], RULE)
        sketch(n,x,y,w,h)
        disc(x+13,y+12,10 if hero else 9,INK)
        label(x+13,y+12,f"{n:02}","m",12 if hero else 10,PAPER,"mm")
        label(x,y+h+7,f"{place.upper()}  /  {date.upper()}","m",10 if hero else 8,RED,limit=w)
        if hero:
            headline(x,y+h+23,title,w-1)
        else:
            label(x,y+h+19,title,"h",14,limit=w-1)
        copy(x,y+h+(75 if hero else 38),detail,11 if hero else 10,w-1,12 if hero else 11)

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
        marker = " ◇" if "agenda" in date else " †" if "18 Nov" in date else " ~" if "forecast" in date else " ‡" if "context" in date else ""
        stroke([(x,y-3),(x+w,y-3)], RULE, .5)
        label(x,y+1,f"{n:02}","m",10,RED)
        label(x+20,y+1,f"{place.upper()}{marker}  ·  {title}","s",11,limit=w-21)
    label(22,955,"◇  Agenda / scheduled     †  18 Nov, carried in 19 Nov editions     ~  Forecast     ‡  Earlier context","m",9,GREEN)
    pen.rectangle(px(22,973,1002,1020),outline=RED,width=4)
    label(31,981,"DATE CHECK","h",14,RED)
    label(156,981,"EARLIER EVENTS ≠ NEW TODAY: pricing, deluge and Gaza operation (18 Nov); Derna seizure (17 Nov).","s",11,INK,limit=833)
    label(156,999,"CONTEXT: COP31 draft (16 Nov); Paris poll (9 Nov); geology (4 Nov). Today’s follow-ups are dated above.","s",11,INK,limit=833)

    destination = ROOT / "assets" / "entry.png"
    # Keep text antialiasing while reserving the small scenes' accent colors.
    reduced = canvas.resize((1024,1024), Image.Resampling.LANCZOS)
    palette = reduced.quantize(colors=224,method=Image.Quantize.MEDIANCUT)
    accents = [PAPER,INK,RED,GREEN,GOLD,"#53cd86","#94e6b3","#103f30",
               "#62ad61","#2d92b2","#ffcf65","#dc302e","#2354b0",
               "#d3bd86","#2871b8","#f4cd43","#318bb0","#77b978",
               "#f7b839","#dcc58d","#ed7370","#d6b66d","#edc78f",
               "#ef9d42","#261437","#241735","#a3e7c2","#ffdb5c",
               "#cdddea","#cadbe9","#cae8df","#e5dfc8"]
    palette.putpalette(palette.getpalette()[:224*3]+[
        int(color[i:i+2],16) for color in accents for i in (1,3,5)])
    reduced.quantize(palette=palette,dither=Image.Dither.NONE).save(
        destination, format="PNG", optimize=True)
    raw = destination.read_bytes()
    assert len(raw) <= 1_048_576
    print(dict(counts), len(raw), sha256(raw).hexdigest())


if __name__ == "__main__":
    front_page()
