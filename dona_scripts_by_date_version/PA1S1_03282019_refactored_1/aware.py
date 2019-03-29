from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from keras.models import Sequential, model_from_json
import keras.backend as K

from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix

import numpy as np


# Build model
def build_model():
    K.clear_session()
    # create model
    model = Sequential()
    model.add(Dense(1024, input_dim=512, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(5, activation='softmax'))
    # Compile model
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adagrad', metrics=['accuracy'])
    return model


# train and fit model (input X_actions and awarenss)
def train_awareness_model(X_actions, awareness):
    label_encoder = LabelEncoder()
    values = np.array(awareness)
    y_actions = label_encoder.fit_transform(values)
    np.random.seed(1234)
    actions_awareness_model = build_model()
    actions_awareness_model.fit(
        X_actions, y_actions, epochs=50, batch_size=100, verbose=0)
    y_actions_pred = actions_awareness_model.predict_classes(X_actions, verbose=0)
    print(confusion_matrix(y_actions, y_actions_pred))
    print("actions_awareness_model is ready")
    return actions_awareness_model, label_encoder

