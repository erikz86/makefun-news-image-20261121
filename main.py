"""A deterministic, hand-rasterized newspaper. Python standard library only."""
import math
import os
import struct
import zlib

W = H = 1024
PAPER = (243, 236, 219)
INK = (26, 24, 20)
GREY = (74, 68, 58)
RED = (164, 30, 30)
BLUE = (30, 56, 94)
SKY = (178, 205, 222)
SEA = (44, 96, 128)
GOLD = (198, 152, 32)
GREEN = (34, 110, 62)
RULE = (140, 132, 118)
WHITE = (255, 255, 255)
BROWN = (122, 84, 52)
pixels = bytearray(PAPER * (W * H))

# Original five-column, seven-row block alphabet; slash separates rows.
PATTERNS = {
 'A':'01110/10001/10001/11111/10001/10001/10001',
 'B':'11110/10001/10001/11110/10001/10001/11110',
 'C':'01111/10000/10000/10000/10000/10000/01111',
 'D':'11110/10001/10001/10001/10001/10001/11110',
 'E':'11111/10000/10000/11110/10000/10000/11111',
 'F':'11111/10000/10000/11110/10000/10000/10000',
 'G':'01111/10000/10000/10111/10001/10001/01111',
 'H':'10001/10001/10001/11111/10001/10001/10001',
 'I':'11111/00100/00100/00100/00100/00100/11111',
 'J':'00111/00010/00010/00010/10010/10010/01100',
 'K':'10001/10010/10100/11000/10100/10010/10001',
 'L':'10000/10000/10000/10000/10000/10000/11111',
 'M':'10001/11011/10101/10101/10001/10001/10001',
 'N':'10001/11001/11001/10101/10011/10011/10001',
 'O':'01110/10001/10001/10001/10001/10001/01110',
 'P':'11110/10001/10001/11110/10000/10000/10000',
 'Q':'01110/10001/10001/10001/10101/10010/01101',
 'R':'11110/10001/10001/11110/10100/10010/10001',
 'S':'01111/10000/10000/01110/00001/00001/11110',
 'T':'11111/00100/00100/00100/00100/00100/00100',
 'U':'10001/10001/10001/10001/10001/10001/01110',
 'V':'10001/10001/10001/10001/10001/01010/00100',
 'W':'10001/10001/10001/10101/10101/11011/10001',
 'X':'10001/10001/01010/00100/01010/10001/10001',
 'Y':'10001/10001/01010/00100/00100/00100/00100',
 'Z':'11111/00001/00010/00100/01000/10000/11111',
 '0':'01110/10001/10011/10101/11001/10001/01110',
 '1':'00100/01100/00100/00100/00100/00100/01110',
 '2':'01110/10001/00001/00010/00100/01000/11111',
 '3':'11110/00001/00001/01110/00001/00001/11110',
 '4':'00010/00110/01010/10010/11111/00010/00010',
 '5':'11111/10000/10000/11110/00001/00001/11110',
 '6':'01110/10000/10000/11110/10001/10001/01110',
 '7':'11111/00001/00010/00100/01000/01000/01000',
 '8':'01110/10001/10001/01110/10001/10001/01110',
 '9':'01110/10001/10001/01111/00001/00001/01110',
 ' ':'00000/00000/00000/00000/00000/00000/00000',
 ',':'00000/00000/00000/00000/00100/00100/01000',
 '.':'00000/00000/00000/00000/00000/00110/00110',
 '-':'00000/00000/00000/11111/00000/00000/00000',
 ':':'00000/00110/00110/00000/00110/00110/00000',
 '$':'00100/01111/10100/01110/00101/11110/00100',
 '+':'00000/00100/00100/11111/00100/00100/00000',
}
FONT = {k: v.split('/') for k, v in PATTERNS.items()}


def rect(x, y, w, h, color):
    assert 0 <= x <= x+w <= W and 0 <= y <= y+h <= H
    row = bytes(color) * w
    for yy in range(y, y+h):
        i = (yy * W + x) * 3
        pixels[i:i+w*3] = row


def outline(x, y, w, h, color, t=1):
    rect(x, y, w, t, color)
    rect(x, y+h-t, w, t, color)
    rect(x, y, t, h, color)
    rect(x+w-t, y, t, h, color)


def line(x0, y0, x1, y1, color, thickness=1):
    dx, dy = abs(x1-x0), -abs(y1-y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        rect(x0, y0, thickness, thickness, color)
        if x0 == x1 and y0 == y1:
            break
        e = 2 * err
        if e >= dy:
            err += dy
            x0 += sx
        if e <= dx:
            err += dx
            y0 += sy


def circle(x, y, radius, color):
    for yy in range(-radius, radius+1):
        span = math.isqrt(radius*radius-yy*yy)
        rect(x-span, y+yy, 2*span+1, 1, color)


def polygon(points, color):
    for y in range(min(p[1] for p in points), max(p[1] for p in points)+1):
        cuts = []
        for a, b in zip(points, points[1:]+points[:1]):
            if min(a[1], b[1]) <= y < max(a[1], b[1]):
                cuts.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
        cuts.sort()
        for a, b in zip(cuts[::2], cuts[1::2]):
            left, right = math.ceil(a), math.floor(b)
            if right >= left:
                rect(left, y, right-left+1, 1, color)


def star(x, y, radius, color):
    pts = []
    for i in range(10):
        a = i*math.pi/5-math.pi/2
        r = radius if i % 2 == 0 else radius*0.4
        pts.append((round(x+math.cos(a)*r), round(y+math.sin(a)*r)))
    polygon(pts, color)


def width(text, scale):
    return (sum(4 if c == ' ' else 6 for c in text)-1)*scale if text else 0


text_bounds = []


def text(text, x, y, scale=2, color=INK, box=None):
    assert all(c in FONT for c in text), text
    w, h = width(text, scale), 7*scale
    assert 0 <= x and x+w <= W and 0 <= y and y+h <= H, text
    if box:
        bx, by, bw, bh = box
        assert bx <= x and x+w <= bx+bw and by <= y and y+h <= by+bh, text
    for ox, oy, ow, oh in text_bounds:
        assert x+w <= ox or ox+ow <= x or y+h <= oy or oy+oh <= y, text
    text_bounds.append((x, y, w, h))
    for c in text:
        for row, bits in enumerate(FONT[c]):
            for col, bit in enumerate(bits):
                if bit == '1':
                    rect(x+col*scale, y+row*scale, scale, scale, color)
        x += (4 if c == ' ' else 6)*scale


def centered(s, y, scale=2, color=INK, x=24, w=976):
    text(s, x+(w-width(s, scale))//2, y, scale, color, (x,y,w,7*scale))


def wrap(s, w, scale=2):
    rows = []
    for word in s.split():
        assert width(word, scale) <= w, word
        if rows and width(rows[-1]+' '+word, scale) <= w:
            rows[-1] += ' '+word
        else:
            rows.append(word)
    return rows


def paragraph(s, x, y, w, bottom, color=GREY):
    for row in wrap(s, w):
        text(row, x, y, 2, color, (x,0,w,bottom))
        y += 20
    return y


def draw():
    outline(6,6,1012,1012,INK,2)
    outline(12,12,1000,1000,RULE)
    centered('THE WORLD TODAY',30,6)
    rect(24,106,976,2,INK)
    centered('SATURDAY, 21 NOVEMBER 2026 - KYIV - WASHINGTON - LONDON',116)
    rect(24,138,976,1,INK)
    centered('WAR SPILLS INTO POLAND',150,4,RED)
    centered('RUSSIAN MISSILE LANDS IN POLAND AS 400 DRONES AND 110 MISSILES HIT UKRAINE',192)
    rect(24,216,976,4,INK)
    rect(24,228,476,224,BLUE)
    for x,y in [(47,248),(121,263),(254,241),(351,275),(464,249)]:
        star(x,y,3,SKY)
    for x,y in [(65,244),(195,235),(305,250)]:
        line(x,y,x+83,y+71,GOLD,3)
        line(x+28,y+24,x+83,y+71,WHITE)
        circle(x+84,y+72,4,WHITE)
    for x,y,w in [(24,365,42),(69,342,48),(121,377,37),(163,329,54),(223,359,42),(271,347,53),(330,378,42),(378,355,45)]:
        rect(x,y,w,424-y,INK)
        for xx in range(x+9,x+w-5,14):
            for yy in range(y+12,412,19):
                rect(xx,yy,4,5,GOLD)
    polygon([(175,329),(190,302),(204,329)],INK)
    line(190,292,190,309,INK,2)
    rect(24,414,476,14,INK)
    for x in [58,143,245,315,386]:
        polygon([(x-16,424),(x-10,401),(x-3,411),(x+4,390),(x+16,424)],RED)
        polygon([(x-7,424),(x,406),(x+8,424)],GOLD)
    rect(444,305,3,119,RULE)
    rect(447,307,43,20,WHITE)
    rect(447,327,43,20,RED)
    centered('THE STRIKE THAT CROSSED A BORDER',432,2,WHITE,24,476)
    y = paragraph('RUSSIA LAUNCHED A MASSIVE ATTACK ON UKRAINE: MORE THAN 400 DRONES AND 110 MISSILES. AT LEAST 8 PEOPLE WERE KILLED IN KYIV.',516,228,484,414)
    y = paragraph('A MISSILE LANDED IN POLAND. PRIME MINISTER TUSK CALLED IT A DELIBERATE PROVOCATION.',516,y+10,484,414)
    outline(516,416,484,36,RULE)
    for i,row in enumerate(['400+ DRONES - 110 MISSILES', '- 8 KILLED IN KYIV']):
        centered(row,418+i*18,2,RED,522,472)
    rect(24,466,976,2,INK)
    text('MARKETS IN FREEFALL',24,480,3)
    text('GUILTY OF GENOCIDE',524,480,3)
    rect(24,512,476,92,(234,229,215))
    for x in range(40,500,40):
        line(x,518,x,598,(212,206,190))
    for y in range(524,604,20):
        line(30,y,492,y,(212,206,190))
    pts = [(42,524),(110,531),(169,526),(232,550),(297,547),(363,571),(436,590)]
    for a,b in zip(pts,pts[1:]):
        line(*a,*b,RED,3)
    for p in pts:
        circle(*p,4,RED)
    line(470,534,470,580,RED,4)
    polygon([(457,575),(485,575),(471,593)],RED)
    text('S AND P 500',42,578,2,BLUE)
    rect(524,512,476,92,SKY)
    polygon([(592,539),(670,515),(748,539)],BLUE)
    rect(588,541,164,6,BLUE)
    for x in [600,642,684,726]:
        rect(x,550,12,40,BLUE)
    rect(586,592,170,6,BLUE)
    line(858,529,858,591,GOLD,4)
    circle(860,526,5,GOLD)
    line(820,544,900,544,GOLD,3)
    for x in [827,891]:
        line(x,545,x-13,571,GOLD)
        line(x,545,x+13,571,GOLD)
        polygon([(x-16,571),(x+16,571),(x+9,579),(x-9,579)],GOLD)
    rect(840,592,40,4,GOLD)
    y = paragraph('US STOCKS FELL 3.7 PERCENT IN A SELL-OFF LED BY AI AND CHIP SHARES.',24,614,476,728)
    paragraph('THE S AND P 500 ENTERED A CORRECTION. THE NASDAQ ERASED ITS GAINS FOR 2026.',24,y+10,476,728)
    y = paragraph('THE WORLD COURT RULED MYANMAR RESPONSIBLE FOR GENOCIDE AGAINST THE ROHINGYA.',524,614,476,728)
    paragraph('A STATE HELD TO ACCOUNT BY THE WORLD COURT.',524,y+10,476,728)
    rect(24,736,976,2,INK)
    briefs = [
        ('HEALTH','PANCREATIC CANCER PILL DARAXONRASIB: TUMORS UNDETECTABLE IN 1 OF 12 PATIENTS IN A TRIAL.'),
        ('PROTEST','GEN Z PROTESTS SPREAD TO 25 COUNTRIES ACROSS EUROPE.'),
        ('EUROPE','BRITAIN AND THE EU SIGNED THE BIGGEST POST-BREXIT DEAL YET: FOOD, CARBON AND YOUTH MOBILITY.'),
        ('CLIMATE','COP31 IN ANTALYA RAN PAST ITS DEADLINE AS COUNTRIES SPLIT OVER FOSSIL FUELS.')]
    for i,(title,body) in enumerate(briefs):
        x = 24+244*i
        text(title,x,750,2,RED)
        paragraph(body,x,772,232,888)
        if i:
            rect(x-12,750,1,134,RULE)
    rect(24,896,976,40,INK)
    centered('400+ DRONES - 110 MISSILES - STOCKS DOWN 3.7 PERCENT - GEN Z IN 25 NATIONS',908,2,WHITE)
    centered('ONE IMAGE, ONE DAY, THE WHOLE WORLD - SATURDAY 21 NOVEMBER 2026',958)
    centered('THE WORLD TODAY',984,1)


def chunk(kind, data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)


def main():
    draw()  # All layout assertions complete before any output is written.
    scanlines = b''.join(b'\0'+pixels[y*W*3:(y+1)*W*3] for y in range(H))
    png = (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))
           +chunk(b'IDAT',zlib.compress(scanlines,9))+chunk(b'IEND',b''))
    assert len(png) < 1048576
    directory = os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
    os.makedirs(directory,exist_ok=True)
    with open(os.path.join(directory,'entry.png'),'wb') as output:
        output.write(png)


if __name__ == '__main__':
    main()
