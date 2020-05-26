# from https://github.com/shivaverma/OpenAIGym then navigate to bipedal walker
# probably, not possible to use as all actions get a fractional value not summing up to one
#import gym

# this agent is slow as hell, so better to move on to a model i have more confidence in
# elma time is 10x slower than realtime

import torch
import numpy as np
from ddpg_agent import Agent
import random
#import matplotlib.pyplot as plt

print("Enter ddpg torch, using BipedalWalkerHardcore solution")

#env = gym.make('BipedalWalkerHardcore-v3') # changed from original v2
#state_dim = env.observation_space.shape[0] # returns a number of possible observations, ie 24 -- as listed here https://github.com/openai/gym/wiki/BipedalWalker-v2
#action_dim = env.action_space.shape[0] # returns a number of possible actions, ie 4 

OBSERVATION_SPACE = 19 # 33 # len(game.observation())
ACTION_SPACE = 4 # 4 # action_size = 4 # simplistic, 7 elma, 13 precise
agent = Agent(state_size=OBSERVATION_SPACE, action_size=ACTION_SPACE, random_seed=0)

# agent.actor_local.load_state_dict(torch.load('1checkpoint_actor.pth', map_location="cpu"))
# agent.critic_local.load_state_dict(torch.load('1checkpoint_critic.pth', map_location="cpu"))
# agent.actor_target.load_state_dict(torch.load('1checkpoint_actor.pth', map_location="cpu"))
# agent.critic_target.load_state_dict(torch.load('1checkpoint_critic.pth', map_location="cpu"))
# torch.save(agent.actor_local.state_dict(), 'checkpoint_actor.pth')
# torch.save(agent.critic_local.state_dict(), 'checkpoint_critic.pth')
# torch.save(agent.actor_target.state_dict(), 'checkpoint_actor_t.pth')
# torch.save(agent.critic_target.state_dict(), 'checkpoint_critic_t.pth')

reward_list = []
#def train(game, noise=True):
def train_model(game, batch, total_episodes, noise=True, save_rec=False, training=True):
    for episode in range(total_episodes):
        print('Episode: %d' % (episode))

        observation = game.observation()[:OBSERVATION_SPACE]
        done = False

        while not done:
            prediction = agent.act(observation, noise)
            #print("prediction: %s" % str(prediction))
            # prediction: [[0.1502565  0.20959666 0.22558564 0.40949315]]
            action = np.argmax(prediction)
            #if noise and random.random() < 0.75:
            #    # not working because agent is not aware of this taken action
            #    action = random.randrange(ACTION_SPACE)
            elmainputs = game.action_space()[:ACTION_SPACE] # [0, 0]
            elmainputs[action] = 1 # makes one of zeroes above = 1, ie use that action
            #do_save_rec = (episode==EPISODES_BATCH-1) or game.score > 15 or game.score < -3 # if last episode of batch or good reward
            done = game.loop(elmainputs, save_rec=save_rec)
            next_observation = game.observation()[:OBSERVATION_SPACE]
            reward = game.score_delta

            # next_state, reward, done, info = env.step(action[0]) from old coder

            # probably how the agent learns
            # commented out by old coder -- Save experience in replay memory, and use random sample from buffer to learn.
            # agent.step(state, action, reward, next_state, done) # old

            # start training after agent's batch size is fulfilled
            agent.step(observation, prediction, reward, next_observation, done) # old
            # state = next_state.squeeze() # used in old inner loop

        if game.score > game.hiscore:
            print('episode %d, hiscore: %.2f, time: %.2f' %(episode, game.score, game.timesteptotal * game.realtimecoeff))
        elif game.score < game.lowscore:
            print('episode %d, lowscore: %.2f, time: %.2f' %(episode, game.score, game.timesteptotal * game.realtimecoeff))
        if not training:
            print('batch test run, score: %.2f, time: %.2f' % (game.score, game.timesteptotal * game.realtimecoeff))
        print('episode %d, score: %.2f, time: %.2f' % (episode, game.score, game.timesteptotal * game.realtimecoeff))
        game.batch_hiscore = max(game.batch_hiscore, game.score)
        game.batch_lowscore = min(game.batch_lowscore, game.score)
        game.hiscore = max(game.hiscore, game.score)
        game.lowscore = min(game.lowscore, game.score)
        game.restart(save_rec)

    if training:
        # perform a run based on current training
        print("performing a batch run without noise...")
        train_model(game, batch, total_episodes=1, noise=False, save_rec=True, training=False)

"""
scores = train(episodes=10, step=2000, pretrained=0, noise=0) # old

fig = plt.figure()
plt.plot(np.arange(1, len(reward_list) + 1), reward_list)
plt.ylabel('Score')
plt.xlabel('Episode #')
plt.show()
"""