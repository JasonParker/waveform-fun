import pandas as pd
import numpy as np
import gcsfs
import os

from data.gcp_pull_waveform_data import fetch_settings, generate_record_map, generate_waveform_dataset
from utils.get_labels import get_training_labels, get_t0
from data.bp_features import avg_bp, clean_bp_summary, create_lookback
from retrieve_train_wf import upload_blob

def load_data(pull_local=True):
    """Load data from GCP"""
    fs = gcsfs.GCSFileSystem(project=os.environ['PROJECT_ID'])
    bucket_name = 'physionet_2009'

    training = get_training_labels()

    record_map = generate_record_map(bucket_name, fs, training)
    #x = {e: generate_waveform_dataset(e, record_map, bucket_name, pull_local) for e in record_map['waveform_entities'][0:2]}

    return record_map

def add_features():
    """ Add features and format dataset"""
    fs = gcsfs.GCSFileSystem(project=os.environ['PROJECT_ID'])
    bucket_name = 'physionet_2009'
    training = get_training_labels()
    record_map = generate_record_map(bucket_name, fs, training)
    #for i, rec in enumerate(list(x.values())):
    for e in record_map['waveform_entities'][0:2]:
        rec = generate_waveform_dataset(e, record_map, bucket_name)
        if isinstance(rec, type(None)):
            print("No data found")
            continue
        try:
            df = pd.DataFrame(rec["ABP"])
        except KeyError:
            print("No ABP detected")
            continue
        df = pd.DataFrame(rec, columns=["wave", "time", "ts", "ABP"])
        df = df[~df['ABP'].isna()]
        wave = df["wave"].values[0]
        #if os.path.isfile(f"data/processed/data_{wave}.json"):
        #    continue
        #try:
        new_df = avg_bp(df, time_chunk=60)
        if isinstance(new_df, type(None)):
            continue
        lb_df = create_lookback(new_df)
        clean_df = clean_bp_summary(lb_df)
        #except:
        #    print("failed")
        #    continue
        #if i == 0:
        #    total_df = clean_df
        #else:
        #    total_df = total_df.append(clean_df)

        #clean_df.to_csv(f"data/processed/data_{wave}.csv")
        clean_df.to_json(f"data/processed/data_{wave}.json")

    return clean_df

def add_features_new(e, record_map, outcome_period, input_period, bucket_name='physionet_2009'):
    # open and read record map
    
    
    rec = generate_waveform_dataset(e, record_map, bucket_name)
    #if isinstance(rec, type(None)):
    #    print("No data found")
    #    continue
    #try:
    #    'ABP' in rec.columns
    #except KeyError:
    #    print("No ABP detected")
    #    continue
    df = pd.DataFrame(rec, columns=["wave",'clinical', "time", "ts",'age','sex',"ABP"])
    #df = df[~df['ABP'].isna()]
    wave = df["wave"].values[0]
    outcome_avg = avg_bp(df, time_chunk = outcome_period, time_window = 60)
    input_avg = avg_bp(df, time_chunk = input_period, time_window = 60)
    
    final_df = final_df = outcome_avg.merge(right = input_avg, on = 'start_window', suffixes = ['_outputs','_inputs'])
    
    input_minutes = input_period // 60
    
    final_df.to_json(f"data/processed/data_{wave}_{input_minutes}_avg.json")
    return final_df
        
        

def combine_dataset():
    """Combine CSV files for individual patients into single CSV file"""
    files = os.listdir("data/processed/")
    for idx, fil in enumerate(files):
        if fil.split(".")[-1] == "json":
            df = pd.read_csv(f"data/processed/{fil}")
        if idx == 0:
            total_df = df
        else:
            total_df = total_df.append(df)

    total_df.to_csv("data/processed/processed_all.json")

def push_to_bucket(e,):
    """Push combined dataset to GCP bucket"""
    bucket_name = 'physionet_2009'
    source_path = os.path.join("data/processed", "processed_all.json")
    destination = os.path.join("processed", "processed_all.json")
    upload_blob(bucket_name, source_path, destination)

if __name__ == "__main__":
    print(os.getcwd())
    os.environ["PROJECT_ID"] = "qwiklabs-gcp-04-133e595cc3fe"
    record_map = load_data(pull_local=True)
    for e in record_map['waveform_entities'][2:5]:
        total_df = add_features_new(e, record_map, outcome_period = 60*5, input_period = 60 * 20, bucket_name='physionet_2009')
        #print(e + ': '+ total_df.shape)
    #combine_dataset()
    #push_to_bucket()
