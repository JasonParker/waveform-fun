from datetime import datetime
from flask import Flask, abort, redirect, request
import os

application = Flask(__name__)


@application.route('/ping')
def home_page():
    """Health check route to ensure app is running."""
    return "pong", 201, {'Content-type':'text/html'}


@application.route('/train')
def training_route():
    """Route to initiate model training"""
    ## TODO: Connect this with modeling pipeline code
    ##       Maybe you want to use a thread or similar to enable
    ##       sending a success response to the requester immediately
    ##       rather than waiting for the entire training pipeline to run.
    return f"Model training initiated at {datetime.utcnow()}"


@application.route('/score')
def scoring_route():
    """Route to generate a prediction"""
    ## TODO: Stand up a function on this route that will:
    ##       1. Accept a JSON object of the prediction data
    ##       2. Generate a prediction
    ##       3. Respond with a JSON object including the original
    ##          data and the prediction
    return f"Model training initiated at {datetime.utcnow()}"


if __name__ == "__main__":
    application.run(
        threaded=True,
        host='0.0.0.0',
        port=8080)