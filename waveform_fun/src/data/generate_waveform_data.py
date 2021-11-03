from bs4 import BeautifulSoup
import pandas as pd
import requests
import tarfile

source_url = 'https://archive.physionet.org/challenge/2009/training-set-clinical-data.tar.gz'
target_dir = 'waveform/data'
target_path = f'{target_dir}/training-set-clinical-data.tar.gz'

def generate_waveform_data():
    response = requests.get(source_url, stream=True)
    if response.status_code == 200:
        with open(target_path, 'wb') as f:
            f.write(response.raw.read())

    with tarfile.open(target_path, "r:gz") as tar_file:
        tar_file.extractall(target_dir)

    record_map = pd.read_csv(
        f'{target_dir}/mimic2cdb/MAP', 
        sep="\t", 
        names = ['Clinical', 'Wave', 'Sex', 'Age', 'Birthdate', 'Waveform'],
        index_col = False, 
        skiprows = [0,1])
    
    [fetch_waveforms_for_patient(id) for id in record_map['Wave']]
    return "Workload complete"
    
    
    
def get_url_paths(url, ext='', params={}):

    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return response.raise_for_status()
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent


def fetch_waveforms_for_patient(waveform_id):
    path = f'https://archive.physionet.org/pn5/mimic2db/{waveform_id}/'
    target_path = f'{target_dir}/train_wave/'
    hea_urls = get_url_paths(path, ext="hea")
    dat_urls = get_url_paths(path, ext="dat")
    alarms_urls = get_url_paths(path, ext="alarms")
    urls = hea_urls + dat_urls + alarms_urls
    for url in urls:
        url_target = target_path + url.split('/')[-1]
        response = requests.get(url, stream=True)
        with open(url_target, 'wb') as f:
            f.write(response.content)
            
            
## Functions I'm probably not going to use
def fetch_patient_records_list(waveform_id):
    waveform_lookup_base_url = "https://archive.physionet.org/pn5/mimic2db"

    response = requests.get(
        f"https://archive.physionet.org/pn5/mimic2db/{waveform_id}/RECORDS")
    return response.text.split('\n')


def fetch_record_header(waveform_id, filename):
    response = requests.get(
        f"https://archive.physionet.org/pn5/mimic2db/{waveform_id}/{filename}.hea")
    return response.text.split('\r\n')