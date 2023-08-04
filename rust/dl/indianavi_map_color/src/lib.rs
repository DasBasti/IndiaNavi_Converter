// Setup warnings/errors:
#![forbid(unsafe_code)]
#![deny(bare_trait_objects, unused_doc_comments, unused_import_braces)]
// Clippy:
#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::non_ascii_literal)]

use image::io::Reader as ImageReader;
use image::ImageEncoder;
use image::{GenericImageView, ImageBuffer, ImageError, Pixel, Rgb, RgbImage};
use num_integer::Roots;
use std::io::Cursor;
use std::ops::Deref;

const BLACK: Rgb<u8> = Rgb([0, 0, 0]);
const WHITE: Rgb<u8> = Rgb([255, 255, 255]);
const RED: Rgb<u8> = Rgb([255, 0, 0]);
const BLUE: Rgb<u8> = Rgb([0, 0, 255]);
const GREEN: Rgb<u8> = Rgb([0, 255, 0]);
const YELLOW: Rgb<u8> = Rgb([255, 255, 50]);
const ORANGE: Rgb<u8> = Rgb([255, 127, 0]);

pub fn color_to_raw(c: Rgb<u8>) -> u8 {
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
/*/
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
*/
pub fn map_color(x: u32, y: u32, pixel: Rgb<u8>) -> Rgb<u8> {
    let color_map: [(Rgb<u8>, fn(u32, u32, Vec<Rgb<u8>>) -> Rgb<u8>, Vec<Rgb<u8>>); 33] = [
        (BLACK, full_color, vec![BLACK]),
        (Rgb([127, 127, 127]), fiddyfiddy, vec![BLACK, WHITE]),
        (WHITE, full_color, vec![WHITE]),
        (BLUE, full_color, vec![BLUE]),
        (Rgb([0, 0, 127]), fiddyfiddy, vec![BLACK, BLUE]),
        (RED, full_color, vec![RED]),
        (Rgb([127, 0, 0]), fiddyfiddy, vec![BLACK, RED]),
        (GREEN, full_color, vec![GREEN]),
        (Rgb([0, 127, 0]), fiddyfiddy, vec![BLACK, GREEN]),
        (ORANGE, full_color, vec![ORANGE]),
        (YELLOW, full_color, vec![YELLOW]),
        (Rgb([127, 127, 0]), fiddyfiddy, vec![BLACK, YELLOW]),
        (Rgb([255, 255, 127]), fiddyfiddy, vec![WHITE, YELLOW]),
        (Rgb([0, 255, 255]), fiddyfiddy, vec![WHITE, BLUE]),
        (Rgb([127, 0, 127]), fiddyfiddy, vec![RED, BLUE]),
        (Rgb([127, 255, 0]), fiddyfiddy, vec![YELLOW, GREEN]),
        (Rgb([127, 191, 0]), fiddyfiddy, vec![ORANGE, GREEN]),
        (Rgb([0x7c, 0xa4, 0x7c]), fiddyfiddy, vec![WHITE, GREEN]),
        (Rgb([0xa4, 0x7c, 0x7c]), fiddyfiddy, vec![WHITE, RED]),
        (Rgb([0x7c, 0x7c, 0xa4]), fiddyfiddy, vec![BLUE, BLUE]),
        (Rgb([0xb8, 0x91, 0x81]), fiddyfiddy, vec![ORANGE, ORANGE]),
        (Rgb([0xFF, 0x2C, 0x00]), fiddyfiddy, vec![RED, ORANGE]),
        (Rgb([0xFF, 0x9C, 0x00]), fiddyfiddy, vec![YELLOW, ORANGE]),
        (Rgb([0xAA, 0xD3, 0xDF]), fiddyfiddy, vec![BLUE, WHITE]),
        (Rgb([0xAD, 0xD1, 0x9E]), fiddyfiddy, vec![GREEN, GREEN]),
        (Rgb([0xD9, 0xD0, 0xC9]), fiddyfiddy, vec![BLACK, WHITE]),
        (Rgb([0xF2, 0xE9, 0xD7]), fiddyfiddy, vec![YELLOW, WHITE]),
        (Rgb([0xFC, 0xD6, 0xA4]), fiddyfiddy, vec![ORANGE, ORANGE]),
        (Rgb([0xCD, 0xEB, 0xB0]), fiddyfiddy, vec![WHITE, GREEN]),
        (Rgb([0xE0, 0xDF, 0xDF]), fiddyfiddy, vec![WHITE, YELLOW]),
        (Rgb([0xE8, 0x92, 0xA2]), fiddyfiddy, vec![RED, RED]),
        (Rgb([0x00, 0x92, 0xDA]), fiddyfiddy, vec![BLUE, BLUE]),
        (Rgb([0xE0, 0xDF, 0xDF]), fiddyfiddy, vec![BLACK, BLACK]),
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

/*
fn encode_png<P, Container>(img: &ImageBuffer<P, Container>) -> Result<Vec<u8>, ImageError>
where
    P: Pixel<Subpixel = u8> + 'static,
    Container: Deref<Target = [P::Subpixel]>,
{
    let mut buf = Vec::new();
    let encoder = image::codecs::png::PngEncoder::new(&mut buf);
    encoder.write_image(img, img.width(), img.height(), image::ColorType::Rgb8)?;
    Ok(buf)
}
*/
pub fn convert_image(image_data: &[u8]) -> Result<Vec<u8>, ImageError> {
    let in_img = ImageReader::new(Cursor::new(image_data))
        .with_guessed_format()?
        .decode()?;

    let (w, h) = in_img.dimensions();
    let mut output = RgbImage::new(w, h); // create a new buffer for our output

    let mut pxl: u8 = 0;
    let mut high = true;
    let mut raw = Vec::new();
    for (x, y, pixel) in in_img.pixels() {
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

    Ok(raw)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn black_is_black() {
        let result = map_color(0, 0, Rgb([0, 0, 0]));
        assert_eq!(result, Rgb([0, 0, 0]));
    }
}
