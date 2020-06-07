# agent that does almost nothing
# to be able to monitor and optimize the speed of this system
# without using any real model
import numpy as np

print("Enter Benchmark")

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
    sys.path.append("..")
    import elmaphys, local
    elmaphys.init(local.levpath + '\\ft.lev')
    timestep = 0.00546 # fast play, 80 fps, fastest possible calculated physics according to jon, as slower than this does double or more physics iteration per step
    elmatimestep = timestep * 2.2893772893772893772893772893773
    elmatime = 0.0
    starttime = time.time()
    # def next_frame(accelerate, brake, left, right, turn, supervolt, timestep, time):
    for frames in range(15000):
        kuski_state = elmaphys.next_frame( 1, 0, 0, 0, 0, 0, timestep, timestep*frames )
        if kuski_state['isDead']:
            #if kuski_state[10] > 0:
            elmaphys.restart_level()
        elmatime += elmatimestep

    totaltime = time.time() - starttime
    print("Elmaphys only:")
    print("frames: %d, time: %.2f seconds, elmatime: %.2f seconds; inception speed %dX" % (frames + 1, totaltime, elmatime, elmatime/totaltime))
    print()



def elmaphys_using_step():
    import time, sys
    sys.path.append("..")
    import game, train, elmaphys, local, level
    game = game.Game()
    #elmaphys_only()
    # set vars to make game loop run
    game.arg_man = game.arg_render = game.arg_eol = game.arg_framebyframe = False
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
        # inside step -> loop:
        # game.act, game.has_ended and game.restart take significant time to process
        # though act takes the most
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


def elmaphys_ribot_algorithm(episodes=1000, seed=None):
    """
    Measure how fast this computer can process elma physics,
    when (simplified) ribot algorithm is implemented in place.

    Speed average: over 1000x on K53S,
    but this algorithm didn't perform as well as ribot_algorithm.py

    Things that slow down significantly:
        randomize every frame
        python if, list
        other actions than always gas
    """
    # Zazza: up to 2200X faster than realtime
    import time, sys, level
    sys.path.append("..")
    import elmaphys, local, game
    print( elmaphys.init(local.levpath + '\\ribotAI0.lev') )
    game = game.Game()
    lev = level.Level(local.levpath, 'ribotAI0.lev', game)
    seed = seed if seed is not None else np.random.randint(9999999)
    np.random.seed(seed)
    shortest_distance = 999999.9
    timestep = 0.00546 # fast play, 80 fps, fastest possible calculated physics according to jon, as slower than this does double or more physics iteration per step
    elmatimestep = timestep * 2.2893772893772893772893772893773
    elmatime = 0.0
    n_actions = 2
    maxplaytime = 7.5 # seconds
    frames = int(maxplaytime / elmatimestep)
    best_ride_frames = frames
    unimproved_episodes = 0
    print("%d frames, max %d seconds per episode" % (frames, maxplaytime))
    starttime = time.time()
    #best_sequence = np.random.randint(n_actions, size = (frames))
    best_sequence = np.ones(frames, np.int16)
    sequence = np.ones(frames, np.int16)
    for episode in range(episodes):
        episode_time = 0.0
        elmaphys.restart_level()
        #for frame in range(frames):
        for frame, action in enumerate(sequence):
            #for action in sequence:
            # def next_frame(accelerate, brake, left, right, turn, supervolt, timestep, time):
            #kuski_state = elmaphys.next_frame( 1, 0, 0, 0, 0, 0, timestep, timestep*episodes )
            #actions = np.random.randint(2, size = (6))
            #params = list(actions) + [timestep, episode_time]

            # very slow three rows
            # actions = [0, 0, 0, 0, 0, 0]
            # if action > 0:
            #    actions[action-1] = 1
            # params = actions + [timestep, episode_time]
            # kuski_state = elmaphys.next_frame( *params )

            # much faster
            actions = np.zeros( 7, np.int16 ) # use total actions not n_actions
            actions[action] = 1
            #params = list(actions[1:]) + [timestep, episode_time] # slow
            # episode time causes error if it is above 10, which it will be on 2000 frames, which breaks elmaphys
            # though recs wont be saved correctly without correct episode_time
            kuski_state = elmaphys.next_frame( actions[1], actions[2], actions[3], actions[4], actions[5], actions[6], timestep, episode_time )
            #print("x: %f, frame: %d" % (kuski_state['body']['location']['x'], frame))

            episode_time += timestep
            if kuski_state['isDead'] or kuski_state['finishedTime']:
                #if kuski_state[10] > 0:
                #if kuski_state['finishedTime']:
                #    print(kuski_state['finishedTime'])
                #sequence = sequence[:frame]
                break
        distance = lev.flower_distance(kuski_state)
        if kuski_state['finishedTime'] > 0:
            # create negative distance on finish, the more negative the better
            distance = -9999 + kuski_state['finishedTime']
        #print("episode: %d, distance: %f, survived %d frames, x: %f, episode_time: %f" % (episode, distance, frame, kuski_state['body']['location']['x'], episode_time))

        # handle hiscore
        if distance < shortest_distance:
            best_ride_frames = frame
            shortest_distance = distance
            best_sequence[:] = sequence
            if kuski_state['finishedTime'] > 0:
                elmaphys.save_replay("bench%06d.rec" % (kuski_state['finishedTime']), "ribotAI0.lev")
            print("episode: %d, distance: %f, survived %d frames, x: %f, time: %f, seed: %d" % (episode, lev.flower_distance(kuski_state), frame, kuski_state['body']['location']['x'], episode_time*2.2893772893772893772893772893773, seed))
        else:
            unimproved_episodes += 1

        # randomize sequence
        #n_frames_to_randomize = int(frames/100) # 1%
        #indexes_to_change = np.random.randint( len(best_sequence), size=(n_frames_to_randomize) )
        n_frames_to_randomize = int( np.ceil( unimproved_episodes/1000 ) ) # change one active frame per thousand unimproved
        #n_frames_to_randomize = 1
        indexes_to_change = np.random.randint( best_ride_frames, size=(5*n_frames_to_randomize) )
        sequence[:] = best_sequence
        for index in indexes_to_change:
            #print("episide: %d, updating index: %d" % (episode, index))
            sequence[index] = np.random.randint(n_actions)
        #print(sequence[:100])
        elmatime += episode_time * 2.2893772893772893772893772893773

    totaltime = time.time() - starttime
    print("Ribot algorithm:")
    print("episodes: %d, time: %.2f seconds, elmatime: %.2f seconds; inception speed %dX" % (episode + 1, totaltime, elmatime, elmatime/totaltime))
    print("shortest distance: %f" % (shortest_distance))
    print()


if __name__ == '__main__':
    elmaphys_only()
    elmaphys_using_step()