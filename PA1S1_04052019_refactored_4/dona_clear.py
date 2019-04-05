
# This is the extra refactored and object-oriented version of the system to be deployed on 04/02/2019
from flask import Flask
from flask import request
from flask import render_template

import requests

import pickle
import time
from datetime import datetime, timedelta
from timeit import default_timer as timer
from os import system
import numpy as np

from user import User
from facebook_graphAPI import *


# autopep8 -i dona.py
# parameters
dona = Flask(__name__)

# This is the controller of the MVC pattern. Use it to access user info
# send it to the model and recieve the awareness, statefulness, response
@dona.route("/webhook", methods=['GET', 'POST'])
def listen():
    """This is the main function flask uses to
        listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        print(payload)
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']


                # Send the response or view
                send_message(sender_id, "system is under maintainence, will be back very soon")


    return "ok"


if __name__ == "__main__":
    dona.run()
