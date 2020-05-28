#cython: language_level=3

# https://cython.readthedocs.io/en/latest/index.html
# https://cython.readthedocs.io/en/latest/src/userguide/wrapping_CPlusPlus.html


# make sure cython code is working, visible when importing phys
print("elmaphys.pxd loaded...")

# make sure c code is working, visible when importing phys
cdef extern from "math.h":
    double sin(double x)
print(sin(19))

#cdef struct Level # defined below
#cdef struct LevelData # defined below

# cdefs because otherwise unresolved symbols
from libcpp.string cimport string
from libcpp cimport bool
from libc.stdio cimport *

# https://stackoverflow.com/a/15373598
#cdef extern from "stdio.h":
#    FILE *fdopen(int, const char *)

cdef extern from "smibu_phys/Replay.cpp":
    pass
cdef extern from "smibu_phys/Replay.h" namespace "phys":
    pass
    #cdef cppclass Replay:
    #    void setPlayerCount(int count)

cdef extern from "smibu_phys/LevelData.cpp":
    pass
cdef extern from "smibu_phys/LevelData.h" namespace "phys":
    pass
    #cdef cppclass LevelData:
    #    LevelData() except +

cdef extern from "smibu_phys/Polygon.cpp":
    pass
cdef extern from "smibu_phys/Polygon.h" namespace "phys":
    pass
    #cdef cppclass Polygon:
    #    Polygon() except + # Polygon::~Polygon(void)

cdef extern from "smibu_phys/Errors.cpp":
    pass
cdef extern from "smibu_phys/Errors.h" namespace "phys":
    pass
    #int InternalError(string& error)

cdef extern from "smibu_phys/PlayerData.cpp":
    pass
cdef extern from "smibu_phys/PlayerData.h" namespace "phys":
    pass
    #void doSomeWeirdStuffOn_directionAndThrottling()
    #void initializeRec()
    #void setFlagTag(int isFlagTag)
    # void savePlayer(const std::string &recFileName, FILE *Str, int levId, int isMultiPlayerMode, const std::string& levFileName);
    #void savePlayer(string &recFileName, FILE* Str, int levId, int isMultiPlayerMode, string& levFileName)
    #void saveEvent(double a2, char a3, double a4, short a5)
    # void saveFrame(KuskiState *arg0, double a3, int player1HasFlag, int losingFlag);
    #void saveFrame(KuskiState* arg0, double a3, int player1HasFlag, int losingFlag)
    #cdef cppclass PlayerData:
    #    PlayerData() except +

cdef extern from "smibu_phys/Level.cpp":
    pass
cdef extern from "smibu_phys/Level.h" namespace "phys":
    pass
    #cdef cppclass Level:
    #    Level() except +
    #void sortObjects()
    #void invertObjectYCoords2()
    #void loadFromPath(string& levFileName, bool loadHeadersOnly)
    
cdef extern from "smibu_phys/Levobj.cpp":
    pass
cdef extern from "smibu_phys/Levobj.h" namespace "phys":
    pass
    # void levobjctor(FILE *levFile, signed int levVersion);
    #void levobjctor(FILE* levFile, signed int levVersion)
    #double objectHash()
    
cdef extern from "smibu_phys/top10data.cpp":
    pass
cdef extern from "smibu_phys/top10data.h" namespace "phys":
    pass
    # int readTop10(size_t Count, FILE *File)
    #int readTop10(size_t Count, FILE* File)
    
cdef extern from "smibu_phys/Picture.cpp":
    pass
cdef extern from "smibu_phys/Picture.h" namespace "phys":
    pass
    #double pictureHash()
    # void picturector(FILE *File);
    #void picturector(FILE* File)

cdef extern from "smibu_phys/math2d.cpp":
    pass
cdef extern from "smibu_phys/math2d.h" namespace "phys":
    pass
    #double SquareRoot(double a1)



# actually to be used in python
cdef extern from "smibu_phys/Engine.cpp":
    pass
cdef extern from "smibu_phys/Engine.h" namespace "phys":
    pass
    #cdef cppclass Engine:
    #    Engine(Level* currentLev, LevelData* levelData, double screenScrollDelay, double turnAnimDelay, int isSinglePlayer, int flagTagMode) except +
    #    # phys::Engine::Engine() : currentLev(NULL), levelData(NULL), screenScrollDelay(0.5), turnAnimDelay(0.35), isSinglePlayer(1), flagTagMode(0)
    #    #Engine(Level* currentLev, LevelData* levelData, double screenScrollDelay, double turnAnimDelay, int isSinglePlayer, int flagTagMode) except +
    #    Engine() except +
    #    Engine(Level*, LevelData*, double, int, int) except +
    #    #Engine(Level*, LevelData*, double, int, int)
    #    #Level* currentLev, LevelData* levelData, double screenScrollDelay, turnAnimDelay, int isSinglePlayer, flagTagMode


cdef extern from "smibu_phys/Point2D.cpp":
    pass
cdef extern from "smibu_phys/Point2D.h" namespace "phys":
    #pass
    cdef struct Point2D:
        double x, y
    #cdef cppclass Point2D:
    #    Point2D() except +
    #double length()
    #Point2D ortho()
    #Point2D normalize()

cdef extern from "smibu_phys/BodyPart.cpp":
    pass
cdef extern from "smibu_phys/BodyPart.h" namespace "phys":
    cdef struct BodyPart:
        double rotation
        Point2D location

cdef extern from "smibu_phys/KuskiState.cpp":
    pass
cdef extern from "smibu_phys/KuskiState.h" namespace "phys":
    #cdef struct BikeAnimationState:
    #    int lastDirection
    #    double turnBeginTime
    #    double lastScrollBeginTime
    #    double scrollProgress
    #    double turnAnimProgress
    #cdef struct BikeState:
    #    double asdunk7
    #    BikeAnimationState turndata
    #    BikeAnimationState screenLocation
    cdef struct KuskiState:
        BodyPart body
        BodyPart leftWheel
        BodyPart rightWheel
        Point2D headLocation
        int direction
        int finishedTime # 0 until level finished, also 0 if died -- not in observation space
        bool isDead # not in observation space
        # for ai
        int gravityScrollDirection
        int gravityDir
        Point2D headCenterLocation
        int numTakenApples
        char isThrottling
        double lastRotationTime
        int changeDirPressedLast
        #BikeState bikeState # contains animation, not sure if necessary
        # unnamed
        Point2D pad4
        int pad
        int asd4
        int asd5
        int asdunk5
        double padz1
        double padz2
        double asd6
        double asd7
        double asd3
        double asd8
        double asdunk1
        double asdunk2
    #cdef cppclass KuskiState:
    #    pass
    #    KuskiState() except +



cdef extern from "smibu_phys/ElmaPhys.cpp":
    #Engine init()
    # phys::KuskiState nextFrameKuski(int accelerate, int brake, int left, int right, int turn, int supervolt)
    KuskiState cinit(string pathfilename)
    void restartLevel()
    KuskiState nextFrameKuski(int accelerate, int brake, int left, int right, int turn, int supervolt, double timestep, double time)
    bool saveReplay(string recFilenmae, string levFilename)
    #int main()
