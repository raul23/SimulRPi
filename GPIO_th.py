import multiprocessing
import threading

import pygame
from pynput import keyboard


BCM = 1
HIGH = 1
LOW = 0
IN = 0
OUT = 1
PUD_UP = 1


class PIN:
    def __init__(self, type, pull_up_down=None, initial=None):
        self.type = type
        self.initial = initial
        self.pull_up_down = pull_up_down
        self.state = None
        self.key = None


class GPIO:
    def __init__(self):
        self.mode = None
        self.warnings = True
        self.pins = {}
        self.count = 0
        self.channel_input_key_map = {
            0: '0',
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: 'q',
            11: 'w',
            12: 'e',
            13: 'r',
            14: 't',
            15: 'y',
            16: 'u',
            17: 'i',
            18: 'o',
            19: 'p',
            20: 'a',
            21: 's',
            22: 'd',
            23: 'f',
            24: 'g',
            25: 'h',
            26: 'j',
            27: 'k'
        }
        self.input_key_channel_map = {v: k for k, v in
                                      self.channel_input_key_map.items()}
        self.ouput_channels = []
        self.display_th = threading.Thread(target=self.display_leds, args=())
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        # self.listener.start()
        pygame.init()
        pygame.key.set_repeat(100, 100)
        # self.keyboard_th = threading.Thread(target=self.check_keyboard, args=())
        # self.keyboard_th.start()
        self.keyboard_mp = None

    def start(self):
        multiprocessing.set_start_method('spawn')
        self.keyboard_mp = multiprocessing.Process(target=self.check_keyboard, args=(self.input_key_channel_map, self.pins))
        self.keyboard_mp.daemon = True
        self.keyboard_mp.start()

    @staticmethod
    def check_keyboard(input_key_channel_map, pins):
        # t = threading.currentThread()
        p = multiprocessing.current_process()
        while getattr(p, "do_run", True):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    channel = input_key_channel_map.get(chr(event.key))
                    if pins.get(channel):
                        pins[channel].state = False
                if event.type == pygame.KEYUP:
                    channel = input_key_channel_map.get(chr(event.key))
                    if pins.get(channel):
                        pins[channel].state = True
        # print("Stopping thread: check_keyboard()")
        print("Stopping process: check_keyboard()")

    def display_leds(self):
        print()
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            leds = ''
            # for channel in sorted(self.channel_output_state_map):
            for channel in self.ouput_channels:
                if self.pins.get(channel).state == HIGH:
                    led = "\033[31mo\033[0m"
                else:
                    led = 'o'
                leds += led + ' [{}]   '.format(channel)
            print('  {}\r'.format(leds), end="")
            # print(f'{leds}\r', end="")
            # print("{}".format(leds), end="\r")
        print("Stopping thread: display_leds()")

    def on_press(self, key):
        try:
            # print('alphanumeric key {0} pressed'.format(
            #      key.char))
            if str(key.char).isalnum():
                channel = self.input_key_channel_map.get(key.char)
                if self.pins.get(channel):
                    self.pins[channel].state = False
        except AttributeError:
            # print('special key {0} pressed'.format(
            #  key))
            pass

    def on_release(self, key):
        """
        print('{0} released'.format(
            key))
        """
        if key == keyboard.Key.esc:
            # Stop listener
            return False
        elif hasattr(key, 'char') and str(key.char).isalnum():
            channel = self.input_key_channel_map.get(key.char)
            if self.pins.get(channel):
                self.pins[channel].state = True


gpio = GPIO()


def cleanup():
    # gpio.display_th.do_run = False
    # gpio.display_th.join()
    # gpio.keyboard_th.do_run = False
    # gpio.keyboard_th.join()
    # gpio.listener.stop()
    gpio.keyboard_mp.do_run = False
    gpio.keyboard_mp.join()


def input(channel):
    return gpio.pins[channel].state


def output(channel, state):
    gpio.pins[channel].state = state
    if not gpio.display_th.isAlive():
        # gpio.display_th.start()
        pass


def setmode(mode):
    gpio.mode = mode


# mode = {IN, OUT}
def setup(channel, mode, pull_up_down=None, initial=None):
    gpio.pins[channel] = PIN(mode, pull_up_down=pull_up_down, initial=initial)
    if mode == IN:
        gpio.pins[channel].key = gpio.channel_input_key_map[channel]
        gpio.pins[channel].state = HIGH
    elif mode == OUT:
        gpio.ouput_channels.append(channel)
        gpio.pins[channel].state = LOW


def setwarnings(mode):
    gpio.warnings = mode
