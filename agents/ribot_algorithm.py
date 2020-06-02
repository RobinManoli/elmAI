#import random

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

# SUCCESS actions=ALL ribotAI0.lev
# Processing 149.69 times faster than playing in realtime
# probability 99% to do optimal sequence
# seed 777986
# 7.71 after less than 1400 episodes, using actions=A
# save and switch to actions=ALL
# 7.44 in less than 5000 new episodes


print('\33[92m' + "Enter Ribot Algorithm" + '\33[37m')

class Sequence:
    "A sequence of actions to take"
    def __init__(self, game, ones=True, serial=True, interval_length=800):
        self.game = game
        # where the current interval starts (earlier frames are no fixed and no longer experimented with)
        self.interval_start = 0
        # number of frames to train at a time
        # too short interval means a bad earlier action can never be improved
        # such as a jump that was good at an earlier interval means for sure death at next
        self.interval_length = interval_length
        # how many episodes that have passed without improvements
        self.unevolved_episodes = 0

        # ones means that at the start of the algorithm
        # all actions of this sequence is set to 1
        # otherwise they are all set to 0
        # eg true for acc in elma, because acc is almost always pressed
        # also true for serial
        # but false for the other input keys, as they are used sparingly

        # optimal_actions is the sequence of optimal actions discovered so far
        # distorted_actions is the whole sequence of optimal_actions distorted
        if serial or ones:
            self.optimal_actions = game.np.ones( self.game.n_frames, game.np.int8 )
            self.distorted_actions = game.np.ones( self.game.n_frames, game.np.int8 )
        else:
            self.optimal_actions = game.np.zeros( self.game.n_frames, game.np.int8 )
            self.distorted_actions = game.np.zeros( self.game.n_frames, game.np.int8 )
        # probabilities to take any action
        # will be distorted on distortions
        # x frames, with n_actions per frame
        self.prob_dists = game.np.zeros(( self.game.n_frames, self.game.n_actions ))
        self.initialize() # set probabilities

    def interval_end(self):
        return self.interval_start + self.interval_length




    def distort_serial(self, noise=0.01):
        """
        Each frame has noise probability to do something else.
        Each action (except optimal one) has a fraction of noise probability to be chosen.
        """
        for frame, optimal_action in enumerate(self.optimal_actions):
            n = noise if frame >= self.interval_start else 0
            #print(frame, optimal_action)
            noise_fraction = n / (self.game.n_actions-1) # distribute noise for all non-chosen actions
            self.prob_dists[frame].fill( noise_fraction ) # set all probabilities to noise
            self.prob_dists[frame][optimal_action] = 1 - n # set optimal action probability
            #print( self.prob_dists[frame] )
            #selected_action = self.game.np.random.choice( self.game.n_actions, p=self.prob_dists[frame] )
            #self.distorted_actions[frame] = selected_action

    def initialize(self):
        self.distort_serial(noise=0)

    def evolve(self):
        # not used because train.py only uses probabilities
        "Set distorted actions as optimal actions"
        #self.optimal_actions = self.distorted_actions
        pass


    def save(self):
        db = self.game.db.db
        lev_id = self.game.level.db_row.id
        query = db.level.id == lev_id
        query &= db.sequence.seed == self.game.seed
        row = db(query).select().first()
        if not row:
            row_id = db.sequence.insert( hiscore=self.game.score, episodes=self.game.episode+1, seed=self.game.seed, level=lev_id, actions=list(self.optimal_actions) )
        else:
            row.sequence.update_record( hiscore=self.game.score, episodes=self.game.episode+1, actions=list(self.optimal_actions) )
        db.commit()

    def load(self):
        print("loading sequence: %d" % (self.game.load))
        db = self.game.db.db
        self.db_row = db.sequence[self.game.load]
        self.optimal_actions = self.db_row.actions
        self.game.episode = self.db_row.episodes
        self.game.n_episodes += self.db_row.episodes
        self.initialize() # set probabilities according to loaded actions
        #print( self.prob_dists )


class Agent:
    def __init__(self, game, serial=True):
        self.game = game
        if serial:
            self.sequence = Sequence(self.game, ones=True, serial=True)

# todo: create class with different ways to progress, where serial and whole run are still possible
# make evolutionary and whole runs, where whole is as below
# and evolutionary hoyls 2.5 seconds from start, then after 1000 episodes without improvements keeps first second intact and hoyls from 1-3.5 seconds
# todo: create one sequence per action (paralel)
# optimal (serial) sequence of actions to take

agent = None
def init_model(game):
    global agent
    agent = Agent(game, serial=True)
    if game.load is not None:
        agent.sequence.load()


def predict(game, observation):
    #global sequence
    #print(agent.sequence.optimal_actions)
    if game.frame == 0:
        # first episode and already trained frames act undistorted
        noise = 0 if game.episode == 0 else 0.01
        agent.sequence.distort_serial(noise=noise)
    p = agent.sequence.prob_dists[game.frame]

    if game.frame == agent.sequence.interval_end():
        game.die_programatically = True

    # probabilities need to be returned as first item in array
    return [p]

    """
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
    """


def fit(game, ep_observations, ep_actions, sample_weight,
        batch_size, epochs=1, verbose=0):
    global sequence
    #print(game.score)
    agent.sequence.unevolved_episodes += 1

    if game.score > game.hiscore:
        #agent.sequence.evolve()
        #print( agent.sequence.optimal_actions, ep_actions[:,0] )
        agent.sequence.unevolved_episodes = 0
        agent.sequence.optimal_actions = ep_actions[:,0]

        if game.score > game.level.db_row.hiscore * 0.93:
            # save if at least 93% of hiscore is reached
            # agent.sequence.save()
            pass
        """
        # if last one was a hiscore, update it as the optimal sequence
        #print(sequence)
        #print("fit score: %f, hiscore: %f, len seq: %d, gas ratio before: %f"
        #        % (game.score, game.hiscore, len(sequence), sum(sequence)/len(sequence)),
        #        end=", ")
        sequence = list(ep_actions)
        #print("gas ratio after: %f" % (sum(sequence)/len(sequence)))
        """
    elif agent.sequence.unevolved_episodes > 999999:
        game.winsound.Beep(1637, 123)
        agent.sequence.unevolved_episodes = 0
        # move the training interval forward half the interval length
        agent.sequence.interval_start += int(agent.sequence.interval_length/2)
        if agent.sequence.interval_start > game.n_frames:
            print("Evolution complete at episode: %d" % (game.episode))
            game.episode = game.n_episodes - 2
        else:
            print("Finished first %d frames, evolving forward..." % (agent.sequence.interval_start))
    

def evaluate(game, ep_observations, ep_actions, sample_weight,
            batch_size, verbose=0):
    #print("episode: %d, score: %d" % (game.episode, game.score))
    return 0


if __name__ == '__main__':
    import numpy as np
    class Game:
        pass
    game = Game()
    game.np = np
    game.n_frames = 10
    game.n_actions = 3


    agent = Agent(game, serial=True)
    print( agent.sequence.prob_dists )
    agent.sequence.distort_serial()
    print( agent.sequence.prob_dists )
