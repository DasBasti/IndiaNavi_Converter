// Setup warnings/errors:
#![forbid(unsafe_code)]
#![deny(bare_trait_objects, unused_doc_comments, unused_import_braces)]
// Clippy:
#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::non_ascii_literal)]

use downloader::Downloader;
use error_chain::error_chain;
use image;
use image::GenericImageView;
use image::ImageBuffer;
use image::Rgb;
use num_integer::Roots;
use std::fs::create_dir_all;
use std::fs::File;
use std::io::copy;
use std::io::Cursor;
use std::path::Path;

error_chain! {
     foreign_links {
         Io(std::io::Error);
         HttpRequest(reqwest::Error);
     }
}

const BLACK: Rgb<u8> = image::Rgb([0, 0, 0]);
const WHITE: Rgb<u8> = image::Rgb([255, 255, 255]);
const RED: Rgb<u8> = image::Rgb([255, 0, 0]);
const BLUE: Rgb<u8> = image::Rgb([0, 0, 255]);
const GREEN: Rgb<u8> = image::Rgb([0, 255, 0]);
const YELLOW: Rgb<u8> = image::Rgb([255, 255, 50]);
const ORANGE: Rgb<u8> = image::Rgb([255, 127, 0]);

fn color_to_raw(c: Rgb<u8>) -> u8 {
    match c {
        BLACK => 0,
        WHITE => 1,
        RED => 4,
        BLUE => 3,
        GREEN => 2,
        YELLOW => 5,
        ORANGE => 6,
        _ => 7,
    }
}

fn full_color(_: u32, _: u32, c: Vec<Rgb<u8>>) -> Rgb<u8> {
    c[0]
}

fn fiddyfiddy(x: u32, y: u32, c: Vec<Rgb<u8>>) -> Rgb<u8> {
    if (x % 2) == 1 {
        if (y % 2) == 1 {
            return c[0];
        } else {
            return c[1];
        }
    } else {
        if (y % 2) == 1 {
            return c[1];
        }
    }

    c[0]
}

fn threefourth(x: u32, y: u32, c: Vec<Rgb<u8>>) -> Rgb<u8> {
    if (x % 4) == 0 {
        if (y % 4) == 0 {
            return c[1];
        } else {
            return c[0];
        }
    }

    c[0]
}

fn map_color(x: u32, y: u32, pixel: Rgb<u8>) -> Rgb<u8> {
    let color_map: [(Rgb<u8>, fn(u32, u32, Vec<Rgb<u8>>) -> Rgb<u8>, Vec<Rgb<u8>>); 33] = [
        (BLACK, full_color, vec![BLACK]),
        (image::Rgb([127, 127, 127]), fiddyfiddy, vec![BLACK, WHITE]),
        (WHITE, full_color, vec![WHITE]),
        (BLUE, full_color, vec![BLUE]),
        (image::Rgb([0, 0, 127]), fiddyfiddy, vec![BLACK, BLUE]),
        (RED, full_color, vec![RED]),
        (image::Rgb([127, 0, 0]), fiddyfiddy, vec![BLACK, RED]),
        (GREEN, full_color, vec![GREEN]),
        (image::Rgb([0, 127, 0]), fiddyfiddy, vec![BLACK, GREEN]),
        (ORANGE, full_color, vec![ORANGE]),
        (YELLOW, full_color, vec![YELLOW]),
        (image::Rgb([127, 127, 0]), fiddyfiddy, vec![BLACK, YELLOW]),
        (image::Rgb([255, 255, 127]), fiddyfiddy, vec![WHITE, YELLOW]),
        (image::Rgb([0, 255, 255]), fiddyfiddy, vec![WHITE, BLUE]),
        (image::Rgb([127, 0, 127]), fiddyfiddy, vec![RED, BLUE]),
        (image::Rgb([127, 255, 0]), fiddyfiddy, vec![YELLOW, GREEN]),
        (image::Rgb([127, 191, 0]), fiddyfiddy, vec![ORANGE, GREEN]),
        (
            image::Rgb([0x7c, 0xa4, 0x7c]),
            fiddyfiddy,
            vec![WHITE, GREEN],
        ),
        (image::Rgb([0xa4, 0x7c, 0x7c]), fiddyfiddy, vec![WHITE, RED]),
        (image::Rgb([0x7c, 0x7c, 0xa4]), fiddyfiddy, vec![BLUE, BLUE]),
        (
            image::Rgb([0xb8, 0x91, 0x81]),
            fiddyfiddy,
            vec![ORANGE, ORANGE],
        ),
        (
            image::Rgb([0xFF, 0x2C, 0x00]),
            fiddyfiddy,
            vec![RED, ORANGE],
        ),
        (
            image::Rgb([0xFF, 0x9C, 0x00]),
            fiddyfiddy,
            vec![YELLOW, ORANGE],
        ),
        (
            image::Rgb([0xAA, 0xD3, 0xDF]),
            fiddyfiddy,
            vec![BLUE, WHITE],
        ),
        (
            image::Rgb([0xAD, 0xD1, 0x9E]),
            fiddyfiddy,
            vec![GREEN, GREEN],
        ),
        (
            image::Rgb([0xD9, 0xD0, 0xC9]),
            fiddyfiddy,
            vec![BLACK, WHITE],
        ),
        (
            image::Rgb([0xF2, 0xE9, 0xD7]),
            fiddyfiddy,
            vec![YELLOW, WHITE],
        ),
        (
            image::Rgb([0xFC, 0xD6, 0xA4]),
            fiddyfiddy,
            vec![ORANGE, ORANGE],
        ),
        (
            image::Rgb([0xCD, 0xEB, 0xB0]),
            fiddyfiddy,
            vec![WHITE, GREEN],
        ),
        (
            image::Rgb([0xE0, 0xDF, 0xDF]),
            fiddyfiddy,
            vec![WHITE, YELLOW],
        ),
        (image::Rgb([0xE8, 0x92, 0xA2]), fiddyfiddy, vec![RED, RED]),
        (image::Rgb([0x00, 0x92, 0xDA]), fiddyfiddy, vec![BLUE, BLUE]),
        (
            image::Rgb([0xE0, 0xDF, 0xDF]),
            fiddyfiddy,
            vec![BLACK, BLACK],
        ),
    ];

    //let mut rgb = pixel.clone();
    let mut dist = i32::MAX;
    let mut matched = 0;
    for (idx, color) in color_map.iter().enumerate() {
        // check if color is grayscale
        if (pixel[0] as i32 - pixel[1] as i32 + pixel[1] as i32 - pixel[2] as i32).abs() < 5 {
            if pixel[0] > 200 {
                return WHITE;
            }
            if pixel[0] > 70 {
                return fiddyfiddy(x, y, vec![BLACK, WHITE]);
            }
            return BLACK;
        }

        // calculate distance to the current color
        let d: i32 = ((pixel[0] as i32 - color.0[0] as i32).pow(2)
            + (pixel[1] as i32 - color.0[1] as i32).pow(2)
            + (pixel[2] as i32 - color.0[2] as i32).pow(2))
        .sqrt();

        if d < dist {
            dist = d;
            matched = idx;
        }
    }

    let rgb = color_map[matched].1(x, y, color_map[matched].2.clone());
    rgb
}

// Define a custom progress reporter:
struct SimpleReporterPrivate {
    last_update: std::time::Instant,
    max_progress: Option<u64>,
    message: String,
}
struct SimpleReporter {
    private: std::sync::Mutex<Option<SimpleReporterPrivate>>,
}

impl SimpleReporter {
    #[cfg(not(feature = "tui"))]
    fn create() -> std::sync::Arc<Self> {
        std::sync::Arc::new(Self {
            private: std::sync::Mutex::new(None),
        })
    }
}

impl downloader::progress::Reporter for SimpleReporter {
    fn setup(&self, max_progress: Option<u64>, message: &str) {
        let private = SimpleReporterPrivate {
            last_update: std::time::Instant::now(),
            max_progress,
            message: message.to_owned(),
        };

        let mut guard = self.private.lock().unwrap();
        *guard = Some(private);
    }

    fn progress(&self, current: u64) {
        if let Some(p) = self.private.lock().unwrap().as_mut() {
            let max_bytes = match p.max_progress {
                Some(bytes) => format!("{:?}", bytes),
                None => "{unknown}".to_owned(),
            };
            if p.last_update.elapsed().as_millis() >= 1000 {
                println!(
                    "test file: {} of {} bytes. [{}]",
                    current, max_bytes, p.message
                );
                p.last_update = std::time::Instant::now();
            }
        }
    }

    fn set_message(&self, message: &str) {
        println!("test file: Message changed to: {}", message);
    }

    fn done(&self) {
        let mut guard = self.private.lock().unwrap();
        *guard = None;
        println!("test file: [DONE]");
    }
}

fn main() {
    for z in [14, 16] {
        for x in 34340..34354 {
            for y in 22347..22358 {
                let target = format!("https://c.tile.opentopomap.org/{z}/{x}/{y}.png");
                let dest_folder = format!("tiles/png/{z}/{x}/");
                let dest_name = format!("tiles/png/{z}/{x}/{y}.png");
                let raw_folder = format!("tiles/raw/{z}/{x}/");
                let raw_dest = format!("tiles/raw/{z}/{x}/{y}.raw");
                if Path::new(&dest_name).exists() {
                    println!("skip {dest_name}");
                } else {
                    create_dir_all(&dest_folder).unwrap();
                    let mut downloader = Downloader::builder()
                        .download_folder(std::path::Path::new(&dest_folder))
                        .parallel_requests(16)
                        .user_agent("Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0")
                        .build()
                        .unwrap();
    
                    let dl = downloader::Download::new(&target);
                    println!("{}", target);
                    #[cfg(not(feature = "tui"))]
                    let dl = dl.progress(SimpleReporter::create());
                    
                    let result = downloader.download(&[dl]).unwrap();
                }
                continue;
                let img = image::open(dest_name).expect("File not found!");
                let (w, h) = img.dimensions();
                let mut output = ImageBuffer::new(w, h); // create a new buffer for our output
                let mut pxl: u8 = 0;
                let mut high = true;
                let mut raw = Vec::new();
                for (x, y, pixel) in img.pixels() {
                    let rgb_pixel = image::Rgb([pixel[0], pixel[1], pixel[2]]);
                    let png_pixel = map_color(x, y, rgb_pixel);
                    if high == true {
                        pxl = color_to_raw(png_pixel) << 4;
                    } else {
                        pxl += color_to_raw(png_pixel);
                        raw.push(pxl);
                    }

                    high = !high;

                    output.put_pixel(x, y, png_pixel);
                }

                let mut raw_file = {
                    create_dir_all(raw_folder).unwrap();
                    let fname = raw_dest.clone();
                    println!("will be located under: '{:?}'", fname);
                    File::create(fname).unwrap()
                };

                copy(&mut Cursor::new(raw), &mut raw_file);



                //output.save(format!("tiles/png/{z}/{x}/{y}_dt.png"));

                println!("Processed tiles/{z}/{x}/{y}_dt.png");

                //}));
            }
        }
    }

}
