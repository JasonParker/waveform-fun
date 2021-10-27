import requests
import pandas as pd
import json
import os
from bs4 import BeautifulSoup
from google.cloud import storage


def get_url_paths(url, ext='', params={}):
    """https://www.codegrepper.com/code-examples/python/list+all+the+directory+in+a+website+using+python"""
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
    target_path = 'data/train_wave/'
    hea_urls = get_url_paths(path, ext="hea")
    dat_urls = get_url_paths(path, ext="dat")
    alarms_urls = get_url_paths(path, ext="alarms")
    urls = hea_urls + dat_urls + alarms_urls
    for url in urls:
        url_target = target_path + url.split('/')[-1]
        response = requests.get(url, stream=True)
        with open(url_target, 'wb') as f:
            #f.write(response.raw.read())
            f.write(response.content)

training = {
        'a40439': "H1",
        'a40493': "H1",
        'a40764': "H1",
        'a40834': "H1",
        'a40928': "H1",
        'a41200': "H1",
        'a41447': "H1",
        'a41770': "H1",
        'a41835': "H1",
        'a41882': "H1",
        'a41925': "H1",
        'a42277': "H1",
        'a42397': "H1",
        'a42410': "H1",
        'a42928': "H1",
        'a40006': "H2",
        'a40012': "H2",
        'a40050': "H2",
        'a40051': "H2",
        'a40064': "H2",
        'a40076': "H2",
        'a40096': "H2",
        'a40099': "H2",
        'a40013': "H2",
        'a40019': "H2",
        'a40125': "H2",
        'a40127': "H2",
        'a40154': "H2",
        'a40164': "H2",
        'a40172': "H2",
        'a40282': "C1",
        'a40473': "C1",
        'a40551': "C1",
        'a40802': "C1",
        'a40921': "C1",
        'a41137': "C1",
        'a41177': "C1",
        'a41385': "C1",
        'a41434': "C1",
        'a41466': "C1",
        'a41495': "C1",
        'a41664': "C1",
        'a41934': "C1",
        'a42141': "C1",
        'a42259': "C1",
        'a40207': "C2",
        'a40215': "C2",
        'a40225': "C2",
        'a40234': "C2",
        'a40260': "C2",
        'a40264': "C2",
        'a40277': "C2",
        'a40306': "C2",
        'a40329': "C2",
        'a40355': "C2",
        'a40374': "C2",
        'a40376': "C2",
        'a40384': "C2",
        'a40408': "C2",
        'a40424': "C2",
        }

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

if __name__ == "__main__":

    record_map = pd.read_csv(
        'data/mimic2cdb/MAP',
        sep="\t",
        names = ['Clinical', 'Wave', 'Sex', 'Age', 'Birthdate', 'Wavform'],
        index_col = False,
        skiprows = [0,1])

    training_map = record_map[record_map.Wave.isin(list(training.keys()))]
    
    if not os.path.isdir("data/train_wave"):
        print("Making 'train_wave' dir")
        os.mkdir("data/train_wave")
    
    print("Fetching data from physionet... ")
    for id in training_map["Wave"]:
        print(f"Fetching {id}")
        fetch_waveforms_for_patient(id)

    print("Upload data to bucket... ")
    bucket_name = "physionet_2009"
    for source_file in os.listdir("data/train_wave"):
        source_path = os.path.join("data/train_wave", source_file)
        destination = os.path.join("train_wave", source_file)
        upload_blob(bucket_name, source_path, destination)
