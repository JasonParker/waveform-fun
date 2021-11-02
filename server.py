from flask import Flask, abort, redirect, request


application = Flask(__name__)


@application.route('/ping')
def home_page():
    """Health check route to ensure app is running."""
    return "pong", 201, {'Content-type':'text/html'}


if __name__ == "__main__":
    application.run()