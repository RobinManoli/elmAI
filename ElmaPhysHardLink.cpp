// created by ribot

#include <iostream>
#include <cmath>

#include "Engine.h"
#include "Level.h"
#include "Levobj.h"
#include "KuskiState.h"
#include "InputKeys.h"
#include "ElmaPhysRibotAlg.h"

// init engine globally, so that cython doesn't have to declare phys::Engine
phys::Level lev;
phys::Levobj flower; // first flower
phys::Engine *engine; // use a pointer because otherwise the class is initialized with default level

double * observation(const phys::KuskiState *kuskiState){
    static double arr[13];
    arr[0] = kuskiState->body.location.x;
    arr[1] = kuskiState->body.location.y;
    arr[2] = kuskiState->leftWheel.location.x;
    arr[3] = kuskiState->leftWheel.location.y;
    arr[4] = kuskiState->rightWheel.location.x;
    arr[5] = kuskiState->rightWheel.location.y;
    arr[6] = kuskiState->headLocation.y;
    arr[7] = kuskiState->headLocation.y;
    arr[8] = kuskiState->body.rotation;
    arr[9] = kuskiState->direction;
    arr[10] = kuskiState->isDead;
    arr[11] = kuskiState->finishedTime;

    // body distance from first flower
    double x_distance = flower.location.x - kuskiState->body.location.x;
    double y_distance = flower.location.y - kuskiState->body.location.y;
    arr[12] = sqrt( x_distance * x_distance + y_distance * y_distance );
    return arr;
}

//phys::Engine cinit(std::string path = "C:\\Users\\Sara\\Desktop\\robin\\elma\\lev\\1dg54.lev")
phys::KuskiState cinit(std::string pathfilename)
//double * cinit(std::string pathfilename)
{
    std::cout << "hi\n" << "loading lev: " << pathfilename << "\n";
    // Engine params currentLev(NULL), levelData(NULL), screenScrollDelay(0.5), turnAnimDelay(0.35), isSinglePlayer(1), flagTagMode(0)
    //lev.loadFromPath("C:\\Users\\Sara\\Desktop\\robin\\elma\\lev\\0lp31.lev");
    lev.loadFromPath(pathfilename);
    for (int i = 0; i < lev.objects.size(); i++) {
        if ( lev.objects[i].objType == 1 ){
            flower = lev.objects[i];
            //std::cout << "found flower: " << flower.location.x;
            break;
        }
    }
    //lev.loadFromPath("C:\\Users\\Sara\\Desktop\\robin\\elma\\lev\\qwquu002.lev"); // erroneous levhash - replays for this level become corrupt
    //inputKeys.InputKeys();

    // 16
    //std::cout <<"size of struct Point2d: " << sizeof(struct phys::Point2D) << "\n";

    // 72
    //std::cout <<"size of struct BodyPart: " << sizeof(struct phys::BodyPart) << "\n"; 

    //phys::Engine engine;
    engine = new phys::Engine();
    std::cout << "initPhysicsEngine:\n";
    engine->initPhysicsEngine(lev); //initPhysicsEngine(phys::Level& lev); // also resets players
    //return engine;
    //std::cout << "\nLeave cinit: " << engine->getPlayer(0).body.location.x << ' ' << engine->getPlayer(0).body.location.y; // working
    return engine->getPlayer(0);
    //return observation( &engine->getPlayer(0) ); // working, but not faster
}

void restartLevel(){
    engine->initPhysicsEngine(lev);    
}


// cinit must intialize engine before running nextFrameKuski
//nextFrameKuski( inputKeys, timestep, time)
phys::KuskiState nextFrameKuski(int accelerate, int brake, int left, int right, int turn, int supervolt, double timestep, double time)
//double * nextFrameKuski(int accelerate, int brake, int left, int right, int turn, int supervolt, double timestep, double time)
{
    // todo: send inputKeysPlayer1 from calling program
    std::vector<phys::InputKeys*> inputKeysArray;
    phys::InputKeys inputKeysPlayer1 = phys::InputKeys(); // player1 of 2, probably local players
    inputKeysPlayer1.accelerateKeyState = accelerate;
    inputKeysPlayer1.brakeKeyState = brake;
    inputKeysPlayer1.rotateLeftKeyState = left;
    inputKeysPlayer1.rotateRightKeyState = right;
    inputKeysPlayer1.turnKeyState = turn;
    if (supervolt == 1){
        // although this input works, supervolt didn't always happen -- but seems to work now, especially when no longer using mouse input
        inputKeysPlayer1.rotateLeftKeyState = 1;
        inputKeysPlayer1.rotateRightKeyState = 1;
    }
    inputKeysArray.push_back(&inputKeysPlayer1);
    /*
    if (left || right || supervolt)
    {
        std::cout << "c-> acc: " << inputKeysPlayer1.accelerateKeyState << " brake: " << inputKeysPlayer1.brakeKeyState  << " left: ";
        std::cout << inputKeysPlayer1.rotateLeftKeyState << " right: " << inputKeysPlayer1.rotateRightKeyState << " turn: " << inputKeysPlayer1.turnKeyState << '\n';
    }
    */

    //std::cout << "\nBefore engine.nextFrame: " << engine.getPlayer(0).body.location.x << ' ' << engine.getPlayer(0).body.location.y; // working
    //return engine.nextFrameKuski(inputKeysArray, 0.01, 0.01); // working, so no need to use ribot made function engine.nextFrameKuski
    // int nextFrame(const std::vector<InputKeys*> p1keys, double timeStep, double time);
    if (engine->getPlayer(0).isDead || engine->getPlayer(0).finishedTime) engine->initPhysicsEngine(lev); // revive AFTER having sent kuskiState.isDead or .finishedTime
    engine->nextFrame(inputKeysArray, timestep, time);
    //std::cout << "\nAfter engine.nextFrame: " << engine.getPlayer(0).body.location.x << ' ' << engine.getPlayer(0).body.location.y; // working
    //if (engine.getPlayer(0).isDead) engine.resetPlayers(); // working but doesn't reset player to correct position
    //if (engine.getPlayer(0).isDead) engine.setPlayMode(1, 0); // same as above
    return engine->getPlayer(0); // working
    //return observation( &engine->getPlayer(0) ); // working but not faster
}

// todo: receive filenames or have temp file names
bool saveReplay(std::string recFilenmae, std::string levFilename){
    //void saveReplay(const std::string& recFileName, const std::string& levFileName){
    //void phys::Engine::saveReplay(const std::string& recFileName, const std::string& levFileName)
    engine->saveReplay(recFilenmae, levFilename); // working
    //std::cout << "exiting saveReplay";
    return true; // isn't returned if saveReplay crashes internally
}

int main(int argc, char** argv)
{
    //double * arr1;
    //double * arr2 ;

    cinit("C:\\Users\\Sara\\Desktop\\robin\\elma\\lev\\ribotAI0.lev");
    //arr1 = cinit("C:\\Users\\Sara\\Desktop\\robin\\elma\\lev\\ribotAI0.lev");
    //std::cout << arr1[0] << " " << arr1[1] << "\n";

    /*for (int i = 0; i < 5; i++) {
        //std::cout << engine.nextFrameKuski(inputKeysArray, 0.01, 0.01); // int nextFrame(const std::vector<InputKeys*> p1keys, double timeStep, double time);
        arr2 = nextFrameKuski(1, 0, 0, 0, 0, 0, 0.00546, 0.01);
        std::cout << arr2[0] << " " << arr2[1] << "\n";
    }*/
    int episodes = 1000;
    if (argc > 1)
    {
        episodes = atoi(argv[1]);
    }
    //ribotAlgorithm(engine, lev, flower, episodes); // does not work in python project

    //saveReplay();
    std::cout << "\n\nProgram completed.";
    return 0;
}


/*
// benchmark code
#include <chrono> 
using namespace std::chrono; 
const int FRAMES = 800; // 80 frames 10 seconds
int (int argc, char** argv){
    int frame = 0;
    int actions[FRAMES];

    int episodes = 1000;
    if (argc > 1)
    {
        episodes = atoi(argv[1]); // exec.exe 2000 // to go 2000 runs
    }

    double timestep = 0.00546;  // fast play, 80 fps, fastest possible calculated physics according to jon
    double episodetime = 0;
    double elmatotaltime = 0;
 

    std::vector<phys::InputKeys*> inputKeysArray;
    phys::InputKeys inputKeysPlayer1 = phys::InputKeys(); // player1 of 2, probably local players
    inputKeysPlayer1.accelerateKeyState = 1; // gas all the time is smart
    inputKeysArray.push_back(&inputKeysPlayer1);

    phys::Level lev;
    // on this level death is assured soon, so there will be multiple episodes
    lev.loadFromPath("C:\\Users\\Sara\\Desktop\\robin\\elma\\lev\\0lp31.lev");
    phys::Engine engine;

    std::cout << "Engine and lev loaded...\n";

    auto start = high_resolution_clock::now(); 
    for(int episode = 0; episode < episodes; episode++){
        engine.initPhysicsEngine(lev); // restart lev
        //std::cout << "Episode: " << episode + 1 << "\n";
        for(frame = 0; frame < FRAMES; frame++){
            //std::cout << "Frame: " << frame + 1 << "\n";
            engine.nextFrame(inputKeysArray, timestep, episodetime);
            if (engine.getPlayer(0).isDead || engine.getPlayer(0).finishedTime) break;
            episodetime += timestep;
            elmatotaltime += timestep * 2.2893772893772893772893772893773;
        }
     }
    auto stop = high_resolution_clock::now(); 

    auto duration = duration_cast<milliseconds>(stop - start);
    double seconds = duration.count() / 1000.0;
    std::cout << "Time: " << seconds << ", Elma time: " << elmatotaltime << ", Times fster than realtime: " << elmatotaltime/seconds << "X\n";
    return 0;
}
*/