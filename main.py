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
    """Fixed equirectangular coastlines and geographically located dispatches."""
    draw.rectangle((30, 106, 994, 187), fill=PALE)
    # Natural Earth 1:110m public-domain land, simplified to 0.7 degrees.
    # Coordinates are embedded: rendering never downloads geographic data.
    # Europe/Asia/Africa and the Americas share their real land connections.
    coastlines = [
        [(107,77),(114.1,75.8),(109.4,74.2),(123.2,73),(123.3,73.7),(127,73.6),
         (131.3,70.8),(132.3,71.8),(139.9,71.5),(139.1,72.4),(140.5,72.8),
         (159,70.9),(160.9,69.4),(167.8,69.6),(169.6,68.7),(170.8,69),
         (170.5,70.1),(178.6,69.4),(180,69),(180,65),(177.4,64.6),
         (179.5,62.6),(173.7,61.7),(170.3,59.9),(163.5,59.9),(162,58.2),
         (163.2,57.6),(162.1,54.9),(156.8,51),(155.9,56.8),(163.7,61.1),
         (164.5,62.6),(160.1,60.5),(159.3,61.8),(156.7,61.4),(154.2,59.8),
         (155,59.1),(142.2,59),(135.1,54.7),(139.9,54.2),(141.4,52.2),
         (138.2,46.3),(134.9,43.4),(132.3,43.3),(127.5,39.8),(129.5,36.8),
         (129.1,35.1),(126.5,34.4),(126.1,36.7),(126.9,36.9),(124.7,38.1),
         (125.3,39.6),(121.1,38.9),(121.6,40.9),(118,39.2),(118.9,37.4),
         (122.4,37.5),(119.2,34.9),(121.9,31.7),(121.7,28.2),(115.9,22.8),
         (110.8,21.4),(110.4,20.3),(108.5,21.7),(105.9,19.8),(109.3,13.4),
         (109.2,11.7),(105.2,8.6),(105.1,9.9),(100.1,13.4),(99.2,9.2),
         (103,5.5),(104.2,1.3),(101.4,2.8),(100.1,6.5),(98.3,7.8),
         (98.8,11.4),(97.2,16.9),(94.2,16),(94.3,18.2),(91.4,22.8),
         (87,21.5),(86.5,20.2),(80.3,15.9),(79.9,10.4),(77.5,8),
         (73.5,16),(72.6,21.4),(70.5,20.9),(66.4,25.4),(57.4,25.7),
         (56.5,27.1),(54.7,26.5),(51.5,27.9),(50.1,30.1),(48,30),
         (50.8,24.8),(51.6,25.8),(51.8,24),(54,24.1),(56.4,26.4),
         (56.8,24.2),(59.8,22.3),(55.3,17.2),(43.5,12.6),(42.6,16.8),
         (34.6,28.1),(34.9,29.5),(33.9,27.6),(32.4,29.9),(36.9,22),
         (37.5,18.6),(43.3,12.4),(42.7,11.7),(44.6,10.4),(51.1,12),
         (51,10.6),(47.7,4.2),(39.2,-4.7),(40.8,-14.7),(34.8,-19.8),
         (35.6,-23.7),(32.6,-25.7),(32.2,-28.8),(25.8,-33.9),(19.6,-34.8),
         (18.4,-34.1),(18.2,-31.7),(15.2,-27.1),(14.3,-22.1),(11.8,-18.1),
         (13.7,-10.7),(11.9,-5),(8.8,-1.1),(9.4,3.7),(8.5,4.8),
         (5.9,4.3),(4.3,6.3),(-2,4.7),(-9,4.8),(-16.6,12.2),
         (-17.6,14.7),(-16.1,18.1),(-17,21.9),(-14.4,26.3),(-9.6,29.9),
         (-9.3,32.6),(-5.9,35.8),(-2.2,35.2),(1.5,36.6),(9.5,37.4),
         (11.1,36.9),(10.3,33.8),(19.1,30.3),(21.5,32.8),(28.9,30.9),
         (33.8,31),(36.2,36.7),(27.6,36.7),(26.2,39.5),(33.5,42),
         (38.3,40.9),(41.7,42),(36.7,45.2),(39.1,47.3),(35,46.3),
         (36.3,45.1),(33.9,44.4),(32.5,45.3),(33.3,46.1),(30.7,46.6),
         (27.7,42.6),(28.8,41.1),(22.6,40.3),(24,37.7),(23.1,37.9),
         (22.5,36.4),(19.4,40.3),(19.5,41.7),(13.1,45.7),(12.6,44.1),
         (18.5,40.2),(16.9,40.4),(16.1,38),(15.4,40),(8.9,44.4),
         (3.1,43.1),(3,41.9),(0.8,41),(0.1,38.7),(-2.1,36.7),
         (-5.4,35.9),(-8.9,36.9),(-9.4,43),(-1.4,44),(-1.2,46),
         (-4.6,48.7),(-1.6,48.6),(-1.9,49.8),(1.3,50.1),(4.7,53.1),
         (8.1,53.5),(8.5,57.1),(10.6,57.7),(10.9,56.5),(9.7,55.5),
         (10.9,54),(19.7,54.4),(21.3,55.2),(21.6,57.4),(24.1,57),
         (24.4,58.4),(23.3,59.2),(29.1,60),(22.9,59.8),(21.3,60.7),
         (21.5,63.2),(25.4,65.1),(22.2,65.7),(17.8,62.7),(17.1,61.3),
         (18.8,60.1),(16.8,58.7),(15.9,56.1),(12.9,55.4),(10.4,59.5),
         (8.4,58.3),(5.7,58.6),(5,62),(14.8,67.8),(24.5,71),
         (28.2,71.2),(31.3,70.5),(30,70.2),(31.1,69.6),(40.3,67.9),
         (41.1,66.8),(40,66.3),(33.2,66.6),(34.8,65.9),(34.9,64.4),
         (37,63.8),(37.2,65.1),(39.6,64.5),(42.1,66.5),(43.9,66.1),
         (44.5,66.8),(43.5,68.6),(46.3,68.3),(46.8,67.7),(45.6,67),
         (46.3,66.7),(53.7,68.9),(59.9,68.3),(61.1,68.9),(60.6,69.9),
         (68.5,68.1),(69.2,68.6),(66.9,69.5),(66.7,71),(69.2,72.8),
         (72.6,72.8),(71.8,71.4),(73.7,68.4),(71.3,66.3),(72.4,66.2),
         (75.1,67.8),(73.6,69.6),(74.4,70.6),(73.1,71.4),(74.7,72.8),
         (76.4,71.2),(75.9,71.9),(77.6,72.3),(81.5,71.8),(80.5,73.6),
         (86.8,73.9),(86,74.5),(87.2,75.1),(100.8,76.4),(104.4,77.7),(107,77)],
        [(-90.5,69.5),(-90.6,68.5),(-89.2,69.3),(-87.4,67.2),(-85.5,69.9),
         (-82.6,69.7),(-81.3,69.2),(-81.3,67.6),(-85.8,66.6),(-87.3,64.8),
         (-93.2,62),(-94.7,58.9),(-93.2,58.8),(-92.3,57.1),(-82.3,55.1),
         (-82.1,53.3),(-79.9,51.2),(-78.6,52.6),(-79.8,54.7),(-76.5,56.5),
         (-78.5,58.8),(-77.3,59.9),(-78.1,62.3),(-73.8,62.4),(-69.6,61.1),
         (-69.3,59),(-67.6,58.2),(-64.6,60.3),(-61.8,56.3),(-57.3,54.6),
         (-55.7,52.1),(-60,50.2),(-66.4,50.2),(-71.1,46.8),(-65.1,49.2),
         (-64.2,48.7),(-65.1,48.1),(-64.5,46.2),(-61.5,45.9),(-60.5,47),
         (-59.8,45.9),(-65.4,43.5),(-66.2,44.5),(-64.4,45.3),(-67.1,45.1),
         (-70.7,43),(-70,41.6),(-73.7,40.9),(-71.9,40.9),(-74,40.8),
         (-74.9,38.9),(-75.5,39.5),(-75.9,37.2),(-76.3,39.2),(-77,38.2),
         (-75.7,35.6),(-81.3,31.4),(-80.4,25.2),(-84.1,30.1),(-89.2,30.3),
         (-90.2,29.1),(-93.8,29.7),(-96.6,28.3),(-97.9,22.4),(-96.3,19.3),
         (-94.4,18.1),(-92,18.7),(-90.3,21),(-87.1,21.5),(-88.9,15.9),
         (-83.4,15.3),(-83.8,11.1),(-81.4,8.8),(-79.6,9.6),(-76.8,8.6),
         (-74.9,11.1),(-71.8,12.4),(-71.7,9.1),(-69.9,12.2),(-68.2,10.6),
         (-61.9,10.7),(-62.4,9.9),(-57.1,6),(-54,5.8),(-51.3,4.2),
         (-50,1.7),(-50.4,-0.1),(-44.9,-1.6),(-44.6,-2.7),(-40,-2.9),
         (-35.6,-5.1),(-34.7,-7.3),(-38.7,-13.1),(-40.9,-21.9),(-47.6,-24.9),
         (-48.9,-28.7),(-53.8,-34.4),(-56.2,-34.9),(-58.4,-33.9),(-56.8,-36.9),
         (-59.2,-38.7),(-62.3,-38.8),(-62.7,-41),(-65.1,-41.1),(-63.5,-42.6),
         (-67.3,-45.6),(-67.6,-46.3),(-65.6,-47.2),(-66,-48.1),(-69.1,-50.7),
         (-68.2,-52.3),(-70.8,-52.9),(-71,-53.8),(-74.9,-52.3),(-75.6,-48.7),
         (-74.1,-46.9),(-75.6,-46.6),(-74.4,-44.1),(-73.2,-44.5),(-72.7,-42.4),
         (-74.3,-43.2),(-73.6,-37.2),(-71.4,-32.4),(-70.2,-19.8),(-71.5,-17.4),
         (-76,-14.6),(-79.8,-7.2),(-81.2,-6.1),(-79.8,-2.7),(-81,-2.2),
         (-80.9,-1.1),(-77.1,3.8),(-78.2,8.3),(-79.6,8.9),(-80.9,7.2),
         (-85.7,9.9),(-87.5,13.3),(-103.5,18.3),(-105.5,19.9),(-106,22.8),
         (-113.9,31.6),(-114.8,31.8),(-114.7,30.2),(-109.4,23.4),(-110,22.8),
         (-112.2,24.7),(-112.3,26),(-115.1,27.7),(-114.2,28.6),(-117.3,33),
         (-120.6,34.6),(-124.4,40.3),(-124.7,48.2),(-122.6,47.1),(-122.8,49),
         (-127.4,50.8),(-127.9,52.3),(-134.1,58.1),(-147.1,60.9),(-151.7,59.2),
         (-150.6,61.3),(-158.4,56),(-164.8,54.4),(-157.7,57.6),(-157,58.9),
         (-162,58.7),(-161.9,59.6),(-166.1,61.5),(-164.6,63.1),(-160.8,63.8),
         (-161.5,64.4),(-160.8,64.8),(-165,64.4),(-168.1,65.7),(-161.7,66.1),
         (-166.8,68.4),(-156.6,71.4),(-136.5,68.9),(-128.1,70.5),(-108.9,67.4),
         (-107.8,67.9),(-108.8,68.3),(-108.2,68.7),(-106.2,68.8),(-101.5,67.6),
         (-97.7,68.6),(-96.1,68.2),(-96.1,67.3),(-94.2,69.1),(-96.5,70.1),
         (-95.2,71.9),(-90.5,69.5)],
        [(143.6,-13.8),(145.4,-15),(146.4,-19),(148.8,-20.4),(153.1,-26.1),
         (152.9,-31.6),(150,-37.4),(146.3,-39),(145,-37.9),(143.6,-38.8),
         (140.6,-38),(138.1,-35.6),(138.2,-34.4),(136.8,-35.3),(137.8,-32.9),
         (136,-34.9),(134.3,-32.6),(131.3,-31.5),(118,-35.1),(115,-34.2),
         (115.7,-31.6),(113.3,-26.1),(114.2,-26.3),(113.4,-24.4),(114.1,-21.8),
         (114.2,-22.5),(120.9,-19.7),(125.7,-14.2),(129.6,-15),(130.6,-12.5),
         (132.6,-12.1),(132.4,-11.1),(136.5,-11.9),(135.5,-15),(140.2,-17.7),
         (142.1,-11),(143.6,-13.8)],
        [(-27.1,83.5),(-20.8,82.7),(-31.4,82),(-12.2,81.3),(-20,80.2),
         (-17.7,80.1),(-19.7,78.8),(-18.5,77),(-21.7,76.6),(-19.8,76.1),
         (-19.6,75.2),(-20.7,75.2),(-19.4,74.3),(-23.6,73.3),(-22.3,72.2),
         (-24.8,72.3),(-21.8,70.7),(-25.5,71.4),(-26.4,70.2),(-22.3,70.1),
         (-39.8,65.5),(-42.8,62.7),(-43.4,60.1),(-48.3,60.9),(-51.6,63.6),
         (-54,67.2),(-50.9,69.9),(-54.7,69.6),(-54.4,70.8),(-51.4,70.6),
         (-55.8,71.7),(-54.7,72.6),(-58.6,75.5),(-68.5,76.1),(-71.4,77),
         (-66.8,77.4),(-73.3,78),(-65.7,79.4),(-68,80.1),(-62.7,81.8),
         (-50.4,82.4),(-44.5,81.7),(-46.8,82.6),(-43.4,83.2),(-27.1,83.5)],
        [(-86.6,73.2),(-85.8,72.5),(-82.3,73.8),(-80.7,72.1),(-77.8,72.7),
         (-72.2,71.6),(-67.9,70.1),(-67,69.2),(-68.8,68.7),(-61.9,66.9),
         (-63.9,65),(-68,66.3),(-64.7,63.4),(-65,62.7),(-68.8,63.7),
         (-66.2,61.9),(-74.8,64.7),(-77.7,64.2),(-78.6,64.6),(-77.9,65.3),
         (-74,65.5),(-72.9,67.7),(-79,70.2),(-88.7,70.4),(-90.2,72.2),
         (-88.4,73.5),(-85.8,73.8),(-86.6,73.2)],
        [(-68.5,83.1),(-61.9,82.4),(-76.9,79.3),(-75.4,78.5),(-80.6,76.2),
         (-89.5,76.5),(-87.8,77.2),(-88.3,77.9),(-85,77.5),(-88,78.4),
         (-85.1,79.3),(-86.9,80.3),(-81.8,80.5),(-87.6,80.5),(-91.6,81.9),(-68.5,83.1)],
        [(134.1,-1.2),(135.5,-3.4),(138.3,-1.7),(144.6,-3.9),(147.6,-6.1),
         (147.2,-7.4),(150.7,-10.6),(147.9,-10.1),(144.7,-7.6),(142.6,-9.3),
         (137.6,-8.4),(138.7,-7.3),(137.9,-5.4),(133.7,-3.5),(133,-4.1),
         (132,-2.8),(133.7,-2.2),(130.5,-0.9),(134.1,-1.2)],
        [(117.9,1.8),(119,0.9),(117.8,0.8),(116.1,-4),(110.2,-2.9),
         (109.1,-0.5),(109.7,2),(113,3.1),(116.7,6.9),(119.2,5.4),(117.3,3.2),(117.9,1.8)],
        [(50.1,-13.6),(50.4,-15.7),(47.1,-24.9),(44,-25),(43.3,-22.1),
         (44.4,-20.1),(44.4,-16.2),(47.7,-14.6),(49.2,-12),(50.1,-13.6)],
        [(105.8,-5.9),(102.6,-4.2),(95.3,5.5),(97.5,5.2),(103.8,0.1),
         (103.4,-0.7),(106.1,-3.1),(105.8,-5.9)],
        [(-3,58.6),(-4.1,57.6),(-2,57.7),(-3.1,56),(1.7,52.7),(1.4,51.3),
         (-5.2,50),(-3.4,51.4),(-5.3,52),(-4.2,52.3),(-4.6,53.5),(-2.9,54),
         (-5.6,55.3),(-6.1,56.8),(-5,58.6),(-3,58.6)],
        [(141,37.1),(140.3,35.1),(135.8,33.5),(135.1,34.6),(131,33.9),
         (132,33.1),(131.3,31.5),(130.2,31.4),(129.4,33.3),(132.6,35.4),
         (135.7,35.5),(136.7,37.3),(139.4,38.2),(140.3,41.2),(141.4,41.4),
         (141.9,40),(141,37.1)],
        [(-14.5,66.5),(-13.6,65.1),(-18.7,63.5),(-22.8,64),(-21.8,64.4),
         (-24,64.9),(-22.2,65.4),(-24.3,65.6),(-14.5,66.5)],
        [(-175,66.6),(-169.9,66),(-172.5,65.4),(-173,64.3),(-178.7,66.1),
         (-180,65),(-180,69),(-175,66.6)],
        [(173,-40.9),(174.2,-41.3),(173.1,-43.9),(169.3,-46.6),(166.7,-46.2),(173,-40.9)],
        [(174.6,-36.2),(176.8,-37.9),(178.5,-37.7),(175.2,-41.7),
         (173.8,-39.5),(174.7,-37.4),(172.6,-34.5),(174.6,-36.2)],
        [(143.6,50.7),(144.7,49),(143.2,49.3),(142.6,47.9),(143.5,46.1),
         (142.1,46),(141.7,53.3),(142.7,54.4),(143.6,50.7)],
        [(143.9,44.2),(145.3,44.4),(145.5,43.3),(140,41.6),(142,45.6),(143.9,44.2)],
        [(108.6,-6.8),(110.8,-6.5),(115.7,-8.4),(108.3,-7.8),
         (105.4,-6.9),(106.1,-5.9),(108.6,-6.8)],
        [(-67.8,-53.9),(-65,-54.7),(-69.2,-55.5),(-74.7,-52.8),
         (-71.1,-54.1),(-69.3,-52.5),(-67.8,-53.9)],
        [(-6.8,52.3),(-10,51.8),(-9.7,53.9),(-6.7,55.2),(-5.7,54.6),(-6.8,52.3)],
        [(121.3,18.5),(122.5,17.1),(121.7,14.3),(124,13.8),(124.1,12.5),
         (120.1,15),(121.3,18.5)],
        [(-79.7,22.8),(-74.2,20.3),(-77.8,19.9),(-77.1,20.4),(-78.7,21.6),
         (-81.8,22.6),(-85,21.9),(-82.3,23.2),(-79.7,22.8)],
        [(145.4,-40.8),(148.3,-40.9),(147.9,-43.2),(146,-43.5),(144.7,-41.2),(145.4,-40.8)],
        [(126.4,8.4),(125.4,5.6),(123.6,7.8),(121.9,7.2),(125.4,9.8),(126.4,8.4)],
        # Pacific islands are retained even when smaller than a final pixel.
        [(177.2,-17.1),(178.6,-17.4),(178.5,-18.2),(177.3,-18.2)],
        [(179.0,-16.1),(179.9,-16.2),(179.8,-16.9),(179.1,-16.8)],
        [(166.5,-14.5),(167.1,-14.6),(167.5,-16.6),(168.5,-17.8),(169.4,-19.5)],
    ]
    scale = 4
    atlas = Image.new('RGB', (452*scale, 81*scale), PALE)
    pen = ImageDraw.Draw(atlas)

    def project(lon, lat):
        return ((8 + (lon+180)*436/360)*scale,
                (3 + (84-lat)*74/142)*scale)

    for lon in range(-180, 181, 60):
        pen.line([project(lon, 84), project(lon, -58)], fill='#D3DED5', width=2)
    for lat in (-30, 0, 30, 60):
        pen.line([project(-180, lat), project(180, lat)],
                 fill='#C4D4CA' if lat == 0 else '#D3DED5', width=2)
    for polygon in coastlines:
        points = [project(lon, lat) for lon, lat in polygon]
        pen.polygon(points, fill='#7FA799')
        pen.line(points + points[:1], fill='#608B7F', width=2, joint='curve')

    # Labels occupy open areas beside the corresponding landmass; fine leaders
    # keep the two American labels and Europe clear of the coastline detail.
    labels = [
        ('NORTH AMERICA', (40, 27), (-110, 45), (104, 30)),
        ('SOUTH AMERICA', (92, 67), (-58, -22), (151, 66)),
        ('EUROPE', (193, 12), (14, 52), (222, 22)),
        ('AFRICA', (224, 49), None, None),
        ('ASIA', (321, 20), None, None),
        ('OCEANIA', (360, 68), None, None),
    ]
    for words, (x, y), destination, start in labels:
        if destination:
            pen.line([(start[0]*scale, start[1]*scale), project(*destination)],
                     fill='#8EA79C', width=2)
        pen.text((x*scale, y*scale), words, font=font(9*scale), fill=INK,
                 stroke_width=2, stroke_fill=PALE)

    # Longitude/latitude, rather than hand-placed canvas positions.
    dispatches = [
        ('Crimea', 34.1, 44.9), ('Gaza', 34.45, 31.5),
        ('Khasab', 56.25, 26.18), ('Accra', -0.19, 5.56),
        ('Cape Town', 18.42, -33.93), ('Suva', 178.45, -18.14),
        ('Wellington', 174.78, -41.29),
    ]
    for _, lon, lat in dispatches:
        x, y = project(lon, lat)
        r = 1.7*scale
        pen.ellipse((x-r, y-r, x+r, y+r), fill=RUST, outline=PALE, width=2)
    x, y = project(114.06, 22.54)  # Shenzhen: the lead story.
    r = 3*scale
    pen.ellipse((x-r, y-r, x+r, y+r), fill=RUST, outline=PAPER, width=scale)
    pen.ellipse((x-scale/2, y-scale/2, x+scale/2, y+scale/2), fill=PAPER)
    draw._image.paste(atlas.resize((452, 81), Image.Resampling.LANCZOS), (35, 107))
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
