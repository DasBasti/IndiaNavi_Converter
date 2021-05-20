from PIL import Image, ImageFilter
import pal
import epd5in65f
#import lz4.frame


tile_pal = Image.new("P", (1,1), 255)
tile_pal.putpalette(pal.generate_tiles())
eink_pal = Image.new("P", (1,1), 255)
eink_pal.putpalette(pal.generate_eink())
epd = epd5in65f.EPD()


# load splash.png
img = Image.open("splash.png")
out = img.convert("RGB").quantize(method=None, palette=tile_pal).convert("RGB").filter(ImageFilter.EDGE_ENHANCE).filter(ImageFilter.SHARPEN).quantize(palette=eink_pal)
#out.save("splash_dt.png")

full = Image.new("P", (256*2,256*3), 1)
full.putpalette(pal.generate_eink())
full.paste(out)


tile = Image.new("P", (256,256),1)
tile.putpalette(pal.generate_eink())

for x in range(2):
    for y in range(3):
        tile.paste(full.crop((256*x,256*y,256+(256*x),256+(256*y))))
        name = "tiles/raw/0/{x}/{y}".format(x=x,y=y)
        #tile.save(name+".png")

        r = open(name+".raw", "w+b")
        r.write(bytearray(epd.getbuffer(tile)))
        r.close()

        #z = open(name+".lz4", "w+b")
        #z.write(lz4.frame.compress(bytearray(epd.getbuffer(out))))
        #z.close()
