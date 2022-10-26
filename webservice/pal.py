from math import sqrt, pow

BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 128, 0)
YELLOW = (255, 255, 0)


def generate_tiles():
    values = [0x00, 0x1f, 0x3f, 0x7f, 0xbf, 0xff]
    p = []
    for r in values:
        for g in values:
            for b in values:
                p.append(r)
                p.append(g)
                p.append(b)
    for i in range(768-len(p)):
        p.append(0)

    return p


def generate_eink():
    p = [0,   0,   0,
         255, 255, 255,
         0, 0,  255,
         255,  0,  0,
         0,  255,  0,
         255, 128,  0,
         255, 255, 0,	]
    for i in range(768-len(p)):
        p.append(0)

    return p

# 50/50 dot pattern


def fiddyfiddy(x, y, colors):
    if x % 2:
        if y % 2:
            return colors[0]
        else:
            return colors[1]
    else:
        if y % 2:
            return colors[1]
    return colors[0]


def threefourth(x, y, colors):
    if x % 4 == 0:
        if y % 4 == 0:
            return colors[1]
        else:
            return colors[0]
    return colors[0]

# Format: (color in image), function to map to, [colors for function]
palette = [
    [0, 0, 0],
    [127, 127, 127, fiddyfiddy, [BLACK, WHITE]],
    [255, 255, 255],
    [0, 0, 255],
    [0, 0, 127, fiddyfiddy, [BLACK, BLUE]],
    [255, 0, 0],
    [127, 0, 0, fiddyfiddy, [BLACK, RED]],
    [0, 255, 0],
    [0, 127, 0, fiddyfiddy, [BLACK, GREEN]],
    [255, 128, 0],
    [255, 255, 0],
    [127, 127, 0, fiddyfiddy, [BLACK, YELLOW]],
    [255, 255, 127, fiddyfiddy, [WHITE, YELLOW]],
    [0, 255, 255, fiddyfiddy, [WHITE, BLUE]],
    [127, 0, 127, fiddyfiddy, [RED, BLUE]],
    [127, 255, 0, fiddyfiddy, [YELLOW, GREEN]],
    [127, 191, 0, fiddyfiddy, [ORANGE, GREEN]],
    [0x7c, 0xa4, 0x7c, fiddyfiddy, [WHITE, GREEN]],
    [0xa4, 0x7c, 0x7c, fiddyfiddy, [WHITE, RED]],
    [0x7c, 0x7c, 0xa4, fiddyfiddy, [BLUE, BLUE]],
    [0xb8, 0x91, 0x81, fiddyfiddy, [ORANGE, ORANGE]],
    [0xFF, 0x2C, 0x00, fiddyfiddy, [RED, ORANGE]],
    [0xFF, 0x9C, 0x00, fiddyfiddy, [YELLOW, ORANGE]],
    [0xAA, 0xD3, 0xDF, fiddyfiddy, [BLUE, WHITE]],
    [0xAD, 0xD1, 0x9E, fiddyfiddy, [GREEN,GREEN]],
    [0xD9, 0xD0, 0xC9, fiddyfiddy, [BLACK, WHITE]],
    [0xF2, 0xE9, 0xD7, fiddyfiddy, [YELLOW,WHITE]],
    [0xFC, 0xD6, 0xA4, fiddyfiddy, [ORANGE,ORANGE]],
    [0xCD, 0xEB, 0xB0, fiddyfiddy, [WHITE,GREEN]],
    [0xE0, 0xDF, 0xDF, fiddyfiddy, [WHITE,YELLOW]],
    [0xE8, 0x92, 0xA2, fiddyfiddy, [RED, RED]],
    [0x00, 0x92, 0xDA, fiddyfiddy, [BLUE, BLUE]],
    [0xE0, 0xDF, 0xDF, fiddyfiddy, [BLACK, BLACK]]
]


def map_color(pxl, x, y):

    deltac = 100000
    new_pxl = BLACK

    for color in palette:
        delta = sqrt(pow(color[0]-pxl[0], 2) +
                     pow(color[1]-pxl[1], 2)+pow(color[2]-pxl[2], 2))
        if delta < deltac:
            deltac = delta
            if len(color) > 3:
                new_pxl = color[3](x, y, color[4])
            else:
                new_pxl = (color[0], color[1], color[2])
    return new_pxl
