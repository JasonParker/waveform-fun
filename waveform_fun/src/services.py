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
resp = requests.get(f"{url}/automl_score", verify=False)
print(resp.content.decode())
