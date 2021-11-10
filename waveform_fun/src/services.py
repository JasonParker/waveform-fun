"""
Send a request to flask application
"""
import requests
import json
import os
import pandas as pd
from waveform_fun.src.utils.utils import df_to_json

url = "https://waveform-fun-wdjvwzdfuq-uc.a.run.app"

## Get pong
def pong():
    resp = requests.get(f"{url}/ping", verify=False)
    print(resp.content.decode())

# Get AutoML Scores
def get_automl_scores():
    bp_url = "?sysBP=20&diasBP=30"
    resp = requests.get(f"{url}/automl_score{bp_url}", verify=False)
    print(resp.content.decode())

# Get XGBoost Scores
def get_xgb_scores():
    # Copy file from bucket and load
    bucket_name = "physionet_2009"
    os.system(f'gsutil cp gs://{bucket_name}/processed/x_test.csv .')
    df = pd.read_csv("x_test.csv")
    os.system("rm x_test.csv")

    # Get 100 data points
    df2 = df.iloc[:100]
    df2 = df2.drop(columns=["Unnamed: 0"])
    to_json = df_to_json(df2)
    json_data = json.dumps({"instances": to_json})
    import pdb; pdb.set_trace()
    resp = requests.get(f"{url}/xgboost_score", json=json_data, verify=False)
    import pdb; pdb.set_trace()
    print(resp.content.decode())

# Get train_xgb_model
def train_xgb_model():
    resp = requests.get(f"{url}/train", verify=False)
    print(resp.content.decode())

if __name__ == "__main__":
    get_xgb_scores()
