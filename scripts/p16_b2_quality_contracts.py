"""99既有u64输入合同，保留旧fixture seed/公式，仅容量断言适配明确新增owner。"""
from verify_p16_workload import np, io, cc, checked, state, cache_table, cache_info, integer_oracle, apply_to


def contracts(libs, folder, models, high_hint):
    rng = np.random.default_rng(202610240091)
    axis = np.rint(np.linspace(0, 255, 17)).astype(np.uint8)
    red, green, blue = np.meshgrid(axis, axis, axis, indexing='ij')
    identity = io.SparseLut(io.uniform_grid(17), np.stack([red, green, blue], axis=3))
    identity_path = folder / 'identity17.slut'
    io.save_sparse(identity_path, identity)
    identity_model = cc.from_sparse(io.load_sparse(identity_path, competition=True))
    gray = io.SparseLut(io.uniform_grid(17), np.repeat(red[..., None], 3, axis=3))
    gray_path = folder / 'gray17.slut'
    io.save_sparse(gray_path, gray)
    gray_model = cc.from_sparse(io.load_sparse(gray_path, competition=True))
    # 固定身份后缀使缓存有>255种输出；不得换seed或改模型使门禁通过。
    cases = [('over255_palette', [gray_path, identity_path, identity_path, identity_path], [None] * 4,
              [gray_model, identity_model, identity_model, identity_model], False)]
    mixed = cc.from_sparse(io.load_sparse(identity_path, competition=True))
    for channel, power in enumerate((1., 1.125, .875)):
        mixed.channel_frac[channel] = np.rint(65536 * (mixed.channel_frac[channel] / 65536.) ** power).astype(np.uint32)
    mixed.channel_frac[:, :, 0] = 0
    mixed.channel_frac[:, :, 255] = 65536
    cc.validate(mixed)
    mixed_side = folder / 'mixed-suffix.bin'
    mixed.channel_frac.astype('<u4').tofile(mixed_side)
    cases.append(('mixed_suffix', [gray_path, identity_path, identity_path, identity_path],
                  [None, mixed_side, None, None], [gray_model, mixed, identity_model, identity_model], False))
    ordinary = [io.load_sparse(checked(row), competition=True) for row in models['models']]
    equal = cc.from_sparse(ordinary[0])
    for axis_index in range(3):
        frac = np.rint(65536 * (equal.channel_frac[0, axis_index] / 65536.) ** 1.125).astype(np.uint32)
        equal.channel_frac[:, axis_index] = frac
    equal.channel_frac[:, :, 0] = 0
    equal.channel_frac[:, :, 255] = 65536
    cc.validate(equal)
    assert not np.array_equal(equal.channel_frac[0], cc.from_sparse(ordinary[0]).channel_frac[0])
    equal_side = folder / 'changed-equal-side.bin'
    equal.channel_frac.astype('<u4').tofile(equal_side)
    paths = [checked(row) for row in models['models']]
    cases.append(('changed_equal_sidecar', paths, [equal_side, None, None, None],
                  [equal, *[cc.from_sparse(s) for s in ordinary[1:]]], True))
    cases.append(('single_shared', paths[:1], [None], [cc.from_sparse(ordinary[0])], False))
    for m in (17, 18, 25, 33):
        nodes = np.repeat(rng.integers(120, 129, (m, m, m), np.uint8)[..., None], 3, axis=3)
        path = folder / f'signed-gray{m}.slut'
        io.save_sparse(path, io.SparseLut(io.uniform_grid(m), nodes))
        model = cc.from_sparse(io.load_sparse(path, competition=True))
        cases.append((f'shared_signed_m{m}', [path, identity_path, identity_path, identity_path], [None] * 4,
                      [model, identity_model, identity_model, identity_model], True))
    probes = np.concatenate([rng.integers(0, 256, (8192, 3), np.uint8),
        np.array([[r, g, b] for r in (0, 255) for g in (0, 255) for b in (0, 255)], np.uint8)])
    records = []
    for name, paths, sides, truth_models, expected_direct in cases:
        expected_direct = expected_direct and high_hint
        truth = probes.copy()
        for model in truth_models:
            truth = integer_oracle(model, truth)
        with libs['reference'].chain(paths, sides) as a, libs['candidate'].chain(paths, sides) as b:
            states = {'reference': state(a), 'candidate': state(b)}
            assert bool(states['candidate']['direct']['enabled']) == expected_direct
            assert not states['candidate']['domain']['fast_path_enabled']
            if not expected_direct:
                assert b.model_bytes-a.model_bytes in (8,160328)  # 另由99 proxy逐模型精确核。
            if name == 'over255_palette':
                unique_count = int(np.unique(cache_table(a, cache_info(a))).size)
                assert unique_count > 255
            else:
                unique_count = None
            checks = 0
            for kernel in (0, 1):
                for threads in (1, 4):
                    actual = b.apply(probes.copy(), kernel='avx2' if kernel else 'scalar', threads=threads)
                    assert np.array_equal(actual, truth)
                    raw = apply_to(b.library.dll, b.handle, probes.tobytes(), kernel, threads, 1, 62, False)
                    assert raw == truth.tobytes()
                    checks += 2
            records.append({'case': name, 'state': states, 'expected_direct': expected_direct,
                'oracle_pixels': len(probes), 'backend_comparisons': checks, 'byte_mismatches': 0,
                'over255_cache_unique_count': unique_count})
    return records


