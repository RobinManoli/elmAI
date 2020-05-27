# https://colab.research.google.com/drive/1KuzxUPUL3Y50xQFk8RvsfWDx88vDitZS#scrollTo=WB6Z4ASd5vMX
# https://towardsdatascience.com/deep-reinforcement-learning-pong-from-pixels-keras-version-bf8a0860689f

# gen 1 - seeds 61213
# used non-normalized (non-diffed) observations
# successfully lowers loss to a larger negative value in 1000 episodes
# run.py ft 1 cem render
# need to investigate why that doesn't mean higher reward

# gen 2 - seeds 61213
# successfully increases average score
# plays beautifully until about 600 episodes
# seems to converge at gas only


import numpy as np
import random
# import cPickle as pickle
#import matplotlib.pyplot as plt
#from JSAnimation.IPython_display import display_animation
#from matplotlib import animation
#import gym

import tensorflow as tf
from keras.models import Sequential
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

seed = random.randint(0, 99999)
seed = 61213
print("\nrand seed: %d\n" % (seed))
np.random.seed(seed)
tf.random.set_seed(seed)

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


model = Sequential()
def init_model(game):
    
#    model.add(Conv2D(4, kernel_size=(3,3), padding='same', activation='relu', input_shape = (1,) + (game.n_observations, )))
    model.add(Conv2D(4, kernel_size=(3,3), padding='same', activation='relu', input_shape = (game.n_observations, 1, 1)))
    #model.add(Conv2D(4, kernel_size=(3,3), padding='same', activation='relu', input_shape = (80,80,1)))

    # shape too small for further pooling: https://stackoverflow.com/a/47325544
    #model.add(MaxPool2D(pool_size=(2, 2)))
    #model.add(Conv2D(8, kernel_size=(3,3), padding='same', activation='relu'))
    #model.add(MaxPool2D(pool_size=(2, 2)))
    #model.add(Conv2D(12, kernel_size=(3,3), padding='same', activation='relu'))
    #model.add(MaxPool2D(pool_size=(2, 2)))
    #model.add(Conv2D(16, kernel_size=(3,3), padding='same', activation='relu'))
    #model.add(MaxPool2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(game.n_actions, activation='softmax'))
    model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
    model.summary()
    """
    # model from cem_keras_rl.py
    model = Sequential()
    model.add(Flatten(input_shape=(1600,game.n_observations, )))
    #model.add(Flatten( input_shape = (game.n_observations,) ))
    model.add(Dense(game.n_actions))
    model.add(Activation('softmax'))
    #model.add(Dense(game.n_actions, activation='softmax'))
    #model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
    #model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
    model.compile(optimizer='adam', loss='categorical_crossentropy')
    """

    model.summary()

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


def train_model(game):
    game.arg_render = False
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
            p = model.predict( observations[frame][None,:,:,:] )
            #p = model.predict_classes( prev_observation )
            #print('actions: %s' % (p))
            #print()
            a = np.random.choice( game.n_actions, p=p[0] )
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
                model.fit(ep_observations, ep_actions, sample_weight=ep_rewards, batch_size=buffer, epochs=1, verbose=0)
                
                time_taken[game.episode] = game.frame
                prev_observation = None
                observation = game.reset()
                losses[game.episode] = model.evaluate(ep_observations, 
                                                ep_actions,
                                                sample_weight=ep_rewards,
                                                batch_size=len(ep_observations), 
                                                verbose=0)
                #print(losses[game.episode])
                
                # Print out metrics like rewards, how long each episode lasted etc.
                if game.episode % ( game.n_episodes // 20 ) == 0:
                    game.arg_render = True
                    ave_reward = np.mean(reward_sums[max(0,game.episode-200):game.episode])
                    ave_loss = np.mean(losses[max(0,game.episode-200):game.episode])
                    ave_time = np.mean(time_taken[max(0,game.episode-200):game.episode])
                    acc_ratio = 0.0 + np.count_nonzero(actions == 1)/game.frame
                    
                    print('Episode: {0:d}, Average Loss: {1:.4f}, Average Reward: {2:.2f}, Average steps: {3:.0f}, Acc ratio: {4:.2f}'
                        .format(game.episode, ave_loss, ave_reward, ave_time, acc_ratio))
                else:
                    game.arg_render = False
                game.frame = 0
                break

    print("leaving train_model, episode: %d/%d, done:%s, " % (game.episode+1, game.n_episodes, done))
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

