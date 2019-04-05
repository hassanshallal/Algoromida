

# This is when Dona fail to come up with an answer in other than world related situations.
negative_general_responses = ["I don't know.",
                              "I'm not quite sure about that.",
                              "I'll pass on this.",
                              "I find this a little bit confusing.",
                              "I don't know how to respond to this."]
# This is when Dona realizes it doesn't know something about the world.
negative_world_responses = ["I don't know this specific information.",
                            "I am not aware of this specific information."]

# This is when the user keeps repeating the query over and over again
repeated_query = ["Why are you repeating this over and over again?",
                  "Again!", "I can tell this is the same!"]


# This is to allow Dona to respond to a user asking it to repeat.
stateful_class_2_phrases = ["what?", "what's that?", "what's this?",
                            "what is that?", "what is this?", "say that again!", "repeat that again.", "say this again", "say it again", "repeat this.", "repeat it."]

# This is to allow Dona to exercise class-3 statefulness
stateful_class_3_last_response_phrases = ["Oh, I see.", "I see.", "I see that.", "I see this.", "I can see.", "That's true.", "That is true."]
stateful_class_3_query_phrases = [
    "What do you see?", "See what!", "What's true?", "What is true?"]

# Dona substituting pronouns after realizing class_3 statefulness
query_pronouns = ["i", "i'm", "my", "mine", "me", "myself", "you", "you",  "you're", "your", "yours", "yourself", "i?", "mine?", "me?", "myself?", "you?", "you?", "yours?", "yourself?", "i!", "mine!", "me!", "myself!", "you!", "you!", "yours!", "yourself!", "i_am", "you_are", "am_i", "are_you", "i've", "you've", "i_have", "you_have", "have_i", "have_you"]
response_pronouns = ["you", "you're", "your", "yours", "you", "yourself",  "me", "i",  "i'm",  "my", "mine", "myself", "you?", "yours?", "you?", "yourself?", "me?", "i?", "mine?", "myself?", "you!", "yours!", "you!", "yourself!", "me!", "i!", "mine!", "myself!", "you are", "i am", "are you", "am i", "you've", "i've", "you have", "i have", "have you", "have i"]
assert len(query_pronouns) == len(response_pronouns)

double_query_pronouns = ["i am", "you are", "am i", "are you", "i have", "you have", "have i", "have you"]
double_query_pronouns_dahsed = ["i_am", "you_are", "am_i", "are_you", "i_have", "you_have", "have_i", "have_you"]
assert len(double_query_pronouns) == len(double_query_pronouns_dahsed)


# This is to allow Dona to practice class-4 statefulness
stateful_class_4_phrases_checks = ['how about you', 'what about you', 'how about yourself', 'what about yourself']

stateful_class_4_phrases = ["I think so, how about you?", "how about you?", "how about yourself?", "yes, how about you?", "no, how about you?", "I think so, what about you?", "what about you?", "what about yourself?", "yes, what about you?", "no, what about you?"]

# This is to allow Dona to practice class-5 statefulness
stateful_class_5_phrases = ["Can you stop chatting?", "Can you stop talking?",
"Can you stop typing?", "Just stop.", "Stop.", "stop it.", "shut up."]

stateful_class_5_responses = ["", "Alright!"]
