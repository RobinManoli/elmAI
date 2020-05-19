import pygame

def draw(game):
    game.screen.fill(game.colors.skyblue)

    game.gui.label(game, 'Welcome to AI', 10, 10)

    game.pygame.display.flip()


def drawlev(game, lev):
    pass