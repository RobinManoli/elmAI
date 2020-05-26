def draw(game):
    game.screen.fill(game.colors.skyblue)
    drawlev(game)
    drawbike(game)

    #game.gui.label(game, 'Welcome to LassElma AI', 10, 10)
    game.gui.label(game, '%.2f' % (game.score), 10, 10)
    game.gui.label(game, '%.2f' % (game.last_score), 100, 10)
    game.gui.label(game, '%.2f' % (game.timesteptotal * game.realtimecoeff), game.width-70, 10)
    if game.lasttime:
        game.gui.label(game, 'prev: %.2f' % game.lasttime, game.width-210, 10)
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

def drawbike(game):
    #print( game.kuski_state ) # segmentation fault after pygame.init()
    headx = game.kuski_state['headLocation']['x'] * zoom + xoffset
    heady = -game.kuski_state['headLocation']['y'] * zoom + yoffset
    bodyx = game.kuski_state['body']['location']['x'] * zoom + xoffset
    bodyy = -game.kuski_state['body']['location']['y'] * zoom + yoffset
    lwx = game.kuski_state['leftWheel']['location']['x'] * zoom + xoffset
    lwy = -game.kuski_state['leftWheel']['location']['y'] * zoom + yoffset
    rwx = game.kuski_state['rightWheel']['location']['x'] * zoom + xoffset
    rwy = -game.kuski_state['rightWheel']['location']['y'] * zoom + yoffset

    body_thickness = 2
    if game.kuski_state['direction'] == 0:
        body_polygon = (bodyx - 8, bodyy), (bodyx + 8, bodyy + 4), (bodyx + 8, bodyy - 4)
        body_color = game.colors.yellow
    else:
        body_polygon = (bodyx + 8, bodyy), (bodyx - 8, bodyy + 4), (bodyx - 8, bodyy - 4)
        body_color = game.colors.blue
    game.pygame.draw.circle(game.screen, game.colors.yellow, (int(headx), int(heady)), 4)
    game.pygame.draw.polygon(game.screen, body_color, body_polygon, body_thickness)
    game.pygame.draw.circle(game.screen, game.colors.green, (int(lwx), int(lwy)), 5)
    game.pygame.draw.circle(game.screen, game.colors.green, (int(rwx), int(rwy)), 5)

initlev = False
# check out pygame.camera instead of zooming and offsetting
zoom = 1
xoffset = 0
yoffset = 0
zoomed_polygons = []
zoomed_objects = []
def drawlev(game):
    global initlev, zoom, xoffset, yoffset, zoomed_polygons, zoomed_objects
    if not initlev:
        # do lev stuff once, not on every tick
        initlev = True
        print("xmin %d, xmax %d, ymin %d, ymax %d, width %d, height %d" % (game.level.xmin, game.level.xmax, game.level.ymin, game.level.ymax, game.level.width, game.level.height))
        xratio = game.width / game.level.width
        yratio = game.height / game.level.height
        if xratio < yratio:
            zoom = xratio
            # start x-axis on x-min
            xoffset = -game.level.xmin * zoom
            # center y-axis starting on y-min
            yoffset = -game.level.ymin * zoom + (game.height - game.level.height * zoom ) / 2
        else:
            zoom = yratio
            # start y-axis on y-min
            yoffset = -game.level.ymin * zoom
            # center x-axis starting on x-min
            xoffset = -game.level.xmin * zoom + (game.width - game.level.width * zoom ) / 2
        #print("xratio %d, yratio %d, zoom %d, xoffset %d, yoffset %d" % (xratio, yratio, zoom, xoffset, yoffset))

        for polygon in game.level.polygons:
            if not polygon.grass:
                vertexes = [(v.x*zoom + xoffset, v.y*zoom + yoffset) for v in polygon.vertexes]
                zoomed_polygons.append( vertexes )
        for obj in game.level.objects:
            colors = [None, game.colors.white, game.colors.red, game.colors.black, game.colors.yellow]
            x = obj.x*zoom + xoffset
            y = obj.y*zoom + yoffset
            color = colors[obj.type]
            zoomed_objects.append(( int(x), int(y), color ))
            if obj.type == 4:
                print('Lev start position: %d, %d' % (obj.x, obj.y))

    for obj in zoomed_objects:
        #print(obj)
        game.pygame.draw.circle(game.screen, obj[2], (obj[0], obj[1]), 4)


    for polygon in zoomed_polygons:
        thickness = 1
        #print("drawing %s" % str(polygon.vertexes))
        game.pygame.draw.polygon(game.screen, game.colors.black, polygon, thickness)
        