# https://colab.research.google.com/drive/1KuzxUPUL3Y50xQFk8RvsfWDx88vDitZS#scrollTo=WB6Z4ASd5vMX
# https://towardsdatascience.com/deep-reinforcement-learning-pong-from-pixels-keras-version-bf8a0860689f

# success 1 - ft.lev - seeds 61213 - gamma = 0.99 - n_observations = 19 - n_actions = 2
# game.model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
# used non-normalized (non-diffed) observations
# successfully lowers loss to a larger negative value in 1000 episodes
# need to investigate why that doesn't mean higher reward?
# run.py ft.lev 1 cem render

# success 2
# used diffed observations
# successfully increases average score
# plays beautifully until about 600 episodes
# seems to converge at gas only
# very different learning times

# success 3 - n_actions = 3
# game.model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
# increases average reward until around 1000 - 1500 episodes
# score 45.05 at episode 1271
# seems to converge at gas only after 5000 episodes

# success 4 - ribotai0.lev - seeds 43364 - n_actions = 2
# beat some good human players of this battle https://elma.online/battles/152353
# https://elma.online/r/qvw6j5erj6
# in less than 600 episodes
# run.py ribotai0.lev 1 cem render

# success 5 - changing observations to n_observations 17:
# 8 core positions + body rotation + speeds + direction
# Processing 15 times faster than playing in realtime
# note that this result was reached even with:
# BUG here with prediction always on frame 0
# almost same result as old observations:
# git checkout 44935e0e4b2f91efcde541921d34922def761137
# episode 0, lowscore: -1.89, time: 8.02, died: True, finished: False, seed 28460
# episode 1, lowscore: -1.91, time: 8.31, died: True, finished: False, seed 28460
# episode 2, lowscore: -2.04, time: 7.39, died: True, finished: False, seed 28460
# time: 7.87 in 1332 episodes, seed 28460
# time: 7.86 in 1354 episodes, seed 88148
# time: 7.77 in 309 episodes after above, loaded with seed 41532

# success 6 - actions AR
# alternative version of ribotAI0.lev
# Processing 16 times faster than playing in realtime
# finishing lev actually using R in 1520 episode
# improving best time using R ranging from 9:69 to 9:22, last one in 4867 episodes

# after further investigation, speeds should probably not be observed
# as they are the actual observation

import numpy as np
import random, os
#import gym

import tensorflow as tf
from keras.models import Sequential, load_model
#from keras.layers import Dense, Flatten, Activation
from keras.layers import Dense, MaxPool2D, Flatten, Activation, Conv2D
from keras.optimizers import rmsprop
import keras.backend as K

#%matplotlib inline
#env = gym.make("PongDeterministic-v4")
#env.env.get_action_meanings()
#['NOOP', 'FIRE', 'RIGHT', 'LEFT', 'RIGHTFIRE', 'LEFTFIRE']
#action_space = [4,5] #[No-op, up, down]

print("\nEnter CEM Keras CEM: softmax, sparse_categorical_crossentropy and optimizer rmsprop\n")

def init_model(game):
    tf.random.set_seed(game.seed)
    if game.load is not None:
        game.model = load_model("keras_models\\%s" % (game.load))
    else:
        game.model = Sequential()
        #game.model.add(Conv2D(4, kernel_size=(3,3), padding='same', activation='relu', input_shape = (1,) + (game.n_observations, )))
        game.model.add(Conv2D(4, kernel_size=(3,3), padding='same', activation='relu', input_shape = (game.n_observations, 1, 1)))
        #game.model.add(Conv2D(4, kernel_size=(3,3), padding='same', activation='relu', input_shape = (80,80,1)))

        # shape too small for further pooling: https://stackoverflow.com/a/47325544
        #game.model.add(MaxPool2D(pool_size=(2, 2)))
        #game.model.add(Conv2D(8, kernel_size=(3,3), padding='same', activation='relu'))
        #game.model.add(MaxPool2D(pool_size=(2, 2)))
        #game.model.add(Conv2D(12, kernel_size=(3,3), padding='same', activation='relu'))
        #game.model.add(MaxPool2D(pool_size=(2, 2)))
        #game.model.add(Conv2D(16, kernel_size=(3,3), padding='same', activation='relu'))
        #game.model.add(MaxPool2D(pool_size=(2, 2)))
        game.model.add(Flatten())
        game.model.add(Dense(game.n_actions, activation=game.activation))
        game.model.compile(optimizer=game.optimizer, loss=game.loss)
    game.model.summary()
    """
    # model from cem_keras_rl.py
    model = Sequential()
    game.model.add(Flatten(input_shape=(1600,game.n_observations, )))
    #game.model.add(Flatten( input_shape = (game.n_observations,) ))
    game.model.add(Dense(game.n_actions))
    game.model.add(Activation('softmax'))
    #game.model.add(Dense(game.n_actions, activation='softmax'))
    #game.model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
    #game.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
    game.model.compile(optimizer='adam', loss='categorical_crossentropy')
    """

    game.model.summary()


def predict(game, observation):
    #p = game.model.predict_classes( prev_observation )
    return game.model.predict( observation[None,:,:,:] )


def fit(game, ep_observations, ep_actions, sample_weight,
        batch_size, epochs=1, verbose=0):
    game.model.fit(ep_observations, ep_actions, sample_weight=sample_weight,
                    batch_size=batch_size, epochs=epochs, verbose=verbose)

def evaluate(game, ep_observations, ep_actions, sample_weight,
            batch_size, verbose=0):
    return game.model.evaluate(ep_observations, ep_actions,
        sample_weight=sample_weight, batch_size=batch_size, verbose=verbose)


