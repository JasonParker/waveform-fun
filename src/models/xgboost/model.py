from xgboost import XGBClassifier
import datetime
import logging
import os
import shutil

import hypertune
import numpy as np

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

def load_dataset():
    df = pd.read_csv("src/data/processed/processed_all.csv")
    df = df.drop(columns=["Unnamed: 0", "Unnamed: 0.1"])
    # Drop instances where patient is hypotensive and then isn't later on
    to_drop = df[(df.current_hypotensive == 1) & (df.hypotensive_in_15 == 1.0)]
    new_df = df.drop(to_drop.index)
    new_df["hypotensive_in_15"] = new_df["hypotensive_in_15"].astype(int)

    ## Convert wave data to numerical
    new_df.wave, mapping = pd.factorize(new_df.wave)

    return df

def create_train_and_test(df, split=0.7):
    train_df, test_df = split_by_time(df, split)

    return train_df, test_df

def process_data():
    df = load_dataset()
    train_df, test_df = split_by_time(df)

    y_train = np.array(train_df[LABEL_COLUMN])
    y_test = np.array(test_df[LABEL_COLUMN])
    X_train = train_df[CSV_COLUMNS]
    X_test = test_df[CSV_COLUMNS]

    return X_train, y_train, X_test, y_test

def build_xgboost_model(lr):
    xgb = XGBClassifier(random_state=0, importance="weight")

    return xgb


hpt = hypertune.HyperTune()

class HPTCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        global hpt
        hpt.report_hyperparameter_tuning_metric(
            hyperparameter_metric_tag="val_rmse",
            metric_value=logs["val_rmse"],
            global_step=epoch,
        )

