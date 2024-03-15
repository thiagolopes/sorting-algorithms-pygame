import math
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


def quit():
    pygame.quit()
    sys.exit()


class BubbleSort:
    def __init__(self, elements):
        self.elements = elements
        self.steps_left = len(self.elements)
        self.index_step = 1
        self.dirties = []
        self.finished = True

    def step(self):
        if self.steps_left == 0:
            self.finish()
            return False

        if self.index_step == self.steps_left:
            self.index_step = 1
            self.steps_left -= 1
            return False

        i = self.index_step
        swapped = False
        if elements[i - 1] > elements[i]:
            elements[i - 1], elements[i] = elements[i], elements[i - 1]
            swapped = True
            self.dirties = [i, i - 1]

        self.index_step += 1
        return swapped

    def finish(self):
        self.dirties = []
        self.finished = True

    def reset(self):
        self.steps_left = len(self.elements)
        self.index_step = 1
        self.finished = False
        self.dirties = []
        shuffle(self.elements)


def play_beep():
    pygame.mixer.Sound.play(beep)


class Grid:
    def __init__(self, pos, size, screen):
        self.pos = pos
        self.size = size
        self.surface = pygame.Surface(self.size)
        self.screen = screen

    def draw(self, elements, indexes_dirty, finished):
        self.surface.fill("black")

        top = self.size.x / len(elements)
        left = self.size.y / len(elements)
        offset = self.size.y

        width = math.floor(top) - 1 if top - 1 > 1 else 1
        height = math.ceil(left) if left > 1 else 1

        for i, element in enumerate(elements):
            pos = pygame.Rect(i * top, offset - (element * left), width, height * element)
            if finished:
                self.surface.fill("green", pos)
                continue
            if i in indexes_dirty:
                self.surface.fill("blue", pos)
            else:
                self.surface.fill("white", pos)

        self.screen.blit(self.surface, self.pos)


TOTAL = 128
elements = list(range(1, TOTAL))
bubble = BubbleSort(elements)
play = False

grid_pos = Vector2(5, 5)
grid_size = Vector2(screen.get_width() - 10, screen.get_height() - 10)
grid = Grid(grid_pos, grid_size, screen)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                quit()
            if event.key == pygame.K_RETURN:
                bubble.reset()
                play = False
            if event.key == pygame.K_SPACE:
                play = not play

    if play:
        t = bubble.step()
        if t:
            play_beep()
    if bubble.finished:
        play = False

    # Draw
    screen.fill("black")
    grid.draw(bubble.elements, bubble.dirties, bubble.finished)

    pygame.display.flip()
    # dt = clock.tick(144) / 1000

pygame.quit()
