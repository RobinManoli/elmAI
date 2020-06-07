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

# considering it would take incredibly long time to find good styles for recs
# without a very precise scoring system
# using recs for keypress events was attempted:
# could not finish
# using recs for score
# could not progress

# SUCCESS - new scoring system - seed 308117 - actions A - flat track
# episode 853, score: 284.0752, time: 22.262, apples: 0, FINISHED
# Processing 129.13 times faster than playing in realtime

# Intervals for the first time made sense when using ALL actions and intervals of 800 frames
# Making longer levels into 10 second segments.
# Since it takes forever to get anywhere with all actions, intervals might actually help.
# They do make sense intuitively, practicing the early part of the level first,
# and then stop experimenting with the earlier parts.
# It still should take perhaps 10k episodes at least for the first interval to complete.
# After this the realization came that intervals could be started with actions A
# as that has been a successful strategy for easy 800 frame levels.

# SUCCESS - seed 308117 - actions ALL - flat track
# interval_length=800, patience=25
# episode 1055 (starting with 854), score: 97.5694, time: 23.837, apples: 0, FINISHED
# continuing from above success (853 episodes, actions A)
# this result is indicating a short patience along with new rule of not allowing optimal sequence shorter than interval
# is a very fast way to finish a lev with all keys
# probably can't be recreated because had setting 0.02 in score every frame

# SUCCESS - seed 308117 - actions ALL - warm up
# interval_length=500, patience=25
# episode 2032, score: 113.0984/30.0000, time: 18.738, apples: 1, FINISHED
# Processing 109.71 times faster than playing in realtime
# probably can't be recreated because created possibility to move interval_start backwards
# after backtracking:
# episode 8096, score: 77.4957/125.2934, time: 19.350, apples: 1, fps: 80 FINISHED
# episode 8781, score: 117.9096/125.2934, time: 18.675, apples: 1, fps: 80 FINISHED

# still not able to finish upbhill battle easily, so created possibility to backtrack interval

# SUCCESS - actions ALL
# interval_length=500, patience=25
# without backtracking:
# int04: episode 1437, score: 135.0718/135.0718, time: 58.825, apples: 1, fps: 80 FINISHED, seed 308117 
# int03: episode 13836, score: 543.4605/100.0000, time: 36.112, apples: 2, fps: 80 FINISHED, seed: 621836
# int05: increasing death pentalty from 0 (above) to 2, made first bump easier

# all above are without negated y-value (since bike y values are opposite of level)

# how to proceed?
# probably the best would be to cut up levels to training level chunks
# make ai perform well a few seconds until rec is good
# then when 100% completed, load that sequence without noise, and proceed with new training lev

print('\33[92m' + "Enter Ribot Algorithm" + '\33[37m')

class Sequence:
    "A sequence of actions to take"
    # todo: paralel, to make multiple actions allowed at once
    def __init__(self, game, ones=True, serial=True, interval_length=800, patience=2500, noise=0.01):
        self.game = game
        # where the current interval starts (earlier frames are no fixed and no longer experimented with)
        self.interval_start = 0
        # number of frames to train at a time
        # too short interval means a bad earlier action can never be improved
        # such as a jump that was good at an earlier interval means for sure death at next
        self.interval_length = interval_length
        self.patience = patience
        # how many episodes that have passed without improvements
        self.unevolved_episodes = 0
        self.db_row = None
        self.max_frames = self.game.n_frames
        self.noise = noise
        self.temp_noise = None

        # ones means that at the start of the algorithm
        # all actions of this sequence is set to 1
        # otherwise they are all set to 0
        # eg true for acc in elma, because acc is almost always pressed
        # also true for serial
        # but false for the other input keys, as they are used sparingly

        # optimal_actions is the sequence of optimal actions discovered so far
        # distorted_actions is the whole sequence of optimal_actions distorted
        if serial or ones:
            self.optimal_actions = game.np.ones( self.max_frames, game.np.int8 )
            self.distorted_actions = game.np.ones( self.max_frames, game.np.int8 )
        else:
            self.optimal_actions = game.np.zeros( self.max_frames, game.np.int8 )
            self.distorted_actions = game.np.zeros( self.max_frames, game.np.int8 )
        # probabilities to take any action
        # will be distorted on distortions
        # x frames, with n_actions per frame
        self.prob_dists = game.np.zeros(( self.max_frames, self.game.n_actions ))
        self.initialize() # set probabilities

    def interval_end(self):
        return self.interval_start + self.interval_length

    def distort_serial(self, noise=None):
        """
        Each frame has noise probability to do something else.
        Each action (except optimal one) has a fraction of noise probability to be chosen.
        """
        if noise is None:
            noise = self.noise if self.temp_noise is None else self.temp_noise
        for frame, optimal_action in enumerate(self.optimal_actions):
            n = noise if frame >= self.interval_start else 0
            #print(frame, optimal_action)
            noise_fraction = n / (self.game.n_actions-1) # distribute noise for all non-chosen actions
            self.prob_dists[frame].fill( noise_fraction ) # set all probabilities to noise
            self.prob_dists[frame][optimal_action] = 1 - n # set optimal action probability
            #print( self.prob_dists[frame] )
            #selected_action = self.game.np.random.choice( self.game.n_actions, p=self.prob_dists[frame] )
            #self.distorted_actions[frame] = selected_action

    def shuffle_serial(self, noise=0.01):
        """
        Change one action's place with another previous or following action
        """
        # todo: only shuffle within interval
        # shuffle noise of the frames
        for _ in range( int(len(self.optimal_actions)*noise) ):
            index = self.game.np.random.choice( range(len(self.optimal_actions)) )
            action = self.optimal_actions[index]
            diff = self.game.np.random.choice((-1, 1))
            diff = 1 if index == 0 else diff
            diff = -1 if index == len(self.optimal_actions) - 1 else diff
            old_action = self.optimal_actions[index+diff]
            self.optimal_actions[index+diff] = action
            self.optimal_actions[index] = old_action
        self.distort_serial(noise=0)

    def initialize(self):
        self.distort_serial(noise=0)

    def truncate(self):
        if self.interval_end() > self.max_frames:
            self.interval_start = self.max_frames - self.interval_length

    def evolve(self, ep_actions):
        self.unevolved_episodes += 1

        if self.game.score > self.game.hiscore:
            #print( "updating sequence %d %d" % (len(self.optimal_actions), len(ep_actions[:,0]) ))
            self.unevolved_episodes = 0
            self.temp_noise = None
            self.optimal_actions = ep_actions[:,0]

        if self.game.score > self.game.level.db_row.hiscore:
            self.save()

        if self.game.kuski_state['finishedTime'] > 0:
            # when an lev is finished, longer rides are not necessary to try, so crop the buffer
            self.max_frames = len( self.optimal_actions )
            self.truncate()

        if self.unevolved_episodes > self.patience:
            if len( self.optimal_actions ) < self.interval_end():
                # evolution so far has a shorter sequence than the interval
                # which probably means that the sequence has a death
                # so start again (and perhaps again), until this problem is solved
                if self.temp_noise is None:
                    self.temp_noise = self.noise
                # double noise
                if self.temp_noise < 0.4:
                    self.temp_noise *= 1.5
                    print('patience ended too soon, so far survived %d/%d frames, temp noise now: %s' % ( len(self.optimal_actions), self.interval_end(), self.temp_noise ))
                elif self.interval_start > 0:
                    interval_end = self.interval_end()
                    # backtracking, canceled because worse performance
                    # but could try to move 100 frames at the time instead
                    # move start a bit backwards
                    #self.interval_start -= int(self.interval_length/3)
                    #self.interval_start = max(self.interval_start, 0) # minimum 0
                    # keep end at the same place
                    #self.interval_length = interval_end - self.interval_start
                    #self.temp_noise = None
                    #print("couldn't progress, moving back and increasing interval, now training %d - %d" % (self.interval_start, self.interval_end()))
                self.unevolved_episodes = 0
            elif self.interval_end() < self.max_frames:
                #print("patience ended, %d" % (len(self.optimal_actions)))
                self.game.winsound.Beep(1637, 123)
                self.game.winsound.Beep(1765, 123)
                self.unevolved_episodes = 0
                # move the training interval forward half the interval length
                self.interval_start += int(self.interval_length/2)
                # decrease interval length, because it might increase in other places
                # cancelled because worse performance
                #self.interval_length = int(self.interval_length * 0.75) # no longer able to finish int 01 or 04
                #self.interval_length = max(100, self.interval_length) # minimum 100
                self.truncate()
                #if self.interval_start > self.max_frames:
                ##    print("Evolution complete at episode: %d" % (self.game.episode))
                #    self.game.episode = self.game.n_episodes - 2
                #else:
                print("Finished first %d frames, now practicing %d-%d, best ride length: %d" \
                % (self.interval_start, self.interval_start, self.interval_end(), len(self.optimal_actions)))
            elif self.interval_length < self.max_frames:
                # working, but better to practice intervals increasing from end to improve time?
                pass
                # patience ended after last interval
                # so now noise should be throughout the whole sequence
                #print("patience lost after last interval, now experimenting on whole level, max frames: %d" % (self.max_frames))
                #self.interval_start = 0
                #self.interval_length = self.max_frames
                #self.game.winsound.Beep(1637, 123)
                #self.game.winsound.Beep(1765, 123)


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
        db = self.game.db.db
        self.db_row = db.sequence[self.game.load]
        #print("loading sequence: %d, %s" % (self.game.load, self.db_row))
        self.optimal_actions = self.db_row.actions
        self.game.episode = self.db_row.episodes
        self.game.n_episodes += self.db_row.episodes
        self.game.set_seed( self.db_row.seed )
        self.initialize() # set probabilities according to loaded actions
        #print( self.prob_dists )

    def load_from_rec(self):
        import math
        from elma.models import LeftVoltEvent
        from elma.models import RightVoltEvent
        from elma.models import TurnEvent
        print("loading sequence from rec: %s" % (self.game.rec))
        for event in self.game.rec.events:
            frame = math.ceil(event.time * self.game.fps)
            if type(event) in (LeftVoltEvent, RightVoltEvent, TurnEvent):
                #print(event, frame)
                pass
            # [accelerate, brake, left, right, turn, supervolt]
            self.optimal_actions[frame] = 3 if type(event) == LeftVoltEvent and self.optimal_actions[frame] == 1 else self.optimal_actions[frame]
            self.optimal_actions[frame] = 4 if type(event) == RightVoltEvent else self.optimal_actions[frame]
            self.optimal_actions[frame] = 5 if type(event) == TurnEvent else self.optimal_actions[frame]
            self.optimal_actions[frame] = 6 if type(event) == LeftVoltEvent and self.optimal_actions[frame] == RightVoltEvent else self.optimal_actions[frame]
            #print( "set action %d for frame %d" % (self.optimal_actions[frame], frame) )
        self.initialize()

class Agent:
    def __init__(self, game, serial=True, interval_length=800, patience=2500):
        self.game = game
        if serial:
            self.sequence = Sequence(self.game, ones=True, serial=True, interval_length=interval_length, patience=patience)

# todo: create one sequence per action (paralel)
# todo: adjust noise according to fps
# todo: improve ride from end? so that when patience ended for training end, backtrack to improve earlier? 
# todo: make progress phases, such as gas only, or add actions if changing noise didn't help?
# optimal (serial) sequence of actions to take

agent = None
def init_model(game):
    global agent
    # set interval to huge to turn interval training off
    # interval of 500-800 and patience 25 makes it possible to progress quickly
    # but not so quick so that the level is never completed
    # good for completing int 01, 03 and 04
    #agent = Agent(game, serial=True, interval_length=800, patience=25)
    agent = Agent(game, serial=True, interval_length=5000, patience=25)
    if game.rec is not None:
        agent.sequence.load_from_rec()
    if game.load is not None:
        agent.sequence.load()
    #print( agent.sequence.optimal_actions )



def predict(game, observation):
    #global sequence
    #print(agent.sequence.optimal_actions)
    if game.frame == 0:
        # first episode and already trained frames act undistorted
        # the best results have been using noise = 0.01, but that doesn't choose difficult styles
        n = 0.01 if game.hiscore < 300 else 0.01
        noise = 0 if game.episode == 0 or (agent.sequence.db_row is not None and game.episode == agent.sequence.db_row.episodes) or game.arg_test else n
        #if game.frame % 2 == 0:
        agent.sequence.distort_serial(noise=noise)
        #else:
        #agent.sequence.shuffle_serial(noise=0)
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
    agent.sequence.evolve(ep_actions)

    '''
    # below is test code to measure distance from rec after whole ride
    # which had no success
    # get distance after whole ride
    x = game.rec.frames[ game.recframe ].position.x
    y = game.rec.frames[ game.recframe ].position.y
    X = game.kuski_state['body']['location']['x']
    Y = game.kuski_state['body']['location']['y']
    # distance from rec position
    distance = (x-X) * (x-X) + (y-Y) * (y- Y)

    # warmup specifics
    if game.timesteptotal * game.realtimecoeff > 7.58 and game.kuski_state['numTakenApples'] == 0:
        #print('apples not taken, punished with distance')
        x2 = game.level.apples[0].x
        y2 = game.level.apples[0].y
        # not exactly correct distance, because not considering if rec has passed bike or not
        # but at least a clear sign it's off
        distance += 2 * ((x2-X) * (x2-X) + (y2-Y) * (y2- Y))

    #print("episode: %d, frame: %d, recframe: %d, score_delta: %f, score: %f, distance: %f, x: %f, X: %f, y: %f, Y:%f, seed: %d, elmatime: %f" \
    #    % (game.episode, game.frame, game.recframe, game.score_delta, game.score, distance, x, X, y, Y, game.seed, game.timesteptotal))
    # distance after first ride of sequence (actions from rec, died after 2.463)
    # 7.312168
    # so give big bonus for any ride better than that, more bonus for more distance
    if distance < 8:
        game.score += (10-distance) * 5 * game.timesteptotal"""
        """
        # if last one was a hiscore, update it as the optimal sequence
        #print(sequence)
        #print("fit score: %f, hiscore: %f, len seq: %d, gas ratio before: %f"
        #        % (game.score, game.hiscore, len(sequence), sum(sequence)/len(sequence)),
        #        end=", ")
        sequence = list(ep_actions)
        #print("gas ratio after: %f" % (sum(sequence)/len(sequence)))
        '''


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
