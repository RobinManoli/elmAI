import draw, gui, colors

class Game:
    def __init__(self, pygame, size):
        # init pygame
        self.pygame = pygame
        self.size = self.width, self.height = size
        self.screen = pygame.display.set_mode(self.size)
        self.fullscreen = False
        # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
        self.font = pygame.font.SysFont("monospace", 18)

        self.gui = gui
        self.draw = draw
        self.colors = colors
        gui.game = self
        draw.game = self
