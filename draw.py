# https://stackoverflow.com/questions/19746552/pygame-camera-follow-in-a-2d-tile-game

def draw(game):
    game.screen.fill(game.colors.skyblue)
    drawkeys(game)
    drawlev(game)
    drawbike(game)

    #game.gui.label(game, 'Welcome to LassElma AI', 10, 10)
    game.gui.label(game, 'score: %.2f' % (game.score), 10, 10)
    game.gui.label(game, 'prev score: %.2f' % (game.last_score), 150, 10)
    game.gui.label(game, 'time: %.2f' % (game.timesteptotal * game.realtimecoeff), game.width-120, 10)
    if game.lasttime:
        game.gui.label(game, 'prev time: %.2f' % game.lasttime, game.width-320, 10)
        #game.gui.label(game, 'total: %.2f' % game.elmatimetotal, game.width-350, 10)

    # draw lev coords
    mx, my = game.pygame.mouse.get_pos()
    levx = game.level.xmin - (game.width/zoom - game.level.width)/2 + mx/zoom
    levy = game.level.ymin - (game.height/zoom - game.level.height)/2 + my/zoom
    # keep coords visible on screen
    mx = game.width - 110 if mx > game.width - 110 else mx
    my = game.height - 20 if my > game.height - 20 else my
    game.gui.label(game, '%d x %d' % (levx, levy), mx+15, my)
    

    # todo: optimize display using .update or whatnot (opengl?) https://www.pygame.org/docs/ref/display.html#pygame.display.flip
    game.pygame.display.flip()

bikexoffset = 0
bikeyoffset = 0
def drawbike(game):
    global bikexoffset, bikeyoffset

    #print( game.kuski_state ) # segmentation fault after pygame.init()
    headx = game.kuski_state['headLocation']['x'] * zoom + levxoffset
    heady = -game.kuski_state['headLocation']['y'] * zoom + levyoffset
    # headCenterLocation is more like neck or heart location
    headcx = game.kuski_state['headCenterLocation']['x'] * zoom + levxoffset
    headcy = -game.kuski_state['headCenterLocation']['y'] * zoom + levyoffset
    #bodyx = game.kuski_state['body']['location']['x'] * zoom + levxoffset
    #bodyy = -game.kuski_state['body']['location']['y'] * zoom + levyoffset
    lwx = game.kuski_state['leftWheel']['location']['x'] * zoom + levxoffset
    lwy = -game.kuski_state['leftWheel']['location']['y'] * zoom + levyoffset
    rwx = game.kuski_state['rightWheel']['location']['x'] * zoom + levxoffset
    rwy = -game.kuski_state['rightWheel']['location']['y'] * zoom + levyoffset
    #body_rot = self.kuski_state['body']['rotation']

    # rec coords taken from smibu_phys/PlayerData.cpp
    # using elmadev
    if game.rec is not None and game.recframe < len(game.rec.frames):
        frame = game.rec.frames[game.recframe]
        rec_body_x = frame.position.x * zoom + levxoffset
        rec_body_y = -frame.position.y * zoom + levyoffset
        rec_lw_x = (frame.left_wheel_position.x / 1000 + frame.position.x) * zoom + levxoffset
        rec_lw_y = -(frame.left_wheel_position.y / 1000 + frame.position.y) * zoom + levyoffset
        rec_rw_x = (frame.right_wheel_position.x / 1000 + frame.position.x) * zoom + levxoffset
        rec_rw_y = -(frame.right_wheel_position.y / 1000 + frame.position.y) * zoom + levyoffset
        rec_hx = (frame.head_position.x / 1000 + frame.position.x) * zoom + levxoffset
        rec_hy = -(frame.head_position.y / 1000 + frame.position.y) * zoom + levyoffset
        #this->xCoordLeftWheel.push_back((int)((kuski->leftWheel.location.x - kuski->body.location.x) * 1000));
        #this->yCoordLeftWheel.push_back((int)((kuski->leftWheel.location.y - kuski->body.location.y) * 1000));
        #this->xCoordRightWheel.push_back((int)((kuski->rightWheel.location.x - kuski->body.location.x) * 1000));
        #this->yCoordRightWheel.push_back((int)((kuski->rightWheel.location.y - kuski->body.location.y) * 1000));
        #this->xCoordHead.push_back((int)((kuski->headCenterLocation.x - kuski->body.location.x) * 1000));
        game.pygame.draw.circle(game.screen, game.colors.violet + (100,), (int(rec_body_x), int(rec_body_y)), int(0.4*zoom), 2)
        game.pygame.draw.circle(game.screen, game.colors.violet, (int(rec_lw_x), int(rec_lw_y)), int(0.4*zoom), 2)
        game.pygame.draw.circle(game.screen, game.colors.violet, (int(rec_rw_x), int(rec_rw_y)), int(0.4*zoom), 2)
        game.pygame.draw.circle(game.screen, game.colors.cyan, (int(rec_hx), int(rec_hy)), int(0.3*zoom), 2)

    if follow_bike:
        # move cx and cy to center, by calculating distance to center
        bikexoffset = (game.width/2 - headcx) / 2
        bikeyoffset = (game.height/2 - headcy) / 2
        game.redraw = True
    else:
        bikexoffset = 0
        bikeyoffset = 0

    #body_thickness = 2
    #if game.kuski_state['direction'] == 0:
    #    #body_polygon = (bodyx - 8, bodyy), (bodyx + 8, bodyy + 4), (bodyx + 8, bodyy - 4)
    #    body_polygon = (headx, heady), (lwx, lwy), (rwx, rwy)
    #    body_color = game.colors.yellow
    #else:
    #    #body_polygon = (bodyx + 8, bodyy), (bodyx - 8, bodyy + 4), (bodyx - 8, bodyy - 4)
    #    body_polygon = (headx, heady), (lwx, lwy), (rwx, rwy)
    #    body_color = game.colors.blue
    game.pygame.draw.line( game.screen, game.colors.white, (int(headcx), int(headcy)), (int(headx), int(heady)) )
    game.pygame.draw.line( game.screen, game.colors.black, (int(headcx), int(headcy)), (int(lwx), int(lwy)) )
    game.pygame.draw.line( game.screen, game.colors.black, (int(headcx), int(headcy)), (int(rwx), int(rwy)) )
    #game.pygame.draw.line( game.screen, game.colors.white, (int(rwx), int(rwy)), (int(lwx), int(lwy)) )
    if game.kuski_state['direction'] == 0:
        game.pygame.draw.line( game.screen, game.colors.black, (int(headx), int(heady)), (int(rwx), int(rwy)) )
        pass
    else:
        game.pygame.draw.line( game.screen, game.colors.black, (int(headx), int(heady)), (int(lwx), int(lwy)) )
    game.pygame.draw.circle(game.screen, game.colors.yellow, (int(headx), int(heady)), int(0.3*zoom))
    #game.pygame.draw.polygon(game.screen, body_color, body_polygon, body_thickness)
    game.pygame.draw.circle(game.screen, game.colors.green, (int(lwx), int(lwy)), int(0.4*zoom))
    game.pygame.draw.circle(game.screen, game.colors.green, (int(rwx), int(rwy)), int(0.4*zoom))


def zoomlev(game):
    "zoom fill level"
    global zoom, levxoffset, levyoffset
    #print("xmin %d, xmax %d, ymin %d, ymax %d, width %d, height %d" % (game.level.xmin, game.level.xmax, game.level.ymin, game.level.ymax, game.level.width, game.level.height))
    xratio = game.width / game.level.width
    yratio = game.height / game.level.height
    if xratio < yratio:
        zoom = xratio
        # start x-axis on x-min
        levxoffset = -game.level.xmin * zoom
        # center y-axis starting on y-min
        levyoffset = -game.level.ymin * zoom + (game.height - game.level.height * zoom ) / 2
    else:
        zoom = yratio
        # start y-axis on y-min
        levyoffset = -game.level.ymin * zoom
        # center x-axis starting on x-min
        levxoffset = -game.level.xmin * zoom + (game.width - game.level.width * zoom ) / 2
    #print("xratio %d, yratio %d, zoom %d, levxoffset %d, levyoffset %d" % (xratio, yratio, zoom, levxoffset, levyoffset))


zoom = 1
levxoffset = 0
levyoffset = 0
zoomed_polygons = []
zoomed_objects = []
follow_bike = False
def drawlev(game):
    global zoom, zoomed_polygons, zoomed_objects, levxoffset, levyoffset, follow_bike
    if game.redraw:
        # do lev stuff once, not on every tick
        game.redraw = True
        zoomed_polygons = []
        zoomed_objects = []
        zoom_mode = game.zoom_mode % 9
        if zoom_mode == 0:
            zoomlev(game)
            follow_bike = False
        else:
            zoom = 20 * zoom_mode
            follow_bike = True
        levxoffset += bikexoffset
        levyoffset += bikeyoffset

        for polygon in game.level.polygons:
            if not polygon.grass:
                vertexes = [(v.x*zoom + levxoffset, v.y*zoom + levyoffset) for v in polygon.vertexes]
                zoomed_polygons.append( vertexes )
        for obj in game.level.objects:
            colors = [None, game.colors.white, game.colors.red, game.colors.black, game.colors.yellow]
            x = obj.x*zoom + levxoffset
            y = obj.y*zoom + levyoffset
            color = colors[obj.type]
            zoomed_objects.append(( int(x), int(y), color ))
            #if obj.type == 4:
            #    print('Lev start position: %d, %d' % (obj.x, obj.y))

    for obj in zoomed_objects:
        #print(obj)
        game.pygame.draw.circle(game.screen, obj[2], (obj[0], obj[1]), int(0.4*zoom))


    for polygon in zoomed_polygons:
        thickness = 1
        #print("drawing %s" % str(polygon.vertexes))
        game.pygame.draw.polygon(game.screen, game.colors.black, polygon, thickness)

def drawkeys(game):
    # [accelerate, brake, left, right, turn, supervolt]
    # print(game.input)
    width = 100
    height = 20
    # 0 means pressed = fill
    a_outline = 0 if game.input[0] else 2
    b_outline = 0 if game.input[1] else 2
    l_outline = 0 if game.input[2] else 2
    r_outline = 0 if game.input[3] else 2
    t_outline = 0 if game.input[4] else 2
    game.pygame.draw.rect(game.screen, game.colors.yellow,
        (game.width-width-10 + width / 3, game.height-height*3-10, width/3, height), a_outline)
    game.pygame.draw.rect(game.screen, game.colors.yellow,
        (game.width-width-10, game.height-height*2-10, width/3, height), l_outline)
    game.pygame.draw.rect(game.screen, game.colors.yellow,
        (game.width-width-10 + width / 3, game.height-height*2-10, width/3, height), b_outline)
    game.pygame.draw.rect(game.screen, game.colors.yellow,
        (game.width-width-10 + 2 * width / 3, game.height-height*2-10, width/3, height), r_outline)
    game.pygame.draw.rect(game.screen, game.colors.yellow,
        (game.width-width-10, game.height-height-10, width, height), t_outline)


# using rec.py
"""if game.recframe < game.rec.n_frames:
    rec_body_x = game.rec.body_xs[game.recframe] * zoom + levxoffset
    rec_body_y = -game.rec.body_ys[game.recframe] * zoom + levyoffset
    rec_lwx = rec_body_x + game.rec.lwxs[game.recframe]/100 * zoom + levxoffset
    rec_lwy = -game.rec.lwys[game.recframe]/100 * zoom + levyoffset
    rec_rwx = game.rec.rwxs[game.recframe] * zoom + levxoffset
    rec_rwy = -game.rec.rwys[game.recframe] * zoom + levyoffset
    print(rec_body_x, rec_lwx)
    game.pygame.draw.circle(game.screen, game.colors.yellow, (int(rec_body_x), int(rec_body_y)), 4, 2)
    game.pygame.draw.circle(game.screen, game.colors.green, (int(rec_lwx), int(rec_body_y)), 4, 1)
    game.pygame.draw.circle(game.screen, game.colors.green, (int(rec_rwx), int(rec_rwy)), 4, 1)"""
