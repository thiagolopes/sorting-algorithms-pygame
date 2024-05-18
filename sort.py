import array
import math
import sys
from contextlib import nullcontext
from random import SystemRandom

import pygame

HEIGHT = 700
WIDTH = 700
TAU = math.pi * 2
TOTAL = 128
BAR_SIZE = 24

random = SystemRandom()


class Bar:
    border_size = 2
    font_size = 14

    def __init__(self, size, screen, pos=(0, 0)):
        self.size = size
        self.margin = 8
        self.screen = screen
        self.pos = pygame.Rect(pos[0], pos[1], screen.get_width(), size)
        self.text = pygame.font.SysFont("Monospace", self.font_size, False)
        self.textb = pygame.font.SysFont("Monospace", self.font_size, True)
        self.border = pygame.Rect(
            self.pos.x + self.border_size,
            self.pos.y + self.border_size,
            self.pos.width - (self.border_size * 2),
            self.pos.height - (self.border_size * 2),
        )
        self.surface = pygame.Surface(pygame.Vector2(self.pos.w, self.pos.h))

        # red is border
        # darkmagenta is inner
        # text_color is green

    def draw_next_text(self, text, pos, color, bold=False):
        if bold:
            text_render = self.textb.render
        else:
            text_render = self.text.render

        text_image = text_render(text, True, color)
        self.surface.blit(text_image, pos)
        pos += pygame.Vector2(text_image.get_width() + self.margin, 0)

    def draw(self, *texts):
        # TODO avoid redraw - BUG
        self.surface.fill("darkmagenta")

        accum = pygame.Vector2(self.margin, self.border_size)
        text = " - ".join(texts)
        self.draw_next_text(text, accum, "white", True)

        self.screen.blit(self.surface, self.pos)


# TODO maybe implement draw event - as observer
class Grid:
    margin = 1

    def __init__(self, screen, padding_top, padding_bottom=0):
        self.pos = pygame.Vector2(0, padding_top)
        self.size = pygame.Vector2(screen.get_width(), screen.get_height() - padding_top - padding_bottom)
        self.screen = screen
        self.surface = pygame.Surface(self.size)
        self.last_dirty_indexes = []
        # TODO move to theme
        # blue is background
        # white is idle
        # red is touched
        # green finished

    def draw_column(self, index, height, element, color):
        top = self.size.x / height
        left = self.size.y / height

        width = max(top - 1, 1)
        height = math.ceil(left) * element

        pos = pygame.Rect(index * top, self.size.y - (element * left), width, height)
        self.surface.fill(color, pos)

    def draw_dirties(self, elements, dirties):
        for index in self.last_dirty_indexes:
            self.draw_column(index, len(elements), elements[index], "white")

        for d in dirties:
            self.draw_column(d, len(elements), len(elements), "blue")
            self.draw_column(d, len(elements), elements[d], "red")
        self.last_dirty_indexes = dirties.copy()

    def draw_full(self, elements, color):
        self.surface.fill("blue")
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


class Event:
    QUIT = (pygame.QUIT, None)
    ESC = (pygame.KEYDOWN, pygame.K_ESCAPE)
    SHUFFLE = (pygame.KEYDOWN, pygame.K_RETURN)
    PAUSE = (pygame.KEYDOWN, pygame.K_SPACE)
    NEXT_STEP = (pygame.KEYDOWN, pygame.K_n)
    RESTART = (pygame.KEYDOWN, pygame.K_BACKSPACE)
    RANDOMIZE = (pygame.KEYDOWN, pygame.K_r)
    MUTE = (pygame.KEYDOWN, pygame.K_m)

    @classmethod
    def manual(cls):
        manual_itens = {"PAUSE": "space", "SHUFFLE": "enter", "RESTART": "backspace"}
        ignore = ["QUIT", "ESC"]
        attrs = (name for name in vars(cls).keys() if name.isupper() and name not in ignore)
        manual = []
        for attr in attrs:
            if attr in manual_itens.keys():
                manual.append("[{}]{}".format(manual_itens[attr], attr.lower()))
            else:
                manual.append("[{}]{}".format(attr[0].lower(), attr[1:].lower()))
        return " ".join(manual)

    def get(self):
        for event in pygame.event.get():
            if hasattr(event, "key"):
                key = event.key
            else:
                key = None
            yield (event.type, key)


class Beeper:
    bits = 16  # int16
    sample_rate = 44100  # CD Quality
    freq = 440  # Hz
    volume = 0.1

    def __init__(self, size, start=0, duration=0.04):
        "Generate one sample per index"
        self.duration = duration
        self.size = size
        self.beeps = []
        self.start = start
        pygame.mixer.init()
        pygame.mixer.pre_init(self.sample_rate, self.bits)

    def __getitem__(self, index):
        return self.beeps[index]

    def sin_wave(self, amp, freq, t):
        return int(amp * math.sin(TAU * freq * t))

    def wave(self, freq, duration, speaker=None):
        amp = 2 ** (self.bits - 1) - 1  # amplitude of 32767 bits
        sample_range = range(0, int(duration * self.sample_rate))

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
        for i in range(self.start, self.size):
            freq = self.n_note(i)
            buffer = self.wave(freq, self.duration)
            sound = pygame.mixer.Sound(buffer=buffer)
            self.beeps.append(sound)


class Timer:
    def __init__(self, title=None):
        self.title = (title or "").title()
        self.total = 0
        self._frame_time = 0

    def reset(self):
        self.total = 0

    def start_tick(self):
        self._frame_time = pygame.time.get_ticks()

    def end_tick(self):
        self.total += pygame.time.get_ticks() - self._frame_time
        self._frame_time = 0

    def __str__(self):
        if self.title:
            return f"[TIMER] {self.title} took {self.total}ms"
        return "{self.total}ms"

    def __enter__(self):
        self.start_tick()
        return self

    def __exit__(self, *exc):
        self.end_tick()


class Engine:
    def __init__(self, height, width, array_len, timer):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.mute = False
        self.play = False
        self.algorithms = []
        self.algorithm = None
        self.array_len = array_len
        self.timer = timer

    @property
    def title(self):
        pygame.display.get_caption()

    @title.setter
    def title(self, title):
        pygame.display.set_caption(title)

    @property
    def algorithm_class(self):
        if self.algorithm is not None:
            return self.algorithms[self.algorithms.index(self.algorithm.__class__)]
        if self.algorithms:
            return self.algorithms[0]
        assert True, "Do not reach here, add algorithm to work"

    @property
    def finished(self):
        return self.algorithm.finished

    def time_it(self, force):
        if self.play or force:
            return self.timer
        return nullcontext()

    def add_algorithm(self, algorithm):
        self.algorithms.append(algorithm)
        if not self.algorithm:
            self.reset()

    def reset(self, shuffle=False, randomize=False):
        elements = list(range(0, self.array_len))
        finished = True
        self.play = False

        if shuffle:
            random.shuffle(elements)
            finished = False
        elif randomize:
            elements = [random.randint(0, self.array_len) for _ in range(0, self.array_len)]
            finished = False

        algorithm = self.algorithm_class(elements)
        algorithm.finished = finished
        self.algorithm = algorithm
        self.timer.reset()

    def end_frame(self):
        pygame.display.update()

    def shutdown(self):
        print(self.algorithm.elements)
        pygame.quit()
        sys.exit(0)

    def run(self, force=False):
        t = False
        if self.play or force:
            t = self.algorithm.step()
            if self.algorithm.finished:
                self.play = False
        return t, self.algorithm


engine = Engine(HEIGHT, WIDTH, TOTAL, Timer())
engine.title = "Sorting Algorithms"
engine.add_algorithm(BubbleSort)

bar = Bar(BAR_SIZE, engine.screen)
bar_bottom = Bar(BAR_SIZE, engine.screen, (0, HEIGHT - BAR_SIZE))
grid = Grid(engine.screen, BAR_SIZE, BAR_SIZE)
event = Event()

beeper_time = Timer("generate beeps")
# beeper_time2 = Timer("generate beeps 2")
# beeper = Beeper(engine.array_len, engine.array_len - int(engine.array_len / 2))
# beeper = Beeper(engine.array_len - int(engine.array_len / 2))
# beeper.generate()

with beeper_time:
    beeper = Beeper(engine.array_len)
    beeper.generate()
print(str(beeper_time))

event_manual = event.manual()
bar_bottom.draw(event_manual)

while True:
    run_step = False
    for ev in event.get():
        match ev:
            case event.ESC | event.QUIT:
                engine.shutdown()
            case event.SHUFFLE:
                engine.reset(shuffle=True)
            case event.PAUSE:
                engine.play = not engine.play
            case event.RESTART:
                engine.reset()
            case event.RANDOMIZE:
                engine.reset(randomize=True)
            case event.MUTE:
                engine.mute = not engine.mute
            case event.NEXT_STEP:
                run_step = True

    # TODO split timer for algorithm and all draws
    with engine.time_it(force=run_step):
        t, algorithm = engine.run(force=run_step)
        if not engine.mute and t:
            beeper[algorithm.dirty_index[-1]].play()

        grid.draw(algorithm.elements, algorithm.dirty_index, engine.finished)
        bar.draw(str(algorithm), repr(algorithm), f"{engine.timer.total}ms", ("[MUTED]" if engine.mute else ""))
    engine.end_frame()

engine.shutdown()
