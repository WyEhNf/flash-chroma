// Portable C++17 implementation of the R14 offline fitting pipeline:
//   1. Curvature-adaptive knot placement (streaming 1D second-derivative profiles)
//   2. Separable 1D Hat-basis warm start via Cholesky decomposition + tensor contraction
//   3. 15-point Lovasz tetrahedral stencil normal equation assembly (2-pass even/odd slab)
//   4. 3-channel simultaneous Jacobi-preconditioned Conjugate Gradient solver
//   5. 8-colour checkerboard integer coordinate descent
#include "jshc/lut.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <utility>
#include <vector>

#if defined(_OPENMP)
#include <omp.h>
#endif

namespace jshc {

namespace {

constexpr int kSubgridSize = 64;
constexpr int kNumChannels = 3;
constexpr int kNumUpperNeighbors = 7;
constexpr int kNumTotalNeighbors = 14;

struct RgbFloat {
  float r = 0.0f;
  float g = 0.0f;
  float b = 0.0f;

  float& operator[](int c) { return (&r)[c]; }
  const float& operator[](int c) const { return (&r)[c]; }
};

struct LovaszStencilSystem {
  std::vector<float> diag;                        // [M] diagonal H_{u,u}
  std::vector<std::array<float, 14>> neighbors;   // [M][14] 7 upper + 7 lower stencil weights
  std::vector<RgbFloat> rhs;                      // [M] right-hand side b = W^T y
  std::array<int32_t, 7> offsets{};               // 7 positive index offsets
  int32_t max_offset = 0;
};

inline void eval_full_chain_pixel(const std::vector<const FullLut*>& chain,
                                  uint8_t r, uint8_t g, uint8_t b, uint8_t* out) {
  for (const FullLut* F : chain) {
    const size_t idx = ((static_cast<size_t>(r) << 16) | (static_cast<size_t>(g) << 8) | b) * 3;
    r = F->data[idx];
    g = F->data[idx + 1];
    b = F->data[idx + 2];
  }
  out[0] = r;
  out[1] = g;
  out[2] = b;
}

// In-place Cholesky inversion of an (m x m) symmetric positive-definite matrix.
void invert_spd_matrix(std::vector<double>& A, int m) {
  std::vector<double> L(m * m, 0.0);
  for (int i = 0; i < m; ++i) {
    for (int j = 0; j <= i; ++j) {
      double sum = A[i * m + j];
      for (int k = 0; k < j; ++k) sum -= L[i * m + k] * L[j * m + k];
      L[i * m + j] = (i == j) ? std::sqrt(std::max(sum, 1e-12)) : (sum / L[j * m + j]);
    }
  }

  std::vector<double> L_inv(m * m, 0.0);
  for (int i = 0; i < m; ++i) {
    L_inv[i * m + i] = 1.0 / L[i * m + i];
    for (int j = i + 1; j < m; ++j) {
      double sum = 0.0;
      for (int k = i; k < j; ++k) sum -= L[j * m + k] * L_inv[k * m + i];
      L_inv[j * m + i] = sum / L[j * m + j];
    }
  }

  for (int i = 0; i < m; ++i) {
    for (int j = 0; j <= i; ++j) {
      double sum = 0.0;
      for (int k = i; k < m; ++k) sum += L_inv[k * m + i] * L_inv[k * m + j];
      A[i * m + j] = A[j * m + i] = sum;
    }
  }
}

void compute_grid_knots(const std::vector<const FullLut*>& chain, uint32_t m, bool adaptive,
                        int num_threads, SparseLut& L, std::array<std::vector<double>, 3>& grid_d) {
  for (int a = 0; a < 3; ++a) {
    L.grid[a].resize(m);
    grid_d[a].resize(m);
  }

  if (!adaptive) {
    for (int a = 0; a < 3; ++a) {
      for (uint32_t i = 0; i < m; ++i) {
        grid_d[a][i] = static_cast<double>(i) * 255.0 / static_cast<double>(m - 1);
        L.grid[a][i] = static_cast<float>(grid_d[a][i]);
      }
    }
    return;
  }

  constexpr int kSliceGrid = 16;
  constexpr int kTotalLines = 3 * kSliceGrid * kSliceGrid;
  std::array<std::array<uint64_t, 256>, 3> global_d2{};

#if defined(_OPENMP)
#pragma omp parallel num_threads(num_threads)
#endif
  {
    std::array<std::array<uint64_t, 256>, 3> local_d2{};
    std::array<uint8_t, 256 * 3> line{};

#if defined(_OPENMP)
#pragma omp for schedule(static)
#endif
    for (int lid = 0; lid < kTotalLines; ++lid) {
      const int axis = lid / (kSliceGrid * kSliceGrid);
      const int rem = lid % (kSliceGrid * kSliceGrid);
      const uint8_t u = static_cast<uint8_t>((rem / kSliceGrid) * 16);
      const uint8_t v = static_cast<uint8_t>((rem % kSliceGrid) * 16);

      for (int x = 0; x < 256; ++x) {
        const uint8_t ux = static_cast<uint8_t>(x);
        line[3 * x + 0] = (axis == 0) ? ux : u;
        line[3 * x + 1] = (axis == 1) ? ux : ((axis == 0) ? u : v);
        line[3 * x + 2] = (axis == 2) ? ux : v;
      }

      for (const FullLut* F : chain) {
        const uint8_t* const tab = F->data.data();
        for (int x = 0; x < 256; ++x) {
          const size_t o = ((static_cast<size_t>(line[3 * x]) << 16) |
                            (static_cast<size_t>(line[3 * x + 1]) << 8) | line[3 * x + 2]) * 3;
          line[3 * x + 0] = tab[o + 0];
          line[3 * x + 1] = tab[o + 1];
          line[3 * x + 2] = tab[o + 2];
        }
      }

      for (int x = 1; x < 255; ++x) {
        int diff_sum = 0;
        for (int c = 0; c < 3; ++c) {
          const int prev = line[3 * (x - 1) + c];
          const int curr = line[3 * x + c];
          const int next = line[3 * (x + 1) + c];
          diff_sum += std::abs(next - 2 * curr + prev);
        }
        local_d2[axis][x] += static_cast<uint64_t>(diff_sum);
      }
    }

#if defined(_OPENMP)
#pragma omp critical
#endif
    {
      for (int a = 0; a < 3; ++a) {
        for (int x = 1; x < 255; ++x) global_d2[a][x] += local_d2[a][x];
      }
    }
  }
  (void)num_threads;

  constexpr double kInvSamples = 1.0 / (kSliceGrid * kSliceGrid * 3.0);
  for (int a = 0; a < 3; ++a) {
    std::array<double, 256> prof{};
    std::array<double, 256> dens{};
    std::array<double, 256> cdf{};

    for (int x = 1; x < 255; ++x) prof[x] = static_cast<double>(global_d2[a][x]) * kInvSamples;
    prof[0] = prof[1];
    prof[255] = prof[254];

    for (int x = 0; x < 256; ++x) dens[x] = std::pow(prof[x], 0.4);
    const double mean_dens = std::accumulate(dens.begin(), dens.end(), 0.0) / 256.0;
    for (int x = 0; x < 256; ++x) dens[x] = 0.5 * dens[x] / (mean_dens + 1e-8) + 0.5;

    cdf[0] = 0.0;
    for (int x = 1; x < 256; ++x) cdf[x] = cdf[x - 1] + 0.5 * (dens[x] + dens[x - 1]);
    for (int x = 0; x < 256; ++x) cdf[x] /= cdf[255];

    for (uint32_t i = 0; i < m; ++i) {
      const double target = static_cast<double>(i) / static_cast<double>(m - 1);
      auto it = std::upper_bound(cdf.begin(), cdf.end() - 1, target);
      const int k = std::max(0, static_cast<int>(it - cdf.begin()) - 1);
      const double denom = cdf[k + 1] - cdf[k];
      grid_d[a][i] = (denom > 1e-12) ? (static_cast<double>(k) + (target - cdf[k]) / denom)
                                     : static_cast<double>(k);
    }

    grid_d[a][0] = 0.0;
    grid_d[a][m - 1] = 255.0;
    for (uint32_t i = 1; i < m; ++i) {
      grid_d[a][i] = std::max(grid_d[a][i], grid_d[a][i - 1] + 2.0);
    }
    for (uint32_t i = 0; i < m; ++i) {
      const double upper_bound = 255.0 - 2.0 * static_cast<double>(m - 1 - i);
      grid_d[a][i] = std::min(grid_d[a][i], upper_bound);
      L.grid[a][i] = static_cast<float>(grid_d[a][i]);
      grid_d[a][i] = static_cast<double>(L.grid[a][i]);
    }
  }
}

void compute_axis_lookup_tables(const std::array<std::vector<double>, 3>& grid_d, SparseLut& L) {
  const uint32_t m = L.m;
  for (int a = 0; a < 3; ++a) {
    const auto& g = grid_d[a];
    for (int x = 0; x < 256; ++x) {
      auto it = std::upper_bound(g.begin(), g.end(), static_cast<double>(x));
      const int cell = std::clamp(static_cast<int>(it - g.begin()) - 1, 0, static_cast<int>(m) - 2);
      const double frac = (static_cast<double>(x) - g[cell]) / (g[cell + 1] - g[cell]);
      const int32_t fq = std::clamp(static_cast<int32_t>(std::floor(frac * kOne + 0.5)), 0, kOne);
      L.idx[a][x] = static_cast<uint8_t>(cell);
      L.frac[a][x] = static_cast<uint32_t>(fq);
    }
  }
}

std::vector<RgbFloat> compute_separable_initial_guess(
    const SparseLut& L, const std::array<uint8_t, kSubgridSize>& v_coord,
    const std::vector<uint8_t>& Y_sub, int num_threads) {
  const uint32_t m = L.m;
  std::array<std::vector<float>, 3> P_mat;

  for (int a = 0; a < 3; ++a) {
    std::vector<double> B(kSubgridSize * m, 0.0);
    for (int q = 0; q < kSubgridSize; ++q) {
      const int x = v_coord[q];
      const int cell = L.idx[a][x];
      const double f = static_cast<double>(L.frac[a][x]) / static_cast<double>(kOne);
      B[q * m + cell] += 1.0 - f;
      B[q * m + cell + 1] += f;
    }

    std::vector<double> BtB(m * m, 0.0);
    for (uint32_t i = 0; i < m; ++i) {
      for (uint32_t j = 0; j < m; ++j) {
        double sum = (i == j) ? 1e-6 : 0.0;
        for (int q = 0; q < kSubgridSize; ++q) sum += B[q * m + i] * B[q * m + j];
        BtB[i * m + j] = sum;
      }
    }
    invert_spd_matrix(BtB, static_cast<int>(m));

    P_mat[a].resize(m * kSubgridSize);
    for (uint32_t i = 0; i < m; ++i) {
      for (int q = 0; q < kSubgridSize; ++q) {
        double sum = 0.0;
        for (uint32_t j = 0; j < m; ++j) sum += BtB[i * m + j] * B[q * m + j];
        P_mat[a][i * kSubgridSize + q] = static_cast<float>(sum);
      }
    }
  }

  const size_t M = static_cast<size_t>(m) * m * m;
  std::vector<float> T1(static_cast<size_t>(m) * kSubgridSize * kSubgridSize * kNumChannels, 0.0f);
  std::vector<float> T2(static_cast<size_t>(m) * m * kSubgridSize * kNumChannels, 0.0f);
  std::vector<RgbFloat> x0(M);

#if defined(_OPENMP)
#pragma omp parallel num_threads(num_threads)
#endif
  {
#if defined(_OPENMP)
#pragma omp for schedule(static)
#endif
    for (int i = 0; i < static_cast<int>(m); ++i) {
      float* const dst = &T1[static_cast<size_t>(i) * kSubgridSize * kSubgridSize * kNumChannels];
      for (int qr = 0; qr < kSubgridSize; ++qr) {
        const float weight = P_mat[0][i * kSubgridSize + qr];
        if (std::abs(weight) < 1e-9f) continue;
        const uint8_t* const src = &Y_sub[qr * kSubgridSize * kSubgridSize * kNumChannels];
        for (int k = 0; k < kSubgridSize * kSubgridSize * kNumChannels; ++k) {
          dst[k] += weight * static_cast<float>(src[k]);
        }
      }
    }

#if defined(_OPENMP)
#pragma omp for schedule(static)
#endif
    for (int ij = 0; ij < static_cast<int>(m * m); ++ij) {
      const int i = ij / static_cast<int>(m);
      const int j = ij % static_cast<int>(m);
      float* const dst = &T2[static_cast<size_t>(ij) * kSubgridSize * kNumChannels];
      for (int qg = 0; qg < kSubgridSize; ++qg) {
        const float weight = P_mat[1][j * kSubgridSize + qg];
        if (std::abs(weight) < 1e-9f) continue;
        const float* const src =
            &T1[(static_cast<size_t>(i) * kSubgridSize + qg) * kSubgridSize * kNumChannels];
        for (int k = 0; k < kSubgridSize * kNumChannels; ++k) {
          dst[k] += weight * src[k];
        }
      }
    }

#if defined(_OPENMP)
#pragma omp for schedule(static)
#endif
    for (int ij = 0; ij < static_cast<int>(m * m); ++ij) {
      const float* const src = &T2[static_cast<size_t>(ij) * kSubgridSize * kNumChannels];
      for (uint32_t k = 0; k < m; ++k) {
        RgbFloat sum{};
        for (int qb = 0; qb < kSubgridSize; ++qb) {
          const float weight = P_mat[2][k * kSubgridSize + qb];
          sum.r += weight * src[3 * qb + 0];
          sum.g += weight * src[3 * qb + 1];
          sum.b += weight * src[3 * qb + 2];
        }
        x0[static_cast<size_t>(ij) * m + k] = sum;
      }
    }
  }
  (void)num_threads;
  return x0;
}

LovaszStencilSystem assemble_lovasz_stencil(const SparseLut& L,
                                            const std::array<uint8_t, kSubgridSize>& v_coord,
                                            const std::vector<uint8_t>& Y_sub, int num_threads) {
  const uint32_t m = L.m;
  const size_t M = static_cast<size_t>(m) * m * m;
  const int32_t sr = static_cast<int32_t>(m * m);
  const int32_t sg = static_cast<int32_t>(m);
  const int32_t sb = 1;

  LovaszStencilSystem sys;
  sys.diag.assign(M, 0.0f);
  sys.neighbors.assign(M, std::array<float, kNumTotalNeighbors>{});
  sys.rhs.assign(M, RgbFloat{});
  sys.offsets = {sb, sg, sg + sb, sr, sr + sb, sr + sg, sr + sg + sb};
  sys.max_offset = sr + sg + sb;

  std::vector<std::array<float, kNumUpperNeighbors>> upper_weights(M);
  std::vector<int> cell_q_start(m, kSubgridSize);
  std::vector<int> cell_q_end(m, 0);
  for (int q = 0; q < kSubgridSize; ++q) {
    const int cell = L.idx[0][v_coord[q]];
    cell_q_start[cell] = std::min(cell_q_start[cell], q);
    cell_q_end[cell] = std::max(cell_q_end[cell], q + 1);
  }

  constexpr float kInvOne = 1.0f / static_cast<float>(kOne);

  // Two-pass (even/odd R-cell) lock-free parallel assembly.
  for (int parity = 0; parity < 2; ++parity) {
#if defined(_OPENMP)
#pragma omp parallel for schedule(dynamic, 1) num_threads(num_threads)
#endif
    for (int cr = parity; cr < static_cast<int>(m) - 1; cr += 2) {
      for (int qr = cell_q_start[cr]; qr < cell_q_end[cr]; ++qr) {
        const uint8_t r = v_coord[qr];
        const int32_t off_r = static_cast<int32_t>(L.idx[0][r]) * sr;
        const int32_t fr = static_cast<int32_t>(L.frac[0][r]);

        for (int qg = 0; qg < kSubgridSize; ++qg) {
          const uint8_t g = v_coord[qg];
          const int32_t off_rg = off_r + static_cast<int32_t>(L.idx[1][g]) * sg;
          const int32_t fg = static_cast<int32_t>(L.frac[1][g]);
          const uint8_t* const y_row = &Y_sub[((qr * kSubgridSize + qg) * kSubgridSize) * 3];

          for (int qb = 0; qb < kSubgridSize; ++qb) {
            const uint8_t b = v_coord[qb];
            const int32_t u0 = off_rg + static_cast<int32_t>(L.idx[2][b]);
            const int32_t fb = static_cast<int32_t>(L.frac[2][b]);

            struct AxisOrder {
              int32_t frac;
              int bit;
              int32_t stride;
            };
            std::array<AxisOrder, 3> ord = {{
                {fr, 4, sr},
                {fg, 2, sg},
                {fb, 1, sb},
            }};
            if (ord[1].frac > ord[0].frac) std::swap(ord[0], ord[1]);
            if (ord[2].frac > ord[0].frac) std::swap(ord[0], ord[2]);
            if (ord[2].frac > ord[1].frac) std::swap(ord[1], ord[2]);

            const std::array<int32_t, 4> v_idx = {
                u0,
                u0 + ord[0].stride,
                u0 + ord[0].stride + ord[1].stride,
                u0 + sys.max_offset,
            };
            const std::array<int, 4> mask = {0, ord[0].bit, ord[0].bit | ord[1].bit, 7};
            const std::array<float, 4> w = {
                static_cast<float>(kOne - ord[0].frac) * kInvOne,
                static_cast<float>(ord[0].frac - ord[1].frac) * kInvOne,
                static_cast<float>(ord[1].frac - ord[2].frac) * kInvOne,
                static_cast<float>(ord[2].frac) * kInvOne,
            };

            const RgbFloat target{
                static_cast<float>(y_row[3 * qb + 0]),
                static_cast<float>(y_row[3 * qb + 1]),
                static_cast<float>(y_row[3 * qb + 2]),
            };

            for (int a = 0; a < 4; ++a) {
              if (w[a] == 0.0f) continue;
              const int32_t va = v_idx[a];
              sys.diag[va] += w[a] * w[a];
              sys.rhs[va].r += w[a] * target.r;
              sys.rhs[va].g += w[a] * target.g;
              sys.rhs[va].b += w[a] * target.b;

              for (int e = a + 1; e < 4; ++e) {
                if (w[e] == 0.0f) continue;
                const int slot = (mask[e] - mask[a]) - 1;
                upper_weights[va][slot] += w[a] * w[e];
              }
            }
          }
        }
      }
    }
  }

#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(num_threads)
#endif
  for (long long u = 0; u < static_cast<long long>(M); ++u) {
    for (int k = 0; k < kNumUpperNeighbors; ++k) {
      sys.neighbors[u][k] = upper_weights[u][k];
      sys.neighbors[u][kNumUpperNeighbors + k] =
          (u >= sys.offsets[k]) ? upper_weights[u - sys.offsets[k]][k] : 0.0f;
    }
  }
  (void)num_threads;
  return sys;
}

void solve_jacobi_cg(const LovaszStencilSystem& sys, const std::vector<RgbFloat>& x0,
                     int num_threads, RgbFloat* x_padded) {
  const size_t M = sys.diag.size();
  constexpr float kLambda = 1e-4f;

  std::vector<float> A_diag(M);
  std::vector<float> P_inv(M);
  std::vector<RgbFloat> rhs_reg(M);
  std::vector<RgbFloat> r(M), z(M), Ap(M);
  std::vector<RgbFloat> p_buf(M + 2 * static_cast<size_t>(sys.max_offset));
  RgbFloat* const p = p_buf.data() + sys.max_offset;

  for (size_t u = 0; u < M; ++u) {
    const float d = sys.diag[u];
    const float D = d + 1.0f;
    A_diag[u] = d + kLambda * D;
    P_inv[u] = 1.0f / A_diag[u];
    for (int c = 0; c < kNumChannels; ++c) {
      rhs_reg[u][c] = sys.rhs[u][c] + kLambda * D * x0[u][c];
      x_padded[u][c] = x0[u][c];
    }
  }

  auto apply_stencil = [&](const RgbFloat* vec_in, RgbFloat* vec_out) {
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(num_threads)
#endif
    for (long long u = 0; u < static_cast<long long>(M); ++u) {
      const float ad = A_diag[u];
      RgbFloat sum{ad * vec_in[u].r, ad * vec_in[u].g, ad * vec_in[u].b};
      const auto& nb = sys.neighbors[u];
      for (int k = 0; k < kNumUpperNeighbors; ++k) {
        const float wu = nb[k];
        const float wd = nb[kNumUpperNeighbors + k];
        const RgbFloat& vu = vec_in[u + sys.offsets[k]];
        const RgbFloat& vd = vec_in[u - sys.offsets[k]];
        sum.r += wu * vu.r + wd * vd.r;
        sum.g += wu * vu.g + wd * vd.g;
        sum.b += wu * vu.b + wd * vd.b;
      }
      vec_out[u] = sum;
    }
  };

  apply_stencil(x_padded, Ap.data());

  std::array<double, 3> rz{0.0, 0.0, 0.0};
  std::array<double, 3> rhs_norm2{0.0, 0.0, 0.0};
  for (size_t u = 0; u < M; ++u) {
    for (int c = 0; c < kNumChannels; ++c) {
      const float rc = rhs_reg[u][c] - Ap[u][c];
      const float zc = P_inv[u] * rc;
      r[u][c] = rc;
      z[u][c] = zc;
      p[u][c] = zc;
      rz[c] += static_cast<double>(rc) * static_cast<double>(zc);
      rhs_norm2[c] += static_cast<double>(rhs_reg[u][c]) * static_cast<double>(rhs_reg[u][c]);
    }
  }

  for (int iter = 0; iter < 20; ++iter) {
    apply_stencil(p, Ap.data());

    std::array<double, 3> pAp{0.0, 0.0, 0.0};
    for (size_t u = 0; u < M; ++u) {
      for (int c = 0; c < kNumChannels; ++c) {
        pAp[c] += static_cast<double>(p[u][c]) * static_cast<double>(Ap[u][c]);
      }
    }

    std::array<float, 3> alpha{};
    for (int c = 0; c < kNumChannels; ++c) {
      alpha[c] = (pAp[c] > 1e-20) ? static_cast<float>(rz[c] / pAp[c]) : 0.0f;
    }

    std::array<double, 3> rz_next{0.0, 0.0, 0.0};
    std::array<double, 3> r_norm2{0.0, 0.0, 0.0};
    for (size_t u = 0; u < M; ++u) {
      const float pinv = P_inv[u];
      for (int c = 0; c < kNumChannels; ++c) {
        x_padded[u][c] += alpha[c] * p[u][c];
        const float rc = r[u][c] - alpha[c] * Ap[u][c];
        const float zc = pinv * rc;
        r[u][c] = rc;
        z[u][c] = zc;
        rz_next[c] += static_cast<double>(rc) * static_cast<double>(zc);
        r_norm2[c] += static_cast<double>(rc) * static_cast<double>(rc);
      }
    }

    if (r_norm2[0] <= 1e-9 * rhs_norm2[0] && r_norm2[1] <= 1e-9 * rhs_norm2[1] &&
        r_norm2[2] <= 1e-9 * rhs_norm2[2]) {
      break;
    }

    std::array<float, 3> beta{};
    for (int c = 0; c < kNumChannels; ++c) {
      beta[c] = (rz[c] > 1e-20) ? static_cast<float>(rz_next[c] / rz[c]) : 0.0f;
      rz[c] = rz_next[c];
    }
    for (size_t u = 0; u < M; ++u) {
      for (int c = 0; c < kNumChannels; ++c) {
        p[u][c] = z[u][c] + beta[c] * p[u][c];
      }
    }
  }
}

void refine_integer_lattice(const LovaszStencilSystem& sys, uint32_t m, int num_threads,
                            RgbFloat* x_padded) {
  const size_t M = sys.diag.size();
  for (size_t u = 0; u < M; ++u) {
    for (int c = 0; c < kNumChannels; ++c) {
      x_padded[u][c] = std::clamp(std::floor(x_padded[u][c] + 0.5f), 0.0f, 255.0f);
    }
  }

  for (int sweep = 0; sweep < 4; ++sweep) {
    int changed = 0;
    for (int color = 0; color < 8; ++color) {
      const uint32_t pi = (color >> 2) & 1;
      const uint32_t pj = (color >> 1) & 1;
      const uint32_t pk = color & 1;

#if defined(_OPENMP)
#pragma omp parallel for schedule(static) reduction(+ : changed) num_threads(num_threads)
#endif
      for (uint32_t i = pi; i < m; i += 2) {
        for (uint32_t j = pj; j < m; j += 2) {
          for (uint32_t k = pk; k < m; k += 2) {
            const long long u = (static_cast<long long>(i) * m + j) * m + k;
            const float d = sys.diag[u];
            if (d <= 0.0f) continue;

            const float half_d = 0.5f * d;
            RgbFloat grad{
                d * x_padded[u].r - sys.rhs[u].r,
                d * x_padded[u].g - sys.rhs[u].g,
                d * x_padded[u].b - sys.rhs[u].b,
            };

            const auto& nb = sys.neighbors[u];
            for (int s = 0; s < kNumUpperNeighbors; ++s) {
              const float wu = nb[s];
              const float wd = nb[kNumUpperNeighbors + s];
              const RgbFloat& vu = x_padded[u + sys.offsets[s]];
              const RgbFloat& vd = x_padded[u - sys.offsets[s]];
              grad.r += wu * vu.r + wd * vd.r;
              grad.g += wu * vu.g + wd * vd.g;
              grad.b += wu * vu.b + wd * vd.b;
            }

            for (int c = 0; c < kNumChannels; ++c) {
              if (grad[c] + half_d < -1e-6f && x_padded[u][c] + 1.0f <= 255.0f) {
                x_padded[u][c] += 1.0f;
                ++changed;
              } else if (-grad[c] + half_d < -1e-6f && x_padded[u][c] - 1.0f >= 0.0f) {
                x_padded[u][c] -= 1.0f;
                ++changed;
              }
            }
          }
        }
      }
    }
    if (changed == 0) break;
  }
  (void)num_threads;
}

}  // namespace

SparseLut fit_r14(const std::vector<const FullLut*>& chain, uint32_t m, int threads,
                  bool adaptive) {
  if (chain.empty() || m < 2 || m > 256) {
    throw std::runtime_error("invalid fit_r14 arguments");
  }

#if defined(_OPENMP)
  const int num_threads = (threads > 0) ? threads : omp_get_max_threads();
#else
  const int num_threads = 1;
  (void)threads;
#endif

  SparseLut L;
  L.m = m;
  std::array<std::vector<double>, 3> grid_d;

  // Step 1 & 2: Compute grid knots and Q16 lookup tables.
  compute_grid_knots(chain, m, adaptive, num_threads, L, grid_d);
  compute_axis_lookup_tables(grid_d, L);

  // Step 3: Sample the 64^3 composite subgrid.
  std::array<uint8_t, kSubgridSize> v_coord{};
  for (int q = 0; q < kSubgridSize; ++q) {
    v_coord[q] = static_cast<uint8_t>(std::floor(q * 255.0 / (kSubgridSize - 1) + 0.5));
  }

  std::vector<uint8_t> Y_sub(kSubgridSize * kSubgridSize * kSubgridSize * kNumChannels);
#if defined(_OPENMP)
#pragma omp parallel for schedule(static) num_threads(num_threads)
#endif
  for (int qr = 0; qr < kSubgridSize; ++qr) {
    for (int qg = 0; qg < kSubgridSize; ++qg) {
      uint8_t* const out_row = &Y_sub[((qr * kSubgridSize + qg) * kSubgridSize) * kNumChannels];
      for (int qb = 0; qb < kSubgridSize; ++qb) {
        eval_full_chain_pixel(chain, v_coord[qr], v_coord[qg], v_coord[qb], out_row + 3 * qb);
      }
    }
  }

  // Step 4: Separable 1D Hat-basis initial guess.
  const std::vector<RgbFloat> x0 =
      compute_separable_initial_guess(L, v_coord, Y_sub, num_threads);

  // Step 5: Assemble 15-point Lovasz tetrahedral stencil normal equations.
  const LovaszStencilSystem sys = assemble_lovasz_stencil(L, v_coord, Y_sub, num_threads);

  // Step 6 & 7: Solve via Jacobi-CG and refine on the integer lattice.
  const size_t M = static_cast<size_t>(m) * m * m;
  std::vector<RgbFloat> x_buf(M + 2 * static_cast<size_t>(sys.max_offset));
  RgbFloat* const x_padded = x_buf.data() + sys.max_offset;

  solve_jacobi_cg(sys, x0, num_threads, x_padded);
  refine_integer_lattice(sys, m, num_threads, x_padded);

  L.nodes.resize(M * kNumChannels);
  for (size_t u = 0; u < M; ++u) {
    L.nodes[3 * u + 0] = static_cast<uint8_t>(static_cast<int>(x_padded[u].r));
    L.nodes[3 * u + 1] = static_cast<uint8_t>(static_cast<int>(x_padded[u].g));
    L.nodes[3 * u + 2] = static_cast<uint8_t>(static_cast<int>(x_padded[u].b));
  }
  L.prepare();
  return L;
}

}  // namespace jshc
