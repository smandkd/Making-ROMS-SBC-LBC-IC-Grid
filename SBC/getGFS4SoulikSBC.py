# ==================================================================
# 2018.08.21 00시 부터 240시간 후(10일 후) 예측 자료 다운로드 코드
# ==================================================================
#%%
import sys
import os 
from urllib.request import build_opener
import requests 
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# opener = build_opener()

# filelist = [
#   'https://data.rda.ucar.edu/ds083.3/2018/201808/gdas1.fnl0p25.2018082100.f06.grib2',
#   'https://data.rda.ucar.edu/ds083.3/2018/201808/gdas1.fnl0p25.2018082100.f09.grib2'
# ]

# for file in filelist:
#     ofile = os.path.basename(file)
#     sys.stdout.write("downloading " + ofile + " ... ")
#     sys.stdout.flush()
#     infile = opener.open(file)
#     outfile = open(ofile, "wb")
#     outfile.write(infile.read())
#     outfile.close()
#     sys.stdout.write("done\n")

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
file_numbers = [f'{i:03}' for i in range(0, 385, 3)]
download_dir = '/home/tkdals/pyroms/SBC/GFS/201808/20180821'
max_retries = 3  # Maximum number of retries for each file

# For downloading gdas
# base_url = 'https://data.rda.ucar.edu/ds083.3/2018/201808/'
# file_prefix = 'gdas1.fnl0p25.2018082100.f'
# file_suffix = '.grib2'
# file_numbers = [f'{i:02}' for i in range(0, 10, 3)]
# download_dir = '/home/tkdals/pyroms/SBC/GDAS/201808/201808/'

if not os.path.exists(download_dir):
    os.makedirs(download_dir)

def download_file(file_url, local_path):
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

for file_number in file_numbers:
    file_name = f'{file_prefix}{file_number}{file_suffix}'
    file_url = base_url + file_name
    local_path = os.path.join(download_dir, file_name)
    
    sys.stdout.write(f"downloading {file_name} ... ")
    sys.stdout.flush()
    
    if not download_file(file_url, local_path):
        sys.stdout.write(f"failed to download {file_nam