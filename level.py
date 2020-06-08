import sys, os.path, struct#, math

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
        self.game = game if game else None
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
        #self.maxplaytime = None
        #self.hiscore = None # save recs and progress when this hiscore is beaten

        if path and filename:
            self.read(path, filename)

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
        db = self.game.db.db
        #query = db.level.reclink == self.reclink # don't do this to be able to edit levels in editor
        query = db.level.filename == self.filename
        lev_row = db(query).select().first()
        if not lev_row:
            maxplaytime = input("Max play time for %s: " % (self.filename))
            hiscore = input("Hiscore: ")
            if maxplaytime.isnumeric:
                maxplaytime = float(maxplaytime)
                hiscore = float(hiscore) if hiscore.isnumeric() else 50
                row_id = db.level.insert( filename=self.filename, reclink=self.reclink, maxplaytime=maxplaytime, hiscore=hiscore )
                lev_row = db.level[row_id]
                db.commit()
        self.db_row = lev_row

    def distance(self, obj, x, y):
        # remember to flip the y-axis, as lev y is negated compared to bike y
        dx = obj.x - x
        dy = obj.y - y
        #return math.sqrt( dx*dx + dy*dy )
        # faster than sqrt and correct
        return dx*dx + dy*dy

    def flower_distance(self, kuski_state):
        body_x = kuski_state['body']['location']['x']
        #body_x = kuski_state[0]
        body_y = -kuski_state['body']['location']['y']
        #body_y = kuski_state[1]
        #print("flower distance, flower x: %f, flower y: %f, body_x: %f, body_y: %f" % (self.flowers[0].x, self.flowers[0].y, body_x, body_y))
        return self.distance(self.flowers[0], body_x, body_y)

    def reward(self):
        # todo: as this reward is per frame, create also a function that is at the end of episode
        # keep reward function simple, which means any progress near flower is the reward
        # and keep a time limit so that speed becomes a reward too
        #score = -0.1 # reduce score every frame, to penalize time # skip this because it could make gas only seem good
        #score = -0.0001 # slight score reduction every frame
        if self.game.arg_eol:
            # as eol doesn't have kuski_state as dict() implemented, and doesn't train anyway
            # return some values to not cause calculation errors in train.py
            import random
            self.game.score_delta = random.random()
            self.game.score += self.game.score_delta
            return self.game.score_delta

        # score should not be 0 to avoid std errors? RuntimeWarning: invalid value encountered in true_divide
        # slight positive score that will value survival?
        # since otherwise dying instantly causes less negative points than following rec
        score = 0.0
        if self.game.kuski_state['numTakenApples'] > self.game.num_taken_apples:
            # note that it can be more than one apple taken in a frame
            self.game.num_taken_apples += self.game.kuski_state['numTakenApples'] - self.game.num_taken_apples
            score += 20

        #if self.game.kuski_state[11] > 0:
        if self.game.kuski_state['finishedTime']:
            score += 40
            #finished_time = self.game.timesteptotal * self.game.realtimecoeff
            finished_time = self.game.kuski_state['finishedTime'] / 100.0
            #finished_time = self.game.kuski_state[11] / 100.0
            margin = (self.db_row.maxplaytime - finished_time) # bigger margin better score
            score +=  margin * margin * 30
        #elif self.game.kuski_state[10] > 0:
        elif self.game.kuski_state['isDead']:
            #print("isDead: %f" % (self.game.kuski_state[10]))
            if self.game.rec is None:
                # punish death (unless following a rec?)
                # too much punishment might cause passivity,
                # but might be needed to reward survival in tough spots
                score -= 2
                #pass
        elif self.game.rec is not None:
            # body distance from rec
            # it's very complicated to balance distance per frame, and avoid death and not be passive
            # don't reward here, instead reward distance after whole sequence
            """
            x = self.game.rec.frames[ self.game.recframe ].position.x
            y = self.game.rec.frames[ self.game.recframe ].position.y
            X = self.game.kuski_state['body']['location']['x']
            Y = self.game.kuski_state['body']['location']['y']
            distance = (x-X) * (x-X) + (y-Y) * (y- Y)
            if distance < 1:
                score += 0.05
            elif distance > 2:
                score -= 0.05
            #print(distance)
            #distance = distance if distance < 10 else 10
            #score -= distance*distance"""
            pass

        #elif self.db_row.reward_type == "flowerDistance":
        else:
            # todo: select order of apples to move towards first
            # note that all apples might not have to be added, such as first apple in internal 04
            # also note that imaginary apples or killers (or training lev) might have to be added, such as for int 05
            if len(self.apples) > self.game.kuski_state['numTakenApples']:
                apple_index = 0 if self.db_row.apples is None else self.db_row.apples[self.game.kuski_state['numTakenApples']]
                distance = self.distance(self.apples[apple_index], self.game.kuski_state['body']['location']['x'], -self.game.kuski_state['body']['location']['y'])
                prev_distance = self.distance(self.apples[apple_index], self.game.prev_kuski_state['body']['location']['x'], -self.game.prev_kuski_state['body']['location']['y'])
            else:
                distance = self.flower_distance(self.game.kuski_state)
                prev_distance = self.flower_distance(self.game.prev_kuski_state)
            #distance = self.game.kuski_state[12]
            #prev_distance = self.game.prev_kuski_state[12]
            score -= (distance - prev_distance)/300

        self.game.score += score
        self.game.score_delta = score
        #if self.game.arg_framebyframe:
        #    print("episode: %d, frame: %d, recframe: %d, score_delta: %f, score: %f, apples: %d" \
        #        % (self.game.episode, self.game.frame, self.game.recframe, score, self.game.score, self.game.num_taken_apples))
        return score

            # todo: last_distance
            #self.hiscore = # do not announce hiscore lower than this
            #self.lowscore = # do not announce lowscore higher than this

    def filename_wo_ext(self):
        return self.filename.split('.')[0] if self.filename else ''