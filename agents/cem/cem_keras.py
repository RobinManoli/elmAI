# https://colab.research.google.com/drive/1KuzxUPUL3Y50xQFk8RvsfWDx88vDitZS#scrollTo=WB6Z4ASd5vMX
# https://towardsdatascience.com/deep-reinforcement-learning-pong-from-pixels-keras-version-bf8a0860689f

# gen 1 - ft.lev - seeds 61213 - gamma = 0.99 - n_observations = 19 - n_actions = 2
# game.model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
# used non-normalized (non-diffed) observations
# successfully lowers loss to a larger negative value in 1000 episodes
# need to investigate why that doesn't mean higher reward?
# run.py ft.lev 1 cem render

# gen 2
# used diffed observations
# successfully increases average score
# plays beautifully until about 600 episodes
# seems to converge at gas only
# very different learning times

# gen 3 - n_actions = 3
# game.model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
# increases average reward until around 1000 - 1500 episodes
# score 45.05 at episode 1271
# seems to converge at gas only after 5000 episodes

# gen 4 - ribotai0.lev - seeds 43364 - n_actions = 2
# beat some good human players of this battle https://elma.online/battles/152353
# https://elma.online/r/qvw6j5erj6
# in less than 600 episodes
# run.py ribotai0.lev 1 cem render

# gen 5 - changing observations to:
# 8 core positions + body rotation + speeds + direction
# Processing 15 times faster than playing in realtime
# almost same result as old observations:
# time: 7.87 in 1332 episodes, seed 28460
# time: 7.86 in 1354 episodes, seed 88148
# time: 7.77 in 309 episodes after above, loaded with seed 41532


import numpy as np
import random, os
# import cPickle as pickle
#import matplotlib.pyplot as plt
#from JSAnimation.IPython_display import display_animation
#from matplotlib import animation
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

# todo: set and print this from game.set_seed()
#seed = random.randint(0, 99999)
#seed = 61213 # learns well but converges into gas only
#seed = 85711 # starts with gas only
#seed = 43364 # fast and good times on ribotai0.lev, beats killer on ribotai1.lev
#print("\nrand seed: %d\n" % (seed))

def discount_rewards(game, r):
    """ take 1D float array of rewards and compute discounted reward """
    discounted_r = np.zeros_like(r)
    running_add = 0
    for t in reversed(range(len(discounted_r))):
        running_add =  r[t] + running_add * game.gamma # belman equation
        discounted_r[t] = running_add
    return discounted_r

def discount_n_standardise(game, r):
    dr = discount_rewards(game, r)
    dr = (dr - dr.mean()) / dr.std()
    return dr


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

# pretrain loop
"""
observation = game.reset()
rewards = []
    p = np.random.dirichlet( [1] * len(game.n_actions), 1 ).ravel()
    a = np.random.choice( len(game.n_actions), p=p )
    #action = action_space[a]
    print("actions: %s" % a)
    action = game.action_space(a)
    observation, reward, done, info = game.step(action)
    r.append(reward)
    if done:
        break
        
rewards = np.array(rewards)
"""

render = None
def train_model(game):
    global render

    if game.training and render is None:
        render = False # initialize
    else:
        render = game.arg_render
    game.arg_render = render
    reward_sums = np.zeros(game.n_episodes)
    losses = np.zeros(game.n_episodes)
    time_taken = np.zeros(game.n_episodes)
    #print("initial reset %f" % (game.timesteptotal))
    observation = game.reset()
    #print( observation )

    for game.episode in range(game.n_episodes):
        reward_sum = 0
        #im_shape = (80, 80, 1)
        #observation_shape = (game.n_observations, 1)
        observation_shape = (game.n_observations, 1, 1)
        prev_observation = None
    
        buffer = 1600 # 80 fps * 20 seconds = 1600 game frames maximum
        observations = np.zeros(( buffer, ) + observation_shape)
        #observations = np.zeros(( buffer, 1 ))
        actions = np.zeros(( buffer, 1 ))
        rewards = np.zeros(( buffer ))
        frame = 0
        done = False
        for game.frame in range(buffer):
            #if game.episode % 50 == 0:
            #    print(game.episode)
            #while episodes < n_episodes:
            #x = preprocess(observation)
            #xs[k] = x - prev_frame if prev_frame is not None else np.zeros(im_shape)
            #prev_frame = x        
            #observations[frame] = prev_observation.astype(np.float)[:,:,None] # preprocess
            #observations[frame] = prev_observation
            # convert shape 19 to 19,1,1
            observation = observation.reshape(-1,1)[:, np.newaxis]
            #observations[game.frame] = prev_observation # working but not normalized
            # normalize by only recording difference of past observations
            observations[game.frame] = observation - prev_observation if prev_observation is not None else np.zeros(observation_shape)
            #print()
            #print(observations[frame])
            #print()
            prev_observation = observation
            
            #print(observations[frame][None,:,:,:])
            # Take an action given current state of policy model
            p = game.model.predict( observations[frame][None,:,:,:] )
            #p = game.model.predict_classes( prev_observation )
            #print('probabilities: %s' % (p))
            #print()
            if game.noise:
                a = np.random.choice( game.n_actions, p=p[0] )
            else:
                a = np.argmax(p)
            #action = action_space[a]
            action = a
            actions[game.frame] = a
            
            # Renew state of environment
            observation, reward, done, _ = game.step(action)
            #reward_sum += reward # record total rewards # game.score
            rewards[game.frame] = reward # record reward per step
            
            if done:
                reward_sums[game.episode] = game.score
                
                # trunc to actual gathered values
                ep_observations = observations[:game.frame]
                ep_actions = actions[:game.frame]
                ep_rewards = rewards[:game.frame]
                ep_rewards = discount_n_standardise(game, ep_rewards)

                #print("training run...")
                # batch size is probably how many frames to train per iteration
                # so let's use all frames of the episode
                if game.training:
                    game.model.fit(ep_observations, ep_actions, sample_weight=ep_rewards, batch_size=buffer, epochs=1, verbose=0)
                
                time_taken[game.episode] = game.frame
                prev_observation = None
                observation = game.reset()
                losses[game.episode] = game.model.evaluate(ep_observations, 
                                                ep_actions,
                                                sample_weight=ep_rewards,
                                                batch_size=len(ep_observations), 
                                                verbose=0)
                #print(losses[game.episode])
                
                # Print out metrics like rewards, how long each episode lasted etc.
                if game.episode > 0 and game.episode % 100 == 0: # game.episode % ( game.n_episodes // 20 ) == 0:
                    game.arg_render = True
                    ave_reward = np.mean(reward_sums[max(0,game.episode-200):game.episode])
                    ave_loss = np.mean(losses[max(0,game.episode-200):game.episode])
                    ave_time = np.mean(time_taken[max(0,game.episode-200):game.episode])
                    acc_ratio = 0.0 + np.count_nonzero(actions == 1)/game.frame

                    elapsed_time, elapsed_elma_time, unit = game.elapsed_time()


                    print(game.GREEN + 'Episode: {0:d}/{1:d}, Average Loss: {2:.4f}, Average Reward: {3:.2f}, Average steps: {4:.0f}'
                        .format(game.episode, game.n_episodes, ave_loss, ave_reward, ave_time))
                    print('Acc ratio: %.2f' % acc_ratio
                        + ', Real time: %.02f %s' % (elapsed_time, unit)
                        + ', Elma time: %.02f %s' % (elapsed_elma_time, unit)
                        + ', seed: %d' % (game.seed)
                        + game.WHITE)
                else:
                    if not game.arg_test:
                        game.arg_render = False
                game.frame = 0
                break
        if not game.running:
            # respond to exiting (after run complete)
            break
    game.episode += 1
    print("leaving train_model, episode: %d/%d, done:%s, " % (game.episode, game.n_episodes, done))
    """if game.training:
        # perform a run based on current training
        print("performing a batch run without noise...")
        game.training = False
        train_model(game) # test here
        game.training = True"""


#window = 20
#plt.plot(losses[:episodes])
#plt.plot(np.convolve(losses[:episodes], np.ones((window,))/window, mode='valid'))
#plt.show()

#plt.plot(reward_sums[:episodes])
#plt.plot(np.convolve(reward_sums[:episodes], np.ones((window,))/window, mode='valid'))
#plt.show()

