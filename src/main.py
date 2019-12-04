#
# Copyright (c) 2019. Asutosh Nayak (nayak.asutosh@ymail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#

import os
import pandas as pd
from keras.utils import np_utils
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from ga_engine import GAEngine
import numpy as np
import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout
from keras.datasets import mnist
from keras.callbacks import ModelCheckpoint, EarlyStopping
import numpy as np
from logger import Logger
import pickle
from utils import *
from logger import Logger
import datetime
import time

search_space_mlp = {
    'input_size': 784,
    'batch_size': [80, 100, 120],
    'layers': [
        {
            'nodes_layer_1': [10, 50, 60, 80, 500],
            'do_layer_1': [0.0, 0.1, 0.2, 0.3, 0.4],
            'activation_layer_1': ['relu', 'sigmoid']
        },
        {
            'nodes_layer_1': [10, 50, 60, 80, 500],
            'do_layer_1': [0.0, 0.1, 0.2, 0.3, 0.4],
            'activation_layer_1': ['relu', 'sigmoid'],

            'nodes_layer_2': [10, 50, 60, 80, 500],
            'do_layer_2': [0.0, 0.1, 0.2, 0.3, 0.4],
            'activation_layer_2': ['relu', 'sigmoid']
        },
        {
            'nodes_layer_1': [10, 50, 60, 80, 500],
            'do_layer_1': [0.0, 0.1, 0.2, 0.3, 0.4],
            'activation_layer_1': ['relu', 'sigmoid'],

            'nodes_layer_2': [10, 50, 60, 80, 500],
            'do_layer_2': [0.0, 0.1, 0.2, 0.3, 0.4],
            'activation_layer_2': ['relu', 'sigmoid'],

            'nodes_layer_3': [10, 50, 60, 80, 500],
            'do_layer_3': [0.0, 0.1, 0.2, 0.3, 0.4],
            'activation_layer_3': ['relu', 'sigmoid']
        }
    ],
    'lr': [1e-2, 1e-3, 1e-4],
    'epochs': [3000],
    'optimizer': ['rmsprop', 'sgd', 'adam'],
    'output_nodes': 10,
    'output_activation': 'softmax',
    'loss': 'categorical_crossentropy'
}

# search_space_mlp = {
#     'input_size': 4,
#     'batch_size': [10, 50, 100],
#     'layers': [
#         {
#             'nodes_layer_1': [200, 300, 500, 700, 900],
#             'do_layer_1': [0.0, 0.1, 0.2, 0.3, 0.4],
#             'activation_layer_1': ['relu', 'sigmoid']
#         },
#         {
#             'nodes_layer_1': [200, 300, 500, 700, 900],
#             'do_layer_1': [0.0, 0.1, 0.2, 0.3, 0.4],
#             'activation_layer_1': ['relu', 'sigmoid'],
#
#             'nodes_layer_2': [100, 300, 500, 700, 900],
#             'do_layer_2': [0.0, 0.1, 0.2, 0.3, 0.4],
#             'activation_layer_2': ['relu', 'sigmoid']
#         },
#         {
#             'nodes_layer_1': [300, 500, 700, 900],
#             'do_layer_1': [0.0, 0.1, 0.2, 0.3, 0.4],
#             'activation_layer_1': ['relu', 'sigmoid'],
#
#             'nodes_layer_2': [100, 300, 500, 700, 900],
#             'do_layer_2': [0.0, 0.1, 0.2, 0.3, 0.4],
#             'activation_layer_2': ['relu', 'sigmoid'],
#
#             'nodes_layer_3': [100, 300, 500, 700, 900],
#             'do_layer_3': [0.0, 0.1, 0.2, 0.3, 0.4],
#             'activation_layer_3': ['relu', 'sigmoid']
#         }
#     ],
#     'lr': [1e-2, 1e-3, 1e-4, 1e-5],
#     'epochs': [3000],
#     'optimizer': ['rmsprop', 'sgd', 'adam'],
#     'output_nodes': 10,
#     'output_activation': 'softmax',
#     'loss': 'categorical_crossentropy'
# }
OUTPUT_PATH = 'outputs'
test_loss = 0.07
test_acc = 0.99
mode = 'max'
time_limit = 300  # minutes
ga_history_list = []
ga_history_dict = {}
best_scores = []
start_time = get_readable_ctime()
start_time_epoch = datetime.datetime.now()


def get_data_mnist():
    num_classes = 10
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    # print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)
    # print(x_train[1][5])
    x_train = x_train.reshape(x_train.shape[0], x_train.shape[1] * x_train.shape[2])
    x_test = x_test.reshape(x_test.shape[0], x_test.shape[1] * x_test.shape[2])
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    # print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)
    return x_train, y_train, x_test, y_test


def get_data_iris():
    dataframe = pd.read_csv("./inputs/Iris.csv")
    dataset = dataframe.values
    X = dataset[:, 1:5].astype(float)
    Y = dataset[:, 5]
    # encode class values as integers
    encoder = LabelEncoder()
    encoder.fit(Y)
    encoded_y = encoder.transform(Y)
    # convert integers to dummy variables (i.e. one hot encoded)
    dummy_y = np_utils.to_categorical(encoded_y)
    x_train, x_test, y_train, y_test = train_test_split(X, dummy_y, test_size=0.3)
    return x_train, y_train, x_test, y_test


def func_eval(model, **kwargs):
    x_train, y_train, x_test, y_test = get_data_mnist()
    es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=20, min_delta=0.0001)
    history = model.fit(x_train, y_train, batch_size=kwargs['batch_size'], epochs=500, verbose=2,
                        validation_split=0.3, callbacks=[es])
    val_error = np.amin(history.history['val_loss'])
    train_error = np.amin(history.history['loss'])
    log("train/val errors:", train_error, val_error)
    score = model.evaluate(x_test, y_test, verbose=0)  # (loss, accuracy)
    log('eval test keys:', model.metrics_names)
    log('eval test res:', score)
    res_dict = {'train_error': train_error, 'val_error': val_error}
    for i, key in enumerate(model.metrics_names):
        res_dict[key] = score[i]
    ga_history_list.append(res_dict)
    return score[0] if mode == 'min' else score[1]


def exit_check(best_score):
    # return False
    return np.abs(best_score) >= test_acc or ((datetime.datetime.now()-start_time_epoch).seconds/60) >= time_limit


def on_generation_end(best_score, generation_count):
    log("on_generation_end: best_score=", best_score, "generation_count=", generation_count)
    # if generation_count % 5:
    ga_history_dict[generation_count] = ga_history_list.copy()
    ga_history_list.clear()
    best_scores.append(best_score)
    pickle.dump(ga_history_dict, open(os.path.join(OUTPUT_PATH, 'history_' + start_time), 'wb'))
    pickle.dump(best_scores, open(os.path.join(OUTPUT_PATH, 'best_scores_' + start_time), 'wb'))
    log('history dumped...')


def func_eval_dummy(model, **kwargs):
    ga_history_list.append({})
    return np.random.uniform(0, 1, 2)


ga_engine_ = GAEngine(search_space_mlp, mutation_probability=0.3, exit_check=exit_check,
                      on_generation_end=on_generation_end, func_eval=func_eval, population_size=3, opt_mode=mode).run()

plot_iterable(best_scores)
plot_history(pickle.load(open(os.path.join('history_' + start_time), 'rb')))
