import random, time

DOUBLECLICKTIME = 200 # ms
dblclock = None
MAXIMIZED = False
key_is_down = []

def loop(game):
    pygame = game.pygame

    if game.arg_framebyframe:
        if pygame.K_p in key_is_down:
            forward(game)
        else:
            game.do_next_frame = False
        if pygame.K_o in key_is_down:
            rewind(game)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
        # pygame often crashes after keydown, if elmaphys is called any time after
        # input starts on mouse down and ends on mouseup; sustain input in between
        #elif event.type in (self.pygame.MOUSEBUTTONDOWN, self.pygame.MOUSEBUTTONUP, self.pygame.KEYDOWN, self.pygame.KEYUP):
        #game.input = elmainput(game, event)
        elmainput(game, event)

        # proceed with next frame, in frame by frame manual play mode, by pressing any button
        #if event.type == self.pygame.KEYDOWN:
        #    self.do_next_frame = True
        #elif event.type == self.pygame.KEYUP:
        #    self.do_next_frame = False
        #    #self.draw.draw(game, event, self.input, elmaphys) # draw only on self.input
        #self.draw.draw(game, event, elmaphys) # proceed drawing only on events, eg when mouse moves

    if game.do_next_frame: # and not game.rewind:
        #print(game.frame, game.input) # len(game.kuski_states), game.kuski_state['body']['location']['x']
        game.kuski_states.append( game.kuski_state )
        game.inputs.append( game.input[:] )

def rewind(game):
    #print(game.frame, game.recframe, game.timesteptotal, game.input) # game.kuski_state['body']['location']['x'] len(game.kuski_states)
    if game.frame > 0:
        #print("before rewind, frame: %d, rewind: %d, inputs: %s, input: %s" % (game.frame, game.rewind, len(game.inputs), game.input))
        time.sleep(0.01)
        game.frame -= 1
        game.rewind += 1
        game.timesteptotal -= game.timestep
        game.kuski_state = game.kuski_states[game.frame]
        game.input = game.inputs[game.frame][:]
        #print("after rewind, frame: %d, rewind: %d, inputs: %s, input: %s" % (game.frame, game.rewind, len(game.inputs), game.input))

def forward(game):
    #print("before forward, frame: %d, rewind: %d, inputs: %s, input: %s" % (game.frame, game.rewind, len(game.inputs), game.input))
    if len(game.kuski_states) == 0:
        game.kuski_states.append( game.initial_kuski_state )

    if game.rewind and len(game.inputs) > game.frame:
        if game.input[:] == game.inputs[game.frame][:]:
            #print('future frame same, fast forward, %s %s' % (game.input, game.inputs[game.frame]))
            # next frame same keypress as before (already calculated)
            time.sleep(0.01)
            game.frame += 1
            game.rewind -= 1
            game.timesteptotal += game.timestep
            # there is a kuski state before first frame, but not an input
            # so there will always be one more kuski state than inputs
            game.kuski_state = game.kuski_states[game.frame]
            # input exists if last frame has been played, and if not set input to same as last frame
            game.input = game.inputs[game.frame][:] if len(game.inputs) > game.frame else game.inputs[game.frame - 1][:]
        else:
            #print('future frame different, recalculate, inputs: %s' % (len(game.inputs)))
            # next frame not store, recalculate
            game.elmaphys.restart_level()
            game.inputs = game.inputs[:game.frame]
            game.kuski_states = game.kuski_states[:game.frame+1]
            game.rewind = 0
            # recalculate from beginning
            for i, input in enumerate(game.inputs):
                params = input + [game.timestep, game.timesteptotal]
                game.elmaphys.next_frame(*params)
            game.do_next_frame = True
            #print('calculation done, inputs: %s' % (len(game.inputs)))


    else:
        game.do_next_frame = True
    #print("after forward, frame: %d, rewind: %d, inputs: %s, input: %s" % (game.frame, game.rewind, len(game.inputs), game.input))

def elmainput(game, event):
    #print("event happened: %s" % (event))
    global dblclock, MAXIMIZED
    pygame = game.pygame
    accelerate = brake = left = right = turn = supervolt = 0 # random.choice([0,1])

    if game.arg_framebyframe:
        if event.type in (pygame.KEYUP, pygame.KEYDOWN):
            # keydown is only triggered once, not continuously
            # but elmainput is only triggered when there is an event
            if event.key in (pygame.K_f, ):
                # proceed one frame per keypress F
                #print('f triggered')
                if event.type == pygame.KEYDOWN:
                    forward(game)
            elif event.key in (pygame.K_d, ):
                # rewind one frame per keypress D
                #print('o triggered')
                if event.type == pygame.KEYDOWN:
                    rewind(game)

            if event.key in (pygame.K_p, ):
                # proceed while holding key P
                #print('p triggered')
                if event.type == pygame.KEYDOWN:
                    key_is_down.append( pygame.K_p )
                    forward(game)
                elif event.type == pygame.KEYUP:
                    key_is_down.remove( pygame.K_p )
            elif event.key in (pygame.K_o, ):
                # rewind while holding key O
                #print('o triggered')
                if event.type == pygame.KEYDOWN:
                    key_is_down.append( pygame.K_o )
                    rewind(game)
                elif event.type == pygame.KEYUP:
                    key_is_down.remove( pygame.K_o )

    if event.type == pygame.KEYUP:
        # game.do_next_frame is False when playing frame by frame
        # on frame by frame (play mode 1), toggle input keys
        if game.arg_framebyframe:
            #print('keyup triggered', game.input)
            ### PLAY ELMA
            if event.key in (pygame.K_ESCAPE, ):
                game.running = False
                #print('game running: %s' % game.running )
            if event.key in (pygame.K_LSHIFT, ):
                game.input[0] = 1 if game.input[0] == 0 else 0
            if event.key in (pygame.K_LCTRL, pygame.K_SPACE):
                game.input[4] = 1 if game.input[4] == 0 else 0
            if event.key in (pygame.K_DOWN, ):
                game.input[1] = 1 if game.input[1] == 0 else 0
            if event.key in (pygame.K_LEFT, ):
                game.input[2] = 1 if game.input[2] == 0 else 0
            if event.key in (pygame.K_RIGHT, ):
                game.input[3] = 1 if game.input[3] == 0 else 0
            #if event.key in (pygame.K_UP, ):
            #    supervolt = 1

    if event.type == pygame.KEYDOWN:
        #print('keydown triggered', game.input)
        #if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:

        # game.do_next_frame is False when playing frame by frame
        if not game.arg_framebyframe:
            ### PLAY ELMA
            if event.key in (pygame.K_ESCAPE, ):
                game.running = False
                #print('game running: %s' % game.running )
            if event.key in (pygame.K_LSHIFT, ):
                accelerate = 1
            if event.key in (pygame.K_LCTRL, pygame.K_SPACE):
                turn = 1
            if event.key in (pygame.K_DOWN, ):
                brake = 1
            if event.key in (pygame.K_LEFT, ):
                left = 1
            if event.key in (pygame.K_RIGHT, ):
                right = 1
            if event.key in (pygame.K_UP, ):
                supervolt = 1

        ### WINDOW CONTROLS
        if event.key in (pygame.K_z, ):
            game.zoom_mode += 1
            game.redraw = True

        if event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT:
            #print('alt enter')
            import win32gui, win32con
            from win32api import GetSystemMetrics
            hwnd = win32gui.GetForegroundWindow()
            if MAXIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                MAXIMIZED = False
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                MAXIMIZED = True

    elif event.type == pygame.VIDEORESIZE:
        game.width = event.w
        game.height = event.h
        game.size = (game.width, game.height)
        game.screen = pygame.display.set_mode(game.size, pygame.RESIZABLE)
        game.redraw = True

    elif event.type == pygame.MOUSEBUTTONDOWN:
        dblclick = False
        if not dblclock or dblclock.tick() > DOUBLECLICKTIME:
            dblclock = pygame.time.Clock()
        else:
            dblclick = True

        lbutton, midbutton, rbutton = pygame.mouse.get_pressed()
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
    if game.arg_framebyframe:
        #return game.input
        pass
    else:
        game.input = [accelerate, brake, left, right, turn, supervolt]
        #return [accelerate, brake, left, right, turn, supervolt]

