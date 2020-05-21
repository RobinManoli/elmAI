# distutils: language = c++

from celmaphys cimport nextFrameKuski
from celmaphys cimport main

print("elmaphys.pyx loaded...")

def next_frame():
    return nextFrameKuski()
    #return dict( **nextFrameKuski() )
    #main()
    #body_location_x = nextFrameKuski().body
    #return body_location_x
    #print( "body_location_x % s" % body_location_x )
    #body_location_x = nextFrameKuski()
    #print( "body_location_x % s" % body_location_x )
    #body_location_x = nextFrameKuski()
    #print( "body_location_x % s" % body_location_x )
