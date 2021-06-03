import os
import math
import urllib.request
from PIL import Image, ImageFilter, ImageOps
import pal
import epd5in65f
import lz4.frame
from multiprocessing import Pool


url_template = "https://platinenmacher.tech/navi/tiles/{z}/{x}/{y}.png"
epd = epd5in65f.EPD()
eink_pal = Image.new("P", (1, 1), 0)
eink_pal.putpalette(pal.generate_eink())
img_pal = Image.new("P", (1, 1), 0)
img_pal.putpalette(pal.generate_tiles())
total = 0
done = 0
percent = 0


def lon2tile(lon, zoom):
    return math.floor(((lon + 180) / 360) * math.pow(2, zoom))


def lat2tile(lat, zoom):
    return math.floor(((1 - math.log(math.tan((lat * math.pi) / 180) + 1 / math.cos((lat * math.pi) / 180)) / math.pi) / 2) * math.pow(2, zoom))


def get_tiles(lon, lat, zoom):
    jobs = []
    for z in zoom:
        jobs.extend(get_jobs_for(lon, lat, z))

    total = len(jobs)

    with Pool(processes=6) as pool:
        done = 0
        ret = pool.imap(process_image, jobs)
        for txt in ret:
            done += 1
            print("({0:1.2f}%): {1}".format(100*done/total, txt))
        pool.close()


def process_image(job):
    os.makedirs(job.get("img_folder"), exist_ok=True)
    os.makedirs(job.get("job_folder"), exist_ok=True)
    os.makedirs(job.get("lz4_folder"), exist_ok=True)
    # load images from server if not in cache
    url = "local"
    if not os.path.isfile((job.get("img_folder")+job.get("img_file"))):
        urllib.request.urlretrieve(job.get("url"), job.get(
            "img_folder")+job.get("img_file"))
        url = job.get("url")
    t = Image.open(job.get("img_folder")+job.get("img_file"))
    # use quantize functions instead of PIL quantize
    out = t.convert("RGB").filter(ImageFilter.EDGE_ENHANCE)

    out_pixel = out.load()

    for px in range(t.size[0]):
        for py in range(t.size[1]):
            out_pixel[px, py] = pal.map_color(out_pixel[px, py], px, py)

    out.save(job.get("img_folder") +
             job.get("img_file").replace(".png", "_dt.png"))

    # lz4 compress raw image
    z = open((job.get("lz4_folder")+job.get("img_file")
              ).split(".")[0]+".lz4", "w+b")
    z.write(lz4.frame.compress(bytearray(epd.getbuffer(out))))
    z.close()

    r = open((job.get("job_folder")+job.get("img_file")
              ).split(".")[0]+".raw", "w+b")
    r.write(bytearray(epd.getbuffer(out)))
    r.close()
    return("{0} -> {1}".format(url, job.get("img_folder")+job.get("img_file")))


def get_jobs_for(lon, lat, zoom):

    # generate tile limits for download
    x = [lon2tile(lon[0], zoom), lon2tile(lon[1], zoom)]
    y = [lat2tile(lat[0], zoom), lat2tile(lat[1], zoom)]

    # switch if reversed
    if y[0] > y[1]:
        a = y[0]
        y[1] = y[0]
        y[0] = a

    if x[0] > x[1]:
        a = x[0]
        x[1] = x[0]
        x[0] = a

    # add tiles to the limits
    x[1] += 10
    x[0] -= 10
    y[1] += 10
    y[0] -= 10

    print(
        'Tiles: ({4}/{0}/{1}.png) -> ({4}/{2}/{3}.png)'.format(x[0], y[0], x[1], y[1], zoom))
    jobs = []
    for dx in range(abs(x[1]-x[0])):
        for dy in range(abs(y[1]-y[0])):
            url = url_template.format(z=zoom, x=x[0]+dx, y=y[0]+dy)
            img_folder = "tiles/png/{z}/{x}/".format(z=zoom, x=x[0]+dx)
            job_folder = "tiles/raw/{z}/{x}/".format(z=zoom, x=x[0]+dx)
            lz4_folder = "tiles/lz4/{z}/{x}/".format(z=zoom, x=x[0]+dx)
            img_file = "{y}.png".format(z=zoom, x=x[0]+dx, y=y[0]+dy)
            jobs.append({"url": url, "lz4_folder": lz4_folder, "job_folder": job_folder,
                        "img_folder": img_folder, "img_file": img_file})
    print('Jobs: {0}'.format(len(jobs)))
    return jobs


def convert_to_c_file(filename):
    if not os.path.isfile(filename):
        return
    raw = lz4.frame.open(filename, "r")
    c = "#include <stdio.h>\n"
    c += "const uint8_t "+filename.split(".")[0].replace("/", "_")+"[]={\n"
    counter = 0
    for b in raw.read():
        counter += 1
        c += "0x{:02x}, ".format(b)
        if counter == 16:
            counter = 0
            c += "\n"
    c += "};"
    c_file = open(filename.split(".")[0]+".c", "w")
    c_file.write(c)
    c_file.close()


def get_map(lon, lat, zoom, jobfolder):
    get_tiles(lon, lat, zoom)
    # zip up all the raw files for download
