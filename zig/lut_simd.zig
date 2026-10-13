// Portable Zig built-in SIMD (@Vector) implementation of Q16 tetrahedral interpolation.
// Zero architecture-specific intrinsics or inline assembly; uses only Zig core language
// @Vector, @select, @max, @min, and @splat primitives.

const kQ: u5 = 16;
const kOne: i32 = 1 << kQ;
const kHalf: i32 = 1 << (kQ - 1);

inline fn gatherI(comptime N: usize, table: [*]const i32, idx: @Vector(N, i32)) @Vector(N, i32) {
    var out: [N]i32 = undefined;
    inline for (0..N) |lane| {
        const i: usize = @intCast(idx[lane]);
        out[lane] = table[i];
    }
    return out;
}

inline fn gatherU(comptime N: usize, table: [*]const u32, idx: @Vector(N, i32)) @Vector(N, i32) {
    var out: [N]i32 = undefined;
    inline for (0..N) |lane| {
        const i: usize = @intCast(idx[lane]);
        out[lane] = @bitCast(table[i]);
    }
    return out;
}

inline fn extractByte(comptime N: usize, packed_rgb: @Vector(N, i32), comptime shift: u5) @Vector(N, i32) {
    const mask: @Vector(N, i32) = @splat(0xFF);
    const sh: @Vector(N, u5) = @splat(shift);
    return (packed_rgb >> sh) & mask;
}

inline fn interpolateChannel(
    comptime N: usize,
    c0: @Vector(N, i32),
    c1: @Vector(N, i32),
    c2: @Vector(N, i32),
    c3: @Vector(N, i32),
    f1: @Vector(N, i32),
    f2: @Vector(N, i32),
    f3: @Vector(N, i32),
) @Vector(N, i32) {
    const sh: @Vector(N, u5) = @splat(kQ);
    const half: @Vector(N, i32) = @splat(kHalf);
    const acc = (c0 << sh) + (c1 - c0) * f1 + (c2 - c1) * f2 + (c3 - c2) * f3;
    return (acc + half) >> sh;
}

fn run(comptime N: usize,
    off_table: [*]const i32,
    frac_table: [*]const u32,
    strides: [*]const i32,
    packed_nodes: [*]const u32,
    in_rgb: [*]const u8,
    out_rgb: [*]u8,
    n: usize,
) void {
    const off_r = off_table;
    const off_g = off_table + 256;
    const off_b = off_table + 512;

    const frac_r = frac_table;
    const frac_g = frac_table + 256;
    const frac_b = frac_table + 512;

    const sr: @Vector(N, i32) = @splat(strides[0]);
    const sg: @Vector(N, i32) = @splat(strides[1]);
    const sb: @Vector(N, i32) = @splat(strides[2]);
    const s_tot: @Vector(N, i32) = sr + sg + sb;

    var i: usize = 0;
    while (i + N <= n) : (i += N) {
        const p = in_rgb + 3 * i;
        var r_arr: [N]i32 = undefined;
        var g_arr: [N]i32 = undefined;
        var b_arr: [N]i32 = undefined;
        inline for (0..N) |lane| {
            r_arr[lane] = p[3 * lane + 0];
            g_arr[lane] = p[3 * lane + 1];
            b_arr[lane] = p[3 * lane + 2];
        }
        const r: @Vector(N, i32) = r_arr;
        const g: @Vector(N, i32) = g_arr;
        const b: @Vector(N, i32) = b_arr;

        const base = gatherI(N, off_r, r) + gatherI(N, off_g, g) + gatherI(N, off_b, b);
        const fr = gatherU(N, frac_r, r);
        const fg = gatherU(N, frac_g, g);
        const fb = gatherU(N, frac_b, b);

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

        const v0 = gatherU(N, packed_nodes, base);
        const v1 = gatherU(N, packed_nodes, base + smax);
        const v2 = gatherU(N, packed_nodes, base + s_tot - smin);
        const v3 = gatherU(N, packed_nodes, base + s_tot);

        const out_r = interpolateChannel(
            N,
            extractByte(N, v0, 0),
            extractByte(N, v1, 0),
            extractByte(N, v2, 0),
            extractByte(N, v3, 0),
            f1,
            f2,
            f3,
        );
        const out_g = interpolateChannel(
            N,
            extractByte(N, v0, 8),
            extractByte(N, v1, 8),
            extractByte(N, v2, 8),
            extractByte(N, v3, 8),
            f1,
            f2,
            f3,
        );
        const out_b = interpolateChannel(
            N,
            extractByte(N, v0, 16),
            extractByte(N, v1, 16),
            extractByte(N, v2, 16),
            extractByte(N, v3, 16),
            f1,
            f2,
            f3,
        );

        const q = out_rgb + 3 * i;
        inline for (0..N) |lane| {
            q[3 * lane + 0] = @intCast(out_r[lane]);
            q[3 * lane + 1] = @intCast(out_g[lane]);
            q[3 * lane + 2] = @intCast(out_b[lane]);
        }
    }
}

// Separate ABI symbols make lane width an explicit, reproducible experiment.
pub export fn jshc_tetra_zig_simd4(off: [*]const i32, frac: [*]const u32, strides: [*]const i32, nodes: [*]const u32, input: [*]const u8, output: [*]u8, n: usize) callconv(.c) void {
    run(4, off, frac, strides, nodes, input, output, n);
}
pub export fn jshc_tetra_zig_simd(off: [*]const i32, frac: [*]const u32, strides: [*]const i32, nodes: [*]const u32, input: [*]const u8, output: [*]u8, n: usize) callconv(.c) void {
    run(8, off, frac, strides, nodes, input, output, n);
}
pub export fn jshc_tetra_zig_simd16(off: [*]const i32, frac: [*]const u32, strides: [*]const i32, nodes: [*]const u32, input: [*]const u8, output: [*]u8, n: usize) callconv(.c) void {
    run(16, off, frac, strides, nodes, input, output, n);
}
