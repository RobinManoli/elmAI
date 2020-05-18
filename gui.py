import pygame

font = pygame.font.SysFont("monospace", 18)

def label(screen, text, x=0, y=0, color=(0,0,0)):
    "Text without box"
    text = str(text)
    output = font.render(text, 1, color)
    screen.blit(output, (x, y))

def message(text, x=None, y=None, line=0, color=None):
    "Text inside box"
    size = game.font.size(text)
    width = size[0] + 10
    height = size[1] + 10
    x = game.width/2 - size[0]/2 if x is None else x
    y = game.height/4 - size[1]/2  + line * (size[1] + 15)if y is None else y

    pygame.draw.rect(game.screen, color or game.draw.yellow, (x,y,width,height), 0) # draw container
    textcolor = game.draw.black if color != game.draw.black else game.draw.yellow
    label(text, x=x+5, y=y+5, color=textcolor)

def dialog(line, color=None):
    message(line['line'])
    
    if 'options' in line.keys():
        for i, option in enumerate(line['options']):
            message('%d - %s' % (i+1, option.text), line=i+1, color=game.draw.green)

def window(width=1, height=1, row=0, col=0, color=None):
    width = 240 * width
    height = 150 * height
    width = game.width - 10 if width > game.width - 10 else width
    thickness = 0 # outline pixel width or fill
    x = 5 + col * 262
    y = game.height - height - 5 - row * 162 * height
    pygame.draw.rect(game.screen, color or game.draw.yellow, (x,y,width,height), thickness) # draw container
