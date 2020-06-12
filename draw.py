# https://stackoverflow.com/questions/19746552/pygame-camera-follow-in-a-2d-tile-game

def draw(game):
    game.screen.fill(game.colors.skyblue)
    drawkeys(game)
    drawlev(game)
    drawbody(game)

    #game.gui.label(game, 'Welcome to LassElma AI', 10, 10)
    game.gui.label(game, 'score: %.3f   prev score: %.2f' % (game.score, game.last_score), 10, 10)
    game.gui.label(game, 'time: %.3f' % (game.timesteptotal * game.realtimecoeff), game.width-130, 10)
    if game.lasttime:
        game.gui.label(game, 'prev time: %.2f' % game.lasttime, game.width-330, 10)
        #game.gui.label(game, 'total: %.2f' % game.elmatimetotal, game.width-350, 10)

    # display events one second back and forth in time
    if game.rec is not None:
        displayed_events = ["%.3f %s" % (event.time*game.realtimecoeff, type(event).__name__[:-5]) for event in game.rec.events if abs(event.time*game.realtimecoeff - game.timesteptotal*game.realtimecoeff) < 1]
        displayed_events = ', '.join(displayed_events)
        game.gui.label(game, '%s' % (displayed_events), 10, 50)
    game.gui.label(game, 'frame: %d   fps: %d   apples: %d   finish: %.2f   rotation time: %.3f' % \
        (game.frame, game.fps, game.kuski_state['numTakenApples'], game.kuski_state['finishedTime']/100, game.timesteptotal-game.kuski_state['lastRotationTime']), 10, 30)

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

def draw_bodypart(game, orig_x, orig_y, rotation, radius, image, image_rotation=0.0, scale_factor=1.0, is_turned_right=None):
    """
    Draws a body part zoomed and offset.
    The image is expected to be a square.
    Image rotation is the rotation of the original .png image (ie the bike is rotated 35 degrees)
    Scale factor is for bike which in game has a weird radius in comparison to drawn size.
    """

    # scale and position
    pixel_width = image.get_size()[0]
    zoom_diameter = radius * 2 * zoom * scale_factor
    scale = zoom_diameter / pixel_width
    x = orig_x * zoom + levxoffset - zoom_diameter / 2
    y = -orig_y * zoom + levyoffset - zoom_diameter / 2

    # transform
    radian = 57.2957795
    transformed_image = image
    if is_turned_right is None:
        is_turned_right = game.kuski_state['direction']
    if is_turned_right:
        image_rotation = -image_rotation
        transformed_image = game.pygame.transform.flip(image, True, False) # flipx, flipy
    transformed_image = game.pygame.transform.rotozoom(transformed_image, rotation * radian + image_rotation, scale)

    # offset and blit
    bbox = transformed_image.get_rect()
    offset = (bbox[2] - zoom_diameter)/2
    game.screen.blit(transformed_image, (x-offset, y-offset))
    return x, y


bikexoffset = 0
bikeyoffset = 0
pi = 3.141592653589793
# taken from smibu_phys/PlayerData.cpp
rec_body_rotation_factor = 10000.0 / (pi + pi)
rec_wheel_rotation_factor = 250.0 / (pi + pi)
def drawbody(game):
    global bikexoffset, bikeyoffset
    #print(game.kuski_state['body']['rotation'])
    # radius from KuskiState.cpp and .h
    draw_bodypart(game, game.kuski_state['headLocation']['x'], game.kuski_state['headLocation']['y'], game.kuski_state['body']['rotation'], radius=0.238, image=game.image_head)
    draw_bodypart(game, game.kuski_state['leftWheel']['location']['x'], game.kuski_state['leftWheel']['location']['y'],
        game.kuski_state['leftWheel']['rotation'], radius=0.4, image=game.image_wheel)
    draw_bodypart(game, game.kuski_state['rightWheel']['location']['x'], game.kuski_state['rightWheel']['location']['y'],
        game.kuski_state['rightWheel']['rotation'], radius=0.4, image=game.image_wheel)
    # draw bike at position of headCenterLocation, which seems more like body center location (or heart) -- looks better because no human body is drawn
    bikex, bikey = draw_bodypart(game, game.kuski_state['headCenterLocation']['x'], game.kuski_state['headCenterLocation']['y'], game.kuski_state['body']['rotation'],
        radius=0.3, image=game.image_bike, image_rotation=35.0, scale_factor=2.0)
    #bodyx = game.kuski_state['body']['location']['x'] * zoom + levxoffset - body_size / 2
    #bodyy = -game.kuski_state['body']['location']['y'] * zoom + levyoffset - body_size / 2
    #print(game.kuski_state['headLocation']['y'] - game.kuski_state['headCenterLocation']['y'])

    # rec coords taken from smibu_phys/PlayerData.cpp
    # using elmadev
    if game.rec is not None and game.recframe + game.recframe_offset < len(game.rec.frames) and game.recframe + game.recframe_offset >= 0:
        frame = game.rec.frames[game.recframe + game.recframe_offset]
        # head position seems to be headCenterLocation, which is 0.6299999999999999 under headLocation
        draw_bodypart(game, frame.head_position.x / 1000.0 + frame.position.x, frame.head_position.y / 1000.0 + frame.position.y + 0.6299999999999999,
            frame.rotation/rec_body_rotation_factor, radius=0.238, image=game.rec_image_head, is_turned_right=frame.is_turned_right)
        draw_bodypart(game, frame.left_wheel_position.x / 1000.0 + frame.position.x, frame.left_wheel_position.y / 1000.0 + frame.position.y,
            frame.left_wheel_rotation / rec_wheel_rotation_factor, radius=0.4, image=game.rec_image_wheel)
        draw_bodypart(game, frame.right_wheel_position.x / 1000.0 + frame.position.x, frame.right_wheel_position.y / 1000.0 + frame.position.y,
            frame.right_wheel_rotation / rec_wheel_rotation_factor, radius=0.4, image=game.rec_image_wheel)
        # draw bike at position of headCenterLocation, which seems more like body center location (or heart) -- looks better because no human body is drawn
        draw_bodypart(game, frame.head_position.x / 1000.0 + frame.position.x, frame.head_position.y / 1000.0 + frame.position.y,
            frame.rotation/rec_body_rotation_factor, radius=0.3, image=game.rec_image_bike, image_rotation=35.0, scale_factor=2.0, is_turned_right=frame.is_turned_right)

    if follow_bike:
        # move cx and cy to center, by calculating distance to center
        bikexoffset = (game.width/2 - bikex) / 2
        bikeyoffset = (game.height/2 - bikey) / 2
        game.redraw = True
    else:
        bikexoffset = 0
        bikeyoffset = 0

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
        zoom_mode = game.zoom_mode % 8
        if zoom_mode == 0:
            zoomlev(game)
            follow_bike = False
        else:
            zoom = 25 + 25 * zoom_mode
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

# below is working way to draw bike as lines and circles
#body_thickness = 2
#if game.kuski_state['direction'] == 0:
#    #body_polygon = (bodyx - 8, bodyy), (bodyx + 8, bodyy + 4), (bodyx + 8, bodyy - 4)
#    body_polygon = (headx, heady), (lwx, lwy), (rwx, rwy)
#    body_color = game.colors.yellow
#else:
#    #body_polygon = (bodyx + 8, bodyy), (bodyx - 8, bodyy + 4), (bodyx - 8, bodyy - 4)
#    body_polygon = (headx, heady), (lwx, lwy), (rwx, rwy)
#    body_color = game.colors.blue
#game.pygame.draw.line( game.screen, game.colors.white, (int(headcx), int(headcy)), (int(headx), int(heady)) )
#game.pygame.draw.line( game.screen, game.colors.black, (int(headcx), int(headcy)), (int(lwx), int(lwy)) )
#game.pygame.draw.line( game.screen, game.colors.black, (int(headcx), int(headcy)), (int(rwx), int(rwy)) )
#game.pygame.draw.line( game.screen, game.colors.white, (int(rwx), int(rwy)), (int(lwx), int(lwy)) )
#if game.kuski_state['direction'] == 0:
#    game.pygame.draw.line( game.screen, game.colors.black, (int(headx), int(heady)), (int(rwx), int(rwy)) )
#   pass
#else:
#    game.pygame.draw.line( game.screen, game.colors.black, (int(headx), int(heady)), (int(lwx), int(lwy)) )
#game.pygame.draw.circle(game.screen, game.colors.yellow, (int(headx), int(heady)), int(0.3*zoom))
#game.pygame.draw.polygon(game.screen, body_color, body_polygon, body_thickness)
#game.pygame.draw.circle(game.screen, game.colors.green, (int(lwx), int(lwy)), int(0.4*zoom))
#game.pygame.draw.circle(game.screen, game.colors.green, (int(rwx), int(rwy)), int(0.4*zoom))

# working, draw rec as lines and circles
"""rec_body_x = frame.position.x * zoom + levxoffset
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
game.pygame.draw.circle(game.screen, game.colors.cyan, (int(rec_hx), int(rec_hy)), int(0.3*zoom), 2)"""



# working code that was later simplified
"""
    head_radius = 0.238
    head_image_width = 189 # pixel width
    head_size = head_radius * 2 * zoom
    head_scale = head_size / head_image_width

    body_radius = 0.3 # as setting in code for some strange reason
    body_image_width = 380 # pixel width
    body_size = body_radius * 2 * zoom * 2 # increase size by this factor to draw bike to a more correct size
    body_scale = body_size / body_image_width

    wheel_radius = 0.4
    wheel_image_width = 240
    wheel_size = wheel_radius * 2 * zoom
    wheel_scale = wheel_size / wheel_image_width

    #print( game.kuski_state ) # segmentation fault after pygame.init()
    headx = game.kuski_state['headLocation']['x'] * zoom + levxoffset - head_size / 2
    heady = -game.kuski_state['headLocation']['y'] * zoom + levyoffset - head_size / 2
    # headCenterLocation seems like body center location (or heart) - draw bike here as no human body is drawn
    headcx = game.kuski_state['headCenterLocation']['x'] * zoom + levxoffset - body_size / 2
    headcy = -game.kuski_state['headCenterLocation']['y'] * zoom + levyoffset - body_size / 2
    # this might be bike x rather than body, as body and bike are used interchangably in code
    #bodyx = game.kuski_state['body']['location']['x'] * zoom + levxoffset - body_size / 2
    #bodyy = -game.kuski_state['body']['location']['y'] * zoom + levyoffset - body_size / 2
    lwx = game.kuski_state['leftWheel']['location']['x'] * zoom + levxoffset - wheel_size / 2
    lwy = -game.kuski_state['leftWheel']['location']['y'] * zoom + levyoffset - wheel_size / 2
    rwx = game.kuski_state['rightWheel']['location']['x'] * zoom + levxoffset - wheel_size / 2
    rwy = -game.kuski_state['rightWheel']['location']['y'] * zoom + levyoffset - wheel_size / 2
    #print(wheel_scale)
    #body_rot = self.kuski_state['body']['rotation']

    #game.transformed_image_head = game.pygame.transform.rotate(game.image_head, game.kuski_state['body']['rotation'] * 57.2957795) # radians to degrees
    #game.transformed_image_bike = game.pygame.transform.rotate(game.image_bike, game.kuski_state['body']['rotation'] * 57.2957795 + 90)
    #game.transformed_image_head = game.pygame.transform.scale(game.transformed_image_head, (head_scale, head_scale))
    #game.transformed_image_bike = game.pygame.transform.scale(game.transformed_image_bike, (body_scale, body_scale))
    # radians to degrees, and max(pixel_w, pixel_h)
    radian = 57.2957795
    if game.kuski_state['direction'] == 0:
        game.transformed_image_head = game.image_head
        game.transformed_image_bike = game.image_bike
        body_rotation_fix = 35 # original image is rotated 35 degrees
    else:
        game.transformed_image_head = game.pygame.transform.flip(game.image_head, True, False) # flipx, flipy
        game.transformed_image_bike = game.pygame.transform.flip(game.image_bike, True, False)
        body_rotation_fix = -35
    game.transformed_image_head = game.pygame.transform.rotozoom(game.transformed_image_head, game.kuski_state['body']['rotation'] * radian, head_scale)
    game.transformed_image_bike = game.pygame.transform.rotozoom(game.transformed_image_bike, game.kuski_state['body']['rotation'] * radian+body_rotation_fix, body_scale)
    game.transformed_image_left_wheel = game.pygame.transform.rotozoom(game.image_wheel, game.kuski_state['rightWheel']['rotation'] * radian, wheel_scale)
    game.transformed_image_right_wheel = game.pygame.transform.rotozoom(game.image_wheel, game.kuski_state['rightWheel']['rotation'] * radian, wheel_scale)

    # the bounding box gets bigger when an image is rotated, so it will not rotate against its center
    # solve this by subtracting half the size difference when blitting
    h_bbox = game.transformed_image_head.get_rect()
    h_offset = (h_bbox[2] - head_size)/2
    body_bbox = game.transformed_image_bike.get_rect()
    body_offset = (body_bbox[2] - body_size)/2
    lw_bbox = game.transformed_image_left_wheel.get_rect()
    lw_offset = (lw_bbox[2] - wheel_size)/2
    rw_bbox = game.transformed_image_right_wheel.get_rect()
    rw_offset = (rw_bbox[2] - wheel_size)/2

    #game.screen.blit(game.transformed_image_head, (headx-h_offset, heady-h_offset))
    #game.screen.blit(game.transformed_image_bike, (headcx-body_offset, headcy-body_offset))
    #game.screen.blit(game.transformed_image_left_wheel, (lwx-lw_offset, lwy-lw_offset))
    #game.screen.blit(game.transformed_image_right_wheel, (rwx-rw_offset, rwy-rw_offset))"""