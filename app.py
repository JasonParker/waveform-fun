from datetime import datetime
from flask import Flask, abort, redirect, request
import os

from waveform_fun.models.xgb_trainer.task import train
from src.utils.predict_tabular_data import predict_tabular_classification_sample, predict_custom_trained_model_sample, predict_xgb_classification_sample

application = Flask(__name__)

@application.route('/')
def home_page():
    """Health check route to ensure app is running."""
    return "hello world", 201, {'Content-type':'text/html'}

@application.route('/ping')
def ping_page():
    """Health check route to ensure app is running."""
    return "pong", 201, {'Content-type':'text/html'}


@application.route('/train')
def xgb_training_route():
    """Route to initiate model training"""
    ## TODO: Connect this with modeling pipeline code
    ##       Maybe you want to use a thread or similar to enable
    ##       sending a success response to the requester immediately
    ##       rather than waiting for the entire training pipeline to run.
    train()
    return f"XGBoost model training initiated at {datetime.utcnow()}"


@application.route('/score')
def scoring_route():
    """Route to generate a prediction"""
    ## TODO: Stand up a function on this route that will:
    ##       1. Accept a JSON object of the prediction data
    ##       2. Generate a prediction
    ##       3. Respond with a JSON object including the original
    ##          data and the prediction
    return f"Model scoring initiated at {datetime.utcnow()}"

@application.route('/automl_score')
def scoring_route_auto_ml():
    """Route to generate a prediction"""
    # TODO: Stand up a function on this route that will:
    #       1. Accept a JSON object of the prediction data
    #       2. Generate a prediction
    #       3. Respond with a JSON object including the original
    #          data and the prediction
    #print("It started")
    sys_BP = request.args.get('sysBP', type=float)
    dias_BP = request.args.get('diasBP', type=float)
    map_BP = (sys_BP + 2 * dias_BP) / 3
    end_window_str = str(0)
    ##print(type(end_window_str))
    start_window_str = str(0)
    print(type(start_window_str))

    pred_input = {'avg_sys':str(sys_BP),
                  'avg_map':str(map_BP),
                  'avg_dias':str(dias_BP),
                  'end_window': end_window_str,
                  'start_window':start_window_str}
    
    predictions = predict_tabular_classification_sample(
        project="741350817607",
        endpoint_id="8317875832869617664",
        location="us-central1",instance_dict=pred_input)
    
    for prediction in predictions:
        current_pred = dict(prediction)
    ##return f"Patient Hypotensive in 15 min prediction: {datetime.utcnow()}"
    return f"Patient Hypotensive in 15 min prediction: {current_pred}"

@application.route('/xgboost_score', methods=["GET", "POST"])
def scoring_route_xgboost():
    """Route to generate a prediction"""
    ## TODO: Stand up a function on this route that will:
    ##       1. Accept a JSON object of the prediction data
    ##       2. Generate a prediction
    ##       3. Respond with a JSON object including the original
    ##          data and the prediction
    json_data = request.json["instances"]
    
    probas = predict_xgb_classification_sample(
        project="741350817607",
        endpoint_id="3560245039017754624",
            location="us-central1", instance_dict=json_data)

    predictions = [1 if x > 0.5 else 0 for x in probas]
    
    return f"Patient Hypotensive in 15 min predictions: {predictions}"


if __name__ == "__main__":
    application.debug=True
    application.run(
        threaded=True,
        host='0.0.0.0',
        port=8080)
