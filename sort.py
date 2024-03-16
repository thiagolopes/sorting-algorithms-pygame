import math
import random
import sys

import pygame

RUNNING = True
TOTAL = 128
START = 1


def quit():
    pygame.quit()
    sys.exit()


def play_beep():
    pygame.mixer.Sound.play(beep)


class Bar:
    def __init__(self, pos, screen):
        self.pos = pos
        self.screen = screen
        self.surface = pygame.Surface(pygame.Vector2(pos.w, pos.h))
        self.text = pygame.font.SysFont("Monospace", 18)

        self.title_pos = pygame.Vector2(2, 0)

    def draw(self, algorithm, meta):
        self.surface.fill("dimgray", self.pos)
        title = self.text.render(algorithm, True, "green")
        self.surface.blit(title, self.title_pos)

        meta_text = self.text.render(meta, True, "white")
        meta_pos = pygame.Vector2(self.title_pos.x + title.get_width() + 4, self.title_pos.y)
        self.surface.blit(meta_text, meta_pos)

        self.screen.blit(self.surface, self.pos)


class BubbleSort:
    def __init__(self, elements):
        self.elements = elements
        self.steps_left = len(self.elements)
        self.index_step = START
        self.dirty_index = []
        self.finished = True

        self.step_count = 0

    def __str__(self):
        return "Bubble Sort"

    def __repr__(self):
        return f"< Finished: {self.finished} | Step count: {self.step_count} | Time Lapse: TODO >"

    def step(self):
        self.dirty_index = []

        if self.finished:
            return False

        if self.steps_left == 0:
            self.finish()
            return False

        if self.index_step == self.steps_left:
            self.index_step = START
            self.steps_left -= 1
            return False

        i = self.index_step
        il = self.index_step - 1
        self.dirty_index.append(i)
        if elements[il] > elements[i]:
            elements[il], elements[i] = elements[i], elements[il]
            self.dirty_index.append(il)
        self.index_step += 1

        self.step_count += 1
        return True

    def finish(self):
        self.dirty = []
        self.finished = True

    def reset(self):
        self.steps_left = len(self.elements)
        self.index_step = START
        self.dirty_index = []
        self.finished = False
        self.step_count = 0
        random.shuffle(self.elements)


class Grid:
    margin = 1

    def __init__(self, pos, size, screen):
        self.pos = pos
        self.size = size
        self.screen = screen
        self.surface = pygame.Surface(self.size)
        self.last_dirty_indexes = []

    def draw_index(self, index, total, element, color):
        top = self.size.x / total
        left = self.size.y / total

        width = top - 1
        height = math.ceil(left) * element

        if width < 1:
            width = 1

        pos = pygame.Rect(index * top, self.size.y - (element * left), width, height)
        self.surface.fill(color, pos)

    def draw_clear_last_indexes(self):
        for ld in self.last_dirty_indexes:
            self.draw_index(ld, len(elements), elements[ld], "white")

    def draw(self, elements, dirty_index, finished):
        self.draw_clear_last_indexes()

        if dirty_index:
            for d in dirty_index:
                self.draw_index(d, len(elements), len(elements), "black")
                self.draw_index(d, len(elements), elements[d], "red")
            self.last_dirty_indexes = dirty_index.copy()
        else:
            self.surface.fill("black")
            for i, element in enumerate(elements):
                color = "white"
                if finished:
                    color = "green"
                self.draw_index(i, len(elements), element, color)

        self.screen.blit(self.surface, self.pos)


pygame.init()
beep = pygame.mixer.Sound("beep.wav")
beep.set_volume(0.05)
screen = pygame.display.set_mode((1280, 780))
pygame.display.set_caption("Bubble sort - <space> sort, <enter> reset")

TOTAL +=1
elements = list(range(START, TOTAL))
bubble = BubbleSort(elements)
play = False

bar_size = 24
grid_gap = 10
grid_pos = pygame.Vector2(0, bar_size)
grid_size = pygame.Vector2(screen.get_width(), screen.get_height() - bar_size)
grid = Grid(grid_pos, grid_size, screen)

bar_pos = pygame.Rect(0, 0, screen.get_width(), bar_size)
bar = Bar(bar_pos, screen)

while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                quit()
            if event.key == pygame.K_RETURN:
                play = False
                bubble.reset()
            if event.key == pygame.K_SPACE:
                play = not play
            if event.key == pygame.K_n:
                bubble.step()
            if event.key == pygame.K_BACKSPACE:
                play = False
                elements = list(range(START, TOTAL))
                bubble = BubbleSort(elements)
            if event.key == pygame.K_r:
                play = False
                elements = [random.randint(START, TOTAL - 1) for _ in range(START, TOTAL)]
                bubble = BubbleSort(elements)
                bubble.finished = False

    if play:
        t = bubble.step()
        if t:
            play_beep()
    if bubble.finished:
        play = False

    # Draw
    grid.draw(bubble.elements, bubble.dirty_index, bubble.finished)
    bar.draw(str(bubble), repr(bubble))

    pygame.display.flip()

pygame.quit()
