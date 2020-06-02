import sys, os.path, struct, math

class BodyPart:
    def __init__( self, x, y, rotation ):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.frames = []

class Frame:
    def __init__( self, body, lw, rw, head, turn ):
        """self.body = body
        self.lw = lw
        self.rw = rw
        self.head = head
        self.turn = turn"""
        self.x = x
        self.y = y
        self.rotation = rotation


class Rec:
    def __init__( self, path=None, filename=None, game=None ):
        self.game = game if game else None
        self.frames = []
        self.events = []
        self.reclink = None
        self.path = path
        self.filename = filename

        if path and filename:
            self.read()


    def read(self, verbose=False):
        pathfilename = os.path.join( self.path, self.filename )
        try:
            f = open(pathfilename, 'rb')
        except:
            raise
        self.n_frames = struct.unpack('i', f.read(4))[0]
        f.read(12) # 0's
        self.reclink = struct.unpack('i',f.read(4)) # same as in readlev

        levfilename = b''.join( struct.unpack('16c', f.read(16)) )
        self.levfilename = levfilename.split(b'\x00')[0].decode('ascii')

        print('Rec Frames: %d' % self.n_frames)
        print('Rec Time: ~%.2f' % (self.n_frames * 0.0333333333 ))
        #print('Levhash: ' + str(self.reclink))
        #print('Levname: ' + self.levfilename)

        self.body_xs = []
        self.body_ys = []
        self.lwxs = []
        self.lwys = []
        self.rwxs = []
        self.rwys = []
        self.head_xs = []
        self.head_ys = []
        self.body_rotations = []
        self.lw_rotations = []
        self.rw_rotations = []
        self.turns = []

        # read rec as recedit by ribot from 2006
        for i, arr in enumerate((self.body_xs, self.body_ys, self.lwxs, self.lwys,
            self.rwxs, self.rwys, self.head_xs, self.head_ys, self.body_rotations,
            self.lw_rotations, self.rw_rotations, self.turns)):
            #print(i, arr)
            for frame in range(0, self.n_frames):
                # self.body_xs, self.body_ys
                if i < 2:
                    val = struct.unpack('f', f.read(4) )
                # self.lwxs, self.lwys, self.rwxs, self.rwys, self.head_xs, self.head_ys, self.body_rotations
                elif i < 9:
                    val = struct.unpack('h', f.read(2) )
                # self.lw_rotations, self.rw_rotations, self.turns
                else:
                    val = struct.unpack('b', f.read(1) )
                arr.append( val )
        #print("body xs: %d, frames: %d, body xs 0: %s, body xs -1: %s, body ys 0: %s" \
        #    % (len(self.body_xs), self.n_frames, self.body_xs[0], self.body_xs[-1], self.body_ys[0]))

        """db = self.game.db.db
        query = db.level.reclink == self.reclink
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
        self.db_row = lev_row"""

    def filename_wo_ext(self):
        return self.filename.split('.')[0] if self.filename else ''

if __name__ == '__main__':
    import local
    rec = Rec(local.recpath, filename='warmup.rec')
