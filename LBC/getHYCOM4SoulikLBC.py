#%%
import os
import time
from datetime import datetime, timedelta
from urllib import parse, request
from concurrent.futures import ThreadPoolExecutor, as_completed
from netCDF4 import Dataset
import logging

# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 실험명
expname = 'Soulik'
grd_version = 'v2'

# 경계장 날짜 설정
date_beg = datetime(2018, 8, 21, 0)
date_end = datetime(2018, 8, 25, 0)

server = 'https://ncss.hycom.org/thredds/ncss'
version = 'GLBv0.08'
expt = 'expt_93.0'
server = '/'.join([server, version, expt])

strideTime = 1  # 시간 해상도
strideHoriz = 2  # 수평 해상도
extraHoriz = 2.0  # 추가 수평 범위

# ROMS 격자 정보 가져오기
roms_grid_fname = '../Grid/' + expname + '_grd_' + grd_version + '.nc'
if not os.path.isfile(roms_grid_fname):
    logging.error("==>Error: not found - %s", roms_grid_fname)
else:
    with Dataset(roms_grid_fname) as roms_grid:
        minmaxLonR = [round(roms_grid['lon_vert'][:].min() - extraHoriz, 3),  # 서쪽 경도
                      round(roms_grid['lon_vert'][:].max() + extraHoriz, 3)]  # 동쪽 경도
        minmaxLatR = [round(roms_grid['lat_vert'][:].min() - extraHoriz, 3),  # 남쪽 위도
                      round(roms_grid['lat_vert'][:].max() + extraHoriz, 3)]  # 북쪽 위도
        logging.info('==>Info: %s %s', minmaxLonR, minmaxLatR)

# 기본 URL 생성
qGrid = [('north', minmaxLatR[1]), ('west', minmaxLonR[0]), ('east', minmaxLonR[1]), ('south', minmaxLatR[0]),  # NWES
         ('disableProjSubset', 'on'), ('horizStride', strideHoriz),
         ('vertCoord', ''), ('addLatLon', 'true'), ('accept', 'netcdf4')]
params = parse.urlencode(qGrid, encoding='UTF-8', doseq=True)
urls = {
    'ts3z': f"{server}/ts3z?{params}&var=water_temp&var=salinity",
    'uv3z': f"{server}/uv3z?{params}&var=water_u&var=water_v",
    'ssh': f"{server}/ssh?{params}&var=surf_el"
}
logging.info(urls)

# 자료 저장 함수 정의
def getHYCOM(prefix, tinfo, dt, vnames, clobber=False, retries=3, delay=10):
    outfile = f'./HYCOM/HYCOM4{expname}_{prefix}_{dt.strftime("%Y-%m-%dT%H:%M:%SZ")}.nc4'
    if os.path.isfile(outfile) and not clobber:
        logging.info('==>Info: already exists %s', outfile)
        return

    url = f"{urls[prefix]}&{tinfo}"
    attempt = 0

    while attempt < retries:
        try:
            logging.info('==>Info[%s]: %s to %s', prefix, url, outfile)
            request.urlretrieve(url, outfile)

            for v in vnames:
                os.system(f'ncpdq -O -P upk {outfile} {outfile}')
            return

        except Exception as e:
            logging.error("Error: %s", e)
            attempt += 1
            logging.info("Retrying %s (%d/%d) after %d seconds...", prefix, attempt, retries, delay)
            time.sleep(delay)

    logging.error("==>Error: Failed to retrieve %s data after %d attempts.", prefix, retries)

# 다운로드를 병렬로 실행하기 위한 함수
def parallel_download(dt, strideTime):
    query = [('time_start', dt.strftime('%Y-%m-%dT%H:%M:%SZ')),
             ('time_end', dt.strftime('%Y-%m-%dT%H:%M:%SZ')),
             ('timeStride', 1)]
    tinfo = parse.urlencode(query, encoding='UTF-8', doseq=True)

    tasks = [
        ('ts3z', tinfo, dt, ['water_temp', 'salinity']),
        ('uv3z', tinfo, dt, ['water_u', 'water_v']),
        ('ssh', tinfo, dt, ['surf_el'])
    ]

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(getHYCOM, prefix, tinfo, dt, vnames) for prefix, tinfo, dt, vnames in tasks]
        for future in as_completed(futures):
            future.result()

if not os.path.isdir('HYCOM'):
    os.makedirs('./HYCOM')

dt = date_beg
while dt <= date_end:
    parallel_download(dt, strideTime)
    dt += timedelta(hours=3 * strideTime)
# %%
