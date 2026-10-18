"""核对完整照片频数合并后，各测度均值和重复键质量保持。"""
import json
import numpy as np
from run_joint_grid_study import merge_frequency_mass

frequency = np.zeros(17,np.uint32)
frequency[[3,8,15]] = [4,2,7]
boundary = np.array([0,0,5,16],np.int64)
hotspots = np.array([3,8,8,16],np.int64)
allocation = {'cube':.48,'photos':.48,'boundary':.02,'hotspots':.02}
mass = merge_frequency_mass(frequency,boundary,hotspots,allocation)
loss = np.sqrt(np.arange(17,dtype=float)+1)
independent = (.48*loss.mean()+.48*float(frequency@loss)/int(frequency.sum())
    +.02*loss[boundary].mean()+.02*loss[hotspots].mean())
error = abs(float(mass@loss)-independent)
if abs(mass.sum()-1)>1e-14 or error>1e-14 or np.any(mass<0):
    raise AssertionError('完整照片颜色质量合并改变测度目标')
print(json.dumps({'contracts':1,'status':'通过','objective_error':error,'total_mass':float(mass.sum()),
    'scope':'小型重复键/混合测度数学合同，不代替照片或模型精度验收'},ensure_ascii=False))
