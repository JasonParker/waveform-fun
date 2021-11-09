"""
Send a request to flask application
"""
import requests

url = "https://waveform-fun-wdjvwzdfuq-uc.a.run.app"

## Get pong
#resp = requests.get(f"{url}/ping", verify=False)
#print(resp.content.decode())
# Get Scores
resp = requests.get(f"{url}/score", verify=False)
print(resp.content.decode())

# Get AutoML Scores
bp_url = "?sysBP=20&diasBP=30"
resp = requests.get(f"{url}/automl_score{bp_url}", verify=False)
print(resp.content.decode())

# Get train_xgb_model
#resp = requests.get(f"{url}/train", verify=False)
#print(resp.content.decode())
