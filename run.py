import sys, time, os
import game, level, local, train

try:
    os.system('color') # init colors early in script
    game = game.Game()
    game.args = sys.argv


    # todo: bug or feature? with enough args number can be omitted and train forever
    # todo: actions=ABLRTS?

    if len(game.args) < 3:
        # the commandline args have been discontinued for now
        # as developing both them and a tkinter gui seems counter productive
        #print("usage: %s 0lp31.lev 100 render man test fps30|fps500|fps1000 rltf|cem|ddpg" % (os.path.basename(__file__)))
        #print("for running level 0lp31.lev, 100 episodes with chosen flags")
        #print("order of flags dont matter")
        #print("shortcut: %s 0lp31 <-- will play manually if no other flags" % (os.path.basename(__file__)))
        #print("default flags: fps80")
        import config
        config.GUI(game)
    else:
        game.arg_man = True if 'man' in game.args else False # play manually
        game.arg_render = True if 'render' in game.args or game.arg_man else False # render gfx with pygame
        game.arg_test = True if 'test' in game.args else False # play manually
        #game.arg_load = True if 'load' in game.args else False # play manually
        game.arg_fps1000 = True if 'fps1000' in game.args else False
        game.arg_fps500 = True if 'fps500' in game.args else False
        game.arg_fps30 = True if 'fps30' in game.args else False
        # in case of more cem implementations, they can here be called cem1, cem2, etc
        game.arg_cem = True if 'cem' in game.args else False
        game.arg_ddpg = True if 'ddpg' in game.args else False #
        game.arg_rltf = True if 'rltf' in game.args else False # reinforcement learning tensorflow

    levfilename = game.args[1]
    game.level = level.Level(local.levpath, levfilename, game)
    #game.maxplaytime = int(game.args[2]) if game.args[2].isnumeric() else 0 # quit script after last run has exceeded this many seconds
    game.n_episodes = int(game.args[2]) if game.args[2].isnumeric() else 0 # quit script after last run has exceeded this many seconds

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

    print("fps: %f" % ( 1/(game.timestep*game.realtimecoeff) ))

    # calc timestep for fps
    # 1/30/2,2893772893772893772893772893773 = 0,01456
    # 1/80/2,2893772893772893772893772893773 = 0,00546
    # 1/1000/2,2893772893772893772893772893773 = 0,0004368
    # fast/slow below means how the gameplay feels in pygame
    #game.timestep = 0.015 # ultra fast play, makes elma crash
    #game.timestep = 0.01 # very fast play, makes elma unstable and wheels going everywhere
    #game.timestep = 0.001 # slow play

    training_mod = None
    if game.arg_benchmark:
        sys.path.append("agents\\")
        #import cem_strange_rewards as training_mod
        import benchmark as training_mod
        training_mod.init_model(game)
    elif game.arg_cem:
        sys.path.append("agents\\cem\\")
        #import cem_strange_rewards as training_mod
        import cem_keras as training_mod
        training_mod.init_model(game)
    elif game.arg_ddpg:
        sys.path.append("agents\\ddpg_torch\\")
        import train as training_mod
    elif game.arg_rltf:
        sys.path.append("agents\\")
        import rl_tf as training_mod
    game.training_mod = training_mod
    if training_mod and not game.arg_test:
        game.training = True

    if game.arg_eol:
        game.init_eol()
    elif game.arg_render:
        game.init_pygame()

    # after pygame.init()
    import elmaphys # must be imported after pygame.init()
    game.kuski_state = elmaphys.init(game.level.path + '\\' + game.level.filename)
    game.initial_kuski_state = game.kuski_state
    # todo, do not do this? needed now because level maxtimes are set inside rewards
    game.prev_kuski_state = game.kuski_state
    game.elmaphys = elmaphys
    #print('kuski state: ' + str(game.kuski_state))

    game.running = True
    game.starttime = time.time()
    if game.training_mod is not None:
        while game.episode < game.n_episodes:
            secondsplayed = time.time() - game.starttime
            #secondsleft = game.maxplaytime - secondsplayed
            print()
            #print('Batch %d, last batch hiscore: %f, last batch lowscore: %f, %d minutes played' % (game.batch, game.batch_hiscore, game.batch_lowscore, secondsplayed/60))
            game.batch_hiscore = 0
            game.batch_lowscore = 0
            train.train_model(game)
            game.batch += 1
    else:
        print("playing manually")
        while game.running:
            game.loop()

        print(game.running)

    print('SESSION FINISHED:')
    game.winsound.Beep(1231, 123)
    game.winsound.Beep(1631, 123)
    game.winsound.Beep(2631, 123)
    game.winsound.Beep(1631, 123)
    elapsed_time, elapsed_elma_time, unit = game.elapsed_time()
    print('Session hiscore: %f' % (game.hiscore))
    print('Session lowscore: %f' % (game.lowscore))
    print('Real time: %.02f %s' % (elapsed_time, unit))
    print('Elma time: %.02f %s' % (elapsed_elma_time, unit))
    if elapsed_time != 0:
        print('Processing %.02f times faster than playing in realtime' % (elapsed_elma_time/elapsed_time))
    #print( len(game.observation()) )
    #print( game.observation() )
    # make terminal output visible before automatically closing
    input("Press return to exit")

except KeyboardInterrupt:
    if game.eol is not None:
        # def toggle_keys(press_or_release_func, accelerate, brake, left, right, turn, supervolt):
        game.eol.toggle_keys(game.eol.ReleaseKey, True, True, True, True, True, True)

except Exception as e:
    import traceback
    print( traceback.format_exc() )
    print(e)
    # make terminal output visible before automatically closing
    input("Press return to exit")