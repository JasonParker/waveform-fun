import argparse
import json
import os

import model

def _parse_arguments(argv):
    """ Not currently used"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--batch_size",
        help="Batch size for training steps",
        type=int,
        default=32,
    )
    parser.add_argument(
        "--eval_data_path",
        help="GCS location pattern of eval files",
        required=True,
    )
    parser.add_argument(
        "--nbuckets",
        help="Number of buckets to divide lat and lon with",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--lr", help="learning rate for optimizer", type=float, default=0.001
    )
    parser.add_argument(
        "--num_evals",
        help="Number of times to evaluate model on eval data training.",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--num_examples_to_train_on",
        help="Number of examples to train on.",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--output_dir",
        help="GCS location to write checkpoints and export models",
        default=os.getenv("AIP_MODEL_DIR"),
    )
    parser.add_argument(
        "--train_data_path",
        help="GCS location pattern of train files containing eval URLs",
        required=True,
    )

    args, _ = parser.parse_known_args()

    hparams = args.__dict__
    print("output_dir", hparams["output_dir"])
    model.train_and_evaluate(hparams)

def main():
    """
    This function will perform model training
    """
    xgb = model.build_xgboost_model()
    trained, predictions = model.train_and_evaluate(xgb)

if __name__ == "__main__":
    main()
