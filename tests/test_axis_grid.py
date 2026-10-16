"""有限网格DP的独立路径枚举、Q16弦代价与255边界覆盖合同。"""
import itertools
import numpy as np
from lutlab import axis_grid as ag


def test_two_pass_minimax_matches_exhaustive_paths():
    rng = np.random.default_rng(2026101741)
    n,m = 9,4
    for _ in range(12):
        worst = np.full((n,n),ag.INF,np.int64)
        sse = worst.copy()
        for a in range(n):
            for b in range(a+1,min(n,a+5)):
                worst[a,b],sse[a,b] = rng.integers(0,6),rng.integers(0,25)
        for method in ("minimax","sse"):
            knots,record = ag.choose_knots(worst,sse,m,max_step=4,objective=method)
            values = []
            for middle in itertools.combinations(range(1,n-1),m-2):
                path = (0,*middle,n-1)
                if max(np.diff(path)) > 4:
                    continue
                maximum = max(int(worst[a,b]) for a,b in zip(path[:-1],path[1:]))
                total = sum(int(sse[a,b]) for a,b in zip(path[:-1],path[1:]))
                penalty = sum((end*(m-1)-(n-1)*k)**2 for k,end in enumerate(path))
                values.append(((maximum,total,penalty) if method == "minimax" else (total,penalty)))
            expected = min(values)
            actual = (record["selected_worst_squared"],record["selected_sse"],record["tie_penalty"]) if method == "minimax" else (record["selected_sse"],record["tie_penalty"])
            assert actual == expected
            assert knots[0] == 0 and knots[-1] == n-1 and len(knots) == m


def test_one_code_peak_requires_adjacent_knots_and_integer_chord_matches_scalar():
    curves = np.zeros((9,1,3),np.uint8)
    curves[3,0,0] = 255
    worst,sse = ag.chord_costs(curves,max_step=4)
    for a in range(8):
        for b in range(a+1,min(9,a+5)):
            errors = []
            for x in range(a,b+1):
                f = ((x-a)*65536*2+(b-a))//(2*(b-a))
                out = [((65536-f)*int(curves[a,0,c])+f*int(curves[b,0,c])+32768)//65536 for c in range(3)]
                errors.append(sum((out[c]-int(curves[x,0,c]))**2 for c in range(3)))
            assert worst[a,b] == max(errors) and sse[a,b] == sum(errors)
    knots,record = ag.choose_knots(worst,sse,5,max_step=4)
    assert knots.tolist() == [0.,2.,3.,4.,8.] and record["selected_worst_squared"] == 0
    no_adjacent,_ = ag.chord_costs(curves,min_step=2,max_step=4)
    _,record = ag.choose_knots(no_adjacent,sse,5,min_step=2,max_step=4)
    assert record["selected_worst_squared"] > 0


def test_curves_include_missing_255_boundary_and_deduplicate_hot_lines():
    def source(rgb):
        result = np.zeros_like(rgb)
        result[:,2] = np.where((rgb[:,0] == 255)&(rgb[:,1] == 255),123,0)
        return result
    curves,meta = ag.axis_curves(source,1,np.array([[255,255,0]]*4,np.uint8),anchors=9,hot_lines=4)
    assert [255,0] in meta["line_pairs"]
    where = meta["line_pairs"].index([255,0])
    assert curves[255,where,2] == 123 and curves[254,where,2] == 0
    assert len({tuple(p) for p in meta["line_pairs"]}) == len(meta["line_pairs"])
    assert meta["hot_lines"] <= 4
