import time, random, winsound
import numpy as np
import db

class Game:
    def __init__(self):
        self.set_terminal_colors()
        self.db = db
        self.init_db()
        #self.set_seed()
        self.pygame = None
        self.eol = None
        self.np = np
        self.winsound = winsound
        self.arg_render_snapshot = False
        self.render_snapshots = []

        # man framebyframe vars
        self.inputs = []
        self.kuski_states = []
        self.timesteps = []
        self.rewind = 0
        self.do_next_frame = False

        # to check this: make replay and store timesteptotal,
        # then check rec time in elma 12.53 28.67
        # for example timestep = 0.002 with timesteptotal of 12.53 makes a rec of 28.67 seconds
        # so 28.67 / 12.53 ~ 2,29, which is pretty much jon's constant 
        self.realtimecoeff = 2.289377289377289681482352534658275544643402099609375 # provided by PlayerData.h 2.2893772893772893772893772893773 # exact number provided by jon
        self.timesteptotal = 0.0 # total timesteps current run
        self.lasttime = None # how much time in seconds last run will be in the .rec file
        self.elmatimetotal = 0 # how much elma time that would have been spent if this session would have been play in real time in elma
        self.starttime = None # start from when training starts # time.time() # now, when this session started
        self.input = [0, 0, 0, 0, 0, 0]
        self.score_delta = 0 # score of last frame
        self.score = 0 # total score gathered this run
        self.last_score = 0 # total score gathered last run
        self.hiscore = -20 # highest score this session, should be lower than death, so that bad rides also register
        self.lowscore = -20 # lowest score this session, should be same as or lower than hiscore
        self.batch_hiscore = 0 # highest score this batch
        self.batch_lowscore = 0 # lowest score this batch
        self.num_taken_apples = 0

        self.training = False
        self.noise = True
        self.model = None
        self.load = None
        self.rec = None
        self.activation = 'softmax'
        self.optimizer = 'rmsprop'
        self.loss = 'sparse_categorical_crossentropy'
        self.batch = 0
        self.frame = 0
        self.recframe = 0
        self.recframe_offset = 0
        self.episode = 0
        self.n_episodes = 1
        self.n_actions = 1 # first action is noop
        self.n_frames = 0
        # [accelerate, brake, left, right, turn, supervolt]
        # self.actions[0] is elmainputs for noop
        # append full list of elmainputs to send for each available game action
        self.actions = [[0, 0, 0, 0, 0, 0]]
        self.actions_str = '' # any letters of ABLRTS
        self.n_observations = 1 # len(game.observation())
        self.gamma = 0.99 # discount factor
        self.learning_rate = 0.01
        self.save_rec = False
        self.training = False
        self.died = False
        self.finished = False
        self.die_programatically = False

    def has_ended(self):
        return self.kuski_state['isDead'] or self.kuski_state['finishedTime'] > 0
        #return self.kuski_state[10] > 0 or self.kuski_state[11] > 0
    
    def end(self):
        #print("Ended level programatically")
        self.elmaphys.restart_level()

    def rec_name(self, suffix='ai'):
        filenametime = "%.02f" % (self.timesteptotal * self.realtimecoeff)
        filenametime = filenametime.replace('.', '') # remove dot from filename, because elma can't handle it
        #filename = "00x%s_%d_%s.rec" % (filenametime, self.score, self.level.filename_wo_ext()) # old format
        filename = "%s_%sribot-%s.rec" % (self.level.filename_wo_ext(), filenametime, suffix) #02x2226ribot-ai
        return filename
    
    def model_save_name(self):
        filename = self.rec_name()
        filename += "_seed%d_" % (self.seed)
        #filename += "episodes%d_" % (self.episode) # to use this it should calc the total also if model was loaded
        filename += "observations%d_" % (self.n_observations)
        filename += "actions%s_" % (self.actions_str)
        filename += "lr%f_" % (self.learning_rate)
        filename += "gamma%f_" % (self.gamma)
        filename += "%s_%s_%s" % (self.activation, self.optimizer, self.loss)
        return filename

    def set_fps(self, fps=80, timestep=None):
        if timestep is None:
            # set fps by fps value
            fps = max(fps, 30) # min 30 which is way too unstable anyway
            self.timestep = (1 / fps) / self.realtimecoeff
            self.fps = fps
        else:
            # set fps by timestpe value
            self.timestep = timestep
            self.fps = int( 1/(self.timestep * self.realtimecoeff) )
        self.realtimestep = 1 / self.fps
        print("fps: %d, timestep: %.4f, realtimestep: %.4f" % ( self.fps, self.timestep, self.realtimestep ))

    def restart(self):
        if self.arg_eol:
            # as eol doesn't have kuski_state as dict() implemented
            return

        self.lasttime = self.timesteptotal * self.realtimecoeff
        #print('time: %.2f, score: %.2f, timesteptotal: %.2f' % (self.lasttime, self.score, self.timesteptotal))
        self.elmatimetotal += self.lasttime
        self.timesteptotal = 0.0
        #if self.kuski_state[10] > 0:
        if self.kuski_state['isDead']:
            self.died = True
            #print('kuski died, time: %.2f, score: %.2f' % (self.lasttime, self.score))
            pass
        #elif self.kuski_state[11] > 0:
        elif self.kuski_state['finishedTime']:
            self.finished = True
            #print(
            #    self.VIOLET + 'lev completed, time: %.2f, score: %.2f, var finishedTime: %.2f, episode: %d'
            #    % (self.lasttime, self.score, self.kuski_state['finishedTime'], self.episode),
            #    self.WHITE)
        if self.save_rec or self.hiscore and self.score > self.level.db_row.hiscore and not self.arg_man:
            #self.elmaphys.save_replay("00x%s_%d_%s.rec" % (filenametime, self.score, random.randint(10,99)), self.level.filename) # working
            self.elmaphys.save_replay(self.rec_name(), self.level.filename) # working
            self.winsound.Beep(1231, 123)
            self.winsound.Beep(1231, 123)
            #if self.model is not None:
            #    print('saving keras model: ' + self.model_save_name())
            #    self.model.save("keras_models\\" + self.model_save_name())
        #if self.maxplaytime and time.time() - self.starttime > self.maxplaytime:
        #    self.running = False

        outcome = ''
        outcome = 'FINISHED' if self.finished else outcome
        outcome = 'DIED' if self.died else outcome
        output = 'episode %d, score: %.4f/%.4f, time: %.3f, apples: %d, fps: %d, seed: %d, %s' % \
            (self.episode, self.score, self.level.db_row.hiscore, self.lasttime,
            self.kuski_state['numTakenApples'], self.fps, self.seed, outcome)
        self.last_score = self.score
        if self.score > self.hiscore:
            self.winsound.Beep(1231, 123)
            self.hiscore = self.score
            if self.score > self.level.db_row.hiscore and not self.arg_man:
                self.level.db_row.update_record(hiscore=self.score)
                self.db.db.commit()
            print(self.YELLOW + output + self.WHITE)
        elif self.score < self.lowscore:
            self.lowscore = self.score
            #print(self.YELLOW + output + self.WHITE)
        if self.episode == 0:
            print(self.YELLOW + output + self.WHITE)
        if not self.training:
            # print this when periodical test runs happen, ie arg_render are set temporarily
            # or when playing manually
            print(output)
        #print('episode %d, score: %.2f, time: %.2f' % (episode, self.score, self.timesteptotal * self.realtimecoeff))
        self.batch_hiscore = max(self.batch_hiscore, self.score)
        self.batch_lowscore = min(self.batch_lowscore, self.score)

        self.num_taken_apples = 0
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

    # emulate openai env.method
    def reset(self):
        # check if game has progressed (don't restart if resetting as first action in agent)
        #print("game.reset, ep: %d, frame: %d" % (self.episode, self.frame))
        self.die_programatically = False # before return
        if self.timesteptotal > 0:
            self.restart()
        if self.arg_eol:
            self.eol.reset(self)
            return self.eol.observation()[:self.n_observations]
        #return self.observation()[:self.n_observations]
        #return self.kuski_state[:self.n_observations]
        return np.array(self.timesteptotal)

    # emulated openai env.method
    def step(self, action):
        elmainputs = self.actions[action][:] # [0, 0, ...]
        #print(self.episode, self.frame, action, elmainputs)
        done = self.loop(elmainputs)
        if self.arg_eol:
            observation = self.eol.observation()[:self.n_observations] # after action taken
        else:
            #observation = self.observation()[:self.n_observations] # after action taken
            #observation = self.kuski_state[:self.n_observations]
            observation = np.array(self.timesteptotal)
        reward = self.score_delta
        info = dict()
        return observation, reward, done, info

    # emulated openai env.method
    def render(self):
        # render is done by self, not outside script
        pass



    # moved to eventhandler
    #def handle_input(self):
    #    pass

    def loop(self, actions=None):
        "run the game loop, return true if done"
        self.prev_kuski_state = self.kuski_state

        # render can be temporarily set to true to display periodical runs
        # but only do render if pygame is initiated
        if (self.arg_render or self.arg_man or self.arg_framebyframe) and self.pygame is not None:
            self.eventhandler.loop(self)

        # after eventhandler but before return in framebyframe
        if self.rec is not None:
            self.recframe = int(self.timesteptotal * self.realtimecoeff * 30)
            if self.recframe >= len( self.rec.frames ):
                # don't go beyond last frame of rec
                self.recframe = len( self.rec.frames ) - 1

        if self.arg_framebyframe and self.arg_man and not self.do_next_frame:
            #print("not looping")
            # draw screen before any keypress
            self.draw.draw(self)
            return

        done = self.act(actions) or self.die_programatically

        # see above comment on rendering
        if (self.arg_render or self.arg_man or self.arg_framebyframe) and self.pygame is not None:
            if self.arg_framebyframe and not self.arg_man:
                input('>')
            self.draw.draw(self)
            if self.arg_man and self.do_next_frame:
                self.frame += 1
            elif self.arg_test:
                time.sleep(0.01)

            if self.arg_render_snapshot and self.frame % 10 == 0:
                pathfilename = "snapshots\\snapshot%03d.png" % self.frame
                self.pygame.image.save(self.screen, pathfilename)
                try:
                    from PIL import Image
                    im = Image.open(pathfilename)
                    self.render_snapshots.append( im )
                    #print('Loaded %s for gif' % (im))
                except:
                    raise
        #print( elmaphys.next_frame() ) # segmentation fault after pygame.init()
        #print('game running: %s' % self.running )
        #time.sleep(1)
        if not done:
            # if game hasn't quit level by max playtime, check if died/finished
            done = self.has_ended()
        if self.has_ended() and self.arg_man and not self.arg_framebyframe:
            self.restart()
        return done

    def act(self, actions=None):
        "perform actions with elma physics, return true if done"
        if actions is None:
            actions = self.input

        #print(self.episode, self.frame, actions)
        # self.input = [0, 0, 0, 0, 0, 0]
        # [accelerate, brake, left, right, turn, supervolt]
        # start right automatically, even if turn button is not included in agent actions
        if self.rec is None and not self.arg_man and self.frame == 0 and self.level.db_row.start_right:
            actions[4] = 1
            #print(self.episode, self.frame, actions)
            pass

        params = actions + [self.timestep, self.timesteptotal]
        #print(self.frame, params)
        if self.arg_eol and not self.has_ended():
            self.kuski_state = self.eol.next_frame( self, *params )
        else:
            self.kuski_state = self.elmaphys.next_frame( *params )
        #print(self.kuski_state)
        #if self.has_ended():
        #    self.restart()
        self.level.reward()
        self.timesteptotal += self.timestep
        #print(self.score_delta, self.timesteptotal, self.level.db_row.maxplaytime)
        #print("episode: %d, score delta: %.2f, score: %.2f" % (self.episode, self.score_delta, self.score))
        # done is not yet implemented in eol
        if not self.arg_eol and not self.arg_man and self.level.db_row.maxplaytime and self.timesteptotal * self.realtimecoeff > self.level.db_row.maxplaytime:
            #print('max play time over')
            return True
        return False


    def observation(self):
        pass
        # todo: instead of creating python dict kuski_state,
        # observation would probably be faster if returned from elmaphys.pyx
        # since many kuskistate values are not used MUCH elsewhere in code
        # used at the time of writing: isDead, finishedTime, body location x, y (in level for flower distance)

        # BodyPart body
        # BodyPart leftWheel
        # BodyPart rightWheel
        # Point2D headLocation
        # Point2D headCenterLocation

        # observation optimized as array so no longer used
        """body_x = self.kuski_state['body']['location']['x']
        body_y = self.kuski_state['body']['location']['y']
        #body_spd_x = self.kuski_state['body']['dword58']['x']
        #body_spd_y = self.kuski_state['body']['dword58']['y']
        lwx = self.kuski_state['leftWheel']['location']['x']
        lwy = self.kuski_state['leftWheel']['location']['y']
        #lw_spd_x = self.kuski_state['leftWheel']['dword58']['x']
        #lw_spd_y = self.kuski_state['leftWheel']['dword58']['y']
        rwx = self.kuski_state['rightWheel']['location']['x']
        rwy = self.kuski_state['rightWheel']['location']['y']
        #rw_spd_x = self.kuski_state['rightWheel']['dword58']['x']
        #rw_spd_y = self.kuski_state['rightWheel']['dword58']['y']
        head_x = self.kuski_state['headLocation']['x']
        head_y = self.kuski_state['headLocation']['y']
        body_rot = self.kuski_state['body']['rotation']
        #body_rot_spd = self.kuski_state['body']['rotationSpeed']
        direction = self.kuski_state['direction'] + 0.0 # int"""


        #lwr = self.kuski_state['leftWheel']['rotation']
        #rwr = self.kuski_state['rightWheel']['rotation']
        #head_cx = self.kuski_state['headCenterLocation']['x'] # this is more like body location, or at least very close
        #head_cy = self.kuski_state['headCenterLocation']['y'] # this is more like body location, or at least very close
        #gravityScrollDirection = self.kuski_state['gravityScrollDirection']/10 + 0.0 # int # normalized
        #gravityDir = self.kuski_state['gravityDir']/10 + 0.0 # int # normalized
        #numTakenApples = self.kuski_state['numTakenApples']# + 0.0 # int
        #changeDirPressedLast = self.kuski_state['changeDirPressedLast'] + 0.0 # int
        #lastRotationTime = self.kuski_state['lastRotationTime']/100 # double # normalized? starts with 100, doesn't seem to increase but didn't try to turn
        #print(gravityDir)
        #print(body_x, head_cx)

        # full, game.observation() -- 33
        # unnamed
        #pad4_x = self.kuski_state['pad4']['x']
        #pad4_y = self.kuski_state['pad4']['y']
        #pad = self.kuski_state['pad'] + 0.0 # int
        #asd4 = self.kuski_state['asd4'] + 0.0 # int
        #asd5 = self.kuski_state['asd5'] + 0.0 # int
        #asdunk5 = self.kuski_state['asdunk5'] + 0.0 # int
        #padz1 = self.kuski_state['padz1'] # double
        #padz2 = self.kuski_state['padz2'] # double
        #asd6 = self.kuski_state['asd6'] # double
        #asd7 = self.kuski_state['asd7'] # double
        #asd3 = self.kuski_state['asd3'] # double
        #asd8 = self.kuski_state['asd8'] # double
        #asdunk1 = self.kuski_state['asdunk1'] # double
        #asdunk2 = self.kuski_state['asdunk2'] # double
        # not used
        #char isThrottling
        #BikeState bikeState # contains animation, not sure if necessary
        #return np.array([body_x, body_y, lwx, lwy, rwx, rwy, head_x, head_y, body_rot, direction])
        #return np.array([body_x, body_y, lwx, lwy, rwx, rwy, head_x, head_y, body_rot, direction, body_spd_x, body_spd_y, lw_spd_x, lw_spd_y, rw_spd_x, rw_spd_y, body_rot_spd])
        #return np.array([body_x, body_y, body_r, lwx, lwy, lwr, rwx, rwy, rwr, head_x, head_y, head_cx, head_cy, direction, gravityScrollDirection,
        #gravityDir, numTakenApples, changeDirPressedLast, lastRotationTime, pad4_x, pad4_y, pad, asd4, asd5, asdunk5, padz1, padz2, asd6, asd7, asd3, asd8, asdunk1, asdunk2])

    def elapsed_time(self):
        elapsed_time = time.time() - self.starttime
        elapsed_elma_time = self.elmatimetotal
        if elapsed_time > 3600:
            elapsed_time /= 3600
            elapsed_elma_time /= 3600
            unit = 'hours'
        elif elapsed_time > 60:
            elapsed_time /= 60
            elapsed_elma_time /= 60
            unit = 'minutes'
        else:
            unit = 'seconds'
        return elapsed_time, elapsed_elma_time, unit

    def set_seed(self, seed=None):
        if seed is None:
            import random
            seed = random.randint(0, 999999)
        self.seed = seed
        np.random.seed(self.seed)
        #tf.random.set_seed(self.seed) # set in model if it uses tf
        print(self.BLUE2, "\nseed: %d\n" % self.seed, self.WHITE)


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


    def init_db(self):
        self.setting = dict()
        db = self.db.db
        for setting in ('seed', 'episodes', 'level', 'fps', 'agent', 'actions', 'man', 'render', 'test', 'eol', 'load', 'framebyframe'):
            query = db.setting.name == setting
            row = db(query).select().first()
            if not row:
                value = input("Value for %s (index for list value): " % (setting))
                int_value = int(value) if value.isnumeric() else None
                str_value = value if not value.isnumeric() else None
                row_id = db.setting.insert( name=setting, str_value=str_value, int_value=int_value )
                row = db.setting[row_id]
                db.commit()
            self.setting[setting] = row


    def init_eol(self):
        import eol
        self.eol = eol
        self.realtimecoeff = 0 # not applicable in eol, as eol runs in realtime

    def init_pygame(self):
        import os, pygame, eventhandler, draw, gui, colors
        from win32api import GetSystemMetrics

        self.width = int( GetSystemMetrics(0)/2 )
        self.height = int( GetSystemMetrics(1)/2 )
        self.size = self.width, self.height
        #os.environ['SDL_VIDEO_CENTERED'] = '1'
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.width, 31)
        pygame.init()
        pygame.display.set_caption('ElmAI')
        # pygame.event.set_blocked([pygame.KEYDOWN, pygame.KEYUP]) # block keydown that crashes phys? still crashing on keypress
        self.pygame = pygame
        #self.size = 800, 640
        #self.width, self.height = self.size
        self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.redraw = True
        self.zoom_mode = 3
        # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
        self.font = pygame.font.SysFont("monospace", 18)
        self.eventhandler = eventhandler
        self.gui = gui
        self.draw = draw
        self.colors = colors
        #gui.game = self
        #draw.game = self
        self.image_head = pygame.image.load('gfx\\q1head.png').convert_alpha()
        self.image_bike = pygame.image.load('gfx\\q1bike.png').convert_alpha()
        self.image_wheel = pygame.image.load('gfx\\q1wheel.png').convert_alpha()

        if self.rec is not None:
            self.rec_image_head = pygame.image.load('gfx\\q1head_outline.png').convert_alpha()
            self.rec_image_bike = pygame.image.load('gfx\\q1bike_outline.png').convert_alpha()
            self.rec_image_wheel = pygame.image.load('gfx\\q1wheel_outline.png').convert_alpha()
