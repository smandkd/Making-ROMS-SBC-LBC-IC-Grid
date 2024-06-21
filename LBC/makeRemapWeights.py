# ====================================================
# 이 파이썬 파일은 Terminal 창에서 실행하는걸 추천 
# ====================================================
#%%
import matplotlib.pyplot as plt

import os, sys, subprocess
from datetime import datetime

import numpy as np
from netCDF4 import Dataset, num2date, date2num

import pyroms
import pyroms_toolbox

# load local tools
sys.path.append(os.path.abspath('../Tools/'))
from getGridHYCOM import getGridHYCOM
# %%
expname = 'Soulik'; version = 'v2'

# 격자 정보를 얻기 위한 샘플(시작) 날짜 설정
date_beg = datetime(2018,8,21,0) # year, month, day, hour
ymdh_beg = date_beg.strftime('%Y-%m-%dT%H:%M:%SZ')

src_name = 'HYCOM'
dst_name = expname # Note) must be same name in gridid.txt
hycom_file_path = f"/home/tkdals/pyroms2/LBC/HYCOM/HYCOM4{expname}_ts3z_{ymdh_beg}.nc4"

src_grd = getGridHYCOM(hycom_file_path, 'water_temp', name=src_name)
if src_grd is None:
    raise SystemExit("Could not load HYCOM grid. Exiting.")

os.environ['PYROMS_GRIDID_FILE'] = './gridid.txt'
dst_grd = pyroms.grid.get_ROMS_grid(dst_name.upper())

print(f"Source Grid: {src_grd}")
print(f"Destination Grid: {dst_grd}")
# %%
print("==>Info: creating remap_grid_HYCOM_t.nc")
pyroms_toolbox.Grid_HYCOM.make_remap_grid_file(src_grd)

print("==>Info: creating remap_grid_Soulik_rho.nc")
pyroms.remapping.make_remap_grid_file(dst_grd, Cpos='rho')

print("==>Info: creating remap_grid_Soulik_u.nc")
pyroms.remapping.make_remap_grid_file(dst_grd, Cpos='u')

print("==>Info: creating remap_grid_Soulik_v.nc")
pyroms.remapping.make_remap_grid_file(dst_grd, Cpos='v')
# %%
print(dst_grd)
#%%
# %%
# compute remap weights
# input namelist variables for bilinear remapping at rho points
grid1_file = 'remap_grid_%s_t.nc'%src_name
grid2_file = 'remap_grid_%s_rho.nc'%dst_name
interp_file1 = 'remap_weights_' + src_name + '_to_' + dst_name + '_bilinear_t_to_rho.nc'
interp_file2 = 'remap_weights_' + dst_name + '_to_' + src_name + '_bilinear_rho_to_t.nc'
map1_name = src_name + ' to ' + dst_name + ' Bilinear Mapping' # or 'Distance weighted avg of nearest neighbors'
map2_name = dst_name + ' to ' + src_name + ' Bilinear Mapping' # or 'Distance weighted avg of nearest neighbors'
num_maps = 1 # = 2 if grid1 -> grid2 and grid2 -> grid1
map_method = 'bilinear' # or 'distwgt'

pyroms.remapping.compute_remap_weights(grid1_file, grid2_file, \
                                       interp_file1, interp_file2, map1_name, \
                                       map2_name, num_maps, map_method)
print("==>Info: creating %s & %s"%(interp_file1,interp_file2))
# %%
# compute remap weights
# input namelist variables for bilinear remapping at rho points
grid1_file = 'remap_grid_%s_t.nc'%src_name
grid2_file = 'remap_grid_%s_rho.nc'%dst_name
interp_file1 = 'remap_weights_' + src_name + '_to_' + dst_name + '_bilinear_t_to_rho.nc'
interp_file2 = 'remap_weights_' + dst_name + '_to_' + src_name + '_bilinear_rho_to_t.nc'
map1_name = src_name + ' to ' + dst_name + ' Bilinear Mapping' # or 'Distance weighted avg of nearest neighbors'
map2_name = dst_name + ' to ' + src_name + ' Bilinear Mapping' # or 'Distance weighted avg of nearest neighbors'
num_maps = 1 # = 2 if grid1 -> grid2 and grid2 -> grid1
map_method = 'bilinear' # or 'distwgt'

pyroms.remapping.compute_remap_weights(grid1_file, grid2_file, \
                                       interp_file1, interp_file2, map1_name, \
                                       map2_name, num_maps, map_method)
print("==>Info: creating %s & %s"%(interp_file1,interp_file2))
# compute remap weights
# input namelist variables for bilinear remapping at rho points
grid1_file = 'remap_grid_' + src_name + '_t.nc'
grid2_file = 'remap_grid_' + dst_name + '_u.nc'
interp_file1 = 'remap_weights_' + src_name + '_to_' + dst_name + '_bilinear_t_to_u.nc'
interp_file2 = 'remap_weights_' + dst_name + '_to_' + src_name + '_bilinear_u_to_t.nc'
map1_name = src_name + ' to ' + dst_name + ' Bilinear Mapping' # or 'Distance weighted avg of nearest neighbors'
map2_name = dst_name + ' to ' + src_name + ' Bilinear Mapping' # or 'Distance weighted avg of nearest neighbors'
num_maps = 1 # = 2 if grid1 -> grid2 and grid2 -> grid1
map_method = 'bilinear' # or 'distwgt'

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
map1_name = src_name + ' to ' + dst_name + ' Bilinear Mapping' # or 'Distance weighted avg of nearest neighbors'
map2_name = dst_name + ' to ' + src_name + ' Bilinear Mapping' # or 'Distance weighted avg of nearest neighbors'
num_maps = 1 # = 2 if grid1 -> grid2 and grid2 -> grid1
map_method = 'bilinear' # or 'distwgt'

pyroms.remapping.compute_remap_weights(grid1_file, grid2_file, \
                                       interp_file1, interp_file2, map1_name, \
                                       map2_name, num_maps, map_method)
print("==>Info: creating %s & %s"%(interp_file1,interp_file2))