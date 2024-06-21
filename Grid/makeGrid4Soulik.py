#%% 
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
#from matplotlib.mlab import griddata
from scipy.interpolate import griddata

import matplotlib.colors as colors
# from scipy.signal import medfilt2d
import netCDF4

import pyroms
import pyroms_toolbox
from bathy_smoother import *
# %%
Lm = 430
Mm = 320

# 위경도 영역 지정
lon0 = 117.; lat0 = 52. # 영역의 왼쪽 위
lon1 = 117.; lat1 = 20. # 영역의 왼쪽 아래
lon2 = 160.; lat2 = 20. # 영역의 오른쪽 아래
lon3 = 160.; lat3 = 52. # 영역의 오른쪽 위
centerLonLat     = [126.564, 33.457] # 영역의 중심 경위도 (투영법에서 참조하는 중심 위치임)
trueLatLowerUpper= [ 30., 40.] # 지도투영에 의해 발생하는 위도 왜곡에서 지표면과 교차되는 아랫지점과 윗지점

M = Basemap(projection='lcc', lat_0=centerLonLat[1], lon_0=centerLonLat[0], \
            lat_1=trueLatLowerUpper[0], lat_2=trueLatLowerUpper[1], \
            resolution='i',width=7000000,height=5500000) # set width & height widely just to check
            #llcrnrlon=lon1,llcrnrlat=lat1,urcrnrlon=lon3,urcrnrlat=lat3, resolution='i')
# M.latmin; M.lonmin; M.latmax; M.lonmax

lonp = np.array([lon0,lon1,lon2,lon3])
latp = np.array([lat0,lat1,lat2,lat3])
beta = np.array([1, 1, 1, 1])

## 격자의 모서리를 수정하지 않고 주어진 값으로 수평 격자를 만들 경우:
hgrd = pyroms.grid.Gridgen(lonp, latp, beta, (Mm+3, Lm+3), proj=M)

lonv, latv = list(M(hgrd.x_vert, hgrd.y_vert, inverse=True))
hgrd = pyroms.grid.CGrid_geo(lonv, latv, M)

# %matplotlib inline
#from matplotlib.patches import Polygon
_=M.drawcoastlines(); _=M.drawcountries(); _=M.drawmapboundary()
_=M.fillcontinents(color='coral',lake_color='aqua')
#x, y = M([lon0,lon1,lon2,lon3],[lat0,lat1,lat2,lat3])
#xy = list(zip(x,y))
#poly = Polygon(xy, facecolor='red', alpha=0.4)
#_=plt.gca().add_patch(poly)


x,y = M(hgrd.lon_rho.flatten(),hgrd.lat_rho.flatten())
_=M.plot(x,y,'bo',markersize=0.1)
# %%
for xx, yy in M.coastpolygons:
    xa = np.array(xx, np.float32)
    ya = np.array(yy, np.float32)
    vv = np.zeros((xa.shape[0],2))
    vv[:, 0] = xa
    vv[:, 1] = ya
    hgrd.mask_polygon(vv, mask_value=0)
# %%
coast = pyroms.utility.get_coast_from_map(M)
pyroms.grid.edit_mask_mesh_ij(hgrd, coast=coast)
# %%
datadir = os.getenv('HOME') + '/Data/Topog/ETOPO'

lats = np.loadtxt(os.path.join(datadir, 'etopo20lats.gz'))
lons = np.loadtxt(os.path.join(datadir, 'etopo20lons.gz'))

topo = np.loadtxt(os.path.join(datadir, 'etopo20data.gz'))

topo = -topo
hmin = 5
topo = np.where(topo < hmin, hmin, topo)
# %%
lon, lat = np.meshgrid(lons, lats)
points = np.array([lon.flatten(), lat.flatten()]).T
h = griddata(np.array(points), topo.flatten(), (hgrd.lon_rho, hgrd.lat_rho), method='linear')
h = np.where(h < hmin, hmin, h)
idx = np.where(hgrd.mask_rho == 0)
h[idx] = hmin

hraw = h.copy()
# %%
RoughMat = bathy_tools.RoughnessMatrix(h, hgrd.mask_rho)
print('Max Roughness value is :', RoughMat.max())

# smooth the raw bathy using the direct iterative method from Martinho and Batteen (2006)
rx0_max = 0.35
h = bathy_smoothing.smoothing_Positive_rx0(hgrd.mask_rho, h, rx0_max)
# check bathymetry roughness again

RoughMat = bathy_tools.RoughnessMatrix(h, hgrd.mask_rho)
print('Max Roughness value is :', RoughMat.max())
# %%
# vertical coordinate
theta_b = 0.1
theta_s = 7.0
Tcline = 50
N = 30
vgrd = pyroms.vgrid.s_coordinate_4(h, theta_b, theta_s, Tcline, N, hraw=hraw)
# %%
os.environ['PYROMS_GRIDID_FILE'] = './gridid.txt'

grd_name = 'Soulik'; version = 'v2'
grd = pyroms.grid.ROMS_Grid(grd_name, hgrd, vgrd)

# write grid to netcdf file
pyroms.grid.write_ROMS_grid(grd, filename='Soulik_grd_'+version+'.nc')
# %%
#!ncdump -h Soulik.nc
os.environ['PYROMS_GRIDID_FILE'] = './gridid.txt'
grd = pyroms.grid.get_ROMS_grid('SOULIK')
print(grd)

lon  = grd.hgrid.lon_rho
lat  = grd.hgrid.lat_rho
h    = grd.vgrid.h
mask = grd.hgrid.mask_rho
idx  = np.where(mask == 0)
h[idx] = 0
# %%
fig = plt.figure()
_=M.drawcoastlines()
_=M.drawcountries()

x,y = M(lon, lat)
clevs = np.arange(0,5000,100)
# cs = M.contourf(x,y,h,clevs,cmap=plt.cm.rainbow,extend='max')
cs = M.contourf(x,y,h,clevs,extend='max')
# %%
