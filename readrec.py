import sys
import os.path
import struct

if len(sys.argv) < 2: print ( "usage: readrec.py rec.rec" )
else:
    filename = sys.argv[1]
    #f = open( os.path.join('levels',sys.argv[1]), 'rb' )
    f = open(filename, 'rb')
    n_frames = struct.unpack('i', f.read(4))[0]
    f.read(12) # 0's
    # levhash = f.read(4) # or unpack with 'd' ?
    levhash = struct.unpack('i',f.read(4)) # same as in readlev

    levname = b''.join( struct.unpack('16c', f.read(16)) )
    levname = levname.split(b'\x00')[0].decode('ascii')

    print ( 'Frames: %d' % n_frames)
    print ( 'Time: ~%.2f' % (n_frames * 0.0333333333 ) )
    print ( 'Levhash: ' + str(levhash))
    print ( 'Levname: ' + levname )
    
    x = []
    y = []
    lwx = [] # left wheel
    lwy = []
    rwx = [] # right wheel
    rwy = []
    hx =[] # head
    hy = []
    rot = [] # rotation
    lwrot = []
    rwrot = []
    turn = []

    # read rec as recedit by ribot from 2006
    for i, arr in enumerate((x, y, lwx, lwy, rwx, rwy, hx, hy, rot, lwrot, rwrot, turn)):
        for frame in range(0, n_frames):
            if i < 2:
                val = struct.unpack('f', f.read(4) )
            elif i < 9:
                val = struct.unpack('h', f.read(2) )
            else:
                val = struct.unpack('b', f.read(1) )
            arr.append( val )
            #print(val)

    print ('old recedit first frame:', x[0], y[0], lwx[0], lwy[0], rwx[0], rwy[0], hx[0], hy[0], rot[0], lwrot[0], rwrot[0], turn[0] )

    """polys = int(struct.unpack('d',f.read(8))[0])
    print ( 'Polygons: ' + str(polys) )
    for p in range(polys):
        print ( 'Polygon ' + str(p) + ':' )
        if struct.unpack('i',f.read(4))[0] == 1:
            print ( ' Grass: Yes' )
        else:
            print ( ' Grass: No' )
        vs = int(struct.unpack('i',f.read(4))[0])
        vstr = ( ' Verteces: ' + str(vs) + ' (' )
        for v in range(vs):
            vstr += str(struct.unpack('d',f.read(8))[0]) + ', '
            vstr += str(struct.unpack('d',f.read(8))[0]) + ', '
        vstr = vstr[:-2] + ')'
        print vstr
            
    obs = int(struct.unpack('d',f.read(8))[0])
    print ( 'Objects: ' + str(obs) )
    for o in range(obs):
        ostr = ' Object ' + str(o) + ': '
        ostr += 'x=' + str(struct.unpack('d',f.read(8))[0]) + ' '
        ostr += 'y=' + str(struct.unpack('d',f.read(8))[0]) + ' '
        otype = struct.unpack('i',f.read(4))[0]
        if otype == 1: ostr += 'flower(1) '
        elif otype == 2: ostr += 'apple(2) '
        elif otype == 3: ostr += 'killer(3) '
        elif otype == 4: ostr += 'start(4) '
        else: ostr += 'errortype(' + str(otype) + ') '
        ostr += 'gravity='
        ograv = struct.unpack('i',f.read(4))[0]
        if ograv == 0: ostr += 'normal(0) '
        elif ograv == 1: ostr += 'up(1) '
        elif ograv == 2: ostr += 'down(2) '
        elif ograv == 3: ostr += 'left(3) '
        elif ograv == 4: ostr += 'right(4) '
        else: ostr += 'errorvalue(' + str(ograv) + ') '
        ostr += ( 'animation#=' + str(struct.unpack('i',f.read(4))[0]) )
        print ( ostr )"""

    f.close()



