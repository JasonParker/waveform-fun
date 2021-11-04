import argparse
import datetime
import json
import os

from waveform_fun.models.xgb_trainer import model

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        help="GCS location to write checkpoints and export models",
        default=None,
    )

    parser.add_argument(
        "--job-dir",
        help="this model ignores this field, but it is required by gcloud",
        default="junk",
    )

    args, _ = parser.parse_known_args()
    hparams = args.__dict__
    hparams.pop("job-dir", None)
    if hparams["output_dir"] is None:
        BUCKET = "physionet_2009"
        TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        hparams["output_dir"] = f"gs://{BUCKET}/models/trained_xgb_model_{TIMESTAMP}"
    print("output_dir", hparams["output_dir"])
    xgb = model.build_xgboost_model()
    trained, predictions = model.train_and_evaluate(xgb, hparams["output_dir"])
