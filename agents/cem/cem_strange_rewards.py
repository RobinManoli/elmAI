# from https://medium.com/@rafal.plis/using-reinforcement-learning-and-cross-entropy-to-play-and-conquer-cartpole-v1-7837f66a45ce
# CartPole_v1_Cross_Entropy.py

# originally this code had no discount factor,
# and was causing errors with the strange solution of creating a list with the length of the score
# result:
# after up to 45 minutes of elma time training with different seeds, 2 actions and 19 or 33 observation points, the policy would result in gas only until death
# with seed 10970 the training resulted in do nothing all ride, even though there were good runs in training,
# or with higher learning rate 0.01, it was do nothing until third batch which was gas only until death

import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior() # https://stackoverflow.com/a/55573434
import pandas as pd
#import matplotlib.pyplot as plt
import random

print("Enter CEM Simple training, using tf.nn.softmax_cross_entropy_with_logits_v2")

#env = gym.make('CartPole-v1')  # read more about gym environments here: https://gym.openai.com/envs/#classic_control
#OBSERVATION_SPACE = env.observation_space.shape[0]  # 4
#ACTION_SPACE = env.action_space.n  # 2

OBSERVATION_SPACE = 19 # 33 # len(game.observation())
ACTION_SPACE = 2 # 4 # action_size = 4 # simplistic, 7 elma, 13 precise

#seed = random.randint(0, 99999)
#seed = 10331 # good randseed that takes action from beginning, makes a 8.19 run before training, at batch 0 episode 16, irrespective of learning rate and gamma
seed = 10970 # seed in which bike doesn't go into gas only mode
print("\nrand seed: %d\n" % (seed))
tf.set_random_seed(seed)
random.seed(seed)
# === tensorflow part - creating the graph
LEARNING_RATE = 0.01
observationsPlaceholder = tf.placeholder(
    shape=[None, OBSERVATION_SPACE], dtype=tf.float64)
actionsPlaceholder = tf.placeholder(
    shape=[None, ACTION_SPACE], dtype=tf.float64)
weights = tf.Variable(tf.random_uniform(
    shape=[OBSERVATION_SPACE, ACTION_SPACE], dtype=tf.float64))
model = tf.matmul(observationsPlaceholder, weights)
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(
    logits=model, labels=actionsPlaceholder))
train = tf.train.AdamOptimizer(LEARNING_RATE).minimize(loss)
sess = tf.Session()
sess.run(tf.global_variables_initializer())

#EPISODES_BATCH = 100  # number of episodes as the baseline for selecting the elites
QUANTILE = 0.9  # boundary for elite selection
GAMMA = 0.99 # discount factor for reward


def discount_rewards(r):
    """ take 1D float array of rewards and compute discounted reward """
    discounted_r = np.zeros_like(r)
    running_add = 0
    for t in reversed(range(0, len(r))):
        running_add = running_add * GAMMA + r[t]
        discounted_r[t] = running_add
    return discounted_r

def train_model(game, batch, total_episodes, noise=True, save_rec=False, training=True):
    df = pd.DataFrame()
    for episode in range(total_episodes):
        #print('Episode: %d' % (episode))
        #observation = env.reset()
        observation = game.observation()[:OBSERVATION_SPACE]
        #print("training new batch, first observation: %s" % (observation))

        actions = []
        observations = []
        observations.append(observation)
        rewards = []
        done = False

        while not done:
            prediction = sess.run(
                model, feed_dict={observationsPlaceholder: observation.reshape(1, -1)})
            #if not training:
            #    print('prediction: ' + str(prediction)) #  [[  9.11149316 -79.07163118 -19.19156362 -22.72220977]]
            action = np.argmax(prediction)
            if noise and random.random() < 0.75:
                action = random.randrange(ACTION_SPACE)
            elmainputs = game.action_space()[:2] # [0, 0]
            elmainputs[action] = 1 # makes one of zeroes above = 1
            #do_save_rec = (episode==EPISODES_BATCH-1) or game.score > 15 or game.score < -3 # if last episode of batch or good reward
            done = game.loop(elmainputs, save_rec=save_rec or game.score > 8)
            observation = game.observation()[:OBSERVATION_SPACE]
            #print("action: %s, elmatime %.02f, reward: %.02f"  % (action, game.timesteptotal * game.realtimecoeff, reward))
            #print("action: %s, observation: %s, reward: %s"  % (action, observation, reward))
            # action: 1, observation [-1.29032274  2.99978588 -0.36351211 -2.27277322], reward: -7.111706757670028

            observations.append(observation)
            rewards.append(game.score_delta)
            actions.append(elmainputs)

        if game.score > game.hiscore:
            print('episode %d, hiscore: %.2f, time: %.2f' %(episode, game.score, game.timesteptotal * game.realtimecoeff))
        elif game.score < game.lowscore:
            print('episode %d, lowscore: %.2f, time: %.2f' %(episode, game.score, game.timesteptotal * game.realtimecoeff))
        if not training:
            print('batch test run, score: %.2f, time: %.2f' % (game.score, game.timesteptotal * game.realtimecoeff))
        #print('episode %d, score: %.2f, time: %.2f' % (episode, game.score, game.timesteptotal * game.realtimecoeff))
        game.batch_hiscore = max(game.batch_hiscore, game.score)
        game.batch_lowscore = min(game.batch_lowscore, game.score)
        game.hiscore = max(game.hiscore, game.score)
        game.lowscore = min(game.lowscore, game.score)

        rewards = discount_rewards(rewards)
        game.restart(save_rec)

        try:
            df = pd.concat(
                [df, pd.concat(
                    [pd.DataFrame(observations),
                        pd.DataFrame(actions),
                        #pd.DataFrame( [rewards for _ in range(int(rewards))] ) # original code makes no sense, that every frame will get full rewards, and as many as total score
                        pd.DataFrame(rewards)
                    ], axis=1)])
        except ValueError as e:
            print("Pandas concat error: %s" % (e))

    #print('batch complete, training...')
    dfElite = df[df.iloc[:, -1] > df.iloc[:, -1].quantile(QUANTILE)]
    _, l = sess.run([train, loss], feed_dict={observationsPlaceholder: dfElite.iloc[:, 0:OBSERVATION_SPACE].values,
                                              actionsPlaceholder: dfElite.iloc[:, 4:6].values})
    if training:
        # perform a run based on current training
        print("performing a batch run without noise...")
        train_model(game, batch, total_episodes=1, noise=False, save_rec=True, training=False)
#  So here we have just ended the script. Now it is time to use neural network to predict the best moves. Let make it in a one iteration:
"""
observation = env.reset()
rewards = 0
done = False
while not done:
    prediction = sess.run(
        model, feed_dict={observationsPlaceholder: observation.reshape(1, -1)})
    action = np.argmax(prediction)
    observation, reward, done, _ = env.step(action)
    rewards += reward
print("The result is:", rewards)
sess.close()
"""
"""
scores = train(episodes=10, step=2000, pretrained=0, noise=0) # old

fig = plt.figure()
plt.plot(np.arange(1, len(reward_list) + 1), reward_list)
plt.ylabel('Score')
plt.xlabel('Episode #')
plt.show()
"""