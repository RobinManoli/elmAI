# distutils: language = c++

from celmaphys cimport nextFrameKuski
from celmaphys cimport main

print("elmaphys.pyx loaded...")

def run():
    #main()
    body_location_x = nextFrameKuski().body
    print( "body_location_x % s" % body_location_x )
    body_location_x = nextFrameKuski()
    print( "body_location_x % s" % body_location_x )
    body_location_x = nextFrameKuski()
    print( "body_location_x % s" % body_location_x )
