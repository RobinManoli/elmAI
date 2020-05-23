import pygame, sys, time, os
import game, eventhandler

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.display.set_caption('ElmAI')
# pygame.event.set_blocked([pygame.KEYDOWN, pygame.KEYUP]) # block keydown that crashes phys? still crashing on keypress
size = 800, 640
game = game.Game(pygame, size)

#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"0lp31.lev")
#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"1dg54.lev") # qwquu002
game.levpath = r"C:\Users\Sara\Desktop\robin\elma\lev"
game.levfilename = "qwquu002.lev"
game.levtime = 0.0
game.lev_lasttime = None

# calc timestep for 80 fps
# 1/80/2,2893772893772893772893772893773 = 0,00546
# 1/1000/2,2893772893772893772893772893773 = 0,0004368
# fast/slow below means how the gameplay feels in pygame
#game.timestep = 0.015 # ultra fast play, makes elma crash
#game.timestep = 0.01 # very fast play, makes elma unstable and wheels going everywhere
game.timestep = 0.00546 # fast play, fastest possible calculated physics according to jon, as slower than this does double or more physics iteration per step
#game.timestep = 0.001 # slow play
#game.timestep = 0.002 # oke speed play
#ame.timestep = 0.0004368 # 1000 pfs, ultra slow motion, okeol first candidate
#game.timestep = 0.0008736 # 500 pfs, okeol second candidate

# after pygame.init()
import elmaphys # must be imported after pygame.init()
elmaphys.init(game.levpath + '\\' + game.levfilename)


game.running = True
game.input = [0, 0, 0, 0, 0, 0]
while game.running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
        # pygame often crashes after keydown, if elmaphys is called any time after
        # input starts on mouse down and ends on mouseup; sustain input in between
        elif event.type in (game.pygame.MOUSEBUTTONDOWN, game.pygame.MOUSEBUTTONUP, pygame.KEYDOWN, pygame.KEYUP):
            game.input = eventhandler.elmainput(game, event)
            #game.draw.draw(game, event, game.input, elmaphys) # draw only on game.input

        #game.draw.draw(game, event, elmaphys) # proceed drawing only on events, eg when mouse moves
    params = game.input + [game.timestep, game.levtime]
    game.kuski_state = elmaphys.next_frame( *params ) # get kuski state before drawing first time
    if game.kuski_state['isDead'] or game.kuski_state['finishedTime']:
        if game.kuski_state['isDead']:
            print('kusku died: %.2f' % game.levtime)
        else:
            print('lev complete: %.2f' % game.levtime)
        game.lev_lasttime = game.levtime
        game.levtime = 0
        elmaphys.save_replay()

    game.draw.draw(game, event)
    game.levtime += game.timestep
    #print( elmaphys.next_frame() ) # segmentation fault after pygame.init()
    #print('game running: %s' % game.running )
    #time.sleep(1)
