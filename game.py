import time

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
        self.starttime = time.time() # now, when this session started
        self.input = [0, 0, 0, 0, 0, 0]

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


    def restart(self):
        if self.kuski_state['isDead']:
            pass
            #print('kusku died: %.2f' % self.timesteptotal)
        else:
            print('lev complete: %.2f' % self.timesteptotal)
        self.lasttime = self.timesteptotal * self.realtimecoeff
        self.elmatimetotal += self.lasttime
        self.timesteptotal = 0
        filenametime = "%.02f" % self.lasttime
        filenametime = filenametime.replace('.', '') # remove dot from filename, because elma can't handle it
        #elmaphys.save_replay("00x%s.rec" % filenametime, self.levfilename) # working
        if self.maxplaytime and time.time() - self.starttime > self.maxplaytime:
            self.running = False


    def render(self, arg_man):
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.running = False
            # pygame often crashes after keydown, if elmaphys is called any time after
            # input starts on mouse down and ends on mouseup; sustain input in between
            elif arg_man and event.type in (self.pygame.MOUSEBUTTONDOWN, self.pygame.MOUSEBUTTONUP, self.pygame.KEYDOWN, self.pygame.KEYUP):
                self.input = self.eventhandler.elmainput(self, event)
                #self.draw.draw(game, event, self.input, elmaphys) # draw only on self.input
            #self.draw.draw(game, event, elmaphys) # proceed drawing only on events, eg when mouse moves


    def action_space():
        # accelerate = brake = left = right = turn = supervolt = 0
        actions = []
        # simplistic
        actions.append(0) # 00 do nothing
        actions.append(0) # 01 accelerate
        actions.append(0) # 02 brake
        actions.append(0) # 03 turn
        # elma
        actions.append(0) # 04 left
        actions.append(0) # 05 right
        actions.append(0) # 06 supervolt
        # precise
        actions.append(0) # 07 accelerate + left
        actions.append(0) # 08 accelerate + right
        actions.append(0) # 09 accelerate + supervolt
        actions.append(0) # 10 brake + left
        actions.append(0) # 11 brake + right
        actions.append(0) # 12 brake + supervolt
        # super precise turn + other keys, brake + acc

    def observation(self):
        # BodyPart body
        # BodyPart leftWheel
        # BodyPart rightWheel
        # Point2D headLocation
        # Point2D headCenterLocation
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
        return (body_x, body_y, body_r, lwx, lwy, lwr, rwx, rwy, rwr, head_x, head_y, head_cx, head_cy, direction, gravityScrollDirection,
        gravityDir, numTakenApples, changeDirPressedLast, lastRotationTime, pad4_x, pad4_y, pad, asd4, asd5, asdunk5, padz1, padz2, asd6, asd7, asd3, asd8, asdunk1, asdunk2)
