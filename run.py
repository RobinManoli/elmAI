import sys, time, os
import game, level

game = game.Game()
game.args = sys.argv
# todo: bug or feature? with enough args number can be omitted and train forever
if len(game.args) < 3:
    print("usage: %s 0lp31 100 render man fps30|fps500|fps1000 rltf|cem|ddpg" % (os.path.basename(__file__)))
    print("for running level 0lp31.lev, approx 100 real time seconds with chosen flags")
    print("order of flags dont matter")
    print("shortcut: %s 0lp31 <-- will play manually if no other flags" % (os.path.basename(__file__)))
    #print("default flags: fps80")
    if len(game.args) < 2:
        sys.exit()
    game.args.append('man')
game.arg_man = True if 'man' in game.args else False # play manually
game.arg_render = True if 'render' in game.args or game.arg_man else False # render gfx with pygame
game.arg_fps1000 = True if 'fps1000' in game.args else False
game.arg_fps500 = True if 'fps500' in game.args else False
game.arg_fps30 = True if 'fps30' in game.args else False
# in case of more cem implementations, they can here be called cem1, cem2, etc
game.arg_cem = True if 'cem' in game.args else False
game.arg_ddpg = True if 'ddpg' in game.args else False
game.arg_rltf = True if 'rltf' in game.args else False # reinforcement learning tensorflow

#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"0lp31.lev")
#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"1dg54.lev") # qwquu002
levfilename = "%s.lev" % (game.args[1])
game.level = level.Level(r"C:\Users\Sara\Desktop\robin\elma\lev", levfilename, game)
game.maxplaytime = int(game.args[2]) if game.args[2].isnumeric() else 0 # quit script after last run has exceeded this many seconds

if game.arg_fps30:
    game.timestep = 0.01456 # 30 fps, lowest eol framerate but too unstable here to use
elif game.arg_fps500:
    game.timestep = 0.0008736 # 500 fps, okeol second candidate
elif game.arg_fps1000:
    game.timestep = 0.0004368 # 1000 fps, ultra slow motion, okeol first candidate
elif game.arg_man:
    game.timestep = 0.002 # oke speed for playing manually, also this computer (Zazza) renders the game almost with same elma time as real time
else:
    # default timestep
    game.timestep = 0.00546 # fast play, 80 fps, fastest possible calculated physics according to jon, as slower than this does double or more physics iteration per step

# calc timestep for fps
# 1/30/2,2893772893772893772893772893773 = 0,01456
# 1/80/2,2893772893772893772893772893773 = 0,00546
# 1/1000/2,2893772893772893772893772893773 = 0,0004368
# fast/slow below means how the gameplay feels in pygame
#game.timestep = 0.015 # ultra fast play, makes elma crash
#game.timestep = 0.01 # very fast play, makes elma unstable and wheels going everywhere
#game.timestep = 0.001 # slow play

training_mod = None
if game.arg_cem:
    sys.path.append("agents\\cem\\")
    #import cem_strange_rewards as training_mod
    import cem_keras as training_mod
    training_mod.init_model(game)
    game.n_episodes = 1000
elif game.arg_ddpg:
    sys.path.append("agents\\ddpg_torch\\")
    import train as training_mod
elif game.arg_rltf:
    sys.path.append("agents\\")
    import rl_tf as training_mod
    game.n_episodes = 1000
game.training_mod = training_mod

if game.arg_render:
    game.init_pygame()

# after pygame.init()
import elmaphys # must be imported after pygame.init()
game.kuski_state = elmaphys.init(game.level.path + '\\' + game.level.filename)
game.initial_kuski_state = game.kuski_state
game.elmaphys = elmaphys
#print('kuski state: ' + str(game.kuski_state))

game.running = True
game.starttime = time.time()
if game.training_mod:
    while game.running:
        secondsplayed = time.time() - game.starttime
        secondsleft = game.maxplaytime - secondsplayed
        print()
        print('Batch %d, last batch hiscore: %f, last batch lowscore: %f, %d minutes left' % (game.batch, game.batch_hiscore, game.batch_lowscore, secondsleft/60))
        game.batch_hiscore = 0
        game.batch_lowscore = 0
        game.training_mod.train_model(game)
        game.batch += 1
else:
    while game.running:
        game.loop()

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
print('Session hiscore: %f' % (game.hiscore))
print('Session lowscore: %f' % (game.lowscore))
print('Real time: %.02f %s' % (elapsed_time, unit))
print('Elma time: %.02f %s' % (game.elmatimetotal, unit))
print('Processing %.02f times faster than playing in realtime' % (game.elmatimetotal/elapsed_time))
#print( len(game.observation()) )
#print( game.observation() )