# distutils: language = c++

from celmaphys cimport nextFrameKuski
#from celmaphys cimport cinit

print("elmaphys.pyx loaded...")

def init():
    pass
    # makes pygame crash: parachute segmentation fault
    #cinit(bytes( levpathfilename, 'utf-8' ))
    #cinit()

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
