from xgboost import XGBClassifier
from waveform_fun.src.utils.get_labels import get_training_labels
from waveform_fun.src.retrieve_train_wf import upload_blob
import datetime
import joblib
import logging
import os
import pickle
import shutil
from waveform_fun.models.xgb_trainer import preprocessing
import sklearn

#import hypertune
import numpy as np

from sklearn.pipeline import Pipeline

BUCKET = "physionet_2009"

def run_pipeline(model, X_train, y_train, X_test, y_test, verbose=True):
    """Run pipeline in SKlearn to fit and make predictions with a model
    Parameters
    ----------
    model :
        Model to use
    X_train : np.array, shape=(nrows, ncolumns)
        Training features
    y_train : np.array, shape=(nrows,)
        Training label to predict
    X_test : np.array, shape=(nrows, ncolumns)
        Test features
    y_test : np.array, shape=(nrows,)
        Test label to predict
    Returns
    -------
    pipeline : sklearn.Pipeline object
        Pipeline of model
    pipeline_predictions : np.array(nrows)
        Predictions from model
    """
    pipeline = Pipeline(steps=[('m', model)])

    pipeline.fit(X_train, y_train)

    pipeline_predictions = pipeline.predict(X_test)

    if verbose:
        print_metrics(pipeline, X_test, y_test, pipeline_predictions)

    return pipeline, pipeline_predictions

def print_metrics(model, X_test, actual, predicted):
    """Output metrics from model

    Parameters
    ----------
    model : sklearn or xgboost object
        Model to evaluate
    X_test : np.array, shape=(nrows, ncolumns)
        Test features
    actual : np.array, shape=(nrows,)
        Test label to predict
    predict : np.array, shape=(nrows,)
        Label predictions from model

    Returns
    -------
    """
    metrics = sklearn.metrics.classification_report(actual, predicted)
    print(metrics)

    cm = sklearn.metrics.plot_confusion_matrix(model, X_test, actual)

    # Plot ROC curve
    roc = sklearn.metrics.plot_roc_curve(model, X_test, actual)


def build_xgboost_model():
    """Build xgboost model"""
    xgb = XGBClassifier(random_state=0, importance="weight")

    return xgb

def train_and_evaluate(model, output_dir):
    """Train model"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    savedmodel_dir = os.path.join(output_dir, "savedmodel")
    model_export_path = os.path.join(savedmodel_dir, timestamp)

    # Load and process data
    X_train, y_train, X_test, y_test, X_valid, y_valid = preprocessing.process_data()

    # Train model
    xgb_pipeline, xgb_pipeline_predictions = run_pipeline(model,
                                                      X_train,
                                                      y_train,
                                                      X_valid,
                                                      y_valid,
                                                      verbose=False)
    print(xgb_pipeline_predictions)

    # Save model locally
    now = datetime.datetime.now()
    date, time= str(now).split(" ")
    #model.save_model(f"xgb_files/xgbmodel_{date}_{time}.json")
    #model.save_model(f"waveform_fun/models/xgb_trainer/xgb_files/xgbmodel_{date}_{time}.json")
    # Save as json
    model.save_model("model.json")
    # Save as pkl
    #with open('xgbmodel_{date}_{time}.pkl', 'wb') as model_file:
    #    pickle.dump(model, model_file)
    joblib.dump(model, "model.joblib")

    # Write to a bucket
    #upload_blob(BUCKET, f"xgbmodel_{date}_{time}.json", model_export_path) 
    json_file = "model.json"
    pkl_file = "model.pkl"
    joblib_file = "model.joblib"
    os.system(f'gsutil cp {json_file} {model_export_path}/')
    os.system(f'gsutil cp {joblib_file} {model_export_path}/')

    return xgb_pipeline, xgb_pipeline_predictions

#hpt = hypertune.HyperTune()

#class HPTCallback(tf.keras.callbacks.Callback):
#    def on_epoch_end(self, epoch, logs=None):
#        global hpt
#        hpt.report_hyperparameter_tuning_metric(
#            hyperparameter_metric_tag="val_rmse",
#            metric_value=logs["val_rmse"],
#            global_step=epoch,
#        )
#
