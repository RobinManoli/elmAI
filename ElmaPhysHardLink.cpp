// created by ribot

#include <iostream>
#include <cmath>

#include "Engine.h"
#include "Level.h"
#include "KuskiState.h"
#include "InputKeys.h"

// init engine globally, so that cython doesn't have to declare phys::Engine
phys::Level lev;

phys::Engine cinit()
{
    std::cout << "hi\n";
    // Engine params currentLev(NULL), levelData(NULL), screenScrollDelay(0.5), turnAnimDelay(0.35), isSinglePlayer(1), flagTagMode(0)
    //lev.loadFromPath("C:\\Users\\Sara\\Desktop\\robin\\elma\\lev\\0lp31.lev");
    //lev.loadFromPath("C:\\Users\\Sara\\Desktop\\robin\\elma\\lev\\1dg54.lev");
    lev.loadFromPath("C:\\Users\\Sara\\Desktop\\robin\\elma\\lev\\qwquu002.lev");
    //inputKeys.InputKeys();

    phys::Engine engine;
    std::cout << "initPhysicsEngine: ";
    engine.initPhysicsEngine(lev); //initPhysicsEngine(phys::Level& lev); // also resets players
    return engine;
}

phys::Engine engine = cinit();

//nextFrameKuski( inputKeys, timestep, time)
phys::KuskiState nextFrameKuski(int accelerate, int brake, int left, int right, int turn, int supervolt, double timestep, double time)
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
    if (engine.getPlayer(0).isDead || engine.getPlayer(0).finishedTime) engine.initPhysicsEngine(lev); // revive AFTER having sent kuskiState.isDead or .finishedTime
    engine.nextFrame(inputKeysArray, timestep, time);
    //std::cout << "\nAfter engine.nextFrame: " << engine.getPlayer(0).body.location.x << ' ' << engine.getPlayer(0).body.location.y; // working
    //if (engine.getPlayer(0).isDead) engine.resetPlayers(); // working but doesn't reset player to correct position
    //if (engine.getPlayer(0).isDead) engine.setPlayMode(1, 0); // same as above
    return engine.getPlayer(0);
}


int main()
{
    for (int i = 0; i < 5; i++) {
        //std::cout << engine.nextFrameKuski(inputKeysArray, 0.01, 0.01); // int nextFrame(const std::vector<InputKeys*> p1keys, double timeStep, double time);
        nextFrameKuski(1, 0, 0, 0, 0, 0, 0.01, 0.01);
    }

    std::cout << "\n\nProgram completed.";
    return 0;
}
