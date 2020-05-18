# https://cython.readthedocs.io/en/latest/index.html
# https://cython.readthedocs.io/en/latest/src/userguide/wrapping_CPlusPlus.html

# to compile this:
# first open vscode by entering "Developer Command Prompt for VS 2019" and then type "code ."
# python cython-setup.py build_ext --inplace


# make sure cython code is working, visible when importing phys
print("Hello World")

# make sure c code is working, visible when importing phys
cdef extern from "math.h":
    double sin(double x)
print(sin(19))

# working with elma code
# compilation errors -- probably needs to be compiled and handled in c++ before continuing here

cdef struct Level
cdef struct LevelData

cdef extern from "smibu_phys/Engine.cpp":
    pass

cdef extern from "smibu_phys/Engine.h" namespace "phys":
    cdef cppclass Engine:
        Engine() except +
        # phys::Engine::Engine() : currentLev(NULL), levelData(NULL), screenScrollDelay(0.5), turnAnimDelay(0.35), isSinglePlayer(1), flagTagMode(0)
        Engine(Level* currentLev, LevelData* levelData, double screenScrollDelay, double turnAnimDelay, int isSinglePlayer, int flagTagMode) except +
