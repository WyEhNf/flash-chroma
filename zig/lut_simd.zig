// Portable Zig built-in SIMD (@Vector) implementation of Q16 tetrahedral interpolation.
// Zero architecture-specific intrinsics or inline assembly; uses only Zig core language
// @Vector, @select, @max, @min, and @splat primitives.

const Vec8i = @Vector(8, i32);
const Vec8u = @Vector(8, u32);

const kQ: u5 = 16;
const kOne: i32 = 1 << kQ;
const kHalf: i32 = 1 << (kQ - 1);

inline fn gather8i(table: [*]const i32, idx: Vec8i) Vec8i {
    var out: [8]i32 = undefined;
    inline for (0..8) |lane| {
        const i: usize = @intCast(idx[lane]);
        out[lane] = table[i];
    }
    return out;
}

inline fn gather8u(table: [*]const u32, idx: Vec8i) Vec8i {
    var out: [8]i32 = undefined;
    inline for (0..8) |lane| {
        const i: usize = @intCast(idx[lane]);
        out[lane] = @bitCast(table[i]);
    }
    return out;
}

inline fn extractByte(packed_rgb: Vec8i, comptime shift: u5) Vec8i {
    const mask: Vec8i = @splat(0xFF);
    const sh: @Vector(8, u5) = @splat(shift);
    return (packed_rgb >> sh) & mask;
}

inline fn interpolateChannel(
    c0: Vec8i,
    c1: Vec8i,
    c2: Vec8i,
    c3: Vec8i,
    f1: Vec8i,
    f2: Vec8i,
    f3: Vec8i,
) Vec8i {
    const sh: @Vector(8, u5) = @splat(kQ);
    const half: Vec8i = @splat(kHalf);
    const acc = (c0 << sh) + (c1 - c0) * f1 + (c2 - c1) * f2 + (c3 - c2) * f3;
    return (acc + half) >> sh;
}

pub export fn jshc_tetra_zig_simd(
    off_table: [*]const i32,
    frac_table: [*]const u32,
    strides: [*]const i32,
    packed_nodes: [*]const u32,
    in_rgb: [*]const u8,
    out_rgb: [*]u8,
    n: usize,
) callconv(.c) void {
    const off_r = off_table;
    const off_g = off_table + 256;
    const off_b = off_table + 512;

    const frac_r = frac_table;
    const frac_g = frac_table + 256;
    const frac_b = frac_table + 512;

    const sr: Vec8i = @splat(strides[0]);
    const sg: Vec8i = @splat(strides[1]);
    const sb: Vec8i = @splat(strides[2]);
    const s_tot: Vec8i = sr + sg + sb;

    var i: usize = 0;
    while (i + 8 <= n) : (i += 8) {
        const p = in_rgb + 3 * i;
        var r_arr: [8]i32 = undefined;
        var g_arr: [8]i32 = undefined;
        var b_arr: [8]i32 = undefined;
        inline for (0..8) |lane| {
            r_arr[lane] = p[3 * lane + 0];
            g_arr[lane] = p[3 * lane + 1];
            b_arr[lane] = p[3 * lane + 2];
        }
        const r: Vec8i = r_arr;
        const g: Vec8i = g_arr;
        const b: Vec8i = b_arr;

        const base = gather8i(off_r, r) + gather8i(off_g, g) + gather8i(off_b, b);
        const fr = gather8u(frac_r, r);
        const fg = gather8u(frac_g, g);
        const fb = gather8u(frac_b, b);

        var f1 = fr;
        var smax = sr;
        smax = @select(i32, fg > f1, sg, smax);
        f1 = @max(f1, fg);
        smax = @select(i32, fb > f1, sb, smax);
        f1 = @max(f1, fb);

        var f3 = fr;
        var smin = sr;
        smin = @select(i32, fg < f3, sg, smin);
        f3 = @min(f3, fg);
        smin = @select(i32, fb < f3, sb, smin);
        f3 = @min(f3, fb);

        const f2 = (fr + fg + fb) - f1 - f3;

        const v0 = gather8u(packed_nodes, base);
        const v1 = gather8u(packed_nodes, base + smax);
        const v2 = gather8u(packed_nodes, base + s_tot - smin);
        const v3 = gather8u(packed_nodes, base + s_tot);

        const out_r = interpolateChannel(
            extractByte(v0, 0),
            extractByte(v1, 0),
            extractByte(v2, 0),
            extractByte(v3, 0),
            f1,
            f2,
            f3,
        );
        const out_g = interpolateChannel(
            extractByte(v0, 8),
            extractByte(v1, 8),
            extractByte(v2, 8),
            extractByte(v3, 8),
            f1,
            f2,
            f3,
        );
        const out_b = interpolateChannel(
            extractByte(v0, 16),
            extractByte(v1, 16),
            extractByte(v2, 16),
            extractByte(v3, 16),
            f1,
            f2,
            f3,
        );

        const q = out_rgb + 3 * i;
        inline for (0..8) |lane| {
            q[3 * lane + 0] = @intCast(out_r[lane]);
            q[3 * lane + 1] = @intCast(out_g[lane]);
            q[3 * lane + 2] = @intCast(out_b[lane]);
        }
    }
}
