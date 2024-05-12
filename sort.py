import array
import math
import random
import sys

import pygame

HEIGHT = 1280
WIDTH = 780
TAU = math.pi * 2
START = 0
TOTAL = 128
BAR_SIZE = 24
ELEMENTS = list(range(START, TOTAL))


class Bar:
    init_pos = 0
    border_size = 2

    def __init__(self, size, screen):
        self.size = size
        self.margin = 8
        self.screen = screen
        self.pos = pygame.Rect(self.init_pos, self.init_pos, screen.get_width(), size)
        self.text = pygame.font.SysFont("Monospace", 18, False)
        self.textb = pygame.font.SysFont("Monospace", 18, True)
        self.border = pygame.Rect(
            self.pos.x + self.border_size,
            self.pos.y + self.border_size,
            self.pos.width - (self.border_size * 2),
            self.pos.height - (self.border_size * 2),
        )
        self.init_pos = pygame.Vector2(self.margin, self.border_size)
        self.surface = pygame.Surface(pygame.Vector2(self.pos.w, self.pos.h))

    def draw_next_text(self, text, pos, color, bold=False):
        if bold:
            text_render = self.textb.render
        else:
            text_render = self.text.render

        ts = text_render(text, True, color)
        self.surface.blit(ts, pos)
        pos += pygame.Vector2(ts.get_width() + self.margin, 0)

    def draw(self, algorithm, meta, ms, muted):
        # TODO avoid redraw
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

    def __init__(self, padding, screen):
        self.padding = padding
        self.pos = pygame.Vector2(0, padding)
        self.size = pygame.Vector2(screen.get_width(), screen.get_height() - padding)
        self.screen = screen
        self.surface = pygame.Surface(self.size)
        self.last_dirty_indexes = []

    def draw_column(self, index, total, element, color):
        top = self.size.x // total
        left = self.size.y / total

        width = max(top - 1, 1)
        height = math.ceil(left) * element

        pos = pygame.Rect(index * top, self.size.y - (element * left), width, height)
        self.surface.fill(color, pos)

    def draw_dirties(self, elements, dirties):
        for index in self.last_dirty_indexes:
            self.draw_column(index, len(elements), elements[index], "white")

        for d in dirties:
            self.draw_column(d, len(elements), len(elements), "black")
            self.draw_column(d, len(elements), elements[d], "red")
        self.last_dirty_indexes = dirties.copy()

    def draw_full(self, elements, color):
        self.surface.fill("black")
        for column, element in enumerate(elements):
            self.draw_column(column, len(elements), element, color)

    def draw(self, elements, dirty_index, finished):
        if dirty_index:
            self.draw_dirties(elements, dirty_index)
        else:
            color = "white"
            if finished:
                color = "green"
            self.draw_full(elements, color)
        self.screen.blit(self.surface, self.pos)


class BubbleSort:
    def __init__(self, elements):
        self.elements = elements
        self.finished = True
        self.step_count = 0
        self.steps_left = len(self.elements) - 1
        self.index_step = 0
        self.dirty_index = []

    def __str__(self):
        return "Bubble Sort"

    def __repr__(self):
        return f"Finished: {self.finished} | Step count: {self.step_count} | Total: {len(self.elements)}"

    def step(self):
        self.dirty_index.clear()

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
        iplus = i + 1
        self.dirty_index.append(i)
        if elements[i] > elements[iplus]:
            elements[iplus], elements[i] = elements[i], elements[iplus]
            self.dirty_index.append(iplus)

        self.index_step += 1
        self.step_count += 1
        return True

    def finish(self):
        self.dirty_index = []
        self.finished = True


class Interactions:
    def __init__(self):
        self.actions = ["quit", "shuffle", "pause", "next_step", "restart", "randomize", "mute"]

    def start_tick(self):
        for action in self.actions:
            setattr(self, action, False)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.quit = True
                if event.key == pygame.K_RETURN:
                    self.shuffle = True
                if event.key == pygame.K_SPACE:
                    self.pause = True
                if event.key == pygame.K_n:
                    self.next_step = True
                if event.key == pygame.K_BACKSPACE:
                    self.restart = True
                if event.key == pygame.K_r:
                    self.randomize = True
                if event.key == pygame.K_m:
                    self.mute = True


class Beeper:
    bits = 16  # int16
    sample_rate = 44100  # CD Quality
    freq = 440  # Hz
    volume = 0.05

    def __init__(self, size, duration=0.04):
        "Generate one sample per index"
        self.duration = duration
        self.size = size
        self.beeps = []
        pygame.mixer.init()
        pygame.mixer.pre_init(self.sample_rate, self.bits)

    def __getitem__(self, index):
        return self.beeps[index]

    def sin_wave(self, amp, freq, t):
        return int(amp * math.sin(TAU * freq * t))

    def wave(self, freq, duration, speaker=None):
        amp = 2 ** (self.bits - 1) - 1  # amplitude of 32767 bits
        sample_range = range(int(duration * self.sample_rate))

        buffer = array.array("i", (0 for _ in sample_range))
        for sample in sample_range:
            time_len = sample / self.sample_rate
            sine = self.sin_wave(amp, freq, time_len)
            buffer[sample] = int(sine * self.volume)
        return buffer

    def n_note(self, i):
        seed = math.pi
        return self.freq + (i * seed)

    def generate(self):
        for i in range(self.size):
            freq = self.n_note(i)
            buffer = self.wave(freq, self.duration)
            sound = pygame.mixer.Sound(buffer=buffer)
            self.beeps.append(sound)


class Engine:
    def __init__(self, height, width):
        self.mute = False
        self.play = False
        self.time = 0
        self.total_time = 0
        self._frame_time = 0

        pygame.init()
        self.screen = pygame.display.set_mode((height, width))

    @property
    def title(self):
        pygame.display.get_caption()

    @title.setter
    def title(self, title):
        pygame.display.set_caption(title)

    def toggle_play(self):
        self.play = not self.play

    def toggle_mute(self):
        self.mute = not self.mute

    def reset_timer(self):
        self.time = 0

    def start_tick(self):
        if self.play:
            self._frame_time = pygame.time.get_ticks()

    def end_tick(self):
        if self.play:
            self.time += pygame.time.get_ticks() - self._frame_time
            self._frame_time = 0

    def end_frame(self):
        pygame.display.flip()

    def shutdown(self):
        print(ELEMENTS)
        pygame.quit()
        sys.exit()


engine = Engine(HEIGHT, WIDTH)
engine.title = "Sorting Algorithms"
grid = Grid(BAR_SIZE, engine.screen)
bar = Bar(grid.padding, engine.screen)
interactions = Interactions()

beeper = Beeper(len(ELEMENTS))
beeper.generate()

algorithms = [BubbleSort]
algorithm = algorithms[0](ELEMENTS)

while True:
    interactions.start_tick()

    if interactions.quit:
        engine.shutdown()
    if interactions.shuffle:
        engine.play = False
        ELEMENTS = list(range(START, TOTAL))
        random.shuffle(ELEMENTS)
        algorithm = BubbleSort(ELEMENTS)
        algorithm.finished = False
        engine.reset_timer()
    if interactions.pause:
        engine.toggle_play()
    if interactions.next_step:
        algorithm.step()
    if interactions.restart:
        engine.play = False
        ELEMENTS = list(range(START, TOTAL))
        algorithm = BubbleSort(ELEMENTS)
        engine.reset_timer()
    if interactions.randomize:
        engine.play = False
        ELEMENTS = [random.randint(START, TOTAL) for _ in range(START, TOTAL)]
        algorithm = BubbleSort(ELEMENTS)
        algorithm.finished = False
        engine.reset_timer()
    if interactions.mute:
        engine.toggle_mute()

    if algorithm.finished:
        engine.play = False

    engine.start_tick()
    if engine.play:
        t = algorithm.step()
        if not engine.mute and t:
            beeper[algorithm.dirty_index[0]].play()

    # Draw
    grid.draw(algorithm.elements, algorithm.dirty_index, algorithm.finished)
    bar.draw(str(algorithm), repr(algorithm), engine.time, engine.mute)

    engine.end_tick()
    engine.end_frame()

engine.shutdown()
