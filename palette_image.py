from PIL import Image
import pal

width = 50
height = width*len(pal.palette)
img = Image.new('RGB', (width, height), "white")
pixels = img.load()
for c in range(len(pal.palette)):
    for i in range(width):
        for j in range(width):
            if i < width/2:
                pixels[i, j+c*width] = (pal.palette[c][0], pal.palette[c]
                                        [1], pal.palette[c][2])
            else:
                pixels[i, j+c*width] = pal.map_color((pal.palette[c][0], pal.palette[c]
                                                      [1], pal.palette[c][2]), i, j)

img.save("palette.png")
