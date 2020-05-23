import sys, time, os
import game, eventhandler

game = game.Game()
args = sys.argv
if len(args) < 3:
    print("usage: %s 0lp31 100 render man" % (os.path.basename(__file__)))
    print("for running level 0lp31.lev, approx 100 real time seconds with chosen flags")
    print("order of flags dont matter")
    #print("default flags: fps80")
    sys.exit()
arg_man = True if 'man' in args else False # play manually
arg_render = True if 'render' in args or arg_man else False # render gfx with pygame

#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"0lp31.lev")
#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"1dg54.lev") # qwquu002
game.levpath = r"C:\Users\Sara\Desktop\robin\elma\lev"
game.levfilename = "%s.lev" % (args[1])
game.maxplaytime = int(args[2]) if args[2].isnumeric() else 0 # quit script after last run has exceeded this many seconds

if arg_man:
    game.timestep = 0.002 # oke speed for playing manually, also this computer (Zazza) renders the game almost with same elma time as real time
else:
    # default timestep
    game.timestep = 0.00546 # fast play, 80 fps, fastest possible calculated physics according to jon, as slower than this does double or more physics iteration per step

# calc timestep for 80 fps
# 1/80/2,2893772893772893772893772893773 = 0,00546
# 1/1000/2,2893772893772893772893772893773 = 0,0004368
# fast/slow below means how the gameplay feels in pygame
#game.timestep = 0.015 # ultra fast play, makes elma crash
#game.timestep = 0.01 # very fast play, makes elma unstable and wheels going everywhere
#game.timestep = 0.001 # slow play
#ame.timestep = 0.0004368 # 1000 fps, ultra slow motion, okeol first candidate
#game.timestep = 0.0008736 # 500 fps, okeol second candidate


if arg_render:
    import pygame, draw, gui, colors
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    pygame.display.set_caption('ElmAI')
    # pygame.event.set_blocked([pygame.KEYDOWN, pygame.KEYUP]) # block keydown that crashes phys? still crashing on keypress
    game.pygame = pygame
    game.size = 800, 640
    game.width, game.height = game.size
    game.screen = pygame.display.set_mode(game.size)
    # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
    game.font = pygame.font.SysFont("monospace", 18)

    game.gui = gui
    game.draw = draw
    game.colors = colors
    #gui.game = game
    #draw.game = game

# to check this: make replay and store timesteptotal,
# then check rec time in elma 12.53 28.67
# for example timestep = 0.002 with timesteptotal of 12.53 makes a rec of 28.67 seconds
# so 28.67 / 12.53 ~ 2,29, which is pretty much jon's constant 
game.realtimecoeff = 2.2893772893772893772893772893773 # exact number provided by jon
game.timesteptotal = 0.0 # total timesteps current run
game.lasttime = None # how much time in seconds last run will be in the .rec file
game.elmatimetotal = 0 # how much elma time that would have been spent if this session would have been play in real time in elma
game.starttime = time.time() # now, when this session started


# after pygame.init()
import elmaphys # must be imported after pygame.init()
elmaphys.init(game.levpath + '\\' + game.levfilename)

game.running = True
game.input = [0, 0, 0, 0, 0, 0]
while game.running:
    if arg_render:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            # pygame often crashes after keydown, if elmaphys is called any time after
            # input starts on mouse down and ends on mouseup; sustain input in between
            elif arg_man and event.type in (game.pygame.MOUSEBUTTONDOWN, game.pygame.MOUSEBUTTONUP, pygame.KEYDOWN, pygame.KEYUP):
                game.input = eventhandler.elmainput(game, event)
                #game.draw.draw(game, event, game.input, elmaphys) # draw only on game.input
            #game.draw.draw(game, event, elmaphys) # proceed drawing only on events, eg when mouse moves

    params = game.input + [game.timestep, game.timesteptotal]
    game.kuski_state = elmaphys.next_frame( *params ) # get kuski state before drawing first time
    if game.kuski_state['isDead'] or game.kuski_state['finishedTime']:
        if game.kuski_state['isDead']:
            pass
            #print('kusku died: %.2f' % game.timesteptotal)
        else:
            print('lev complete: %.2f' % game.timesteptotal)
        game.lasttime = game.timesteptotal * game.realtimecoeff
        game.elmatimetotal += game.lasttime
        game.timesteptotal = 0
        filenametime = "%.02f" % game.lasttime
        filenametime = filenametime.replace('.', '') # remove dot from filename, because elma can't handle it
        #elmaphys.save_replay("00x%s.rec" % filenametime, game.levfilename) # working
        if game.maxplaytime and time.time() - game.starttime > game.maxplaytime:
            game.running = False

    if arg_render:
        game.draw.draw(game, event)
    game.timesteptotal += game.timestep
    #print( elmaphys.next_frame() ) # segmentation fault after pygame.init()
    #print('game running: %s' % game.running )
    #time.sleep(1)

print('SESSION FINISHED:')
elapsed_time = time.time() - game.starttime
if elapsed_time > 3600:
    elapsed_time /= 3600
    game.elmatimetotal /= 3600
    unit = 'hours'
elif elapsed_time > 60:
    elapsed_time /= 60
    game.elmatimetotal /= 60
    unit = 'minutes'
else:
    unit = 'seconds'
print('Real time: %.02f %s' % (elapsed_time, unit))
print('Elma time: %.02f %s' % (game.elmatimetotal, unit))
print('Processing %.02f times faster than playing in realtime' % (game.elmatimetotal/elapsed_time))