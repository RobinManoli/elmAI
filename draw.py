import level

def draw(game, elmaphys):
    game.screen.fill(game.colors.skyblue)
    drawlev(game)
    drawbike(game, elmaphys)

    game.gui.label(game, 'Welcome to AI', 10, 10)

    # draw lev coords
    mx, my = game.pygame.mouse.get_pos()
    if lev:
        levx = lev.xmin - (game.width/zoom - lev.width)/2 + mx/zoom
        levy = lev.ymin - (game.height/zoom - lev.height)/2 + my/zoom
        # keep coords visible on screen
        mx = game.width - 110 if mx > game.width - 110 else mx
        my = game.height - 20 if my > game.height - 20 else my
        game.gui.label(game, '%d x %d' % (levx, levy), mx+15, my)
    

    # todo: optimize display using .update or whatnot (opengl?) https://www.pygame.org/docs/ref/display.html#pygame.display.flip
    game.pygame.display.flip()

def drawbike(game, elmaphys):
    phys = elmaphys.next_frame()
    #print( phys ) # segmentation fault after pygame.init()
    headx = phys['headLocation']['x'] * zoom + xoffset
    heady = -phys['headLocation']['y'] * zoom + yoffset
    bodyx = phys['body']['location']['x'] * zoom + xoffset
    bodyy = -phys['body']['location']['y'] * zoom + yoffset
    lwx = phys['leftWheel']['location']['x'] * zoom + xoffset
    lwy = -phys['leftWheel']['location']['y'] * zoom + yoffset
    rwx = phys['rightWheel']['location']['x'] * zoom + xoffset
    rwy = -phys['rightWheel']['location']['y'] * zoom + yoffset

    print( "body: %d %d" % (bodyx, bodyy) )
    game.pygame.draw.circle(game.screen, game.colors.yellow, (int(headx), int(heady)), 4)
    game.pygame.draw.circle(game.screen, game.colors.yellow, (int(bodyx), int(bodyy)), 4)
    game.pygame.draw.circle(game.screen, game.colors.green, (int(lwx), int(lwy)), 4)
    game.pygame.draw.circle(game.screen, game.colors.green, (int(rwx), int(rwy)), 4)

lev = None
zoom = 1
xoffset = 0
yoffset = 0
zoomed_polygons = []
zoomed_objects = []
def drawlev(game):
    global lev, zoom, xoffset, yoffset, zoomed_polygons, zoomed_objects
    if not lev:
        # do lev stuff once, not on every tick
        lev = level.Level()
        lev.read(r"C:\Users\Sara\Desktop\robin\elma\lev" ,"0lp31.lev")
        print("xmin %d, xmax %d, ymin %d, ymax %d, width %d, height %d" % (lev.xmin, lev.xmax, lev.ymin, lev.ymax, lev.width, lev.height))
        xratio = game.width / lev.width
        yratio = game.height / lev.height
        if xratio < yratio:
            zoom = xratio
            # start x-axis on x-min
            xoffset = -lev.xmin * zoom
            # center y-axis starting on y-min
            yoffset = -lev.ymin * zoom + (game.height - lev.height * zoom ) / 2
        else:
            zoom = yratio
            # start y-axis on y-min
            yoffset = -lev.ymin * zoom
            # center x-axis starting on x-min
            xoffset = -lev.xmin * zoom + (game.width - lev.width * zoom ) / 2
        #print("xratio %d, yratio %d, zoom %d, xoffset %d, yoffset %d" % (xratio, yratio, zoom, xoffset, yoffset))

        for polygon in lev.polygons:
            if not polygon.grass:
                vertexes = [(v.x*zoom + xoffset, v.y*zoom + yoffset) for v in polygon.vertexes]
                zoomed_polygons.append( vertexes )
        for obj in lev.objects:
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
        