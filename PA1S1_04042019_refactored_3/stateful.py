
import time
from datetime import datetime, timedelta
from timeit import default_timer as timer
from dona_custome_responses import *
import numpy as np


def get_time(this_user_info):
    time_there = datetime.utcnow() + timedelta(hours=int(this_user_info[3]))
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
    time_there = datetime.utcnow() + timedelta(hours=int(this_user_info[3]))
    year = time_there.year
    month = time_there.month
    day = time_there.day
    return str(month) + "/" + str(day) + "/" + str(year)


def simple_replacements(this_user_info, response):
    # Simple replacmenets
    if 'user_name' in response:
        if np.random.uniform() >= 0.5:
            name = this_user_info[1]
        else:
            name = this_user_info[1] + ' ' + this_user_info[2]
        response = response.replace('user_name', name)

    if 'user_gender' in response:
        response = response.replace(
            'user_gender', this_user_info[4])

    if 'get_time()' in response:
        response = response.replace(
            'get_time()', get_time(this_user_info))

    if 'get_date()' in response:
        response = response.replace(
            'get_date()', get_date(this_user_info))

    return response

# We need to thinks of how this is going to be implemented
# we want to instantiate one instance of the class for the whole session
# query, response, query_emb, last_response_emb, this_user_info, this_user_last_two_acs


class Statefulness:
    def __init__(self, statefulness_embeddings):

        #  This will be needed for class-3
        self.double_query_pronouns = double_query_pronouns
        self.double_query_pronouns_dahsed = double_query_pronouns_dahsed

        # These are general data members
        self.statefulness_embeddings = statefulness_embeddings

        # Process some data for statefulness
        self.pronoun_pairs = zip(query_pronouns, response_pronouns)
        self.pronoun_pairs_dict = {}
        for x in self.pronoun_pairs:
            self.pronoun_pairs_dict.setdefault(x[0], []).append(x[1])
        print("pronoun_pairs_dict obtained.")

    def process_stateful_class_1(self, query, response, this_user_last_two_acs):
        # class-1 statefulness: user repeating input
        if query == this_user_last_two_acs[0][0] and this_user_last_two_acs[0][0] != this_user_last_two_acs[1][0]:
            response = "I repeat the same response: " + \
                this_user_last_two_acs[0][1]

        elif query == this_user_last_two_acs[0][0] and this_user_last_two_acs[0][0] == this_user_last_two_acs[1][0]:
            response = repeated_query[np.random.choice(len(repeated_query))]
        return response, 1

    def process_stateful_class_3(self, this_user_last_two_acs):

        last_query = this_user_last_two_acs[0][0].lower()

        for n in range(len(self.double_query_pronouns)):
            if self.double_query_pronouns[n] in last_query:
                last_query = last_query.replace(
                    self.double_query_pronouns[n], self.double_query_pronouns_dahsed[n])

        word_list = last_query.split()

        for n in range(len(word_list)):
            if word_list[n] in self.pronoun_pairs_dict.keys() and word_list[n] == 'you':
                if n == 0:
                    word_list[n] = 'i'
                else:
                    word_list[n] = 'me'
            elif word_list[n] in self.pronoun_pairs_dict.keys() and word_list[n] != 'you':
                replacmenet = self.pronoun_pairs_dict[word_list[n]][0]
                word_list[n] = replacmenet
        output = ' '.join(word for word in word_list)

        if output[0] == "i" and output[1] != "t":
            output = output.capitalize()
        return output

    def process_stateful_class_2_3_5(self, input_emb, statefulness_embeddings_key):
        stateful_ar = np.dot(
            input_emb, self.statefulness_embeddings[statefulness_embeddings_key])[0].tolist()
        stateful_class = len([True for i in stateful_ar if i > 0.99])
        return stateful_class

    def determine_stateful_class(self, query, query_emb, last_response_emb, response):
        if response == 'stateful_response':
            # process classes
            stateful_class_2 = self.process_stateful_class_2_3_5(
                query_emb, 'stateful_class_2_emb')

            stateful_class_3_last_response = self.process_stateful_class_2_3_5(
                last_response_emb, 'stateful_class_3_last_response_emb')
            stateful_class_3_query = self.process_stateful_class_2_3_5(
                query_emb, 'stateful_class_3_query_emb')

            stateful_class_5 = self.process_stateful_class_2_3_5(
                query_emb, 'stateful_class_5_emb')

            # Return
            if stateful_class_2 > 0:
                return 2
            elif stateful_class_3_last_response > 0 and stateful_class_3_query > 0:
                return 3
            elif stateful_class_5 > 0:
                return 5

        elif response != 'stateful_response':
            # Check class-4: two methods one covering for the other: we don't demand stateful_response as a respons here!
            stateful_class_4 = self.process_stateful_class_2_3_5(
                query_emb, 'stateful_class_4_emb')
            if stateful_class_4 == 0:

                for n in stateful_class_4_phrases_checks:
                    if n in query:
                        stateful_class_4 = 1
            # Return
            if stateful_class_4 > 0:
                return 4
            else:
                return -1

    def statefulness(self, query, query_emb, response, last_response_emb, this_user_info, this_user_last_two_acs):

        this_stateful_class = -1

        if len(this_user_last_two_acs) > 0:

            # class-2, 3, 4, 5 statefulness
            this_stateful_class = self.determine_stateful_class(query,
                                                                query_emb, last_response_emb, response)

            if this_stateful_class == 2:
                response = this_user_last_two_acs[0][1]

            elif this_stateful_class == 3:
                last_query = self.process_stateful_class_3(
                    this_user_last_two_acs)
                response = "I thought you just said " + last_query

            elif this_stateful_class == 4:
                response = this_user_last_two_acs[0][1]

            elif this_stateful_class == 5:
                response = " "

        # simple replacements
        response = simple_replacements(this_user_info, response)

        # Check class-1
        if len(this_user_last_two_acs) > 1 and query == this_user_last_two_acs[0][0]:
            response, this_stateful_class = self.process_stateful_class_1(
                query, response, this_user_last_two_acs)

        return response, this_stateful_class
