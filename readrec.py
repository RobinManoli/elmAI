import sys
import os.path
import struct

if len(sys.argv) < 2: print ( "usage: readrec.py rec.rec [rec2.rec to copy reclink from rec.rec]" )

def readrec(filename):
    #f = open( os.path.join('levels',sys.argv[1]), 'rb' )
    f = open(filename, 'rb')
    n_frames = struct.unpack('i', f.read(4))[0]
    f.read(12) # 0's
    # levhash = f.read(4) # or unpack with 'd' ?
    #levhash = struct.unpack('i',f.read(4))[0] # working, but not for writing # same as in readlev
    levhash = b''.join( struct.unpack('4c', f.read(4)) )

    levname = b''.join( struct.unpack('16c', f.read(16)) )

    print ( 'Frames: %d' % n_frames)
    print ( 'Time: ~%.2f' % (n_frames * 0.0333333333 ) )
    print ( 'Levhash: ' + str(levhash))
    print ( 'Levname: ' + levname.split(b'\x00')[0].decode('ascii') )
    
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
    f.close()
    return levhash, levname

if len( sys.argv ) > 1:
    filename = sys.argv[1]
    levhash, levname = readrec(filename)
    print(levhash)
    print(levname)
    print()

if len( sys.argv ) > 2:
    filename = sys.argv[2]
    f = open(filename, 'r+b')
    f.seek(4+12)
    f.write(levhash)
    f.write(levname)
    f.close()
    readrec(filename)


