import sys, os.path, struct, math
# https://github.com/elmadev/elma-python

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
        print('Levname: ' + self.levfilename)

        def munch(f, n):
            return f.read(n)

        def read_float(f):
            return struct.unpack('f', munch(f, 4))[0]

        def read_int16(f):
            return struct.unpack('h', munch(f, 2))[0]

        def read_uint8(f):
            return struct.unpack('B', munch(f, 1))[0]

        self.body_xs = [read_float(f) for _ in range(self.n_frames)]
        self.body_ys = [read_float(f) for _ in range(self.n_frames)]
        self.lwxs = [read_int16(f) for _ in range(self.n_frames)]
        self.lwys = [read_int16(f) for _ in range(self.n_frames)]
        self.rwxs = [read_int16(f) for _ in range(self.n_frames)]
        self.rwys = [read_int16(f) for _ in range(self.n_frames)]
        self.head_xs = [read_int16(f) for _ in range(self.n_frames)]
        self.head_ys = [read_int16(f) for _ in range(self.n_frames)]
        self.body_rotations = [read_int16(f) for _ in range(self.n_frames)]
        self.lw_rotations = [read_uint8(f) for _ in range(self.n_frames)]
        self.rw_rotations = [read_uint8(f) for _ in range(self.n_frames)]
        self.turns = [read_uint8(f) for _ in range(self.n_frames)]
        sound_effect_volumes = [read_int16(f) for _ in range(self.n_frames)]

        #print("body xs: %d, frames: %d, lwxs -1: %s, lwxs 0: %s" \
        #    % (len(self.body_xs), self.n_frames, self.lwxs[-1], self.lwxs[0]))#
        #print(self.lwys)
        print(self.body_xs[0], self.body_ys[0], self.lwxs[0], self.lwys[0],
            self.rwxs[0], self.rwys[0], self.head_xs[0], self.head_ys[0], self.body_rotations[0],
            self.lw_rotations[0], self.rw_rotations[0], self.turns[0])

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
    rec = Rec(local.recpath, filename='wu.rec')
