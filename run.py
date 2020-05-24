import sys, time, os
import game

game = game.Game()
args = sys.argv
if len(args) < 3:
    print("usage: %s 0lp31 100 render man fps500|fps1000" % (os.path.basename(__file__)))
    print("for running level 0lp31.lev, approx 100 real time seconds with chosen flags")
    print("order of flags dont matter")
    #print("default flags: fps80")
    sys.exit()
arg_man = True if 'man' in args else False # play manually
arg_render = True if 'render' in args or arg_man else False # render gfx with pygame
arg_fps1000 = True if 'fps1000' in args else False
arg_fps500 = True if 'fps500' in args else False

#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"0lp31.lev")
#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"1dg54.lev") # qwquu002
game.levpath = r"C:\Users\Sara\Desktop\robin\elma\lev"
game.levfilename = "%s.lev" % (args[1])
game.maxplaytime = int(args[2]) if args[2].isnumeric() else 0 # quit script after last run has exceeded this many seconds

if arg_fps500:
    game.timestep = 0.0008736 # 500 fps, okeol second candidate
elif arg_fps1000:
    game.timestep = 0.0004368 # 1000 fps, ultra slow motion, okeol first candidate
elif arg_man:
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


if arg_render:
    game.init_pygame()

# after pygame.init()
import elmaphys # must be imported after pygame.init()
elmaphys.init(game.levpath + '\\' + game.levfilename)

game.running = True
while game.running:
    if arg_render:
        game.render(arg_man)

    params = game.input + [game.timestep, game.timesteptotal]
    game.kuski_state = elmaphys.next_frame( *params ) # get kuski state before drawing first time
    if game.kuski_state['isDead'] or game.kuski_state['finishedTime']:
        game.restart()

    if arg_render:
        game.draw.draw(game)
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
print( len(game.observation()) )
print( game.observation() )