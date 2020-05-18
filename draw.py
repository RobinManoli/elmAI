import pygame
import colors, gui

def draw(screen):
    screen.fill(colors.skyblue)

    gui.label(screen, 'Welcome to AI', 10, 10)

    pygame.display.flip()
