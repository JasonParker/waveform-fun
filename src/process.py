import pandas as pd
import numpy as np
import gcsfs
import os

from data.gcp_pull_waveform_data import fetch_settings, generate_record_map, generate_waveform_dataset
from utils.get_labels import get_training_labels, get_t0
from data.bp_features import avg_bp, clean_bp_summary

def load_data(pull_local=True):
    """Load data from GCP"""
    fs = gcsfs.GCSFileSystem(project=os.environ['PROJECT_ID'])
    bucket_name = 'physionet_2009'

    training = get_training_labels()

    record_map = generate_record_map(bucket_name, fs, training)
    x = {e: generate_waveform_dataset(e, record_map, bucket_name, pull_local) for e in record_map['waveform_entities'][0:2]}

    return x

def add_features():
    """ Add features and format dataset"""
    fs = gcsfs.GCSFileSystem(project=os.environ['PROJECT_ID'])
    bucket_name = 'physionet_2009'
    training = get_training_labels()
    record_map = generate_record_map(bucket_name, fs, training)
    #for i, rec in enumerate(list(x.values())):
    for i, e in enumerate(record_map['waveform_entities'][0:15]):
        rec = generate_waveform_dataset(e, record_map, bucket_name)
        df = pd.DataFrame(rec["ABP"])
        df = pd.DataFrame(rec, columns=["wave", "time", "ts", "ABP"])
        df = df[~df['ABP'].isna()]
        wave = df["wave"].values[0]
        if os.path.isfile(f"data/processed/data_{wave}.csv"):
            continue
        #try:
        new_df = avg_bp(df, time_chunk=60)
        clean_df = clean_bp_summary(new_df)
        #except:
        #    print("failed")
        #    continue
        #if i == 0:
        #    total_df = clean_df
        #else:
        #    total_df = total_df.append(clean_df)

        clean_df.to_csv(f"data/processed/data_{wave}.csv")

    return clean_df

if __name__ == "__main__":
    #x = load_data(pull_local=True)
    total_df = add_features()
