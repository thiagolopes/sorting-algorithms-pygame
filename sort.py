import sys
import math
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


class BubbleSort:
    def __init__(self, elements):
        self.elements = elements
        self.steps_left = len(self.elements)

    def step(self):
        swapped = False

        for i in range(1, self.steps_left):
            if elements[i - 1] > elements[i]:
                elements[i - 1], elements[i] = elements[i], elements[i - 1]
                swapped = True
        self.steps_left -= 1

        return swapped

    def reset(self):
        self.steps_left = len(self.elements)
        shuffle(self.elements)


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
    width = math.ceil(top) if top > 1 else 1
    height = math.ceil(left) if left > 1 else 1

    for i, element in enumerate(elements):
        pos = pygame.Rect(i * top, offset - (element * left), width, height * element)
        pygame.draw.rect(screen, "red", pos)


TOTAL = 420
elements = list(range(1, TOTAL))
grid_pos = Vector2(screen.get_width(), screen.get_height())
bubble = BubbleSort(elements)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                quit()
            if event.key == pygame.K_RETURN:
                bubble.reset()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        success = bubble.step()
        if success:
            play_beep()

    # Draw
    screen.fill("black")
    draw_grid(bubble.elements, grid_pos)

    pygame.display.flip()
    dt = clock.tick(144) / 1000

pygame.quit()
