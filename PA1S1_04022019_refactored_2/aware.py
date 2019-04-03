from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from keras.models import Sequential, model_from_json
import keras.backend as K

from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix

import warnings
import numpy as np
import pickle



class Awareness:
    
    # We can change the architecture of the awareness model here without
    # the client having access to how is this accomplished.
    
    # So actions_embeddings are passed to the instance upon instantiation from the
    # controller of the MVC
    
    def __init__(self, actions_embeddings):
        self.actions_embeddings  = actions_embeddings
        self.awareness_list = pickle.load(open("awareness", "rb"))
        self.label_encoder = LabelEncoder()
        self.values = np.array(self.awareness_list)
        self.y_actions = self.label_encoder.fit_transform(self.values)
        
        # Instantiate and train a model
        np.random.seed(1234)
        K.clear_session()
        self.model = Sequential()
        self.model.add(Dense(1024, input_dim=512, activation='relu'))
        self.model.add(Dense(256, activation='relu'))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(5, activation='softmax'))
        # Compile model
        self.model.compile(loss='sparse_categorical_crossentropy',
                      optimizer='adagrad', metrics=['accuracy'])
        self.model.fit(self.actions_embeddings, self.y_actions, epochs=50, batch_size=100, verbose=0)
        self.y_actions_pred = self.model.predict_classes(self.actions_embeddings, verbose=0)
        print(confusion_matrix(self.y_actions, self.y_actions_pred))
    
    
    # A function to exercise some level of awareness over the user's query
    # here, we pass query_emb from MVC
    def get_awareness(self, query_emb):
        warnings.filterwarnings(action='ignore', category=DeprecationWarning)
        prediction = self.model.predict_classes(query_emb, verbose=0)
        y_prediction = self.label_encoder.inverse_transform(prediction)
        return y_prediction

