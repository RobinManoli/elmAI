import random

# success actions=A seed=259003 ribotAI0.lev
# probability 90% to do optimal sequence
# episode 1061, hiscore: 198.28, time: 7.82, died: False, finished: True
# Processing 163.43 times faster than playing in realtime
# no idea how this happened as the code was all wrong

# success actions=ALR different flat track permutations
# probability 99% to do optimal sequence
# first time using L and R intelligently

# SUCCESS actions=A ribotAI0.lev
# Processing 114.03 times faster than playing in realtime
# probability 99% to do optimal sequence
# seed 752958
# 7.62 after 2834 episodes, then multiple times again
# 7.61 (score 228) within 5k episodes
# 7.60 (score 230) after 24966 episodes
# beat some good human players of this battle https://elma.online/battles/152353
# https://elma.online/r/qvw6j5erj6

print('\33[92m' + "Enter Ribot Algorithm" + '\33[37m')

# optimal sequence of actions to take
sequence = []
def init_model(game):
    # doesn't work because maxplaytime is not initiated,
    # and cannot be, because so far kuski state is not retrieved
    random.seed( game.seed )
    """global sequence
    game.level.reward()
    frames = game.level.maxplaytime / (game.timestep*game.realtimecoeff) # max time * fps
    frames = int(frames)
    for frame in frames:
        # start with gas only on all frames
        sequence.append(1)"""


def predict(game, observation):
    global sequence
    #print( len(sequence ))
    # randominity happens in train,
    #if random.random() < 0.1:
    #    return random.choice[game.actions]
    p = game.np.zeros( game.n_actions )
    if len(sequence) <= game.frame:
        # if sequence is too short, add gas only to the end of it
        # also make sure to take that action
        # so that in the begining gas only becomes a hiscore to beat
        sequence.append(1)
        p[1] = 1 # set probability for gas first time 100%
    else:
        # if noise is 0.1 it means it's 90% chance to take sequence action
        # and 10% distributed chance to take another
        noise = 0 if game.arg_render else 0.01
        for action in range(game.n_actions):
            if sequence[game.frame] == action:
                p[action] = 1 - noise
            else:
                p[action] = noise/(game.n_actions-1)
    return game.np.array([p])


def fit(game, ep_observations, ep_actions, sample_weight,
        batch_size, epochs=1, verbose=0):
    global sequence
    if game.score > game.hiscore:
        # if last one was a hiscore, update it as the optimal sequence
        #print(sequence)
        #print("fit score: %f, hiscore: %f, len seq: %d, gas ratio before: %f"
        #        % (game.score, game.hiscore, len(sequence), sum(sequence)/len(sequence)),
        #        end=", ")
        sequence = list(ep_actions)
        #print("gas ratio after: %f" % (sum(sequence)/len(sequence)))
    

def evaluate(game, ep_observations, ep_actions, sample_weight,
            batch_size, verbose=0):
    #print("episode: %d, score: %d" % (game.episode, game.score))
    return 0


