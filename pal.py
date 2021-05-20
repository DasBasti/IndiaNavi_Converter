from math import sqrt, pow

def generate_tiles():
    values = [0x00, 0x1f, 0x3f, 0x7f, 0xbf, 0xff]
    p=[]
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
    p=[  0,   0,   0,	
        255, 255, 255,	
        0, 0,  255,	
        255,  0,  0,	
        0,  255,  0,	
        255, 128,  0,	
        255, 255, 0,	]
    for i in range(768-len(p)):
        p.append(0)

    return p

def map_color(pxl, x, y):
    palette=[
             (0,0,0),
             (255,255,255), 
             (0,0,255), 
             (255,0,0), 
             (0,255,0),
             (255,128,0),
             (255,255,0)
    ]
    
    deltac = 100000
    new_pxl = (0,0,0)
    
    for color in palette:
        delta = sqrt(pow(color[0]-pxl[0],2)+pow(color[1]-pxl[1],2)+pow(color[2]-pxl[2],2))
        if delta < deltac:
            deltac = delta
            new_pxl = color
    return new_pxl