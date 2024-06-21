# ====================================================
# https://rda.ucar.edu/datasets/ds084.1/dataaccess/
# 요 사이트에서 GFS 데이터 다운 받고 사용. 
# 
# ====================================================
#%%
import matplotlib.pyplot as plt

import os, sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import xarray as xr
from netCDF4 import Dataset
from pygrib import open as grib

#%%
expname = 'Soulik'; version = 'v2'

tleadmax = 240
dhour = 3

date_beg = datetime(2018,8,21,0)
date_end = datetime(2018,8,25,0)

# ROMS 격자 정보 가져오기warning
roms_grid_fname = '/home/tkdals/pyroms/Grid/'+expname+'_grd_'+version+'.nc'
extraHoriz  = 2.0 # in degrees. use 2 times of delta X or delta Y.

if not os.path.isfile(roms_grid_fname):
    print("==>Error: not found - %s"%roms_grid_fname)
else:
    with Dataset(roms_grid_fname) as roms_grid:
        minmaxLonR = [round(roms_grid['lon_vert'][:].min()-extraHoriz,1), # west
                      round(roms_grid['lon_vert'][:].max()+extraHoriz,1)] # east
        minmaxLatR = [round(roms_grid['lat_vert'][:].min()-extraHoriz,1), # south
                      round(roms_grid['lat_vert'][:].max()+extraHoriz,1)] # north
        print('==>Info: ', minmaxLonR, minmaxLatR)
        
region = {'lat1':minmaxLatR[0],'lat2':minmaxLatR[1],'lon1':minmaxLonR[0],'lon2':minmaxLonR[1]}

# region = {'lat1':19,'lat2':54,'lon1':116,'lon2':161} # south, north, west, east
# region = {'lat1':20,'lat2':50,'lon1':100,'lon2':154} # for LJH's grid

# Grib Fields: {'shortName': [typeOfLevel, level, stepType]}
fldGFS = {'dswrf':['surface',0,'avg'],              # Downward_Short-Wave_Radiation_Flux_surface_6_Hour_Average
          'uswrf':['surface',0,'avg'],              # Upward_Short-Wave_Radiation_Flux_surface_6_Hour_Average
          'dlwrf':['surface',0,'avg'],              # Downward_Long-Wave_Radp_Flux_surface_6_Hour_Average
          'ulwrf':['surface',0,'avg'],              # Upward_Long-Wave_Radp_Flux_surface_6_Hour_Average
          '2r'   :['heightAboveGround',2,'instant'],# 2 metre relative humidity
          'tp'   :['surface',0,'accum'],            # Total Precipitation
          'prate':['surface',0,'avg'],              # Precipitation_rate_surface_6_Hour_Average
         'landn':['surface',0,'instant'],           # Land-sea coverage (nearest neighbor) [land=1,sea=0]
          #'al'   :['surface',0,'avg'],              # Albedo
          #'sde'  :['surface',0,'instant'],          # Snow depth
          #'tcc'  :['unknown',0,'instant'],          # Total Cloud Cover
          #'sp'   :['surface',0,'instant'],          # Surface Air Pressure
          'prmsl':['meanSea',0,'instant'],          # Pressure_reduced_to_MSL_msl
          '10u'  :['heightAboveGround',10,'instant'], # u-component_of_wind_height_above_ground (10 metre)
          '10v'  :['heightAboveGround',10,'instant'], # v-component_of_wind_height_above_ground (10 metre)
          't'    :['surface',0,'instant'],          # Surface Air Temperature
          '2t'   :['heightAboveGround',2,'instant'],# 2 metre temperature
          'lsm'  :['surface',0,'instant'],          # Land-sea mask (0-1)
          'lhtfl':['surface',0,'avg'],      # Latent_heat_net_flux_surface_6_Hour_Average
          'SHTFL':['surface',0,'avg'],              # Sensible_heat_net_flux_surface_6_Hour_Average
           'pevpr':['surface',0,'instant'],          # Potential evaporation rate
          
          }
# the information of attributes { 'netcdf attr name': 'grib attr name'}
attrGrib = {'long_name':'name','units':'units','step_type':'stepType',
            'cf_name':'cfName','cf_var_name':'cfVarName'}

fldROMS = ('Tair', 'Pair', 'Qair', 'Uwind', 'Vwind', 'swrad', 'lwrad_down', 'rain')
# %%
dict_path = '/home/tkdals/pyroms/SBC/GFS'
def getGFS(version, tdate, tau_list, region):
    """
    version: GFSncdc, GFSncep, GFSgdas
    region: {'lat1':-90,'lat2':90,'lon1':0,'lon2':360}
    """
    if version == 'GFSncdc': # '201906/20190601/gfs_4_20190601_1200_0240.grb2'
        header = 'GFS/{}/gfs_4_{}_%3.3i.grb2'.format(
                 tdate.strftime('%Y%m/%Y%m%d'),tdate.strftime('%Y%m%d_%H%M'))
    elif version == 'GFSncep': # 'gfs.2019060112/gfs.t12z.pgrb2.0p25.f0240'
        header = 'GFS/gfs.{}/gfs.{}.pgrb2.0p25.f%3.3i'.format(
                 tdate.strftime('%Y%m%d%H'),tdate.strftime('t%Hz'))
    elif version == 'GFSgdas': # 'gdas.20190601/gdas.t12z.pgrb2.0p25.f009'
        header = 'GDAS/{}/gdas1.fnl0p25.{}.f%2.2i.grib2'.format(
                 tdate.strftime('%Y%m'),tdate.strftime('%Y%m%d00'))
    elif version == 'GFSncar':
        header = 'GFS/{}/gfs.0p25.{}.f%3.3i.grib2'.format(
                 tdate.strftime('%Y%m/%Y%m%d'),tdate.strftime('%Y%m%d00'))
    else: print('==>Error: incorrect version (%s)'%version); return pd.DataFrame()
    
    print('complete read ' + header)
    # create a new GFSraw
    try:
        with grib(header%(tau_list[0])) as grbs:
            time = pd.date_range(tdate, tdate + timedelta(hours=tau_list[-1]), freq='%dH'%dhour)
            
            # get the latitude and longitude informations
            k = 'landn'; v = fldGFS[k]
            sforc = grbs.select(shortName=k, typeOfLevel=v[0], level=v[1])
            gdata = sforc[0].data(lat1=region['lat1'], lat2=region['lat2'],
                                  lon1=region['lon1'], lon2=region['lon2'])
            
            GFSraw = xr.Dataset() # create a new GFSraw
            
            GFSraw['time'] = time
            GFSraw['lat2d'] = (('lat', 'lon'), gdata[1])
            GFSraw['lon2d'] = (('lat', 'lon'), gdata[2])
            
            ntim, nlat, nlon = GFSraw.dims['time'], GFSraw.dims['lat'], GFSraw.dims['lon']
            
            # create empty forcing values
            for k in fldGFS.keys(): 
                GFSraw[k] = (('time', 'lat', 'lon'), np.ones((ntim, nlat, nlon)) * np.nan)
                
            GFSraw.attrs['history'] = grbs.name
    except Exception as ex:
        print('==>Error: %s GFS data at %s'%(ex, header%(tau_list[0]))); return GFSraw
    
    for tnum, tlead in enumerate(tau_list):
        if tlead > tleadmax:
            print('==>Error: exceeded max tlead (%i/%i)'%(tlead, tleadmax)); break
        if tlead % dhour != 0:
            print('==>Error: tlead must be every %i hourly but %i'%(dhour, tlead//dhour)); break
            
        tau_date = tdate + timedelta(hours=tlead)
  
        GFSlocal = header % tlead
        if os.path.isfile(GFSlocal):
            print('==>Info(%s): reading %s for SBC'%(version, GFSlocal))
        else:
            print('==>Error(%s): not found %s for SBC'%(version, GFSlocal)); break
  
        try:
            with grib(GFSlocal) as grbs:
                gdata = {}; ginfo = {}
                for k, v in fldGFS.items():
                    try: 
                        sforc = grbs.select(shortName=k, typeOfLevel=v[0], level=v[1])
                        if len(sforc) == 1: # sforc[0].data()[0]: 0:data, 1:lat, 2:lon
                            sforc = sforc[0]; ginfo[k] = {}
                            for nk, nv in attrGrib.items(): ginfo[k][nk] = sforc[nv]
                            GFSraw[k][tnum, :, :] = sforc.data(lat1=region['lat1'], lat2=region['lat2'],
                                                               lon1=region['lon1'], lon2=region['lon2'])[0]
                        else: 
                            print('==>Error(%s): '%k, sforc); continue # Changed from raising StopIteration
                            
                        # insert attributes if none
                        if 'units' not in GFSraw[k].attrs.keys():
                            for ak, av in attrGrib.items():
                                GFSraw[k].attrs[ak] = sforc[av]
                    except ValueError as e: 
                        print('==>Warning(%s): '%k, e); continue # Changed from raising StopIteration
                            
        except Exception as ex:
            print('==>Error: %s GFS data at %s'%(ex, GFSlocal)); break
            
    return GFSraw # var[name].loc[tau][y,x] as pd.DataFrame()# %%

# %%
def transGFS(GFSraw, time_units='seconds since 2000-01-01 00:00:00'):
    nlat = GFSraw.dims['lat']; nlon = GFSraw.dims['lon']
    
    GFStrn = xr.Dataset() # create a new GFStrn
    # coordinates
    GFStrn['time'] = GFSraw['time']
    GFStrn['lat'] = (('lat'), GFSraw['lat2d'][:, int(nlon / 2)].data[::-1])  # middle latitude
    GFStrn['lon'] = (('lon'), GFSraw['lon2d'][int(nlat / 2), :].data)  # middle longitude

    
    for v in fldROMS:
        if v == 'Tair': # K -> C
            GFStrn[v] = (('tair_time', 'lat', 'lon'), GFSraw['2t'][:, ::-1, :].data - 273.15)
            GFStrn[v].attrs = GFSraw['2t'].attrs
            GFStrn[v].attrs['units'] = 'Celsius'; GFStrn[v].attrs['coordinates'] = 'lon lat'
            GFStrn['tair_time'] = GFSraw['time']
        elif v == 'Pair': # (1 mb = 100 Pa)
            GFStrn[v] = (('pair_time', 'lat', 'lon'), GFSraw['prmsl'][:, ::-1, :].data / 100.)
            GFStrn[v].attrs = GFSraw['prmsl'].attrs
            GFStrn[v].attrs['units'] = 'milibar'; GFStrn[v].attrs['coordinates'] = 'lon lat'
            GFStrn['pair_time'] = GFSraw['time']
        elif v == 'Qair': # %
            GFStrn[v] = (('qair_time', 'lat', 'lon'), GFSraw['2r'][:, ::-1, :].data)
            GFStrn[v].attrs = GFSraw['2r'].attrs # no needed with full copy
            GFStrn[v].attrs['units'] = 'percentage'; GFStrn[v].attrs['coordinates'] = 'lon lat'
            GFStrn['qair_time'] = GFSraw['time']
        elif v == 'Uwind':
            GFStrn[v] = (('wind_time', 'lat', 'lon'), GFSraw['10u'][:, ::-1, :].data)
            GFStrn[v].attrs = GFSraw['10u'].attrs # no needed with full copy
            GFStrn[v].attrs['units'] = 'meter second-1'; GFStrn[v].attrs['coordinates'] = 'lon lat'
            GFStrn['wind_time'] = GFSraw['time']
        elif v == 'Vwind':
            GFStrn[v] = (('wind_time', 'lat', 'lon'), GFSraw['10v'][:, ::-1, :].data)
            GFStrn[v].attrs = GFSraw['10v'].attrs # no needed with full copy
            GFStrn[v].attrs['units'] = 'meter second-1'; GFStrn[v].attrs['coordinates'] = 'lon lat'
            #GFStrn['wind_time'] = GFSraw['time']
        elif v == 'swrad': # Note) upward is negative.  Shorwave = dswsfc - uswsfc
            GFStrn[v] = (('srf_time', 'lat', 'lon'), (GFSraw['dswrf'][:, ::-1, :].data - GFSraw['uswrf'][:, ::-1, :].data))
            if GFSraw['dswrf'].attrs['step_type'] == 'accum': GFStrn[v] /= (dhour * 3600)
            GFStrn[v].attrs = GFSraw['dswrf'].attrs
            GFStrn[v].attrs['long_name'] = 'Net short-wave radiation flux'
            GFStrn[v].attrs['units'] = 'watt meter-2'
            GFStrn[v].attrs['coordinates'] = 'lon lat'
            GFStrn[v][0, :, :] = GFStrn[v][1, :, :] # flux[0] = flux[1]
            GFStrn['srf_time'] = GFSraw['time']
        elif v == 'lwrad_down':
            GFStrn[v] = (('lrf_time', 'lat', 'lon'), GFSraw['dlwrf'][:, ::-1, :].data)
            if GFSraw['dlwrf'].attrs['step_type'] == 'accum': GFStrn[v] /= (dhour * 3600)
            GFStrn[v].attrs = GFSraw['dlwrf'].attrs
            GFStrn[v].attrs['units'] = 'watt meter-2'
            GFStrn[v].attrs['coordinates'] = 'lon lat'
            GFStrn[v][0, :, :] = GFStrn[v][1, :, :] # flux[0] = flux[1]
            GFStrn['lrf_time'] = GFSraw['time']
        elif v == 'rain':
            #Rho_w = 1000. # water density (kg/m^3)
            #GFStrn[v] = (('rain_time', 'lat', 'lon'), GFSraw['tp'][:, ::-1, :] * Rho_w)
            #if GFSraw['tp'].attrs['step_type'] == 'accum': GFStrn[v] /= (dhour * 3600)
            #GFStrn[v].attrs = GFSraw['tp'].attrs
            GFStrn[v] = (('rain_time', 'lat', 'lon'), GFSraw['prate'][:, ::-1, :].data)
            if GFSraw['prate'].attrs['step_type'] == 'accum': GFStrn[v] /= (dhour * 3600)
            GFStrn[v].attrs = GFSraw['prate'].attrs
            GFStrn[v].attrs['long_name'] = 'Rain fall rate'
            GFStrn[v].attrs['units'] = 'kilogram meter-2 second-1'
            GFStrn[v].attrs['coordinates'] = 'lon lat'
            GFStrn[v][0, :, :] = GFStrn[v][1, :, :] # flux[0] = flux[1]
            GFStrn['rain_time'] = GFSraw['time']
        else: print('==>Error: incorrect field value - %s'%v); return GFStrn
        
    GFStrn['time'].attrs['long_name'] = 'time'
    GFStrn['lat'].attrs = {'long_name': 'latitude', 'units': 'degrees_north'}
    GFStrn['lon'].attrs = {'long_name': 'longitude', 'units': 'degrees_east'}
        
    # Global attributes
    GFStrn.attrs['Author'] = 'Dong-Hoon Kim (www.dhkim.info)'
    GFStrn.attrs['Comment'] = ''
    GFStrn.attrs['Title'] = 'Surface forcing from GFS dataset for ROMS'
    GFStrn.attrs['Created'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    GFStrn.attrs['History'] = GFSraw.attrs['history']
    
    return GFStrn
# %%
# GFSraw = getGFS('GFSncep', datetime(2019,6,1,12), list(range(0,4,3)), region)
GFSraw = getGFS('GFSncar', date_beg, list(range(0,241,3)), region)
# ds.to_netcdf('test.nc', 'w', format='NETCDF3_CLASSIC', unlimited_dims=['time',])
# _=plt.imshow(ds['2t'][0, :, :]) # var[name][t, y, x]
GFSraw
#%%
GFStrn = transGFS(GFSraw)
#%%
# save to netcdf format
roms_gfs = 'roms_gfs_0p25_sbc_%s.nc'%expname
time_units = {}
for tn in ('time', 'tair_time', 'pair_time', 'qair_time', 'wind_time', 'srf_time', 'lrf_time', 'rain_time'):
    time_units[tn] = {'units': 'days since 2000-01-01 00:00:00'}
    #time_units[tn] = {'units': 'seconds since 2000-01-01 00:00:00'}
GFStrn.to_netcdf(roms_gfs, 'w', format='NETCDF3_CLASSIC', encoding=time_units, unlimited_dims=['time',])
print('\n==>Info: creating %s\n'%roms_gfs)
# _=plt.imshow(dc['Pair'][0, :, :])

