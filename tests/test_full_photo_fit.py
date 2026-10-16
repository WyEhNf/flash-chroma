"""测度标度、整数分量比较及无先验箱约束的独立合同。"""
import itertools
import numpy as np
import scipy.sparse as sp
from lutlab import full_photo_fit as fpf, io, interp


def fixture():
    rng = np.random.default_rng(2026101751)
    model = io.SparseLut(io.uniform_grid(2),rng.integers(0,256,(2,2,2,3),dtype=np.uint8))
    full = np.array(list(itertools.product((0,255),repeat=3)),np.uint8)
    target = rng.integers(0,256,(8,3),dtype=np.uint8)
    points = np.array([[0,0,0],[37,89,123],[37,89,123],[255,0,255]],np.uint8)
    labels = rng.integers(0,256,points.shape,dtype=np.uint8)
    return model,full,target,points,labels


def test_photo_integer_moments_and_equal_mass_match_dense_weighted_problem():
    model,full,target,points,labels = fixture()
    H,b = sp.eye(8,format="csr")/64,target.astype(float)/64
    Hq,bq = fpf.photo_moments(model,points,labels)
    # 独立逐行散加，包含重复像素、非均匀分数及零权重。
    dense = np.zeros((len(points),8),np.int64)
    indices,weights = interp.tetra_index_weights_q(points,*model.tables(),2)
    for r in range(len(points)):
        for j,w in zip(indices[r],weights[r]):dense[r,int(j)] += int(w)
    assert np.array_equal(Hq.toarray(),dense.T @ dense)
    assert np.array_equal(bq,dense.T @ labels.astype(np.int64))
    mix,rhs,mass = fpf.equal_mass_system(H,b,Hq,bq,8,len(points))
    scale = mass["full_mass"]
    expected = scale*(np.eye(8)/8+(dense/65536).T @ (dense/65536)/len(points))
    linear = scale*(target/8+(dense/65536).T @ labels/len(points))
    np.testing.assert_allclose(mix.toarray(),expected,rtol=0,atol=1e-14)
    np.testing.assert_allclose(rhs,linear,rtol=0,atol=1e-12)
    assert mass["full_mass"] == mass["photo_mass"]
    twice,twice_rhs,_ = fpf.equal_mass_system(H,b,*fpf.photo_moments(model,np.tile(points,(2,1)),np.tile(labels,(2,1))),8,2*len(points))
    np.testing.assert_allclose(twice.toarray()/twice.sum(),mix.toarray()/mix.sum(),atol=1e-15)
    np.testing.assert_allclose(twice_rhs/twice.sum(),rhs/mix.sum(),atol=1e-12)


def test_exact_mixed_change_matches_independent_integer_accumulators():
    model,full,target,points,labels = fixture()
    H,b = sp.eye(8,format="csr")/64,target.astype(float)/64
    Hq,bq = fpf.photo_moments(model,points,labels)
    old = model.nodes.reshape(-1,3)
    new = np.flip(old,axis=0).copy()
    def total(nodes,rgb,y):
        indices,weights = interp.tetra_index_weights_q(rgb,*model.tables(),2)
        return sum((sum(int(w)*int(nodes[j,c]) for j,w in zip(indices[r],weights[r]))-65536*int(y[r,c]))**2
                   for r in range(len(rgb)) for c in range(3))
    full_delta = total(new,full,target)-total(old,full,target)
    photo_delta = total(new,points,labels)-total(old,points,labels)
    result = fpf.exact_change(H,b,Hq,bq,old,new,8,len(points))
    assert int(result["full_sse_change_numerator"]) == full_delta
    assert int(result["photo_sse_change_numerator"]) == photo_delta
    assert int(result["equal_mass_change_numerator"]) == len(points)*full_delta+8*photo_delta
    reverse = fpf.exact_change(H,b,Hq,bq,new,old,8,len(points))
    assert int(reverse["equal_mass_change_numerator"]) == -int(result["equal_mass_change_numerator"])


def test_equal_mass_box_matches_diagonal_closed_form_and_preserves_model():
    model,_,target,_,_ = fixture()
    before = model.nodes.copy()
    points = np.zeros((4,3),np.uint8)
    H,b = sp.eye(8,format="csr")/64,target.astype(float)/64
    report = {}
    result = fpf.fit_equal_mass(lambda rgb:np.full_like(rgb,255),model,points,H,b,full_count=8,diagnostics=report)
    expected = target.astype(float)
    expected[0] = (target[0]/8+255)/(1/8+1)
    expected = np.rint(expected).astype(np.uint8)
    assert np.array_equal(result.nodes.reshape(-1,3),expected)
    assert np.array_equal(model.nodes,before)
    assert report["solver"]["feasible"] and report["accepted"] and report["lambda_prior"] == 0
    assert all(np.array_equal(a,b) for a,b in zip(result.tables(),model.tables()))
