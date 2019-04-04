
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
import tensorflow as tf
import tensorflow_hub as hub
import string

from dona_custome_responses import *
from aware import *
from stateful import *
from user import User
from facebook_graphAPI import *


# autopep8 -i dona.py
# parameters
dona = Flask(__name__)
best_of = None
sleep = True
sleep_time = 2
negative_cutoff_world = 0.8
negative_cutoff_others = 0.5
report_awareness_statefulness = False

model_path = "/home/hshallal/dona/universal_sentence_encoder_3"

# A function to report awareness and statefulness


def report_aware_stateful(this_awareness, this_statefulness, this_response):
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


# Preliminary election of a response and the awareness in regards to the user query
# Main prediction function. This is the main brain and it is only based on the
# dot product
def get_a_response(queries, query_emb, best_of, awareness_inst):
    tf.reset_default_graph()
    awareness = awareness_inst.get_awareness(query_emb)[0]
    if awareness == 'w':
        negative_cutoff = negative_cutoff_world
        negative_responses = negative_world_responses
    else:
        negative_cutoff = negative_cutoff_others
        negative_responses = negative_general_responses

    if(queries[0] not in ac_reac_dict.keys()):
        dot_product = np.dot(query_emb, np.array(ac_embeddings).T)
        dot_product = np.ravel(dot_product)

        if best_of == None:
            if np.max(dot_product) >= negative_cutoff:
                best_match = np.argmax(dot_product)
            else:
                best_match = -1

        elif best_of != None:
            options = np.argpartition(dot_product, -best_of)[-best_of:]
            final_options = []
            for n in range(options.shape[0]):
                if dot_product[options[n]] >= negative_cutoff:
                    final_options.append(options[n])

            if len(final_options) > 1:
                best_match = np.random.choice(np.array(final_options))
            elif len(final_options) == 1:
                best_match = final_options[0]
            elif len(final_options) == 0:
                best_match = -1

            # best_match = np.random.choice(np.argpartition(np.ravel(dot_product), -best_of)[-best_of:])

        if best_match == -1:
            final_response = negative_responses[np.random.choice(
                len(negative_responses))]

        elif best_match != -1:
            if len(ac_reac_dict[unique_ac[best_match]]) > 1:
                final_response = np.random.choice(
                    ac_reac_dict[unique_ac[best_match]])
            else:
                final_response = ac_reac_dict[unique_ac[best_match]][0]
        # subprocess.call(["say", final_response])
    else:
        if len(ac_reac_dict[queries[0]]) > 1:
            final_response = np.random.choice(ac_reac_dict[queries[0]])
        else:
            final_response = ac_reac_dict[queries[0]][0]

    return final_response, awareness


print("Functions defined.")

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


# Load data:
actions = pickle.load(open("modified_actions", "rb"))
unique_ac = pickle.load(open("unique_ac", "rb"))
ac_reac_dict = pickle.load(open("ac_reac_dict", "rb"))
ac_embeddings = pickle.load(open("ac_embeddings", "rb"))
print(len(actions), len(unique_ac), len(ac_reac_dict), len(ac_embeddings))
print("Data loaded.")

# Get embeddings for actions to build an awareness model
actions_embeddings = np.array(get_embeddings(actions))

# Instantiate an awareness class instance, train its model, this instance
# will be ready to predict the awareness on the fly
awareness_inst = Awareness(actions_embeddings)
print("actions_awareness_model built.")


# Get embeddings for some statefulness classes and stick all of them in a dict
statefulness_embeddings = {}
statefulness_embeddings['stateful_class_2_emb'] = np.array(
    get_embeddings(stateful_class_2_phrases)).T
statefulness_embeddings['stateful_class_3_last_response_emb'] = np.array(
    get_embeddings(stateful_class_3_last_response_phrases)).T
statefulness_embeddings['stateful_class_3_query_emb'] = np.array(
    get_embeddings(stateful_class_3_query_phrases)).T
statefulness_embeddings['stateful_class_4_emb'] = np.array(
    get_embeddings(stateful_class_4_phrases)).T
statefulness_embeddings['stateful_class_5_emb'] = np.array(
    get_embeddings(stateful_class_5_phrases)).T
print("Statefulness embeddings obtained.")

# Instantiate an instance of Statefulness
statefulness_inst = Statefulness(statefulness_embeddings)
print("statefulness_inst created.")


# This is the model supposed to return awareness, statefulness, and response to
# the controller with access to the database via the user class
def respond(sender, message, this_user_info, this_user_last_two_acs, awareness_inst, statefulness_inst):
    """Formulate a response to the user and pass it on to a function that sends it."""
    queries = []
    queries.append(message.lower())

    # Get certain embeddings once
    query_emb = np.array(get_embeddings(queries))
    # for statefulness
    last_responses = []
    if len(this_user_last_two_acs) > 0:
    	last_responses.append(this_user_last_two_acs[0][1])
    else:
        last_responses.append("")
    last_response_emb = np.array(get_embeddings(last_responses))

    # Get primary response and awareness (works)
    response, awareness = get_a_response(
        queries, query_emb, best_of, awareness_inst)
    print(response + " :before processing")
    print(awareness)


    # Get final response and satatefulness
    modified_response, this_statefulness = statefulness_inst.statefulness(
        message, query_emb,
        response, last_response_emb,
        this_user_info, this_user_last_two_acs)
    #print(modified_response + " :after checking statefulness")
    #print('this_statefulness is: ' + str(this_statefulness))
    # Class-4 statefulness uses get_a_response() which is not in stateful
    # and must be here
    if this_statefulness == 4:
        #print('initial class-4 response: ' + modified_response)
        queries1 = []
        queries1.append(modified_response.lower())
        query_emb1 = np.array(get_embeddings(queries1))
        modified_response, modified_awareness = get_a_response(
            queries1, query_emb1, best_of, awareness_inst)
        #print(modified_response + " :after checking class-4 statefulness")
        #print('this_statefulness is: ' + str(this_statefulness))

    if modified_response == 'stateful_response':
        modified_response = negative_general_responses[np.random.choice(
            len(negative_general_responses))]

    print(modified_response + " :after processing")
    print(this_statefulness)

    if sleep:
        time.sleep(sleep_time)

    return awareness, this_statefulness, modified_response


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

                # send and receive from the model
                this_awareness, this_statefulness, this_response = respond(
                    sender_id, text, this_user_info, this_user_last_two_acs, awareness_inst, statefulness_inst)

                # Send the response or view
                send_message(sender_id, this_response)

                if report_awareness_statefulness:
                    extra_details = report_aware_stateful(
                        this_awareness, this_statefulness, this_response)
                    send_message(sender_id, extra_details)

                # Update the database
                update_info = {}
                update_info['query'] = text
                update_info['response'] = this_response
                update_info['aware'] = this_awareness
                update_info['stateful'] = this_statefulness
                this_user.update_user_info_by_id(sender_id, update_info)

    return "ok"


if __name__ == "__main__":
    dona.run()
