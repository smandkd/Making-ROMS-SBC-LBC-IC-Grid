# ============================================
# 터미널 창에서 실행하는 걸 추천. 
# 주피터에서 실행하면 느려터짐
# ============================================
#%%
import matplotlib.pyplot as plt

import os, sys, subprocess
from datetime import datetime

import numpy as np
from netCDF4 import Dataset, num2date, date2num

import pyroms
import pyroms_toolbox

# load local tools
sys.path.append(os.path.abspath('/home/tkdals/pyroms/Tools/'))
from getGridHYCOM import getGridHYCOM
from remapIC import remapIC
from remapICuv import remapICuv
#%%
# 실험명
expname = 'Soulik'; version = 'v2'

# 초기장 날짜 설정
#date_init = datetime(2018,8,18,12) # year, month, day, hour
date_init = datetime(2018,8,21,0) # year, month, day, hour
ymdh_init = date_init.strftime('%Y-%m-%dT%H:%M:%SZ')

src_name = 'HYCOM'
dst_name = expname # Note) must be same name in gridid.txt

#version = 'GLBv0.08'; expt = 'expt_93.0'
src_grd = getGridHYCOM("./HYCOM4%s_ts3z_%s.nc4"%(expname,ymdh_init),'water_temp',name=src_name)

os.environ['PYROMS_GRIDID_FILE'] = './gridid.txt'
dst_grd = pyroms.grid.get_ROMS_grid(dst_name.upper()) # SOULIKv4
# dst_grd = pyroms.grid.get_ROMS_grid(dst_name.upper()+version) # SOULIKv4
# 원래는 위의 코든데 이상하게 get_ROMS_grid 에서는 SOULIK 을 원함. 그래서 version 빼고 작성

print("==>Info: creating remap_grid_HYCOM_t.nc")
pyroms_toolbox.Grid_HYCOM.make_remap_grid_file(src_grd)

print("==>Info: creating remap_grid_Soulik_rho.nc")
pyroms.remapping.make_remap_grid_file(dst_grd, Cpos='rho')

print("==>Info: creating remap_grid_Soulik_u.nc")
pyroms.remapping.make_remap_grid_file(dst_grd, Cpos='u')

print("==>Info: creating remap_grid_Soulik_v.nc")
pyroms.remapping.make_remap_grid_file(dst_grd, Cpos='v')
#%%
# compute remap weights
# input namelist variables for bilinear remapping at rho points
grid1_file = 'remap_grid_%s_t.nc'%src_name
grid2_file = 'remap_grid_%s_rho.nc'%dst_name
interp_file1 = 'remap_weights_' + src_name + '_to_' + dst_name + '_bilinear_t_to_rho.nc'
interp_file2 = 'remap_weights_' + dst_name + '_to_' + src_name + '_bilinear_rho_to_t.nc'
map1_name = src_name + ' to ' + dst_name + ' Bilinear Mapping'
map2_name = dst_name + ' to ' + src_name + ' Bilinear Mapping'
num_maps = 1 # = 2 if grid1 -> grid2 and grid2 -> grid1
map_method = 'bilinear'

pyroms.remapping.compute_remap_weights(grid1_file, grid2_file, \
                                       interp_file1, interp_file2, map1_name, \
                                       map2_name, num_maps, map_method, \
                                           grid1_periodic='.true.', grid2_periodic='.true.')

print("==>Info: creating %s & %s"%(interp_file1,interp_file2))
# compute remap weights
# input namelist variables for bilinear remapping at rho points
grid1_file = 'remap_grid_' + src_name + '_t.nc'
grid2_file = 'remap_grid_' + dst_name + '_u.nc'
interp_file1 = 'remap_weights_' + src_name + '_to_' + dst_name + '_bilinear_t_to_u.nc'
interp_file2 = 'remap_weights_' + dst_name + '_to_' + src_name + '_bilinear_u_to_t.nc'
map1_name = src_name + ' to ' + dst_name + ' Bilinear Mapping'
map2_name = dst_name + ' to ' + src_name + ' Bilinear Mapping'
num_maps = 1; map_method = 'bilinear'

pyroms.remapping.compute_remap_weights(grid1_file, grid2_file, \
                                       interp_file1, interp_file2, map1_name, \
                                       map2_name, num_maps, map_method)
print("==>Info: creating %s & %s"%(interp_file1,interp_file2))
# compute remap weights
# input namelist variables for bilinear remapping at rho points
grid1_file = 'remap_grid_' + src_name + '_t.nc'
grid2_file = 'remap_grid_' + dst_name + '_v.nc'
interp_file1 = 'remap_weights_' + src_name + '_to_' + dst_name + '_bilinear_t_to_v.nc'
interp_file2 = 'remap_weights_' + dst_name + '_to_' + src_name + '_bilinear_v_to_t.nc'
map1_name = src_name + ' to ' + dst_name + ' Bilinear Mapping'
map2_name = dst_name + ' to ' + src_name + ' Bilinear Mapping'
num_maps = 1; map_method = 'bilinear'

pyroms.remapping.compute_remap_weights(grid1_file, grid2_file, \
                                       interp_file1, interp_file2, map1_name, \
                                       map2_name, num_maps, map_method)
print("==>Info: creating %s & %s"%(interp_file1,interp_file2))
hycom_file = 'HYCOM4Soulik_ssh_%s.nc4'%ymdh_init
roms_file = 'ROMS4%s_ssh_%s.nc4'%(dst_name,ymdh_init)
wts_file = 'remap_weights_%s_to_%s_bilinear_t_to_rho.nc'%(src_name,dst_name)
zeta = remapIC(hycom_file,'surf_el', wts_file, src_grd, dst_grd, roms_file)

# dst_grd for 3D variables
dst_grd3z = pyroms.grid.get_ROMS_grid(dst_name.upper(), zeta=zeta)

with Dataset(roms_file,'r') as ncout:
    _=plt.imshow(ncout['zeta'][0,::-1,:])
#%%
hycom_file = 'HYCOM4Soulik_ts3z_%s.nc4'%ymdh_init
roms_file = 'ROMS4%s_temp_%s.nc4'%(dst_name,ymdh_init)
wts_file = 'remap_weights_%s_to_%s_bilinear_t_to_rho.nc'%(src_name,dst_name)
remapIC(hycom_file,'water_temp', wts_file, src_grd, dst_grd3z, roms_file)

with Dataset(roms_file,'r') as ncout:
    _=plt.imshow(ncout['temp'][0,-1,::-1,:])
# %%
hycom_file = 'HYCOM4Soulik_ts3z_%s.nc4'%ymdh_init
roms_file = 'ROMS4%s_salt_%s.nc4'%(dst_name,ymdh_init)
wts_file = 'remap_weights_%s_to_%s_bilinear_t_to_rho.nc'%(src_name,dst_name)
remapIC(hycom_file,'salinity', wts_file, src_grd, dst_grd3z, roms_file)

with Dataset(roms_file,'r') as ncout:
    _=plt.imshow(ncout['salt'][0,-1,::-1,:])
#%%
hycom_fileuv = 'HYCOM4Soulik_uv3z_%s.nc4'%ymdh_init
roms_fileuv = ['ROMS4%s_u_%s.nc4'%(dst_name,ymdh_init),
               'ROMS4%s_v_%s.nc4'%(dst_name,ymdh_init)]
wts_file = 'remap_weights_%s_to_%s_bilinear_t_to_rho.nc'%(src_name,dst_name)
remapICuv(hycom_fileuv, ['water_u','water_v'], wts_file, src_grd, dst_grd3z, roms_fileuv)

fig = plt.figure(figsize=(10,3))
ax1 = fig.add_subplot(1,2,1); ax2 = fig.add_subplot(1,2,2)
with Dataset(roms_fileuv[0]) as ncu, Dataset(roms_fileuv[1]) as ncv:
    _=ax1.imshow(ncu['u'][0,-1,::-1,:]); _=ax2.imshow(ncv['v'][0,-1,::-1,:])
#%%
# merge file
ic_file = './ROMS4%s_ic_%s.nc4'%(dst_name,ymdh_init)
if os.path.isfile(ic_file) : os.remove(ic_file)

out_file = './ROMS4%s_ssh_%s.nc4'%(dst_name,ymdh_init)
command = ('ncks', '-a', '-O', out_file, ic_file); print(command)
subprocess.check_call(command)
#os.remove(out_file)

out_file = './ROMS4%s_temp_%s.nc4'%(dst_name,ymdh_init)
command = ('ncks', '-a', '-A', out_file, ic_file); print(command)
subprocess.check_call(command)
#os.remove(out_file)

out_file = './ROMS4%s_salt_%s.nc4'%(dst_name,ymdh_init)
command = ('ncks', '-a', '-A', out_file, ic_file); print(command)
subprocess.check_call(command)
#os.remove(out_file)

out_file = './ROMS4%s_u_%s.nc4'%(dst_name,ymdh_init)
command = ('ncks', '-a', '-A', out_file, ic_file); print(command)
subprocess.check_call(command)
#os.remove(out_file)

out_file = './ROMS4%s_v_%s.nc4'%(dst_name,ymdh_init)
command = ('ncks', '-a', '-A', out_file, ic_file); print(command)
subprocess.check_call(command)
#os.remove(out_file)
#%%
print('==>Info: Creating final IC - %s'%ic_file)
fig = plt.figure(figsize=(12,8))
axE = fig.add_subplot(2,3,1); axT = fig.add_subplot(2,3,2); axS = fig.add_subplot(2,3,3)
axU = fig.add_subplot(2,3,5); axV = fig.add_subplot(2,3,6)

with Dataset(ic_file) as ncIC:
    _=axE.imshow(ncIC['zeta'][0,::-1,:])
    _=axT.imshow(ncIC['temp'][0,-1,::-1,:])
    _=axS.imshow(ncIC['salt'][0,-1,::-1,:])
    _=axU.imshow(ncIC['u'][0,-1,::-1,:])
    _=axV.imshow(ncIC['v'][0,-1,::-1,:])