import sys, time, os
import game, level, local, train

try:
    os.system('color') # init colors early in script
    game = game.Game()
    game.args = sys.argv

    if len(game.args) < 2:
        # the commandline args have been discontinued for now
        # as developing both them and a tkinter gui seems counter productive
        print("Start GUI: %s" % (os.path.basename(__file__)))
        print("Same settings as last time, but randomize seed: %s seed" % (os.path.basename(__file__)))
        print("Same settings as last time, set n_episodes (todo: should continue if new seed not set): %s 1000" % (os.path.basename(__file__)))
        import config
        config.GUI(game)
    game.arg_man = True if game.setting['man'].int_value == 1 else False # play manually
    game.arg_render = True if game.setting['render'].int_value == 1 else False # render gfx with pygame
    game.arg_test = True if game.setting['test'].int_value == 1 else False
    game.arg_eol = True if game.setting['eol'].int_value == 1 else False

    seed = None if 'seed' in game.args else game.setting['seed'].int_value
    game.set_seed(seed)
    game.setting['seed'].update_record( int_value=game.seed )

    # [accelerate, brake, left, right, turn, supervolt]
    for selected_action in game.setting['actions'].int_values:
        game.n_actions += 1
        elmainputs = [0, 0, 0, 0, 0, 0]
        elmainputs[selected_action] = 1
        game.actions.append(elmainputs)
        action_names = 'ABLRTS'
        game.actions_str += action_names[selected_action]
    print("actions: %s" % (game.actions_str))

    levfilename = game.setting['level'].str_value
    game.level = level.Level(local.levpath, levfilename, game)
    #game.maxplaytime = int(game.args[2]) if game.args[2].isnumeric() else 0 # quit script after last run has exceeded this many seconds
    game.n_episodes = int(game.args[1]) if len(game.args) > 1 and game.args[1].isnumeric() else game.setting['episodes'].int_value
    game.setting['episodes'].update_record( int_value=game.n_episodes )

    if '30' in game.setting['fps'].str_value.split(' '):
        game.timestep = 0.01456 # 30 fps, lowest eol framerate but too unstable here to use
    elif '500' in game.setting['fps'].str_value.split(' '):
        game.timestep = 0.0008736 # 500 fps, okeol second candidate
    elif '1000' in game.setting['fps'].str_value.split(' '):
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

    # set n_frames before loading training_mod
    n_frames = game.level.db_row.maxplaytime / (game.timestep*game.realtimecoeff) # max time * fps
    game.n_frames = int(n_frames)
    game.load = game.setting['load'].int_value

    print(game.setting['agent'].str_value)
    training_mod = None
    if game.arg_man:
        pass
    elif 'benchmark' in game.setting['agent'].str_value.lower().split():
        sys.path.append("agents\\")
        #import cem_strange_rewards as training_mod
        import benchmark as training_mod
        training_mod.init_model(game)
    elif 'cem' in game.setting['agent'].str_value.lower().split():
        sys.path.append("agents\\cem\\")
        #import cem_strange_rewards as training_mod
        import cem_keras as training_mod
        training_mod.init_model(game)
    elif 'ddpg' in game.setting['agent'].str_value.lower().split():
        sys.path.append("agents\\ddpg_torch\\")
        import train as training_mod
    elif 'rl_tf' in game.setting['agent'].str_value.lower().split():
        sys.path.append("agents\\")
        import rl_tf as training_mod
    elif 'ribot' in game.setting['agent'].str_value.lower().split():
        sys.path.append("agents\\")
        import ribot_algorithm as training_mod
        training_mod.init_model(game)
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
    print('kuski state: ' + str(game.kuski_state))

    game.db.db.commit()
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
    if game.training_mod and hasattr(game.training_mod, 'sequence'):
        print("Ribot Sequence: %s" % (game.training_mod.sequence))

    if game.training_mod is not None and game.pygame is not None:
        print("storing snapshot...")
        game.arg_render = True
        game.arg_render_snapshot = True
        game.n_episodes = 1
        game.reset()
        train.train_model(game)
        from PIL import Image
        game.render_snapshots[0].save('snapshots\\00.gif', save_all=True, append_images=game.render_snapshots[1:], duration=40)

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