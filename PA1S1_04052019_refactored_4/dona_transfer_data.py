from flask import Flask
from flask import request
from flask import render_template

import requests
import sqlite3

import pickle
import time
import datetime
from timeit import default_timer as timer
from os import system
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import string

from user import User


# autopep8 -i dona.py
#FB_API_URL = 'https://www.facebook.com/Dona-chatbot-1349153491892581/?modal=admin_todo_tour'
FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = 'BtdlRsV5l9TeXx/OHmZ1ff/69NfQqNSzKS57mK/RGzE='
PAGE_ACCESS_TOKEN = 'EAAQOaId8zLsBAIEH3YluxPUnlZAQUAEdngPbtCC85qsZCnKRsOKSi8ZC2SwLsig697SZA9GsyuqjETSTQwgSXTyzA1Ygoe1pDIZAKYyiVNCyvaYPguCsq6YFGOXiv9bnLYp8jMZCmqJWh9BUB4tvI5UOULWdO88mvzfoYOAPcfFgZDZD'

# parameters
dona = Flask(__name__)
best_of = 5

# Load data: movie_
unique_ac = pickle.load(open("unique_ac", "rb"))
ac_reac_dict = pickle.load(open("ac_reac_dict", "rb"))
ac_embeddings = pickle.load(open("ac_embeddings", "rb"))


g = tf.Graph()
with g.as_default():
    # We will be feeding 1D tensors of text into the graph.
    text_input = tf.placeholder(dtype=tf.string, shape=[None])
    embed = hub.Module("/home/hshallal/dona/universal_sentence_encoder_2")
    embedded_text = embed(text_input)
    init_op = tf.group(
        [tf.global_variables_initializer(), tf.tables_initializer()])
g.finalize()

# Create session and initialize.
session = tf.Session(graph=g)
session.run(init_op)


# Main prediction function
def get_a_response(queries, best_of=None):
    tf.reset_default_graph()
    if(queries[0] not in ac_reac_dict.keys()):
        queries_embeddings = session.run(
            embedded_text, feed_dict={text_input: queries})
        dot_product = np.dot(np.array(queries_embeddings),
                             np.array(ac_embeddings).T)
        if best_of == None:
            best_match = np.argmax(dot_product)
        else:
            best_match = np.random.choice(np.argpartition(
                np.ravel(dot_product), -best_of)[-best_of:])

        if len(ac_reac_dict[unique_ac[best_match]]) > 1:
            final_response = np.random.choice(
                ac_reac_dict[unique_ac[best_match]])
        else:
            final_response = ac_reac_dict[unique_ac[best_match]][0]
    #subprocess.call(["say", final_response])
    else:
        if len(ac_reac_dict[queries[0]]) > 1:
            final_response = np.random.choice(ac_reac_dict[queries[0]])
        else:
            final_response = ac_reac_dict[queries[0]][0]
    time.sleep(2)
    return final_response
# USER class


class USER:
    # Initializer / Instance Attributes
    def __init__(self, ID):
        self.ID = ID
        target_link = 'https://graph.facebook.com/v2.6/' + ID
        params = (('fields', 'first_name, last_name, locale, timezone, gender'),
                  ('access_token', PAGE_ACCESS_TOKEN),)
        self.response = requests.get(target_link, params=params)
        user_info = self.response.text
        user_info = user_info[1:len(user_info)-1]
        user_info = user_info.replace('"', '')
        user_info = user_info.replace(',', ', ')
        user_info = [x.strip() for x in user_info.split(',')]
        self.first_name = user_info[0].split(":")[1]
        self.last_name = user_info[1].split(":")[1]
        self.locale = user_info[2].split(":")[1]
        self.timezone = user_info[3].split(":")[1]
        self.gender = user_info[4].split(":")[1]
        self.interaction_time = []
        self.user_queries = []
        self.dona_responses = []


# You upload the user_dict after the definition of the USER class
user_dict = pickle.load(open("user_dict", "rb"))

# transferring data from user_dict to users.db
connection = sqlite3.connect('users.db')
cursor = connection.cursor()
insert_query = "INSERT INTO userInteractions VALUES (?, ?, ?, ?)"
for this_id in user_dict.keys():
    this_user = user_dict[this_id]
    check_user = User(this_user.ID)
    for n in range(len(this_user.interaction_time)):
        this_interaction = (this_user.ID,
                            this_user.user_queries[n],
                            this_user.dona_responses[n],
                            this_user.interaction_time[n])

        cursor.execute(insert_query, this_interaction)
        connection.commit()
connection.close()

# https://www.datacamp.com/community/tutorials/facebook-chatbot-python-deploy


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    return result
# https://www.google.com/search?client=safari&rls=en&q=simplejson.errors.JSONDecodeError:+Expecting+value:+line+1+column+1+(char+0)&ie=UTF-8&oe=UTF-8


def respond(sender, message):
    """Formulate a response to the user and
        pass it on to a function that sends it."""
    queries = []
    queries.append(message)
    response = get_a_response(queries)
    send_message(sender, response)

    # We need a function to process response based on what we have.
    # response = response.replace('user_name', user_dict[sender].first_name)

    this_user = User(sender)
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    insert_query = "INSERT INTO userInteractions VALUES (?, ?, ?, ?)"
    this_interaction = (sender,
                        message,
                        response,
                        str(datetime.datetime.now()))

    cursor.execute(insert_query, this_interaction)
    connection.commit()
    connection.close()


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


'''
@dona.route("/")
def home():
    return render_template("index.html")

@dona.route("/get")
def get_bot_response():
    text = request.args.get('msg')
    queries = []
    queries.append(text)
    final_response = get_a_response(queries, best_of)
    return str(final_response)
'''


@dona.route("/webhook", methods=['GET', 'POST'])
def listen():
    """This is the main function flask uses to
        listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                # print(sender_id)
                respond(sender_id, text)
    return "ok"


if __name__ == "__main__":
    dona.run()
