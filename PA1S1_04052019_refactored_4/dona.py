
# In this system, we implemented MVC for the UI and a Facade for the model of the MVC.

# Import modules
from flask import Flask
from flask import request
from flask import render_template

import requests

import pickle
import time
from datetime import datetime, timedelta
from timeit import default_timer as timer
from os import system
import string
import numpy as np

import tensorflow as tf
import tensorflow_hub as hub

# Import respond (Facade pattern of the model), other classes needed by the controller
from respond import *
from user import User
from facebook_graphAPI import *


# autopep8 -i dona.py
# parameters

dona = Flask(__name__)
best_of = None
report_awareness_statefulness = False

model_path = "/home/hshallal/dona/universal_sentence_encoder_3"

# A function to report awareness and statefulness
def report_aware_stateful(this_awareness, this_statefulness):
    # This is for illustration purposes only. We can
    # have a video on youtube and take it from there.

    aware_description = ''
    if this_awareness == 'g':
        aware_description = 'Dona assumes that your message is about a general topic.'
    elif this_awareness == 's':
        aware_description = 'Dona assumes that your message is about Dona.'
    elif this_awareness == 'u':
        aware_description = 'Dona assumes that your message is about yourself.'
    elif this_awareness == 'us':
        aware_description = 'Dona assumes that your message is about both Dona and yourself.'
    elif this_awareness == 'w':
        aware_description = 'Dona assumes that your message is about the world.'

    stateful_descriptios = ''
    if this_statefulness == 1:
        stateful_descriptios = 'Dona thinks that you are repeating your input.'
    elif this_statefulness == 2:
        stateful_descriptios = 'Dona thinks that you want Dona to repeat its last response!'
    elif this_statefulness == 3:
        stateful_descriptios = "Dona thinks you're asking it by referring  to your eralier input!."
    elif this_statefulness == 4:
        stateful_descriptios = "Dona thinks you're asking about its take on something you both are discussing."
    elif this_statefulness == 5:
        stateful_descriptios = 'Dona thinks you asked it to stop chatting or stop communicating.'

    return aware_description + '\n' + stateful_descriptios


# A function to get embeddings from the tensorflow graph in the model
def get_embeddings(list_of_sentences):
    #start = timer()
    tf.reset_default_graph()
    messages_embeddings = []

    tf.logging.set_verbosity(tf.logging.ERROR)
    message_embeddings = session.run(embedded_text, feed_dict={
                                     text_input: list_of_sentences})
    for i, message_embedding in enumerate(np.array(message_embeddings).tolist()):
        message_embedding_snippet = ", ".join(
            (str(x) for x in message_embedding[:3]))
        messages_embeddings.append(message_embedding)
    #end = timer()
    #print(end - start)
    return messages_embeddings

# Create session and initialize.
g = tf.Graph()
with g.as_default():
    # We will be feeding 1D tensors of text into the graph.
    text_input = tf.placeholder(dtype=tf.string, shape=[None])
    embed = hub.Module(model_path)
    embedded_text = embed(text_input)
    init_op = tf.group(
        [tf.global_variables_initializer(), tf.tables_initializer()])
g.finalize()
session = tf.Session(graph=g)
session.run(init_op)
print('Transformer loaded.')

# Get embeddings for actions
actions = pickle.load(open("modified_actions", "rb"))
actions_embeddings = np.array(get_embeddings(actions))
print("Actions embeddings obtained.")

# Get embeddings for some statefulness classes and stick all of them in a dict
statefulness_embeddings = {}
statefulness_embeddings['stateful_class_2_emb'] = np.array(get_embeddings(stateful_class_2_phrases)).T
statefulness_embeddings['stateful_class_3_last_response_emb'] = np.array(get_embeddings(stateful_class_3_last_response_phrases)).T
statefulness_embeddings['stateful_class_3_query_emb'] = np.array(get_embeddings(stateful_class_3_query_phrases)).T
statefulness_embeddings['stateful_class_4_emb'] = np.array(get_embeddings(stateful_class_4_phrases)).T
statefulness_embeddings['stateful_class_5_emb'] = np.array(get_embeddings(stateful_class_5_phrases)).T
print("Statefulness embeddings obtained.")

# This is the model (implemented as a Facade pattern) supposed to
# return awareness, statefulness, and response to
# the controller with access to the database via the user class
respond_inst = Respond(best_of, actions_embeddings, statefulness_embeddings)




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

                # Get user data from the database
                this_user = User(sender_id)
                this_user_info, this_user_last_two_acs = this_user.get_user_info_by_id(
                    sender_id)
                print(this_user_info)
                print(this_user_last_two_acs)

                # Compute embeddings to pass to a Response Facade instance.
                queries = []
                queries.append(text.lower())
                
                # query embeddings
                query_emb = np.array(get_embeddings(queries))
                # last response enbeddings
                last_responses = []
                if len(this_user_last_two_acs) > 0:
                    last_responses.append(this_user_last_two_acs[0][1])
                else:
                    last_responses.append("")
                last_response_emb = np.array(get_embeddings(last_responses))
                
                
                # send and receive from the model
                this_awareness, this_statefulness, this_response = respond_inst.respond(sender_id, this_user_info, this_user_last_two_acs, queries, query_emb, last_response_emb, best_of)
                
                # Class-4 statefulness uses get_a_response() which is not in stateful
                # and must be here
                if this_statefulness == 4:
                    queries1 = []
                    queries1.append(this_response.lower())
                    query_emb1 = np.array(get_embeddings(queries1))
                    this_response, modified_awareness = respond_inst.get_a_response(queries1, query_emb1, best_of)
            
            
                if this_response == 'stateful_response':
                    this_response = negative_general_responses[np.random.choice(len(negative_general_responses))]
                        
                # Send the response or view
                send_message(sender_id, this_response)

                if report_awareness_statefulness:
                    extra_details = report_aware_stateful(
                        this_awareness, this_statefulness, this_response)
                    send_message(sender_id, extra_details)

                # Update the database
                update_info = {}
                update_info['query'] = text.lower()
                update_info['response'] = this_response
                update_info['aware'] = this_awareness
                update_info['stateful'] = this_statefulness
                this_user.update_user_info_by_id(sender_id, update_info)

    return "ok"


if __name__ == "__main__":
    dona.run()
