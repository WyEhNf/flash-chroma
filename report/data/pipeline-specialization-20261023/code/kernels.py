"""原动态、只展开调用、外提数组视图三方对照；数学不变。"""
import numpy as np
from numba import njit,prange
from lutlab import study_kernels

@njit(cache=True,parallel=True)
def mixed(rgb,nodes,indices,fractions,m,kinds):
    out=np.empty_like(rgb)
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        for stage in range(4):
            v=study_kernels.pixel(nodes[stage],indices[stage],fractions[stage],m,r,g,b,kinds[stage])
            r=min(255,max(0,int(np.floor(v[0]+.5))))
            g=min(255,max(0,int(np.floor(v[1]+.5))))
            b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out

@njit(cache=True,parallel=True)
def dispatch_0000(rgb,nodes,indices,fractions,m):
    out=np.empty_like(rgb)
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        v=study_kernels.pixel(nodes[0],indices[0],fractions[0],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[1],indices[1],fractions[1],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[2],indices[2],fractions[2],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[3],indices[3],fractions[3],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out

@njit(cache=True,parallel=True)
def fixed_0000(rgb,nodes,indices,fractions,m):
    out=np.empty_like(rgb)
    n0=nodes[0]; ix0=indices[0]; f0=fractions[0]
    n1=nodes[1]; ix1=indices[1]; f1=fractions[1]
    n2=nodes[2]; ix2=indices[2]; f2=fractions[2]
    n3=nodes[3]; ix3=indices[3]; f3=fractions[3]
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        v=study_kernels.pixel(n0,ix0,f0,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n1,ix1,f1,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n2,ix2,f2,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n3,ix3,f3,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out

@njit(cache=True,parallel=True)
def dispatch_0100(rgb,nodes,indices,fractions,m):
    out=np.empty_like(rgb)
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        v=study_kernels.pixel(nodes[0],indices[0],fractions[0],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[1],indices[1],fractions[1],m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[2],indices[2],fractions[2],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[3],indices[3],fractions[3],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out

@njit(cache=True,parallel=True)
def fixed_0100(rgb,nodes,indices,fractions,m):
    out=np.empty_like(rgb)
    n0=nodes[0]; ix0=indices[0]; f0=fractions[0]
    n1=nodes[1]; ix1=indices[1]; f1=fractions[1]
    n2=nodes[2]; ix2=indices[2]; f2=fractions[2]
    n3=nodes[3]; ix3=indices[3]; f3=fractions[3]
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        v=study_kernels.pixel(n0,ix0,f0,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n1,ix1,f1,m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n2,ix2,f2,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n3,ix3,f3,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out

@njit(cache=True,parallel=True)
def dispatch_0101(rgb,nodes,indices,fractions,m):
    out=np.empty_like(rgb)
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        v=study_kernels.pixel(nodes[0],indices[0],fractions[0],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[1],indices[1],fractions[1],m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[2],indices[2],fractions[2],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[3],indices[3],fractions[3],m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out

@njit(cache=True,parallel=True)
def fixed_0101(rgb,nodes,indices,fractions,m):
    out=np.empty_like(rgb)
    n0=nodes[0]; ix0=indices[0]; f0=fractions[0]
    n1=nodes[1]; ix1=indices[1]; f1=fractions[1]
    n2=nodes[2]; ix2=indices[2]; f2=fractions[2]
    n3=nodes[3]; ix3=indices[3]; f3=fractions[3]
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        v=study_kernels.pixel(n0,ix0,f0,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n1,ix1,f1,m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n2,ix2,f2,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n3,ix3,f3,m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out

@njit(cache=True,parallel=True)
def dispatch_1100(rgb,nodes,indices,fractions,m):
    out=np.empty_like(rgb)
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        v=study_kernels.pixel(nodes[0],indices[0],fractions[0],m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[1],indices[1],fractions[1],m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[2],indices[2],fractions[2],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(nodes[3],indices[3],fractions[3],m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out

@njit(cache=True,parallel=True)
def fixed_1100(rgb,nodes,indices,fractions,m):
    out=np.empty_like(rgb)
    n0=nodes[0]; ix0=indices[0]; f0=fractions[0]
    n1=nodes[1]; ix1=indices[1]; f1=fractions[1]
    n2=nodes[2]; ix2=indices[2]; f2=fractions[2]
    n3=nodes[3]; ix3=indices[3]; f3=fractions[3]
    for i in prange(len(rgb)):
        r,g,b=int(rgb[i,0]),int(rgb[i,1]),int(rgb[i,2])
        v=study_kernels.pixel(n0,ix0,f0,m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n1,ix1,f1,m,r,g,b,1)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n2,ix2,f2,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        v=study_kernels.pixel(n3,ix3,f3,m,r,g,b,0)
        r=min(255,max(0,int(np.floor(v[0]+.5))))
        g=min(255,max(0,int(np.floor(v[1]+.5))))
        b=min(255,max(0,int(np.floor(v[2]+.5))))
        out[i,0],out[i,1],out[i,2]=r,g,b
    return out

