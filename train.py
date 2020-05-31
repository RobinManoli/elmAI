"Loop episodes using any model"

import numpy as np
import random, os
#%matplotlib inline


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


# rendering is here done occasionally if training
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
    steps_per_episode = np.zeros(game.n_episodes)
    #print("initial reset %f" % (game.timesteptotal))
    observation = game.reset()
    #print( observation )

    for game.episode in range(game.n_episodes):
        reward_sum = 0
        #im_shape = (80, 80, 1)
        observation_shape = (game.n_observations, 1, 1)
        prev_observation = None
    
        #buffer = 1600 # 80 fps * 20 seconds = 1600 game frames maximum
        #print(game.level.maxplaytime, game.timestep, game.realtimecoeff)
        # todo: do not initialize level in reward()
        if game.level.maxplaytime is None:
            game.level.reward() # initialize level
        buffer = game.level.maxplaytime / (game.timestep*game.realtimecoeff) # max time * fps
        buffer = int(np.ceil( buffer ))
        observations = np.zeros(( buffer, ) + observation_shape)
        actions = np.zeros(( buffer, 1 ))
        rewards = np.zeros(( buffer ))
        done = False
        for game.frame in range(buffer):
            #if game.episode % 50 == 0:
            #    print(game.episode)
            # convert shape 19 to 19,1,1
            observation = observation.reshape(-1,1)[:, np.newaxis]
            #observations[game.frame] = prev_observation # working but not normalized
            # normalize by only recording difference of past observations
            observations[game.frame] = observation - prev_observation if prev_observation is not None else np.zeros(observation_shape)
            #print()
            #print(observations[game.frame])
            #print()
            prev_observation = observation

            # get a list of probabilities for each action
            p = game.training_mod.predict(game, observations[game.frame])
            #print(observations[game.frame][None,:,:,:])
            #print('probabilities: %s' % (p))
            #print()
            if game.noise:
                a = np.random.choice( game.n_actions, p=p[0] )
            else:
                a = np.argmax(p)
            #action = action_space[a]
            action = a
            actions[game.frame] = a
            observation, reward, done, _ = game.step(action)
            rewards[game.frame] = reward # record reward per step
            
            if done:
                reward_sums[game.episode] = game.score
                #if game.score < 10:
                #    print(rewards[game.frame])
                
                # trunc from buffert to actual gathered values
                ep_observations = observations[:game.frame]
                ep_actions = actions[:game.frame]
                ep_rewards = rewards[:game.frame]
                ep_rewards = discount_n_standardise(game, ep_rewards)

                #print("training run...")
                # batch size is probably how many frames to train per fit iteration
                # so let's use all frames of the episode
                # not (yet?) implemented in eol mode
                if game.training and not game.arg_eol:
                    game.training_mod.fit(game, ep_observations, ep_actions,
                        sample_weight=ep_rewards, batch_size=buffer,
                        epochs=1, verbose=0)

                steps_per_episode[game.episode] = game.frame
                prev_observation = None
                observation = game.reset()
                if not game.arg_eol:
                    # not (yet?) implemented in eol mode
                    losses[game.episode] = game.training_mod.evaluate(game,
                        ep_observations, ep_actions, sample_weight=ep_rewards,
                        batch_size=len(ep_observations), verbose=0)
                #print(losses[game.episode])

                # Print out metrics like rewards, how long each episode lasted etc.
                if not game.arg_eol and game.episode > 0 and game.episode % 100 == 0: # game.episode % ( game.n_episodes // 20 ) == 0:
                    # not (yet?) implemented in eol
                    game.arg_render = True
                    avg_reward = np.mean(reward_sums[max(0,game.episode-200):game.episode])
                    avg_loss = np.mean(losses[max(0,game.episode-200):game.episode])
                    avg_steps = np.mean(steps_per_episode[max(0,game.episode-200):game.episode])
                    acc_ratio = 0.0 + np.count_nonzero(actions == 1)/game.frame

                    elapsed_time, elapsed_elma_time, unit = game.elapsed_time()


                    print(game.GREEN + 'Episode: {0:d}/{1:d}, Average Loss: {2:.4f}, Average Reward: {3:.2f}, Average steps: {4:.0f}'
                        .format(game.episode, game.n_episodes, avg_loss, avg_reward, avg_steps))
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