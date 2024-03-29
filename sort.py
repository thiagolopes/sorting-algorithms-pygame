import array
import math
import random
import sys

import pygame

W = 780
H = 1280
RUNNING = True
START = 0
TOTAL = 128
ELEMENTS = list(range(START, TOTAL))
TAU = math.pi * 2
MUTED = False


def shutdown():
    print(ELEMENTS)
    pygame.quit()
    sys.exit()


class Bar:
    def __init__(self, pos, screen):
        self.pos = pos
        self.screen = screen
        self.surface = pygame.Surface(pygame.Vector2(pos.w, pos.h))
        self.text = pygame.font.SysFont("Monospace", 18, False)
        self.textb = pygame.font.SysFont("Monospace", 18, True)

        border_size = 2
        self.border = pygame.Rect(pos.x + border_size, pos.y + border_size,
                                  pos.width - (border_size * 2), pos.height - (border_size * 2))
        self.margin = 8
        self.init_pos = pygame.Vector2(self.margin, border_size)

    def draw_next_text(self, text, pos, color, bold=False):
        if bold:
            text_render = self.textb.render
        else:
            text_render = self.text.render

        ts = text_render(text, True, color)
        self.surface.blit(ts, pos)
        pos += pygame.Vector2(ts.get_width() + self.margin, 0)

    def draw(self, algorithm, meta, ms, muted):
        self.surface.fill("darkorchid", self.pos)
        self.surface.fill("darkmagenta", self.border)

        pos = self.init_pos.copy()
        self.draw_next_text(algorithm, pos, "white", True)
        self.draw_next_text("- " + meta, pos, "white")
        self.draw_next_text(f"| {ms} (ms)", pos, "white")
        if muted:
            self.draw_next_text("|[MUTED]", pos, "white")

        self.screen.blit(self.surface, self.pos)


class Grid:
    margin = 1

    def __init__(self, pos, size, screen):
        self.pos = pos
        self.size = size
        self.screen = screen
        self.surface = pygame.Surface(self.size)
        self.last_dirty_indexes = []

    def draw_index(self, index, total, element, color):
        top = self.size.x // total
        left = self.size.y / total

        width = max(top - 1, 1)
        height = math.ceil(left) * element

        pos = pygame.Rect(index * top, self.size.y - (element * left), width, height)
        self.surface.fill(color, pos)

    def draw_clear_last_indexes(self, elements):
        for ld in self.last_dirty_indexes:
            self.draw_index(ld, len(elements), elements[ld], "white")

    def draw(self, elements, dirty_index, finished):
        self.draw_clear_last_indexes(elements)

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


class BubbleSort:
    def __init__(self, elements):
        self.elements = elements
        self.finished = True
        self.start_bubble()

    def start_bubble(self):
        self.step_count = 0
        self.steps_left = len(self.elements) - 1
        self.index_step = 0
        self.dirty_index = []

    def __str__(self):
        return "Bubble Sort"

    def __repr__(self):
        return f"Finished: {self.finished} | Step count: {self.step_count} | Total: {len(self.elements)}"

    def step(self):
        self.dirty_index = []

        if self.finished:
            return False

        if self.steps_left == 0:
            self.finish()
            return False

        if self.index_step == self.steps_left:
            self.index_step = 0
            self.steps_left -= 1
            return False

        elements = self.elements
        i = self.index_step
        il = i + 1
        self.dirty_index.append(i)
        if elements[i] > elements[il]:
            elements[il], elements[i] = elements[i], elements[il]
            self.dirty_index.append(il)

        self.index_step += 1
        self.step_count += 1
        return True

    def finish(self):
        self.dirty_index = []
        self.finished = True

    def shuffle(self):
        self.start_bubble()
        self.finished = False
        random.shuffle(self.elements)


pygame.init()

screen = pygame.display.set_mode((H, W))
pygame.mixer.init()
pygame.display.set_caption("Sorting Algorithms")

bubble = BubbleSort(ELEMENTS)
play = False

bar_size = 24
grid_gap = 10
grid_pos = pygame.Vector2(0, bar_size)
grid_size = pygame.Vector2(screen.get_width(), screen.get_height() - bar_size)
grid = Grid(grid_pos, grid_size, screen)

bar_pos = pygame.Rect(0, 0, screen.get_width(), bar_size)
bar = Bar(bar_pos, screen)

time = 0


class Beeper:
    bits = 16  # int16
    sample_rate = 44100  # CD Quality
    freq = 440  # Hz

    def __init__(self, size, duration=0.04):
        "Generate one sample per index"
        self.duration = duration
        self.size = size
        self.beeps = []
        pygame.mixer.pre_init(self.sample_rate, self.bits)

    def sin_wave(self, amp, freq, time):
        return int(amp * math.sin(TAU * freq * time))

    def wave(self, freq, duration, speaker=None):
        amp = 2 ** (self.bits - 1) - 1  # amplitude of 32767 bits
        sample_range = range(int(duration * self.sample_rate))

        buffer = array.array("i", (0 for _ in sample_range))
        for sample in sample_range:
            time = sample / self.sample_rate
            sine = self.sin_wave(amp, freq, time)
            buffer[sample] = sine
        return buffer

    def n_note(self, i):
        return self.freq * 2**(i/12)

    def generate(self):
        for i in range(self.size):
            freq = self.n_note(i)
            buffer = self.wave(freq, self.duration)
            sound = pygame.mixer.Sound(buffer=buffer)
            self.beeps.append(sound)


beeper = Beeper(len(ELEMENTS))
beeper.generate()

while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            shutdown()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                shutdown()
            if event.key == pygame.K_RETURN:
                play = False
                bubble.shuffle()
                time = 0
            if event.key == pygame.K_SPACE:
                play = not play
            if event.key == pygame.K_n:
                bubble.step()
            if event.key == pygame.K_BACKSPACE:
                play = False
                ELEMENTS = list(range(START, TOTAL))
                bubble = BubbleSort(ELEMENTS)
                time = 0
            if event.key == pygame.K_r:
                play = False
                ELEMENTS = [random.randint(START, TOTAL) for _ in range(START, TOTAL)]
                bubble = BubbleSort(ELEMENTS)
                bubble.finished = False
                time = 0
            if event.key == pygame.K_m:
                MUTED = not MUTED

    if bubble.finished:
        play = False

    start_time = None
    if play:
        start_time = pygame.time.get_ticks()
        t = bubble.step()
        if t and not MUTED:
            for d in bubble.dirty_index:
                # module = ELEMENTS[d]
                beeper.beeps[d].play()

    # Draw
    grid.draw(bubble.elements, bubble.dirty_index, bubble.finished)
    bar.draw(str(bubble), repr(bubble), time, MUTED)

    if start_time is not None:
        time += pygame.time.get_ticks() - start_time

    pygame.display.flip()

shutdown()
