import random

# success actions=A seed=259003
# probability 90% to do optimal sequence
# episode 1061, hiscore: 198.28, time: 7.82, died: False, finished: True
# Processing 163.43 times faster than playing in realtime
# no idea how this happened as the code was all wrong

print("Enter Ribot Algorithm")

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
        noise = 0 if game.arg_render else 0.1
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

