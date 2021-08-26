import os
from PIL import Image, ImageFilter
import pal
import epd5in65f
#import lz4.frame


epd = epd5in65f.EPD()


# load splash.png
img = Image.open("splash.png")
# out = img.convert("RGB").quantize(method=None, palette=tile_pal).convert("RGB").filter(
#    ImageFilter.EDGE_ENHANCE).filter(ImageFilter.SHARPEN).quantize(palette=eink_pal)
out = img.convert("RGB").filter(ImageFilter.EDGE_ENHANCE)
out_pixel = out.load()

for px in range(img.size[0]):
    for py in range(img.size[1]):
        out_pixel[px, py] = pal.map_color(out_pixel[px, py], px, py)

out.save("splash_dt.png")

full = Image.new("RGB", (256*2, 256*3), 1)
full.paste(out)

tile = Image.new("RGB", (256, 256), 1)
os.makedirs("tiles", exist_ok=True)
os.makedirs("tiles/raw", exist_ok=True)
os.makedirs("tiles/raw/0", exist_ok=True)
for x in range(2):
    for y in range(3):
        tile.paste(full.crop((256*x, 256*y, 256+(256*x), 256+(256*y))))
        os.makedirs("tiles/raw/0/{x}".format(x=x), exist_ok=True)
        name = "tiles/raw/0/{x}/{y}".format(x=x, y=y)
        # tile.save(name+".png")

        r = open(name+".raw", "w+b")
        r.write(bytearray(epd.getbuffer(tile)))
        r.close()

        #z = open(name+".lz4", "w+b")
        # z.write(lz4.frame.compress(bytearray(epd.getbuffer(out))))
        # z.close()
