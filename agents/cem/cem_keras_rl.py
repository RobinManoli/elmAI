# this code is based on keras rl's cem example
# though since it doesn't seem to accept either learning rate
# or discount functionality I skipped this
# however the example code does have a couple of models that could be tried out

import numpy as np
import random

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.cem import CEMAgent
from rl.memory import EpisodeParameterMemory

#ENV_NAME = 'CartPole-v0'

print("Enter CEM Keras RL, softmax and cross entropy")
OBSERVATION_SPACE = 19 # 33 # len(game.observation())
ACTION_SPACE = 2 # 4 # action_size = 4 # simplistic, 7 elma, 13 precise

#seed = 56173
seed = random.randint(0, 99999)
print("\nrand seed: %d\n" % (seed))

# Get the environment and extract the number of actions.
#env = gym.make(ENV_NAME)
np.random.seed(seed)
#env.seed(123)

nb_actions = ACTION_SPACE
obs_dim = OBSERVATION_SPACE

# Option 1 : Simple model
model = Sequential()
model.add(Flatten(input_shape=(1,) + (OBSERVATION_SPACE, )))
model.add(Dense(nb_actions))
model.add(Activation('softmax'))

# Option 2: deep network
# model = Sequential()
# model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
# model.add(Dense(16))
# model.add(Activation('relu'))
# model.add(Dense(16))
# model.add(Activation('relu'))
# model.add(Dense(16))
# model.add(Activation('relu'))
# model.add(Dense(nb_actions))
# model.add(Activation('softmax'))


print(model.summary())


# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = EpisodeParameterMemory(limit=1000, window_length=1)

cem = CEMAgent(model=model, nb_actions=nb_actions, memory=memory,
               batch_size=50, nb_steps_warmup=20000, train_interval=50, elite_frac=0.05)
cem.compile()

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
def train_model(game, batch, total_episodes, noise=True, save_rec=False, training=True):
    # total_episodes don't make sense here, as model takes total_steps which is set below
    game.arg_render = False
    cem.fit(game, nb_steps=50000, visualize=False, verbose=1)

    # to make render work here, the .arg_render must be True from start
    game.arg_render = True
    # perform a run based on current training
    print()
    #print("performing a batch run without noise...")
    cem.test(game, nb_episodes=1, visualize=False )

# After training is done, we save the best weights.
#cem.save_weights('cem_params.h5f', overwrite=True)

# Finally, evaluate our algorithm for 5 episodes.
