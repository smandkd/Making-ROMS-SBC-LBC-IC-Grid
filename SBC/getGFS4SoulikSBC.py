# ==================================================================
# 2018.08.18 00시 부터 2018.08.25 23시 59분까지 예측 자료 다운로드 코드
# ==================================================================
# %%
""" 
Python script to download selected files from rda.ucar.edu.
After you save the file, don't forget to make it executable
i.e. - "chmod 755 <name_of_script>"
"""
import sys
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure retry strategy
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

base_url = 'https://data.rda.ucar.edu/ds084.1/2018/20180821/'
file_prefix = 'gfs.0p25.2018082100.f'
file_suffix = '.grib2'
forecast_hours = [f'{i:03}' for i in range(0, 241, 3)]
download_dir = '/home/tkdals/pyroms/SBC/GFS/201808/20180821'

#%%
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

def download_file(file_url, local_path):
    max_retries = 3  # Maximum number of retries for each file
    for attempt in range(max_retries):
        try:
            response = http.get(file_url, stream=True)
            response.raise_for_status()
            
            with open(local_path, "wb") as outfile:
                for chunk in response.iter_content(chunk_size=8192):
                    outfile.write(chunk)
            
            sys.stdout.write("done\n")
            return True
        except requests.exceptions.RequestException as e:
            sys.stdout.write(f"failed (attempt {attempt + 1} of {max_retries}): {e}\n")
    return False

for hour in ['00', '06', '12', '18']:
    for forecast_hour in forecast_hours:
        file_name = f'{file_prefix}{forecast_hour}{file_suffix}'
        file_url = base_url + file_name
        local_path = os.path.join(download_dir, file_name)

        if os.path.exists(local_path):
            sys.stdout.write(f"{file_name} already exists, skipping...\n")
            continue

        sys.stdout.write(f"downloading {file_name} ... ")
        sys.stdout.flush()

        if not download_file(file_url, local_path):
            sys.stdout.write(f"failed to download {file_name}\n")
# %%
missing_files = []
# 예측 시간 파일이 모두 존재하는지 확인
for forecast_hour in forecast_hours:
    file_name = f'{file_prefix}{forecast_hour}{file_suffix}'
    local_path = os.path.join(download_dir, file_name)
    
    if not os.path.exists(local_path):
        missing_files.append(file_name)

# 결과 출력
if not missing_files:
    print("모든 파일이 성공적으로 다운로드되었습니다.")
else:
    print("다음 파일들이 누락되었습니다:")
    for file in missing_files:
        print(file)
# %%
