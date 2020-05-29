import time, random
import numpy as np 

class Game:
    def __init__(self):
        self.set_terminal_colors()
        self.set_seed()
        self.pygame = None

        # to check this: make replay and store timesteptotal,
        # then check rec time in elma 12.53 28.67
        # for example timestep = 0.002 with timesteptotal of 12.53 makes a rec of 28.67 seconds
        # so 28.67 / 12.53 ~ 2,29, which is pretty much jon's constant 
        self.realtimecoeff = 2.2893772893772893772893772893773 # exact number provided by jon
        self.timesteptotal = 0.0 # total timesteps current run
        self.lasttime = None # how much time in seconds last run will be in the .rec file
        self.elmatimetotal = 0 # how much elma time that would have been spent if this session would have been play in real time in elma
        self.starttime = None # start from when training starts # time.time() # now, when this session started
        self.input = [0, 0, 0, 0, 0, 0]
        self.score_delta = 0 # score of last frame
        self.score = 0 # total score gathered this run
        self.last_score = 0 # total score gathered last run
        self.hiscore = 0 # highest score this session
        self.lowscore = 0 # lowest score this session
        self.batch_hiscore = 0 # highest score this batch
        self.batch_lowscore = 0 # lowest score this batch

        self.training = False
        self.noise = True
        self.model = None
        self.load = None
        self.activation = 'softmax'
        self.optimizer = 'rmsprop'
        self.loss = 'sparse_categorical_crossentropy'
        self.batch = 0
        self.frame = 0
        self.episode = 0
        self.n_episodes = 1
        self.n_actions = 1 # first action is noop
        # [accelerate, brake, left, right, turn, supervolt]
        # self.actions[0] is elmainputs for noop
        # append full list of elmainputs to send for each available game action
        self.actions = [[0, 0, 0, 0, 0, 0]]
        self.actions_str = '' # any letters of ABLRTS
        self.n_observations = 19 # 33 # len(game.observation())
        self.gamma = 0.99 # discount factor
        self.learning_rate = 0.01
        self.save_rec = False
        self.training = False
        self.died = False
        self.finished = False

    def has_ended(self):
        return self.kuski_state['isDead'] or self.kuski_state['finishedTime'] > 0
    
    def end(self):
        #print("Ended level programatically")
        self.elmaphys.restart_level()

    def rec_name(self):
        filenametime = "%.02f" % self.lasttime
        filenametime = filenametime.replace('.', '') # remove dot from filename, because elma can't handle it
        filename = "00x%s_%d_%s.rec" % (filenametime, self.score, self.level.filename_wo_ext())
        return filename
    
    def model_save_name(self):
        filename = self.rec_name()
        filename += "_seed%d_" % (self.seed)
        filename += "observations%d_" % (self.n_observations)
        filename += "actions%s_" % (self.actions_str)
        filename += "lr%f_" % (self.learning_rate)
        filename += "gamma%f_" % (self.gamma)
        filename += "%s_%s_%s" % (self.activation, self.optimizer, self.loss)
        return filename

    def restart(self):
        self.lasttime = self.timesteptotal * self.realtimecoeff
        #print('time: %.2f, score: %.2f, timesteptotal: %.2f' % (self.lasttime, self.score, self.timesteptotal))
        self.elmatimetotal += self.lasttime
        self.timesteptotal = 0.0
        if self.kuski_state['isDead']:
            self.died = True
            #print('kuski died, time: %.2f, score: %.2f' % (self.lasttime, self.score))
            pass
        elif self.kuski_state['finishedTime']:
            self.finished = True
            print(
                self.VIOLET + 'lev completed, time: %.2f, score: %.2f, var finishedTime: %.2f, episode: %d'
                % (self.lasttime, self.score, self.kuski_state['finishedTime'], self.episode),
                self.WHITE)
        if self.save_rec or self.level.hiscore and self.score > self.level.hiscore:
            #self.elmaphys.save_replay("00x%s_%d_%s.rec" % (filenametime, self.score, random.randint(10,99)), self.level.filename) # working
            self.elmaphys.save_replay(self.rec_name(), self.level.filename) # working
            if self.model is not None:
                print('saving keras model: ' + self.model_save_name())
                self.model.save("keras_models\\" + self.model_save_name())
        #if self.maxplaytime and time.time() - self.starttime > self.maxplaytime:
        #    self.running = False

        self.last_score = self.score
        if self.score > self.hiscore:
            self.hiscore = self.score
            print(self.YELLOW + 'episode %d, hiscore: %.2f, time: %.2f, died: %s, finished: %s' % (self.episode, self.score, self.lasttime, self.died, self.finished) + self.WHITE)
        elif self.score < self.lowscore:
            self.lowscore = self.score
            print(self.YELLOW + 'episode %d, lowscore: %.2f, time: %.2f, died: %s, finished: %s' % (self.episode, self.score, self.lasttime, self.died, self.finished) + self.WHITE)
        if not self.training:
            # print this when periodical test runs happen, ie arg_render are set temporarily
            # or when playing manually
            print('score: %.2f, time: %.2f, died: %s, finished: %s' % (self.score, self.lasttime, self.died, self.finished))
        #print('episode %d, score: %.2f, time: %.2f' % (episode, self.score, self.timesteptotal * self.realtimecoeff))
        self.batch_hiscore = max(self.batch_hiscore, self.score)
        self.batch_lowscore = min(self.batch_lowscore, self.score)

        self.score_delta = 0
        self.score = 0
        self.kuski_state = self.initial_kuski_state
        self.last_kuski_state = self.initial_kuski_state
        self.died = False
        self.finished = False
        if not self.has_ended():
            # if game ended programatically, eg because level max time is up
            # must run after saving rec
            self.end()
        #print('restarted')

    # emulate openai env.methods -- easy to use with code that uses env
    def reset(self):
        # check if game has progressed (don't restart if resetting as first action in agent)
        if self.timesteptotal > 0:
            self.restart()
        return self.observation()[:self.n_observations]
    def step(self, action):
        elmainputs = self.actions[action] # [0, 0, ...]
        #print(elmainputs)
        done = self.loop(elmainputs)
        observation = self.observation()[:self.n_observations] # after action taken
        reward = self.score_delta
        info = dict()
        return observation, reward, done, info
    def render(self):
        # render is done by self, not outside script
        pass



    def handle_input(self):
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.running = False
            # pygame often crashes after keydown, if elmaphys is called any time after
            # input starts on mouse down and ends on mouseup; sustain input in between
            elif event.type in (self.pygame.MOUSEBUTTONDOWN, self.pygame.MOUSEBUTTONUP, self.pygame.KEYDOWN, self.pygame.KEYUP):
                self.input = self.eventhandler.elmainput(self, event)
                #self.draw.draw(game, event, self.input, elmaphys) # draw only on self.input
            #self.draw.draw(game, event, elmaphys) # proceed drawing only on events, eg when mouse moves

    def loop(self, actions=None):
        "run the game loop, return true if done"
        self.prev_kuski_state = self.kuski_state

        # render can be temporarily set to true to display periodical runs
        # but only do render if pygame is initiated
        if self.arg_render and self.pygame is not None:
            self.handle_input()

        done = self.act(actions)

        #print(self.level.reward())

        # see above comment on rendering
        if self.arg_render and self.pygame is not None:
            self.draw.draw(self)
        #print( elmaphys.next_frame() ) # segmentation fault after pygame.init()
        #print('game running: %s' % self.running )
        #time.sleep(1)
        if not done:
            # if game hasn't quit level by max playtime, check if died/finished
            done = self.has_ended()
        if self.has_ended() and self.arg_man:
            self.restart()
        return done

    def act(self, actions=None):
        "perform actions with elma physics, return true if done"
        if actions is None:
            actions = self.input
        params = actions + [self.timestep, self.timesteptotal]
        self.kuski_state = self.elmaphys.next_frame( *params )
        #print(self.kuski_state)
        #if self.has_ended():    
        #    self.restart()
        self.level.reward()
        self.timesteptotal += self.timestep
        #print(self.score_delta, self.timesteptotal, self.level.maxplaytime)
        #print("episode: %d, score delta: %.2f, score: %.2f" % (self.episode, self.score_delta, self.score))
        if not self.arg_man and self.level.maxplaytime and self.timesteptotal * self.realtimecoeff > self.level.maxplaytime:
            #print('max play time over')
            return True
        return False


    def observation(self):
        # BodyPart body
        # BodyPart leftWheel
        # BodyPart rightWheel
        # Point2D headLocation
        # Point2D headCenterLocation

        # basic, game.observation()[:19]
        body_x = self.kuski_state['body']['location']['x']
        body_y = self.kuski_state['body']['location']['y']
        body_r = self.kuski_state['body']['rotation']
        lwx = self.kuski_state['leftWheel']['location']['x']
        lwy = self.kuski_state['leftWheel']['location']['y']
        lwr = self.kuski_state['leftWheel']['rotation']
        rwx = self.kuski_state['rightWheel']['location']['x']
        rwy = self.kuski_state['rightWheel']['location']['y']
        rwr = self.kuski_state['rightWheel']['rotation']
        head_x = self.kuski_state['headLocation']['x']
        head_y = self.kuski_state['headLocation']['y']
        head_cx = self.kuski_state['headCenterLocation']['x']
        head_cy = self.kuski_state['headCenterLocation']['y']
        direction = self.kuski_state['direction'] + 0.0 # int
        gravityScrollDirection = self.kuski_state['gravityScrollDirection']/10 + 0.0 # int # normalized
        gravityDir = self.kuski_state['gravityDir']/10 + 0.0 # int # normalized
        numTakenApples = self.kuski_state['numTakenApples']# + 0.0 # int
        changeDirPressedLast = self.kuski_state['changeDirPressedLast'] + 0.0 # int
        lastRotationTime = self.kuski_state['lastRotationTime']/100 # double # normalized? starts with 100, doesn't seem to increase but didn't try to turn
        #print(gravityDir)

        # full, game.observation() -- 33
        # unnamed
        pad4_x = self.kuski_state['pad4']['x']
        pad4_y = self.kuski_state['pad4']['y']
        pad = self.kuski_state['pad'] + 0.0 # int
        asd4 = self.kuski_state['asd4'] + 0.0 # int
        asd5 = self.kuski_state['asd5'] + 0.0 # int
        asdunk5 = self.kuski_state['asdunk5'] + 0.0 # int
        padz1 = self.kuski_state['padz1'] # double
        padz2 = self.kuski_state['padz2'] # double
        asd6 = self.kuski_state['asd6'] # double
        asd7 = self.kuski_state['asd7'] # double
        asd3 = self.kuski_state['asd3'] # double
        asd8 = self.kuski_state['asd8'] # double
        asdunk1 = self.kuski_state['asdunk1'] # double
        asdunk2 = self.kuski_state['asdunk2'] # double
        # not used
        #char isThrottling
        #BikeState bikeState # contains animation, not sure if necessary
        return np.array([body_x, body_y, body_r, lwx, lwy, lwr, rwx, rwy, rwr, head_x, head_y, head_cx, head_cy, direction, gravityScrollDirection,
        gravityDir, numTakenApples, changeDirPressedLast, lastRotationTime, pad4_x, pad4_y, pad, asd4, asd5, asdunk5, padz1, padz2, asd6, asd7, asd3, asd8, asdunk1, asdunk2])

    def elapsed_time(self):
        elapsed_time = time.time() - self.starttime
        if elapsed_time > 3600:
            elapsed_time /= 3600
            self.elmatimetotal /= 3600
            unit = 'hours'
        elif elapsed_time > 60:
            elapsed_time /= 60
            self.elmatimetotal /= 60
            unit = 'minutes'
        else:
            unit = 'seconds'
        return elapsed_time, unit

    def set_seed(self):
        self.seed = 43364
        print(self.BLUE2, "\nseed: %d\n" % self.seed, self.WHITE)
        #import random
        #self.seed = random.randint(0, 99999)
        np.random.seed(self.seed)
        #tf.random.set_seed(self.seed) # set in model if it uses tf


    def set_terminal_colors(self):
        # terminal colors
        # https://stackoverflow.com/a/39452138
        self.BLACK  = '\33[30m'
        self.RED    = '\33[31m'
        self.GREEN  = '\33[32m'
        self.YELLOW = '\33[33m'
        self.BLUE   = '\33[34m'
        self.VIOLET = '\33[35m'
        self.BEIGE  = '\33[36m'
        self.WHITE  = '\33[37m'
        self.GREY    = '\33[90m'
        self.RED2    = '\33[91m'
        self.GREEN2  = '\33[92m'
        self.BLUE2   = '\33[94m'
        self.WHITE2  = '\33[97m'


    def init_pygame(self):
        import os, pygame, eventhandler, draw, gui, colors
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.display.set_caption('ElmAI')
        # pygame.event.set_blocked([pygame.KEYDOWN, pygame.KEYUP]) # block keydown that crashes phys? still crashing on keypress
        self.pygame = pygame
        self.size = 800, 640
        self.width, self.height = self.size
        self.screen = pygame.display.set_mode(self.size)
        # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
        self.font = pygame.font.SysFont("monospace", 18)
        self.eventhandler = eventhandler
        self.gui = gui
        self.draw = draw
        self.colors = colors
        #gui.game = self
        #draw.game = self

