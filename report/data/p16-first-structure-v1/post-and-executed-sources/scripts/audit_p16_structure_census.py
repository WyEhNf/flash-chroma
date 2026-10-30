"""98纯模型/地址证据离线审计：非零minor、逐字节线集合与全相位总和。"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import struct
import numpy as np


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--structure', required=True, type=Path)
    p.add_argument('--stencils', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('98独立审计不覆盖')
    read = lambda path: json.loads(path.read_text(encoding='utf-8'))
    structure, stencils = read(a.structure/'results.json'), read(a.stencils/'results.json')
    model = Path(structure['model']['path']);raw = model.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == structure['model']['sha256']
    m = struct.unpack_from('<I',raw,8)[0]
    nodes = np.frombuffer(raw,np.uint8,3*m**3,16+12*m+768+3072).reshape(m,m,m,3).astype(np.int64)
    prime = structure['rank_prime'];minor_checks = 0
    for proof in structure['spatial_rank_certificates']+[structure['centered_rgb_rank_certificate']]:
        matrix = ((nodes.reshape(-1,3)-nodes[0,0,0]).T if 'axis' not in proof else
            np.moveaxis(nodes[...,proof['channel']],proof['axis'],0).reshape(m,-1))
        minor = matrix[:,proof['pivot_columns']]
        assert minor.tolist() == proof['selected_minor_integer_entries'] and proof['full_row_rank']
        # 完全独立的Python整数行列式消元，不复用census的NumPy行运算。
        values = [[int(x)%prime for x in row] for row in minor]
        determinant = 1
        for j in range(len(values)):
            k = next(i for i in range(j,len(values)) if values[i][j])
            if j != k:
                values[j],values[k]=values[k],values[j];determinant=-determinant
            pivot=values[j][j];determinant=determinant*pivot%prime
            inverse=pow(pivot,prime-2,prime)
            for i in range(j+1,len(values)):
                factor=values[i][j]*inverse%prime
                values[i]=[(x-factor*y)%prime for x,y in zip(values[i],values[j])]
        assert determinant == proof['selected_minor_determinant_mod_prime'] and determinant
        minor_checks+=1
    models, byte_groups, phase_sums = 0,0,0
    for row in stencils['models']:
        m=row['m'];t=(m+1)//2
        lower=np.stack(np.indices((m-1,m-1,m-1),dtype=np.int64),axis=-1).reshape(-1,3)
        old,new=[],[]
        for order in itertools.permutations(range(3)):
            v=np.repeat(lower[:,None,:],4,axis=1)
            for j,axis in enumerate(order):v[:,j+1:,axis]+=1
            r,g,b=np.moveaxis(v,-1,0)
            old.append(((r*m+g)*m+b)*4)
            new.append(((((r//2)*t+g//2)*t+b//2)*8+4*(r%2)+2*(g%2)+b%2)*4)
        old,new=np.concatenate(old),np.concatenate(new)
        byte_offsets=np.arange(4,dtype=np.int64)
        def exact(offsets,base,unit):
            words=((offsets[:,:,None]+byte_offsets[None,None,:]+base)//unit).reshape(-1,16)
            return 1+(np.diff(words,axis=1)!=0).sum(axis=1)
        for entry in row['all_base_mod64']:
            x,y=exact(old,entry['base_mod64'],64),exact(new,entry['base_mod64'],64)
            assert int(x.sum())==entry['old_total_line_touches'] and int(y.sum())==entry['new_total_line_touches']
            assert [int(x.min()),int(x.max())]==entry['old_per_stencil_min_max']
            assert [int(y.min()),int(y.max())]==entry['new_per_stencil_min_max']
            assert int((y<x).sum())==entry['paired_improved'] and int((y>x).sum())==entry['paired_regressed']
            byte_groups+=2
        page=row['all_page_base_mod4096']
        for name,offsets in [('old',old),('new',new)]:
            values=page[name+'_total_touches']
            for base in (0,1,3,63,64,1023,2047,4093,4095):
                assert int(exact(offsets,base,4096).sum())==values[base];byte_groups+=1
            # 每4字节字跨界占3个相位；相邻字端点间新页占min(gap,4096)相位。
            gaps=offsets[:,1:]-(offsets[:,:-1]+3)
            expected=4096*len(offsets)+12*len(offsets)+int(np.minimum(gaps,4096).sum())
            assert sum(values)==expected;phase_sums+=1
        assert row['all_nodes_restored_uint32'] and row['all_stencil_nodes_and_unique_labels_restored']
        models+=1
    receipt={'passed':True,'exact_nonzero_minors':minor_checks,'model_sizes':models,
        'full_stencil_direct_byte_group_checks':byte_groups,'all4096_phase_sum_identities':phase_sums,
        'native_calls':0,'performance_calls':0,'scope':'非零minor另用Python整数消元；192个mod64×双布局全部stencil直接展开16字节求集合，page九相位同核并核全部4096总和。没有映射颜色输出。'}
    a.output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':
    main()
