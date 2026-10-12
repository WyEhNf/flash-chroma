// Portable Rust built-in SIMD (core::simd / std::simd) implementation of Q16 tetrahedral interpolation.
// Zero architecture-specific intrinsics or inline assembly; uses only Rust's portable_simd
// types (i32x8, usizex8, Mask) and standard operators.
#![feature(portable_simd)]
#![no_std]

use core::simd::prelude::*;
use core::slice;

const K_Q: i32 = 16;
const K_HALF: i32 = 1 << (K_Q - 1);

#[inline(always)]
unsafe fn gather8_i32(table: &[i32], idx: i32x8) -> i32x8 {
    let u_idx: usizex8 = idx.cast();
    unsafe { Simd::gather_select_unchecked(table, Mask::splat(true), u_idx, i32x8::splat(0)) }
}

#[inline(always)]
fn extract_byte(packed: i32x8, shift: i32) -> i32x8 {
    (packed >> i32x8::splat(shift)) & i32x8::splat(0xFF)
}

#[inline(always)]
fn interpolate_channel(
    c0: i32x8,
    c1: i32x8,
    c2: i32x8,
    c3: i32x8,
    f1: i32x8,
    f2: i32x8,
    f3: i32x8,
) -> i32x8 {
    let sh = i32x8::splat(K_Q);
    let half = i32x8::splat(K_HALF);
    let acc = (c0 << sh) + (c1 - c0) * f1 + (c2 - c1) * f2 + (c3 - c2) * f3;
    (acc + half) >> sh
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn jshc_tetra_rust_simd(
    off_table: *const i32,
    frac_table: *const u32,
    strides: *const i32,
    packed_nodes: *const u32,
    packed_len: usize,
    in_rgb: *const u8,
    out_rgb: *mut u8,
    n: usize,
) {
    let off_r = unsafe { slice::from_raw_parts(off_table, 256) };
    let off_g = unsafe { slice::from_raw_parts(off_table.add(256), 256) };
    let off_b = unsafe { slice::from_raw_parts(off_table.add(512), 256) };

    let frac_i32 = frac_table as *const i32;
    let frac_r = unsafe { slice::from_raw_parts(frac_i32, 256) };
    let frac_g = unsafe { slice::from_raw_parts(frac_i32.add(256), 256) };
    let frac_b = unsafe { slice::from_raw_parts(frac_i32.add(512), 256) };

    let nodes = unsafe { slice::from_raw_parts(packed_nodes as *const i32, packed_len) };
    let st = unsafe { slice::from_raw_parts(strides, 3) };

    let sr = i32x8::splat(st[0]);
    let sg = i32x8::splat(st[1]);
    let sb = i32x8::splat(st[2]);
    let s_tot = sr + sg + sb;

    let mut i: usize = 0;
    while i + 8 <= n {
        let p = unsafe { in_rgb.add(3 * i) };
        let r = i32x8::from_array([
            unsafe { *p.add(0) as i32 },
            unsafe { *p.add(3) as i32 },
            unsafe { *p.add(6) as i32 },
            unsafe { *p.add(9) as i32 },
            unsafe { *p.add(12) as i32 },
            unsafe { *p.add(15) as i32 },
            unsafe { *p.add(18) as i32 },
            unsafe { *p.add(21) as i32 },
        ]);
        let g = i32x8::from_array([
            unsafe { *p.add(1) as i32 },
            unsafe { *p.add(4) as i32 },
            unsafe { *p.add(7) as i32 },
            unsafe { *p.add(10) as i32 },
            unsafe { *p.add(13) as i32 },
            unsafe { *p.add(16) as i32 },
            unsafe { *p.add(19) as i32 },
            unsafe { *p.add(22) as i32 },
        ]);
        let b = i32x8::from_array([
            unsafe { *p.add(2) as i32 },
            unsafe { *p.add(5) as i32 },
            unsafe { *p.add(8) as i32 },
            unsafe { *p.add(11) as i32 },
            unsafe { *p.add(14) as i32 },
            unsafe { *p.add(17) as i32 },
            unsafe { *p.add(20) as i32 },
            unsafe { *p.add(23) as i32 },
        ]);

        let base = unsafe {
            gather8_i32(off_r, r) + gather8_i32(off_g, g) + gather8_i32(off_b, b)
        };
        let fr = unsafe { gather8_i32(frac_r, r) };
        let fg = unsafe { gather8_i32(frac_g, g) };
        let fb = unsafe { gather8_i32(frac_b, b) };

        let mut f1 = fr;
        let mut smax = sr;
        smax = fg.simd_gt(f1).select(sg, smax);
        f1 = f1.simd_max(fg);
        smax = fb.simd_gt(f1).select(sb, smax);
        f1 = f1.simd_max(fb);

        let mut f3 = fr;
        let mut smin = sr;
        smin = fg.simd_lt(f3).select(sg, smin);
        f3 = f3.simd_min(fg);
        smin = fb.simd_lt(f3).select(sb, smin);
        f3 = f3.simd_min(fb);

        let f2 = (fr + fg + fb) - f1 - f3;

        let v0 = unsafe { gather8_i32(nodes, base) };
        let v1 = unsafe { gather8_i32(nodes, base + smax) };
        let v2 = unsafe { gather8_i32(nodes, base + s_tot - smin) };
        let v3 = unsafe { gather8_i32(nodes, base + s_tot) };

        let out_r = interpolate_channel(
            extract_byte(v0, 0),
            extract_byte(v1, 0),
            extract_byte(v2, 0),
            extract_byte(v3, 0),
            f1,
            f2,
            f3,
        )
        .to_array();
        let out_g = interpolate_channel(
            extract_byte(v0, 8),
            extract_byte(v1, 8),
            extract_byte(v2, 8),
            extract_byte(v3, 8),
            f1,
            f2,
            f3,
        )
        .to_array();
        let out_b = interpolate_channel(
            extract_byte(v0, 16),
            extract_byte(v1, 16),
            extract_byte(v2, 16),
            extract_byte(v3, 16),
            f1,
            f2,
            f3,
        )
        .to_array();

        let q = unsafe { out_rgb.add(3 * i) };
        for lane in 0..8 {
            unsafe {
                *q.add(3 * lane + 0) = out_r[lane] as u8;
                *q.add(3 * lane + 1) = out_g[lane] as u8;
                *q.add(3 * lane + 2) = out_b[lane] as u8;
            }
        }
        i += 8;
    }
}

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
