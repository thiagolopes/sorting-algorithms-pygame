import sys
from random import shuffle

import pygame
from pygame import Vector2

pygame.init()
beep = pygame.mixer.Sound("beep.wav")
beep.set_volume(0.05)
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Bubble sort - <space> sort, <enter> reset")
clock = pygame.time.Clock()
running = True
dt = 0

def play_beep():
    pygame.mixer.Sound.play(beep)

def quit():
    pygame.quit()
    sys.exit()

def draw_grid(elements, pos):
    top = pos.x / len(elements)
    left = pos.y / len(elements)
    offset = pos.y

    # 1px min
    height = left if left > 1 else 1
    width = top if top > 1 else 1

    for i, element in enumerate(elements):
        pos = pygame.Rect(i * top, offset - (element * left), width, height * element)
        pygame.draw.rect(screen, "red", pos)

TOTAL = 420
elements = list(range(1, TOTAL))
step = len(elements)
# shuffle(elements)
grid_pos = Vector2(screen.get_width(), screen.get_height())

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

    screen.fill("black")

    # draw grid
    draw_grid(elements, grid_pos)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        quit()
    if keys[pygame.K_SPACE]:
        for i in range(1, step):
            if elements[i - 1] > elements[i]:
                elements[i - 1], elements[i] = elements[i], elements[i - 1]
                play_beep()
        step -= 1
    if keys[pygame.K_RETURN]:
        step = len(elements)
        shuffle(elements)

    pygame.display.flip()
    dt = clock.tick(144) / 1000

pygame.quit()
