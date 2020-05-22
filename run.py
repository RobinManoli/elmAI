# https://towardsdatascience.com/teach-your-ai-how-to-walk-5ad55fce8bca
# https://github.com/shivaverma/OpenAIGym/tree/master/bipedal-walker
# https://www.reddit.com/r/reinforcementlearning/comments/9tkk52/have_anyone_solved_bipedalwalkerhardcore/

# https://mopolauta.moposite.com/viewtopic.php?p=264925#p264925 - stini's method
# https://towardsdatascience.com/cross-entropy-method-for-reinforcement-learning-2b6de2a4f3a0

# https://stable-baselines.readthedocs.io/en/master/guide/rl_tips.html
# https://spinningup.openai.com/en/latest/spinningup/rl_intro.html

# tardis uses monte carlo simulation to create data for which its c++ code that is used - uses cython
# http://numba.pydata.org/ - fast machine code
# https://dask.org/ using gpu?

# kosh 09:42:24 before numba I would look at numpy or even tensorflow
# if you have really large arrays and you are doing large numbers of vector type operations you can do them in tensorflow
# numba is useful but you use it AFTER you have already done the stuff in numpy
# partically because if your stuff is not in numpy then numba will not accelerate it much
# exospecies, numba knows about numpy so if you use numpy and then write your code in a specific way that is documented on the numba website you can get LARGE performance gains that will run in parallel and vectorize

import pygame, sys, time, os
import game, keys

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.display.set_caption('ElmAI')
# pygame.event.set_blocked([pygame.KEYDOWN, pygame.KEYUP]) # block keydown that crashes phys? still crashing on keypress
size = 800, 640
game = game.Game(pygame, size)

#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"0lp31.lev")
#lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"1dg54.lev")
game.levpath = r"C:\Users\Sara\Desktop\robin\elma\lev"
game.levfilename = "qwquu002.lev"

# after pygame.init()
import elmaphys # must be imported after pygame.init()
#elmaphys.init(game.levpath + '\\' + game.levfilename)

running = True
elmainput = [0, 0, 0, 0, 0, 0]
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # pygame crashes after keydown, if elmaphys is called any time after
        elif event.type == pygame.KEYDOWN:
            print('keydown')
        # input starts on mouse down and ends on mouseup; sustain input in between
        elif event.type in (game.pygame.MOUSEBUTTONDOWN, game.pygame.MOUSEBUTTONUP):
            elmainput = keys.elmainput(game, event)

        #game.draw.draw(game, event, elmaphys) # proceed drawing only on events, eg when mouse moves
    game.draw.draw(game, event, elmainput, elmaphys)

    #print( elmaphys.next_frame() ) # segmentation fault after pygame.init()
    #print("drew")
    #time.sleep(1)
