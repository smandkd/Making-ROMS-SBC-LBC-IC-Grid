#%%
# Author: Dong-Hoon Kim (http://www.dhkim.info)
import matplotlib.pyplot as plt

import os, sys, subprocess
from datetime import datetime, timedelta

import numpy as np
from netCDF4 import Dataset #, num2date, date2num

import pyroms
import pyroms_toolbox
import glob
# load local tools
sys.path.append(os.path.abspath('../Tools/'))
from getGridHYCOM import getGridHYCOM
from remapBC import remapBC
from remapBCuv import remapBCuv
#%%
# 실험명
expname = 'Soulik'; version = 'v4'

# 경계장 날짜 설정
date_beg = datetime(2018,8,21,0) # year, month, day, hour
date_end = datetime(2018,8,25,0) # year, month, day, hour
ymdh_beg = date_beg.strftime('%Y-%m-%dT%H:%M:%SZ')
ymdh_end = date_end.strftime('%Y-%m-%dT%H:%M:%SZ')

strideTime  = 1 # time resolution. ex) every 3hours * 1 = 3hours

src_name = 'HYCOM'
dst_name = expname # Note) must be same name in gridid.txt

src_grd = getGridHYCOM("/home/tkdals/pyroms2/LBC/HYCOM/HYCOM4%s_ts3z_%s.nc4"%(expname,ymdh_beg),'water_temp',name=src_name)

os.environ['PYROMS_GRIDID_FILE'] = './gridid.txt'
dst_grd = pyroms.grid.get_ROMS_grid(dst_name.upper())

# make a direcotory for saving remapped ROMS files
if not os.path.isdir('ROMS'): os.makedirs('ROMS')

# remap weights file
wts_file = 'remap_weights_%s_to_%s_bilinear_t_to_rho.nc'%(src_name,dst_name)
# %%
dt = date_beg
while(dt <= date_end):
    ymdh = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    hycom_file = '/home/tkdals/pyroms2/LBC/HYCOM/HYCOM4Soulik_ssh_%s.nc4'%ymdh
    roms_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_ssh_%s.nc4'%(dst_name,ymdh)
    zeta = remapBC(hycom_file,'surf_el', wts_file, src_grd, dst_grd, roms_file)

    dt += timedelta(hours=3*strideTime)

# ---
dst_grd3z = pyroms.grid.get_ROMS_grid(dst_name.upper(), zeta=zeta)
# ---

with Dataset(roms_file,'r') as ncout:
    fig = plt.figure(figsize=(15,3))
    ax1 = fig.add_subplot(1,4,1); ax2 = fig.add_subplot(1,4,2)
    ax3 = fig.add_subplot(1,4,3); ax4 = fig.add_subplot(1,4,4)
    _=ax1.plot(ncout['zeta_south'][0,:]); _=ax2.plot(ncout['zeta_north'][0,:])
    _=ax3.plot(ncout['zeta_west'][0,:]);  _=ax4.plot(ncout['zeta_east'][0,:])
# %%
dt = date_beg
while(dt <= date_end):
    ymdh = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    hycom_file = '/home/tkdals/pyroms2/LBC/HYCOM/HYCOM4Soulik_ts3z_%s.nc4'%ymdh
    roms_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_temp_%s.nc4'%(dst_name,ymdh)
    remapBC(hycom_file,'water_temp', wts_file, src_grd, dst_grd3z, roms_file)
    
    dt += timedelta(hours=3*strideTime)

with Dataset(roms_file,'r') as ncout:
    fig = plt.figure(figsize=(15,6))
    ax1 = fig.add_subplot(2,4,1); ax2 = fig.add_subplot(2,4,2)
    ax3 = fig.add_subplot(2,4,3); ax4 = fig.add_subplot(2,4,4)
    _=ax1.plot(ncout['temp_south'][0,-1,:]); _=ax2.plot(ncout['temp_north'][0,-1,:])
    _=ax3.plot(ncout['temp_west'][0,-1,:]);  _=ax4.plot(ncout['temp_east'][0,-1,:])
    ax5 = fig.add_subplot(2,4,5); ax6 = fig.add_subplot(2,4,6)
    ax7 = fig.add_subplot(2,4,7); ax8 = fig.add_subplot(2,4,8)
    _=ax5.imshow(ncout['temp_south'][0,:,:]); _=ax6.imshow(ncout['temp_north'][0,:,:])
    _=ax7.imshow(ncout['temp_west'][0,:,:]);  _=ax8.imshow(ncout['temp_east'][0,:,:])
# %%
dt = date_beg
while(dt <= date_end):
    ymdh = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    hycom_file = '/home/tkdals/pyroms2/LBC/HYCOM/HYCOM4Soulik_ts3z_%s.nc4'%ymdh
    roms_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_salt_%s.nc4'%(dst_name,ymdh)
    remapBC(hycom_file,'salinity', wts_file, src_grd, dst_grd3z, roms_file)
    
    dt += timedelta(hours=3*strideTime)

with Dataset(roms_file,'r') as ncout:
    fig = plt.figure(figsize=(15,6))
    ax1 = fig.add_subplot(2,4,1); ax2 = fig.add_subplot(2,4,2)
    ax3 = fig.add_subplot(2,4,3); ax4 = fig.add_subplot(2,4,4)
    _=ax1.plot(ncout['salt_south'][0,-1,:]); _=ax2.plot(ncout['salt_north'][0,-1,:])
    _=ax3.plot(ncout['salt_west'][0,-1,:]);  _=ax4.plot(ncout['salt_east'][0,-1,:])
    ax5 = fig.add_subplot(2,4,5); ax6 = fig.add_subplot(2,4,6)
    ax7 = fig.add_subplot(2,4,7); ax8 = fig.add_subplot(2,4,8)
    _=ax5.imshow(ncout['salt_south'][0,:,:]); _=ax6.imshow(ncout['salt_north'][0,:,:])
    _=ax7.imshow(ncout['salt_west'][0,:,:]);  _=ax8.imshow(ncout['salt_east'][0,:,:])

# %%
dt = date_beg
while(dt <= date_end):
    ymdh = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    hycom_fileuv = '/home/tkdals/pyroms2/LBC/HYCOM/HYCOM4Soulik_uv3z_%s.nc4'%ymdh
    roms_fileuv = ['/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_u_%s.nc4'%(dst_name,ymdh),
                   '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_v_%s.nc4'%(dst_name,ymdh)]
    remapBCuv(hycom_fileuv,['water_u','water_v'], wts_file, src_grd, dst_grd3z, roms_fileuv)
    
    dt += timedelta(hours=3*strideTime)
#%%
with Dataset(roms_fileuv[0],'r') as ncout:
    fig = plt.figure(figsize=(15,6))
    ax1 = fig.add_subplot(2,4,1); ax2 = fig.add_subplot(2,4,2)
    ax3 = fig.add_subplot(2,4,3); ax4 = fig.add_subplot(2,4,4)
    _=ax1.plot(ncout['u_south'][0,-1,:]); _=ax2.plot(ncout['u_north'][0,-1,:])
    _=ax3.plot(ncout['u_west'][0,-1,:]);  _=ax4.plot(ncout['u_east'][0,-1,:])
    ax5 = fig.add_subplot(2,4,5); ax6 = fig.add_subplot(2,4,6)
    ax7 = fig.add_subplot(2,4,7); ax8 = fig.add_subplot(2,4,8)
    _=ax5.imshow(ncout['u_south'][0,:,:]); _=ax6.imshow(ncout['u_north'][0,:,:])
    _=ax7.imshow(ncout['u_west'][0,:,:]);  _=ax8.imshow(ncout['u_east'][0,:,:])
#%%
with Dataset(roms_fileuv[1],'r') as ncout:
    fig = plt.figure(figsize=(15,6))
    ax1 = fig.add_subplot(2,4,1); ax2 = fig.add_subplot(2,4,2)
    ax3 = fig.add_subplot(2,4,3); ax4 = fig.add_subplot(2,4,4)
    _=ax1.plot(ncout['v_south'][0,-1,:]); _=ax2.plot(ncout['v_north'][0,-1,:])
    _=ax3.plot(ncout['v_west'][0,-1,:]);  _=ax4.plot(ncout['v_east'][0,-1,:])
    ax5 = fig.add_subplot(2,4,5); ax6 = fig.add_subplot(2,4,6)
    ax7 = fig.add_subplot(2,4,7); ax8 = fig.add_subplot(2,4,8)
    _=ax5.imshow(ncout['v_south'][0,:,:]); _=ax6.imshow(ncout['v_north'][0,:,:])
    _=ax7.imshow(ncout['v_west'][0,:,:]);  _=ax8.imshow(ncout['v_east'][0,:,:])

#%%
# merge file
bc_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_bc.nc'%expname
if os.path.isfile(bc_file): os.remove(bc_file)

in_files = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_ssh_*.nc4'%expname; merge_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_ssh_bc.nc'%expname
subprocess.call('ncrcat %s %s'%(in_files,bc_file), shell=True)

in_files = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_temp_*.nc4'%expname; merge_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_temp_bc.nc'%expname
if os.path.isfile(merge_file): os.remove(merge_file)
subprocess.call('ncrcat %s %s'%(in_files,merge_file), shell=True)
subprocess.call('ncks -a -A %s %s'%(merge_file,bc_file), shell=True)

in_files = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_salt_*.nc4'%expname; merge_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_salt_bc.nc'%expname
if os.path.isfile(merge_file): os.remove(merge_file)
subprocess.call('ncrcat %s %s'%(in_files,merge_file), shell=True)
subprocess.call('ncks -a -A %s %s'%(merge_file,bc_file), shell=True)

in_files = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_u_*.nc4'%expname; merge_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_u_bc.nc'%expname
if os.path.isfile(merge_file): os.remove(merge_file)
subprocess.call('ncrcat %s %s'%(in_files,merge_file), shell=True)
subprocess.call('ncks -a -A %s %s'%(merge_file,bc_file), shell=True)

in_files = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_v_*.nc4'%expname; merge_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4%s_v_bc.nc'%expname
if os.path.isfile(merge_file): os.remove(merge_file)
subprocess.call('ncrcat %s %s'%(in_files,merge_file), shell=True)
subprocess.call('ncks -a -A %s %s'%(merge_file,bc_file), shell=True)

print('==>Info: Creating final BC - %s'%bc_file)

#%%
bc_file = '/home/tkdals/pyroms2/LBC/ROMS/ROMS4Soulik_bc.nc'
fig = plt.figure(figsize=(12,2))
axE = fig.add_subplot(2,3,1); axT = fig.add_subplot(2,3,2); axS = fig.add_subplot(2,3,3)
axU = fig.add_subplot(2,3,5); axV = fig.add_subplot(2,3,6)

with Dataset('/home/tkdals/pyroms2/LBC/ROMS/ROMS4Soulik_bc.nc') as ncIC:
    _=axE.imshow(ncIC['zeta_south'][:,:])
    _=axT.imshow(ncIC['temp_south'][-1,:,:])
    _=axS.imshow(ncIC['salt_south'][-1,:,:])
    _=axU.imshow(ncIC['u_south'][-1,:,:])
    _=axV.imshow(ncIC['v_south'][-1,:,:])
#%%
fig = plt.figure(figsize=(12,2))
axE = fig.add_subplot(2,3,1); axT = fig.add_subplot(2,3,2); axS = fig.add_subplot(2,3,3)
axU = fig.add_subplot(2,3,5); axV = fig.add_subplot(2,3,6)

with Dataset(bc_file) as ncIC:
    _=axE.imshow(ncIC['zeta_north'][:,:])
    _=axT.imshow(ncIC['temp_north'][-1,:,:])
    _=axS.imshow(ncIC['salt_north'][-1,:,:])
    _=axU.imshow(ncIC['u_north'][-1,:,:])
    _=axV.imshow(ncIC['v_north'][-1,:,:])
# %%
# %%
