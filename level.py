import sys
import os.path
import struct

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
    def __init__( self ):
        #self.polygons.append( [-24.0, -8.0, 24.0, -8.0, 24.0, 2.0, -24.0, 2.0] ) # std lev
        #self.objects.append( [-2.0, -0.85, 1, 0, 0] ) # flower
        #self.objects.append( [2.0, -0.85, 4, 0, 0] ) # 4=start, 2=apples, 3=killers
        self.polygons = []
        self.objects = []
        self.zoomx = 1
        self.zoomy = 1
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.width = None
        self.height = None
    
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
        f = open(pathfilename, 'rb')
        f.read(7)
        reclink = struct.unpack('i',f.read(4))[0]
        i1 = struct.unpack('d',f.read(8))[0]
        i2 = struct.unpack('d',f.read(8))[0]
        i3 = struct.unpack('d',f.read(8))[0]
        i4 = struct.unpack('d',f.read(8))[0]
        levname = b''.join(struct.unpack('51c',f.read(51)))
        lgr = b''.join(struct.unpack('16c',f.read(16)))
        ground = b''.join(struct.unpack('10c',f.read(10)))
        sky = b''.join(struct.unpack('10c',f.read(10)))

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


