# agent that does almost nothing
# to be able to monitor and optimize the speed of this system
# without using any real model
import numpy as np

def init_model(game):
    return

def predict(game, observations):
    p = np.zeros( game.n_actions ) # create probabilities of 0
    p[0] = 1 # set first action to 100% probability, so array total is 1
    return np.array([p])


def fit(game, ep_observations, ep_actions, sample_weight,
        batch_size, epochs=1, verbose=0):
    return

def evaluate(game, ep_observations, ep_actions, sample_weight,
            batch_size, verbose=0):
    return 0


def elmaphys_only():
    "Measure how fast this computer can process elma physics"
    # Zazza: up to 2200X faster than realtime
    import time, sys
    sys.path.append("..\\")
    import elmaphys, local
    elmaphys.init(local.levpath + '\\ribotAI0.lev')
    timestep = 0.00546 # fast play, 80 fps, fastest possible calculated physics according to jon, as slower than this does double or more physics iteration per step
    elmatimestep = timestep * 2.2893772893772893772893772893773
    elmatime = 0.0
    episodes = 0
    starttime = time.time()
    # def next_frame(accelerate, brake, left, right, turn, supervolt, timestep, time):
    for episodes in range(15000):
        kuski_state = elmaphys.next_frame( 1, 0, 0, 0, 0, 0, timestep, timestep*episodes )
        #if kuski_state['isDead']:
        if kuski_state[10] > 0:
            elmaphys.restart_level()
        elmatime += elmatimestep

    totaltime = time.time() - starttime
    print("Elmaphys only:")
    print("episodes: %d, time: %.2f seconds, elmatime: %.2f seconds; inception speed %dX" % (episodes + 1, totaltime, elmatime, elmatime/totaltime))
    print()

def elmaphys_using_step():
    import time, sys
    sys.path.append("..\\")
    import game, train, elmaphys, local, level
    game = game.Game()
    #elmaphys_only()
    # set vars to make game loop run
    game.arg_man = False
    game.arg_render = False
    game.arg_eol = False
    game.timestep = 0.00546 # fast play, 80 fps, fastest possible calculated physics according to jon, as slower than this does double or more physics iteration per step
    game.elmaphys = elmaphys
    game.level = level.Level(local.levpath, 'ribotAI0.lev', game)
    game.kuski_state = elmaphys.init(game.level.path + '\\' + game.level.filename)
    game.initial_kuski_state = game.kuski_state
    game.reset()
    timestep = 0.00546 # fast play, 80 fps, fastest possible calculated physics according to jon, as slower than this does double or more physics iteration per step
    elmatimestep = timestep * 2.2893772893772893772893772893773
    elmatime = 0.0
    episodes = 0
    steptimes = []
    starttime = time.time()
    for episodes in range(15000):
        stepstart = time.time()
        game.step(0)
        steptime = time.time() - stepstart
        steptimes.append(steptime)
        #print("step time: %f" % (steptime))
        elmatime += elmatimestep
    totaltime = time.time() - starttime
    print("Elmaphys using game.step():")
    print("episodes: %d, time: %.2f seconds, elmatime: %.2f seconds; inception speed %dX" % (episodes + 1, totaltime, elmatime, elmatime/totaltime))
    print("avg steptime: %f, total steptime: %f" % ( np.average(steptimes), sum(steptimes) ))
    print()


if __name__ == '__main__':
    elmaphys_only()
    elmaphys_using_step()