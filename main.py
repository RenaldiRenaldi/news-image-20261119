"""Offline, deterministic world newspaper for Thursday 19 November 2026."""
import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1024
PAPER = '#F8F5ED'
INK = '#142B38'
TEAL = '#246C70'
RUST = '#AB402D'
GRAY = '#63716F'
RULE = '#C4CEC6'
PALE = '#E6EDE5'
FONT_DIR = Path('/usr/share/fonts/truetype')

# The six counts are editorial constraints, checked before drawing.
# Source identifiers resolve to the independently researched ledger in SOURCES.md.
SECTIONS = [
    ('ASIA', [
        ('Shenzhen: Trump, Xi, Putin talks due today', 'A1'),
        ('Rohingya genocide judgment due at UN court', 'A2'),
        ('Duterte impeachment trial reaches Day 44', 'A3'),
        ('Bangladesh: lockdown called for today', 'A4'),
        ('India opens first Test against New Zealand', 'A5'),
        ('Philippines: rain and landslide warnings', 'A6'),
        ('Zamboanga heat index forecast at 45°C', 'A7'),
        ('Heat shortens classes in Cebu and Albay', 'A8'),
    ]),
    ('EUROPE', [
        ('Third bridge attack halts Crimea traffic', 'E1'),
        ('Berlin: US envoys due for Ukraine talks', 'E2'),
        ('UK–EU draft drops “trusted partnership”', 'E3'),
        ('Bulgaria reports vast government data theft', 'E4'),
        ('Italy removes fascist images from exhibition', 'E5'),
        ('Wine output forecast 7% below 5-year mean', 'E6'),
        ('Bulgaria: all 19 Filipino sailors now safe', 'E7'),
    ]),
    ('MIDDLE EAST', [
        ('Oman: tanker hit; UKMTO says crew safe', 'M1'),
        ('Israel pauses E1 settlement contract bids', 'M2'),
        ('Gaza ground raid displaces camp residents', 'M3'),
        ('US sanctions Hezbollah-linked charity', 'M4'),
        ('Saudi coalition reports missile interception', 'M5'),
        ('OPEC defends fossil fuels at COP31', 'M6'),
        ('Gallup report puts UAE atop safety ranking', 'M7'),
    ]),
    ('AMERICAS', [
        ('Anthropic debut due after reported $83 IPO', 'U1'),
        ('GTA VI launches after a 13-year wait', 'U2'),
        ('US panel seeks Microsoft–ByteDance briefing', 'U3'),
        ('Machado questions $100bn US oil agreement', 'U4'),
        ('Pastor convicted in Haiti president plot', 'U5'),
        ('Trump asks top court to keep TPS rollback', 'U6'),
        ('Democrats target Trump circle in probe push', 'U7'),
    ]),
    ('AFRICA', [
        ('South Africa rate decision due this afternoon', 'F1'),
        ('Liberia maritime security dialogue due today', 'F2'),
        ('Accra infrastructure investment summit due', 'F3'),
        ('ECOWAS defence chiefs enter final day', 'F4'),
        ('Kenya: Ruto national address due today', 'F5'),
        ('Polokwane women’s expo reaches final day', 'F6'),
        ('Cape Town tech festival reaches final day', 'F7'),
    ]),
    ('OCEANIA', [
        ('Australia pledges $10m for Pacific oceans', 'O1'),
        ('Air NZ charged over compensation claims', 'O2'),
        ('Vanuatu rejects bank-collapse rumours', 'O3'),
        ('Fiji rights body raises elder-abuse alarm', 'O4'),
        ('Fiji: cultural forgiveness cannot replace law', 'O5'),
        ('Fiji Army wins both Sukuna basketball titles', 'O6'),
    ]),
]


@lru_cache(None)
def font(size, kind='bold'):
    names = {
        'bold': FONT_DIR / 'noto/NotoSans-CondensedBold.ttf',
        'regular': FONT_DIR / 'dejavu/DejaVuSans.ttf',
        'serif': FONT_DIR / 'dejavu/DejaVuSerif-Bold.ttf',
    }
    return ImageFont.truetype(str(names[kind]), size)


def text(draw, xy, words, size=15, fill=INK, kind='bold'):
    draw.text(xy, words, font=font(size, kind), fill=fill)


def center(draw, words, y, size, kind='bold', fill=INK):
    width = draw.textlength(words, font=font(size, kind))
    text(draw, ((W-width)/2, y), words, size, fill, kind)


def lines_for(draw, words, size, width):
    result, line = [], ''
    for word in words.split():
        trial = (line + ' ' + word).strip()
        if draw.textlength(trial, font=font(size)) <= width:
            line = trial
        else:
            if line:
                result.append(line)
            line = word
    if line:
        result.append(line)
    return result


def map_band(draw):
    """Original, deliberately simplified cartographic silhouettes."""
    draw.rectangle((30, 106, 994, 187), fill=PALE)
    continents = [
        [(54,132),(79,118),(112,119),(135,127),(128,140),(110,146),(102,158),(87,162),(72,147),(59,146)],
        [(109,153),(127,153),(137,166),(129,184),(120,176)],
        [(265,129),(281,121),(298,125),(304,136),(292,142),(278,138)],
        [(281,143),(302,143),(312,157),(301,180),(290,174)],
        [(305,128),(333,119),(362,124),(388,120),(420,133),(444,137),(433,149),(411,146),(399,160),(377,151),(361,160),(338,144),(310,142)],
        [(424,163),(451,160),(466,172),(454,181),(436,178)],
        [(253,111),(260,110),(261,118),(255,122)],
        [(108,111),(127,109),(137,116),(124,121)],
    ]
    for polygon in continents:
        draw.polygon(polygon, fill='#7FA799')
    for x, y in [(94,136),(292,133),(326,151),(400,141),(297,160),(449,173)]:
        draw.ellipse((x-3,y-3,x+3,y+3), fill=RUST)
    text(draw, (494,115), '42 dispatches', 24, TEAL)
    text(draw, (495,147), '6 CONTINENTS  /  POLITICS · ECONOMY · CLIMATE · CULTURE', 13)
    text(draw, (495,165), 'Shenzhen to Suva. The world on one page.', 12, GRAY, 'regular')


def section(draw, index, x, y, height):
    name, stories = SECTIONS[index]
    width = 308
    draw.rectangle((x,y,x+width,y+25), fill=TEAL if index != 2 else RUST)
    text(draw,(x+8,y+1),name,17,PAPER)
    label = f'{len(stories):02d} / 19 NOV'
    lw = draw.textlength(label,font=font(11))
    text(draw,(x+width-8-lw,y+7),label,11,PAPER)
    slot = (height-31)/len(stories)
    for n,(headline,source) in enumerate(stories):
        sy = y+29+n*slot
        wrapped = lines_for(draw,headline,15,width-21)
        assert len(wrapped)<=2, (source,wrapped)
        text(draw,(x,sy+3),f'{n+1:02}',9,TEAL)
        for row,line in enumerate(wrapped):
            text(draw,(x+20,sy+row*17),line,15)
        if n+1<len(stories):
            draw.line((x+20,sy+slot-1,x+width,sy+slot-1),fill=RULE,width=1)


def strips(draw):
    draw.rectangle((30,823,994,869),fill=INK)
    text(draw,(42,828),'MARKET PULSE',15,'#E4B766')
    text(draw,(201,827),'ANTHROPIC  $83/share reported IPO  ·  Trading due today on Nasdaq',15,PAPER)
    text(draw,(201,849),'19 NOV REPORT  |  Brent $91.43/bbl  ·  Gold futures $3,736.80/oz  [Gatekeepers / Reuters data]',11,'#C3D5D0')
    draw.rectangle((30,877,994,939),fill='#ECE7D9')
    text(draw,(42,882),'TIMELINE OF THE DAY',14,RUST)
    text(draw,(42,906),'19 NOV · UTC',11,GRAY)
    moments = [
        ('00:14  REPORT','19 Filipino sailors safe','GMA / Bulgaria'),
        ('00:06  REPORT','Air NZ charges filed','RNZ / New Zealand'),
        ('09:00  DUE','Rohingya judgment','ICJ / The Hague'),
        ('TODAY  DUE','Trump–Xi–Putin talks','Shenzhen / China'),
    ]
    # Time order is fixed explicitly rather than derived from machine time.
    moments[0],moments[1] = moments[1],moments[0]
    for i,(stamp,event,place) in enumerate(moments):
        xx = 238+i*188
        draw.line((xx-10,887,xx-10,929),fill=RULE)
        text(draw,(xx,881),stamp,12,TEAL)
        text(draw,(xx,899),event,14)
        text(draw,(xx,920),place,10,GRAY,'regular')
    draw.rectangle((30,947,994,991),fill=PALE)
    text(draw,(42,952),'DAY IN NUMBERS',14,RUST)
    entries = [('13 YEARS','GTA sequel wait'),('19 SAFE','Filipino tanker crew'),('3,401','E1 homes in paused bids'),('$10m','Pacific ocean pledge')]
    for i,(number,label) in enumerate(entries):
        xx = 233+i*187
        text(draw,(xx,949),number,20,TEAL)
        text(draw,(xx,975),label,10,INK,'regular')


def build():
    assert [len(s) for _,s in SECTIONS] == [8,7,7,7,7,6]
    assert sum(len(s) for _,s in SECTIONS) == 42
    image = Image.new('RGB',(W,W),PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((13,13,1010,1010),outline=INK,width=2)
    text(draw,(31,20),'INDEPENDENT WORLD BRIEFING',11,TEAL)
    text(draw,(823,20),'THURSDAY / No. 19',11,TEAL)
    center(draw,'THE WORLD TODAY',34,43,'serif')
    center(draw,'THURSDAY, 19 NOVEMBER 2026',86,16,fill=RUST)
    map_band(draw)
    text(draw,(31,197),'LEAD / SHENZHEN  ·  DIPLOMACY',12,RUST)
    text(draw,(29,213),'THREE POWERS, ONE TABLE',34,INK,'serif')
    text(draw,(31,258),'Trump, Xi and Putin are due to meet today. Nuclear arms control is on Trump’s agenda.',15)
    text(draw,(31,280),'Talks are scheduled; no agreement is being claimed.  Reuters / 19 November dispatch',11,GRAY,'regular')
    for column in range(3):
        x = 31+column*328
        section(draw,column,x,308,259)
        section(draw,column+3,x,580,232)
        if column<2:
            draw.line((x+317,308,x+317,809),fill=RULE)
    strips(draw)
    center(draw,'19 NOVEMBER EDITION  ·  Reports and today’s agenda  ·  “Due” denotes scheduled, not completed',996,9,fill=GRAY)
    return image


def main():
    destination = Path(os.environ.get('MAKEFUN_OUTPUT_DIR','out'))
    destination.mkdir(parents=True,exist_ok=True)
    build().save(destination/'entry.png',format='PNG',optimize=True,compress_level=9)


if __name__ == '__main__':
    main()
