// Setup warnings/errors:
#![forbid(unsafe_code)]
#![deny(bare_trait_objects, unused_doc_comments, unused_import_braces)]
// Clippy:
#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::non_ascii_literal)]

use gpx::Gpx;

use std::fs::File;
use std::io::BufReader;
use unicode_bom::Bom;



pub fn calculate_boundaries(gpx: Gpx, margin: u32) -> ([f64; 2], [f64; 2]) {
    let mut lon_border: [f64; 2] = [90.0, -90.0];
    let mut lat_border: [f64; 2] = [180.0, -180.0];
    for track in &gpx.tracks {
        for s in &track.segments {
            for p in &s.points {
                (lon_border, lat_border) = adjust_boundaries(p, lon_border, lat_border);
            }
        }
    }
    for route in &gpx.routes {
        for p in &route.points {
            (lon_border, lat_border) = adjust_boundaries(p, lon_border, lat_border);
        }
    }

    (lon_border, lat_border)
}

fn adjust_boundaries(
    p: &gpx::Waypoint,
    mut lon_border: [f64; 2],
    mut lat_border: [f64; 2],
) -> ([f64; 2], [f64; 2]) {
    let x = p.point().x();
    let y = p.point().y();
    if x < lon_border[0] {
        lon_border[0] = x;
    } else if x > lon_border[1] {
        lon_border[1] = x;
    }
    if y < lat_border[0] {
        lat_border[0] = y;
    } else if y > lat_border[1] {
        lat_border[1] = y;
    }
    (lon_border, lat_border)
}



pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
