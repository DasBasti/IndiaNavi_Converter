from math import sqrt, pow


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


# Format: (color in image), function to map to, [colors for function]
palette = [
    [0, 0, 0],
    [127, 127, 127, fiddyfiddy, [(0, 0, 0), (255, 255, 255)]],
    [255, 255, 255],
    [0, 0, 255],
    [0, 0, 127, fiddyfiddy, [(0, 0, 0), (0, 0, 255)]],
    [255, 0, 0],
    [127, 0, 0, fiddyfiddy, [(0, 0, 0), (255, 0, 0)]],
    [0, 255, 0],
    [0, 127, 0, fiddyfiddy, [(0, 0, 0), (0, 255, 0)]],
    [255, 128, 0],
    [255, 255, 0],
    [127, 127, 0, fiddyfiddy, [(0, 0, 0), (255, 255, 0)]],
    [255, 255, 127, fiddyfiddy, [(255, 255, 255), (255, 255, 0)]],
    [0, 255, 255, fiddyfiddy, [(255, 255, 255), (0, 0, 255)]],
    [127, 0, 127, fiddyfiddy, [(255, 0, 0), (0, 0, 255)]],
    [127, 255, 0, fiddyfiddy, [(255, 255, 0), (0, 255, 0)]],
    [127, 191, 0, fiddyfiddy, [(255, 128, 0), (0, 255, 0)]],
    [0x7c, 0xa4, 0x7c, fiddyfiddy, [(255, 255, 255), (0, 255, 0)]],
    [0xa4, 0x7c, 0x7c, fiddyfiddy, [(255, 255, 255), (255, 0, 0)]],
    [0x7c, 0x7c, 0xa4, fiddyfiddy, [(255, 255, 255), (0, 0, 255)]],
    [0xb8, 0x91, 0x81, fiddyfiddy, [(255, 255, 255), (255, 128, 0)]],
    [0xFF, 0x2C, 0x00, fiddyfiddy, [(255, 0, 0), (255, 128, 0)]],
    [0xFF, 0x9C, 0x00, fiddyfiddy, [(255, 255, 0), (255, 128, 0)]],
]


def map_color(pxl, x, y):

    deltac = 100000
    new_pxl = (0, 0, 0)

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
