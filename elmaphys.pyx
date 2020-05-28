# distutils: language = c++

from celmaphys cimport nextFrameKuski, saveReplay, cinit, restartLevel
#from celmaphys cimport cinit

print("elmaphys.pyx loaded...")

def init(levpathfilename):
    # makes pygame crash: parachute segmentation fault
    levpathfilename = bytes( levpathfilename, 'utf-8' )
    #print(b"init: " + levpathfilename)
    return cinit(levpathfilename)
    #cinit()
    #pass

def restart_level():
    restartLevel()

def next_frame(accelerate, brake, left, right, turn, supervolt, timestep, time):
    # int accelerate, int brake, int left, int right, int turn, int supervolt
    return nextFrameKuski(accelerate, brake, left, right, turn, supervolt, timestep, time)
    #return dict( **nextFrameKuski() )
    #main()
    #body_location_x = nextFrameKuski().body
    #return body_location_x
    #print( "body_location_x % s" % body_location_x )
    #body_location_x = nextFrameKuski()
    #print( "body_location_x % s" % body_location_x )
    #body_location_x = nextFrameKuski()
    #print( "body_location_x % s" % body_location_x )

def save_replay(rec_filename, lev_filename):
    brec_filename = bytes( rec_filename, 'utf-8' )
    blev_filename = bytes( lev_filename, 'utf-8' )
    saved = saveReplay(brec_filename, blev_filename)
    print("replay %s saved: %s" % (rec_filename, saved) )
    return saved
