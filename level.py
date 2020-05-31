import sys, os.path, struct, math

class Vertex:
    def __init__( self, x, y ):
        self.x = x
        self.y = y


class Polygon:
    def __init__( self, grass ):
        self.grass = grass # bool
        self.vertexes = []

    # note that these extremes include grass polygons,
    # but it shouldn't matter so much because they are about the same size polygons
    def xmin(self):
        return min(v.x for v in self.vertexes)
    def xmax(self):
        return max(v.x for v in self.vertexes)
    def ymin(self):
        return min(v.y for v in self.vertexes)
    def ymax(self):
        return max(v.y for v in self.vertexes)

    def vertexes_as_pairs(self):
        return [(v.x, v.y) for v in self.vertexes]


class Object:
    def __init__( self, x, y, objtype, gravity, animation ):
        self.x = x
        self.y = y
        self.animation = animation

        if objtype not in [1, 2, 3, 4]:
            objtype = 1
        self.type = objtype
        self.type_name = ['', 'flower(1)', 'apple(2)', 'killer(3)', 'start(4)']

        if gravity not in [0, 1, 2, 3, 4]:
            gravity = 0
        self.gravity = gravity
        self.gravity_name = ['normal(0)', 'up(1)', 'down(2)', 'left(3)', 'right(4)']


class Level:
    def __init__( self, path=None, filename=None, game=None ):
        #self.polygons.append( [-24.0, -8.0, 24.0, -8.0, 24.0, 2.0, -24.0, 2.0] ) # std lev
        #self.objects.append( [-2.0, -0.85, 1, 0, 0] ) # flower
        #self.objects.append( [2.0, -0.85, 4, 0, 0] ) # 4=start, 2=apples, 3=killers
        self.polygons = []
        self.objects = []
        self.flowers = []
        self.apples = []
        self.killers = []
        self.startobject = None
        self.zoomx = 1
        self.zoomy = 1
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.width = None
        self.height = None
        self.path = None
        self.filename = None
        self.name = ""
        self.reclink = None
        self.maxplaytime = None
        self.hiscore = None # save recs and progress when this hiscore is beaten

        if path and filename:
            self.read(path, filename)
        self.game = game if game else None

    # note that these extremes include grass polygons,
    # but it shouldn't matter so much because they are about the same size polygons
    def set_xmin(self):
        self.xmin = min(p.xmin() for p in self.polygons)
    def set_xmax(self):
        self.xmax = max(p.xmax() for p in self.polygons)
    def set_ymin(self):
        self.ymin = min(p.ymin() for p in self.polygons)
    def set_ymax(self):
        self.ymax = max(p.ymax() for p in self.polygons)

    def set_width(self):
        self.width = self.xmax - self.xmin
    def set_height(self):
        self.height = self.ymax - self.ymin


    def read(self, path, filename, verbose=False):
        pathfilename = os.path.join( path, filename )
        self.path = path
        self.filename = filename
        f = open(pathfilename, 'rb')
        f.read(7)
        reclink = struct.unpack('i',f.read(4))[0]
        self.reclink = reclink
        i1 = struct.unpack('d',f.read(8))[0]
        i2 = struct.unpack('d',f.read(8))[0]
        i3 = struct.unpack('d',f.read(8))[0]
        i4 = struct.unpack('d',f.read(8))[0]
        levname = b''.join(struct.unpack('51c',f.read(51)))
        lgr = b''.join(struct.unpack('16c',f.read(16)))
        ground = b''.join(struct.unpack('10c',f.read(10)))
        sky = b''.join(struct.unpack('10c',f.read(10)))
        self.name = levname

        if verbose:
            print( 'Reclink: ' + str(reclink) )
            print( 'Integrity 1: ' + str(i1) )
            print( 'Integrity 2: ' + str(i2) )
            print( 'Integrity 3: ' + str(i3) )
            print( 'Integrity 4: ' + str(i4) )
            print( 'Level name: "%s"' % levname )
            print( 'LGR: "%s"' % lgr )
            print( 'Ground: "%s"' % ground )
            print( 'Sky: "%s"' % sky)

        npolys = int(struct.unpack('d',f.read(8))[0])
        if verbose:
            print( 'Polygons: ' + str(npolys) )

        for pnumber in range(npolys):
            grass = struct.unpack('i',f.read(4))[0] == 1
            poly = Polygon(grass)
            if verbose:
                print( 'Polygon ' + str(pnumber) + ':' )
                print( 'Grass: %s' % grass )

            nvertexes = int(struct.unpack('i',f.read(4))[0])
            vstr = ' Verteces: ' + str(nvertexes)
            for v in range(nvertexes):
                vx = struct.unpack('d',f.read(8))[0]
                vy = struct.unpack('d',f.read(8))[0]
                vstr += "(%f, %f), " % (vy, vx)
                vertex = Vertex(vx, vy)
                poly.vertexes.append(vertex)
            self.polygons.append(poly)
            vstr = vstr.rstrip(' ,')
            if verbose:
                print(vstr)
                
        nobjects = int(struct.unpack('d',f.read(8))[0])
        if verbose:
            print ( 'Objects: ' + str(nobjects) )
        for objnumber in range(nobjects):
            x = struct.unpack('d',f.read(8))[0]
            y = struct.unpack('d',f.read(8))[0]
            objtype = struct.unpack('i',f.read(4))[0]
            gravity = struct.unpack('i',f.read(4))[0]
            animation = struct.unpack('i',f.read(4))[0]
            obj = Object(x, y, objtype, gravity, animation)
            self.objects.append( obj )
            if obj.type == 4:
                self.startobject = obj
            elif obj.type == 2:
                self.apples.append( obj )
            elif obj.type == 3:
                self.killers.append( obj )
            else: # 1
                self.flowers.append( obj )

            if verbose:
                objstr = ' Object %d: %f, %f, type %s, gravity %s, animation %s' % (objnumber, x, y, obj.type_name, obj.gravity_name, obj.animation)
                print(objstr)

        f.close()
        self.set_xmin()
        self.set_xmax()
        self.set_ymin()
        self.set_ymax()
        self.set_width()
        self.set_height()
        print('%s start pos: %.02f, %.02f' % (self.filename, self.startobject.x, self.startobject.y))
        print('first flower: %.02f, %.02f' % (self.flowers[0].x, self.flowers[0].y))
        print('reclink: %d' % (self.reclink))

    def distance(self, obj, x, y):
        dx = obj.x - x
        dy = obj.y - y
        return math.sqrt( dx*dx + dy*dy )


    def flower_distance(self, kuski_state):
        #body_x = kuski_state['body']['location']['x']
        body_x = kuski_state[0]
        #body_y = kuski_state['body']['location']['y']
        body_y = kuski_state[1]
        #print("flower distance, flower x: %f, flower y: %f, body_x: %f, body_y: %f" % (self.flowers[0].x, self.flowers[0].y, body_x, body_y))
        return self.distance(self.flowers[0], body_x, body_y)

    def reward(self):
        # keep reward function simple, which means any progress near flower is the reward
        # and keep a time limit so that speed becomes a reward too
        #score = -0.1 # reduce score every frame, to penalize time # skip this because it could make gas only seem good
        score = 0
        #if self.game.kuski_state['finishedTime']:
        if self.game.kuski_state[11] > 0:
            score += 40
            #finished_time = self.game.timesteptotal * self.game.realtimecoeff
            #finished_time = self.game.kuski_state['finishedTime'] / 100.0
            finished_time = self.game.kuski_state[11] / 100.0
            margin = (self.maxplaytime - finished_time) # bigger margin better score
            score +=  margin * margin * 30
        #elif self.game.kuski_state['isDead']:
        elif self.game.kuski_state[10] > 0:
            #print("isDead: %f" % (self.game.kuski_state[10]))
            score -= 10

        if self.filename.lower() == 'ft.lev':
            self.maxplaytime = 20 # elma seconds to play a lev before exit
            self.hiscore = 45.0
            # starting distance = 61
            distance = self.flower_distance(self.game.kuski_state)
            prev_distance = self.flower_distance(self.game.prev_kuski_state)
            # if distance now is larger than distance before: get a negative score
            score -= distance - prev_distance
            #print("prev_distance: %f, distance: %f" %(prev_distance, distance))
            #print("distance: %f" % (distance - prev_distance))

        elif self.filename.lower() == 'ribotai0.lev':
            self.maxplaytime = 10 # elma seconds to play a lev before exit
            if self.reclink == 2052057095:
                self.hiscore = 60
            else:
                self.hiscore = 180 # best score so far 200+ or 7.77s
            distance = self.flower_distance(self.game.kuski_state)
            prev_distance = self.flower_distance(self.game.prev_kuski_state)
            # if distance now is larger than distance before: get a negative score
            score -= distance - prev_distance
            #print("prev_distance: %f, distance: %f" %(prev_distance, distance))
            #print("distance: %f" % (distance - prev_distance))

        elif self.filename.lower() == 'ribotai1.lev':
            self.maxplaytime = 20 # elma seconds to play a lev before exit
            self.hiscore = 100 # best score so far 194 or 7.86s
            distance = self.flower_distance(self.game.kuski_state)
            prev_distance = self.flower_distance(self.game.prev_kuski_state)
            # if distance now is larger than distance before: get a negative score
            score -= distance - prev_distance
            #print("prev_distance: %f, distance: %f" %(prev_distance, distance))
            #print("distance: %f" % (distance - prev_distance))

        elif self.filename.lower() == 'ai.lev':
            self.maxplaytime = 0.1 # elma seconds to play a lev before exit
            self.hiscore = 100 # best score so far 194 or 7.86s
            distance = self.flower_distance(self.game.kuski_state)
            prev_distance = self.flower_distance(self.game.prev_kuski_state)
            # if distance now is larger than distance before: get a negative score
            score -= distance - prev_distance
            #print("prev_distance: %f, distance: %f" %(prev_distance, distance))
            #print("distance: %f" % (distance - prev_distance))
        self.game.score += score
        self.game.score_delta = score
        return score

            # todo: last_distance
            #self.hiscore = # do not announce hiscore lower than this
            #self.lowscore = # do not announce lowscore higher than this

    def filename_wo_ext(self):
        return self.filename.split('.')[0] if self.filename else ''