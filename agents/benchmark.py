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
    # Zazza: almost 2000X faster than realtime
    import time, sys
    starttime = time.time()
    sys.path.append("..\\")
    import elmaphys, local
    elmaphys.init(local.levpath + '\\ribotAI0.lev')
    timestep = 0.00546 # fast play, 80 fps, fastest possible calculated physics according to jon, as slower than this does double or more physics iteration per step
    elmatimestep = timestep * 2.2893772893772893772893772893773
    elmatime = 0.0
    episodes = 0
    # def next_frame(accelerate, brake, left, right, turn, supervolt, timestep, time):
    for i in range(15000):
        kuski_state = elmaphys.next_frame( 1, 0, 0, 0, 0, 0, timestep, timestep*i )
        if kuski_state['isDead']:
            episodes += 1
            elmaphys.restart_level()
        elmatime += elmatimestep

    totaltime = time.time() - starttime
    print("episodes: %d, time: %.2f seconds, elmatime: %.2f seconds; inception speed %dX" % (episodes, totaltime, elmatime, elmatime/totaltime))

if __name__ == '__main__':
    elmaphys_only()