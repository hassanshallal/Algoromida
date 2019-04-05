import pickle
import time
from datetime import datetime, timedelta
from timeit import default_timer as timer
from os import system
import string
import numpy as np

from dona_custome_responses import *
from aware import *
from stateful import *


sleep = True
sleep_time = 2
negative_cutoff_world = 0.8
negative_cutoff_others = 0.5

# This is a Facade pattern design in which the model of the MVC is a Facade of
# two classes: awareness and statefulness

class Respond:
    def __init__(self, best_of, actions_embeddings, statefulness_embeddings):
        self.actions = pickle.load(open("modified_actions", "rb"))
        self.unique_ac = pickle.load(open("unique_ac", "rb"))
        self.ac_reac_dict = pickle.load(open("ac_reac_dict", "rb"))
        self.ac_embeddings = pickle.load(open("ac_embeddings", "rb"))
        print(len(self.actions), len(self.unique_ac), len(self.ac_reac_dict), len(self.ac_embeddings))
        print("Data loaded.")
        
        self.awareness_inst = Awareness(actions_embeddings)
        print("actions_awareness_model built.")
        
        self.statefulness_inst = Statefulness(statefulness_embeddings)
        print("statefulness_inst created.")
     
    def get_a_response(self, queries, query_emb, best_of):
 
        # First make a decison of your dot product cutoff based on awareness
        awareness = self.awareness_inst.get_awareness(query_emb)[0]
        if awareness == 'w':
            negative_cutoff = negative_cutoff_world
            negative_responses = negative_world_responses
        else:
            negative_cutoff = negative_cutoff_others
            negative_responses = negative_general_responses

        # If message or quries are new
        if(queries[0] not in self.ac_reac_dict.keys()):
            dot_product = np.dot(query_emb, np.array(self.ac_embeddings).T)
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

            if best_match == -1:
                final_response = negative_responses[np.random.choice(
                    len(negative_responses))]

            elif best_match != -1:
                if len(self.ac_reac_dict[self.unique_ac[best_match]]) > 1:
                    final_response = np.random.choice(
                        self.ac_reac_dict[self.unique_ac[best_match]])
                else:
                    final_response = self.ac_reac_dict[self.unique_ac[best_match]][0]
            # subprocess.call(["say", final_response])
        # The user's input is known
        else:
            if len(self.ac_reac_dict[queries[0]]) > 1:
                final_response = np.random.choice(self.ac_reac_dict[queries[0]])
            else:
                final_response = self.ac_reac_dict[queries[0]][0]

        return final_response, awareness


    def respond(self, sender, this_user_info, this_user_last_two_acs, queries, query_emb, last_response_emb, best_of):
            
            # Get primary response and awareness (works)
            response, awareness = self.get_a_response(queries, query_emb, best_of)
            #print(response + " :before processing")
            #print(awareness)

            # Get final response and satatefulness
            modified_response, this_statefulness = self.statefulness_inst.statefulness(
                queries[0], query_emb,
                response, last_response_emb,
                this_user_info, this_user_last_two_acs)
            
            #print(modified_response + " :after checking statefulness")
            #print('this_statefulness is: ' + str(this_statefulness))
            
            if sleep:
                time.sleep(sleep_time)

            return awareness, this_statefulness, modified_response
        
        
        
        
        
        
        
        
        
