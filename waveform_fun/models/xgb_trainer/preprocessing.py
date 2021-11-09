from waveform_fun.src.utils.get_labels import get_training_labels
from google.cloud import storage
import datetime
import os
import gcsfs
import shutil

import numpy as np
import pandas as pd

CSV_COLUMNS = [
        "wave",
        "start_window",
        "end_window",
        "avg_sys",
        "avg_dias",
        "avg_map",
        "current_hypotensive",
        ]
LABEL_COLUMN = "hypotensive_in_15"


def get_blob(bucket_name, blob, destination):
    """Retrieve file from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    blob.download_to_filename(destination)

def split_by_time(df, split=0.7):
    """Split into training and testing DFs by time"""
    wave_ids = list(set(df.wave))
    train_splits = dict()
    # Get number of rows for each wave ID
    for ids in wave_ids:
        train_splits[ids] = len(df[df.wave == ids])

    # Split by 70% training, 30% testing
    # Designate first 70% of rows per wave to training
    train_df = pd.DataFrame().reindex_like(df)
    test_df = pd.DataFrame().reindex_like(df)
    train_idx = 0
    test_idx = 0
    for ids, count in train_splits.items():
        split = round(count * split)
        train = df[df.wave == ids].iloc[:split]
        test = df[df.wave == ids].iloc[split:]
        train_df.iloc[train_idx:(train_idx+len(train))] = train
        test_df.iloc[test_idx:(test_idx+len(test))] = test
        train_idx += len(train)
        test_idx += len(test)
        # Drop NAs
    train_df = train_df.dropna()
    test_df = test_df.dropna()

    return train_df, test_df

def split_by_patient(df, train_split=0.6, test_split=0.2):
    """Split into training and testing DFs by patients"""
    # Drop the pressor patients to begin with
    #df = df.drop(df[df.training_label == 'H1'].index)

    # Initialize training and testing sets
    train_df = pd.DataFrame().reindex_like(df)
    test_df = pd.DataFrame().reindex_like(df)
    valid_df = pd.DataFrame().reindex_like(df)
    train_idx = 0
    test_idx = 0
    valid_idx = 0
    for label in ("H2", "C1", "C2", "H1"):
        subset = df[df.training_label == label]
        wave_ids = list(set(subset.wave))
        n_ids = len(wave_ids)
        n_train = round(n_ids * train_split)
        n_test = round(n_ids * test_split)
        n_valid = n_ids - n_train - n_test
        train_ids = wave_ids[0:n_train]
        test_ids = wave_ids[n_train:n_train+n_test]
        valid_ids = wave_ids[n_train+n_test:n_ids]
        train_data = subset[subset.wave.isin(train_ids)]
        test_data = subset[subset.wave.isin(test_ids)]
        valid_data = subset[subset.wave.isin(valid_ids)]
        train_df.iloc[train_idx:(train_idx+len(train_data))] = train_data
        test_df.iloc[test_idx:(test_idx+len(test_data))] = test_data
        valid_df.iloc[valid_idx:(valid_idx+len(valid_data))] = valid_data

        train_idx += len(train_data)
        test_idx += len(test_data)
        valid_idx += len(valid_data)

    # Drop NAs
    train_df = train_df.dropna()
    test_df = test_df.dropna()
    valid_df = valid_df.dropna()

    return train_df, test_df, valid_df

def load_dataset():
    #df = pd.read_csv("waveform_fun/src/data/processed/processed_all.csv")
    bucket_name = 'physionet_2009'
    #os.environ["PROJECT_ID"] = "qwiklabs-gcp-04-133e595cc3fe"
    #fs = gcsfs.GCSFileSystem(project=os.environ['PROJECT_ID'])
    #df = pd.read_csv(
    #        fs.open(f"{bucket_name}/processed/processed_all.csv")
    #        )
    # Copy file from bucket
    os.system(f'gsutil cp gs://{bucket_name}/processed/processed_all.csv .')
    os.system("ls ")
    df = pd.read_csv("processed_all.csv")
    df = df.drop(columns=["Unnamed: 0", "Unnamed: 0.1"])
    # Drop instances where patient is hypotensive and then isn't later on
    to_drop = df[(df.current_hypotensive == 1) & (df.hypotensive_in_15 == 1.0)]
    new_df = df.drop(to_drop.index)
    new_df["hypotensive_in_15"] = new_df["hypotensive_in_15"].astype(int)

    training_labels = get_training_labels()
    new_df["training_label"] = new_df["wave"].apply(lambda x: training_labels[x])

    ## Convert wave data to numerical
    new_df.wave, mapping = pd.factorize(new_df.wave)

    return new_df

def create_train_and_test(df):
    train_df, test_df, valid_df = split_by_patient(df)

    return train_df, test_df, valid_df

def process_data():
    df = load_dataset()
    train_df, test_df, valid_df = split_by_patient(df)

    y_train = np.array(train_df[LABEL_COLUMN])
    y_test = np.array(test_df[LABEL_COLUMN])
    y_valid = np.array(valid_df[LABEL_COLUMN])
    X_train = train_df[CSV_COLUMNS]
    X_test = test_df[CSV_COLUMNS]
    X_valid = valid_df[CSV_COLUMNS]

    return X_train, y_train, X_test, y_test, X_valid, y_valid
