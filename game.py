import time, random
import numpy as np 

class Game:
    def __init__(self):
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
        self.batch = 0
        self.frame = 0
        self.episode = 0
        self.n_episodes = 1
        self.n_actions = 2 # 4 # action_size = 4 # simplistic, 7 elma, 13 precise
        self.n_observations = 19 # 33 # len(game.observation())
        self.gamma = 0.99 # discount factor
        self.learning_rate = 0.01
        self.save_rec = False
        self.training = False
        self.died = False
        self.finished = False


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

    def has_ended(self):
        return self.kuski_state['isDead'] or self.kuski_state['finishedTime'] > 0
    
    def end(self):
        #print("Ended level programatically")
        self.elmaphys.restart_level()

    def restart(self):
        self.lasttime = self.timesteptotal * self.realtimecoeff
        #print('time: %.2f, score: %.2f, timesteptotal: %.2f' % (self.lasttime, self.score, self.timesteptotal))
        self.elmatimetotal += self.lasttime
        self.timesteptotal = 0.0
        if self.kuski_state['isDead']:
            #print('kuski died, time: %.2f, score: %.2f' % (self.lasttime, self.score))
            pass
        elif self.kuski_state['finishedTime']:
            print('lev completed, time: %.2f, score: %.2f' % (self.lasttime, self.score))
        filenametime = "%.02f" % self.lasttime
        filenametime = filenametime.replace('.', '') # remove dot from filename, because elma can't handle it
        if self.save_rec:
            #self.elmaphys.save_replay("00x%s_%d_%s.rec" % (filenametime, self.score, random.randint(10,99)), self.level.filename) # working
            self.elmaphys.save_replay("00x%s_%d.rec" % (filenametime, self.score), self.level.filename) # working
        if self.maxplaytime and time.time() - self.starttime > self.maxplaytime:
            self.running = False

        self.last_score = self.score
        if self.score > self.hiscore:
            self.hiscore = self.score
            print('episode %d, hiscore: %.2f, time: %.2f, died: %s, finished: %s' %(self.episode, self.score, self.lasttime, self.died, self.finished))
        elif self.score < self.lowscore:
            self.lowscore = self.score
            print('episode %d, lowscore: %.2f, time: %.2f, died: %s, finished: %s' %(self.episode, self.score, self.lasttime, self.died, self.finished))
        if not self.training:
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
        #self.n_action_space = 2
    def step(self, action):
        elmainputs = self.action_space(action) # [0, 0, ...]
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
            elif self.arg_man and event.type in (self.pygame.MOUSEBUTTONDOWN, self.pygame.MOUSEBUTTONUP, self.pygame.KEYDOWN, self.pygame.KEYUP):
                self.input = self.eventhandler.elmainput(self, event)
                #self.draw.draw(game, event, self.input, elmaphys) # draw only on self.input
            #self.draw.draw(game, event, elmaphys) # proceed drawing only on events, eg when mouse moves

    def loop(self, actions=None):
        "run the game loop, return true if done"
        self.prev_kuski_state = self.kuski_state

        if self.arg_render:
            self.handle_input()

        done = self.act(actions)

        #print(self.level.reward())

        if self.arg_render:
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

    def action_space(self, action=None):
        # accelerate = brake = left = right = turn = supervolt = 0
        actions = []
        # simplistic, game.action_space()[:2] or game.action_space()[:4]
        #actions.append(0) # do nothing, happens when all actions are 0
        actions.append(0) # 00 accelerate
        actions.append(0) # 01 brake
        actions.append(0) # 02 turn
        # elma, game.action_space()[:6] or game.action_space()[:7]
        actions.append(0) # 03 left
        actions.append(0) # 04 right
        actions.append(0) # 05 supervolt
        if action is not None:
            if action > 0:
                actions[action-1] = 1 # makes one of the zeroes = 1
            return actions

        # precise, game.action_space() -- 13
        # below need to be translated into elmainput of 6 actions or no action (all zeroes)
        """actions.append(0) # 07 accelerate + left
        actions.append(0) # 08 accelerate + right
        actions.append(0) # 09 accelerate + supervolt
        actions.append(0) # 10 brake + left
        actions.append(0) # 11 brake + right
        actions.append(0) # 12 brake + supervolt
        # super precise turn + other keys, brake + acc"""
        return actions


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
        gravityScrollDirection = self.kuski_state['gravityScrollDirection'] + 0.0 # int
        gravityDir = self.kuski_state['gravityDir'] + 0.0 # int
        numTakenApples = self.kuski_state['numTakenApples'] + 0.0 # int
        changeDirPressedLast = self.kuski_state['changeDirPressedLast'] + 0.0 # int
        lastRotationTime = self.kuski_state['lastRotationTime'] # double

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
