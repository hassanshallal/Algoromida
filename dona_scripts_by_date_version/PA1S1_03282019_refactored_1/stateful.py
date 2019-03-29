
import time
from datetime import datetime, timedelta
from timeit import default_timer as timer
from dona_custome_responses import *
import numpy as np


def get_time(this_user_info):
    time_there = datetime.utcnow() + timedelta(hours=int(this_user_info[4]))
    hour = time_there.hour
    minute = time_there.minute
    period = " AM"
    if hour > 12:
        hour = hour - 12
        period = " PM"

    if minute < 10:
        minute = str(0) + str(minute)
    else:
        minute = str(minute)

    return str(hour) + ":" + minute + period


def get_date(this_user_info):
    time_there = datetime.utcnow() + timedelta(hours=int(this_user_info[4]))
    year = time_there.year
    month = time_there.month
    day = time_there.day
    return str(month) + "/" + str(day) + "/" + str(year)


def process_stateful_class_1(query, response, this_user_last_two_acs):
    #print("d")
    #print(query + " is the query")
    #print(this_user_last_two_acs[0][0] + " is this_user_last_two_acs[0][0]")
    #print(this_user_last_two_acs[1][0] + " is this_user_last_two_acs[1][0]")
    # class-1 statefulness
    if query == this_user_last_two_acs[0][0] and this_user_last_two_acs[0][0] != this_user_last_two_acs[1][0]:
        #print("b")
        response = "I repeat the same response: " + this_user_last_two_acs[0][1]

    elif query == this_user_last_two_acs[0][0] and this_user_last_two_acs[0][0] == this_user_last_two_acs[1][0]:
        #print("class_1_statefulness_detected")
        response = repeated_query[np.random.choice(len(repeated_query))]
    return response, 1

def process_stateful_class_3(last_query, pronoun_pairs_dict, double_query_pronouns, double_query_pronouns_dahsed):
    #print('attempting class_3 processing')
    for n in range(len(double_query_pronouns)):
        if double_query_pronouns[n] in last_query:
            last_query = last_query.replace(
                double_query_pronouns[n], double_query_pronouns_dahsed[n])

    word_list = last_query.split()

    for n in range(len(word_list)):
        if word_list[n] in pronoun_pairs_dict.keys() and word_list[n] == 'you':
            if n == 0:
                word_list[n] = 'i'
            else:
                word_list[n] = 'me'
        elif word_list[n] in pronoun_pairs_dict.keys() and word_list[n] != 'you':
            replacmenet = pronoun_pairs_dict[word_list[n]][0]
            word_list[n] = replacmenet
    output = ' '.join(word for word in word_list)
    
    if output[0] == "i" and output[1] != "t":
        output = output.capitalize()
    return output


def determine_stateful_class(query, query_emb, last_response_emb, response, statefulness_embeddings):
    #print('beging checking statefulness class!')
    
    if response == 'stateful_response':
        # Check class-2
        #print('class-2 primary check')
        stateful_class_2_ar = np.dot(query_emb, statefulness_embeddings['stateful_class_2_emb'])[0].tolist()
        stateful_class_2 = len([True for i in stateful_class_2_ar if i > 0.99])
    
        # Check class-3
        #print('class-3 primary check')
        stateful_class_3_last_response_ar = np.dot(
            last_response_emb, statefulness_embeddings['stateful_class_3_last_response_emb'])[0].tolist()
        stateful_class_3_last_response = len(
            [True for i in stateful_class_3_last_response_ar if i > 0.99])

        stateful_class_3_query_ar = np.dot(
            query_emb, statefulness_embeddings['stateful_class_3_query_emb'])[0].tolist()
        stateful_class_3_query = len(
            [True for i in stateful_class_3_query_ar if i > 0.99])
    
         # Check class-5:    
        #print('class-5 primary check')
        stateful_class_5_ar = np.dot(query_emb, statefulness_embeddings['stateful_class_5_emb'])[0].tolist()
        stateful_class_5 = len([True for i in stateful_class_5_ar if i > 0.99])
        
        # Return
        if stateful_class_2 > 0:
            return 2
        elif stateful_class_3_last_response > 0 and stateful_class_3_query > 0:
            return 3
        elif stateful_class_5 > 0:
            return 5

    elif response != 'stateful_response':
        # Check class-4: two methods one covering for the other: we don't demand stateful_response as a respons here!
        #print('class-4 primary check')
        stateful_class_4_ar = np.dot(query_emb, statefulness_embeddings['stateful_class_4_emb'])[0].tolist()
        stateful_class_4 = len([True for i in stateful_class_4_ar if i > 0.99])

        if stateful_class_4 == 0:
            #print('class-4 secondary check')
            for n in stateful_class_4_phrases_checks:
                if n in query:
                    stateful_class_4 = 1
        # Return
        if stateful_class_4 > 0:
            return 4
        else:
            return -1


def statefulness(query, query_emb, response, last_response_emb, this_user_info, this_user_last_two_acs, statefulness_embeddings, pronoun_pairs_dict):
    this_stateful_class = -1
    if len(this_user_last_two_acs) > 0:
        # class-2, 3, 4, 5 statefulness
        #print('checking statefulness class!')
        this_stateful_class = determine_stateful_class(query,
            query_emb, last_response_emb, response, statefulness_embeddings)
        if this_stateful_class == 2:
            #print("class_2_statefulness_detected")
            response = this_user_last_two_acs[0][1]  # last response
        elif this_stateful_class == 3:
            last_query = this_user_last_two_acs[0][0]
            last_query = process_stateful_class_3(last_query.lower(), pronoun_pairs_dict, double_query_pronouns, double_query_pronouns_dahsed)
            #print("class_3_statefulness_detected")
            response = "I thought you just said " + last_query
        elif this_stateful_class == 4:
            #last_response = []
            #last_response.append(this_user_last_two_acs[0][1])
            # respond to its last response
            #print("class_4_statefulness_detected")
            #response, awareness = get_a_response(last_response, best_of)
            response = this_user_last_two_acs[0][1]
        elif this_stateful_class == 5:
            #print("class_5_statefulness_detected")
            response = " "
            
    # Simple replacmenets
    if 'user_name' in response:
        if np.random.uniform() >= 0.5:
            name = this_user_info[1]
        else:
            name = this_user_info[1] + ' ' + this_user_info[2]
        response = response.replace('user_name', name)
    
    if 'user_gender' in response:
        response = response.replace(
            'user_gender', this_user_info[5])
    
    if 'get_time()' in response:
        response = response.replace(
            'get_time()', get_time(this_user_info))
    
    if 'get_date()' in response:
        response = response.replace(
            'get_date()', get_date(this_user_info))
        
    
    # Check class-1
    if len(this_user_last_two_acs) > 1 and query == this_user_last_two_acs[0][0]:
        #print("repeat queries")
        response, this_stateful_class = process_stateful_class_1(
            query, response, this_user_last_two_acs)
        #print(response)
        #print(this_stateful_class)
    
    
    return response, this_stateful_class