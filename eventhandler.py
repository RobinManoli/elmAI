import random

DOUBLECLICKTIME = 200 # ms
dblclock = None

def elmainput(game, event):
    global dblclock
    accelerate = brake = left = right = turn = supervolt = 0 # random.choice([0,1])
    # not working since cython code makes pygame crasch on any keypress
    # also not working because this function is only called on mousebutton
    if event.type == game.pygame.KEYDOWN:
        #if event.key == game.pygame.K_RETURN or event.key == game.pygame.K_SPACE:
        if event.key in (game.pygame.K_LSHIFT, ):
            accelerate = 1
        if event.key in (game.pygame.K_LCTRL, game.pygame.K_SPACE):
            turn = 1
        if event.key in (game.pygame.K_DOWN, ):
            brake = 1
        if event.key in (game.pygame.K_LEFT, ):
            left = 1
        if event.key in (game.pygame.K_RIGHT, ):
            right = 1
        if event.key in (game.pygame.K_UP, ):
            supervolt = 1
    elif event.type == game.pygame.MOUSEBUTTONDOWN:
        dblclick = False
        if not dblclock or dblclock.tick() > DOUBLECLICKTIME:
            dblclock = game.pygame.time.Clock()
        else:
            dblclick = True

        lbutton, midbutton, rbutton = game.pygame.mouse.get_pressed()
        if lbutton:
            if dblclick:
                left = 1
            else:
                accelerate = 1
        if midbutton:
            if dblclick:
                supervolt = 1
            else:
                turn = 1
        if rbutton:
            if dblclick:
                right = 1
            else:
                brake = 1
    #print("acc: %d, brake: %d, left: %d, right: %d, turn: %d, supervolt: %d" % (accelerate, brake, left, right, turn, supervolt))
    return [accelerate, brake, left, right, turn, supervolt]

