"""
Module for providing access to a single, simple, GUI that can easily display data.
It also allows the creation of buttons and sliders for adjusting starting parameters.

Author: Ryan Au
"""

from collections import deque
from queue import Empty, Queue
from tkinter import Scale, ttk, StringVar, TclError, Button as TkButton

import tkinter as tk
from tkinter.constants import HORIZONTAL
import threading
from uuid import UUID, SafeUUID
import time


WINDOW: tk.Tk = None
LABELS = {}
_EXIT_FLAG = True

class Command:
    WAIT_DONE = 0.001
    def __init__(self, func, args):
        self.func = func
        self.args = args
        self.result_given = False
        self.error_given = False
        self.result = None
        # self.cid = UUID(is_safe=SafeUUID.safe)
    def execute(self):
        """To be executed in the main thread"""
        try:
            self.result = self.func(*(self.args))
            self.result_given = True
        except BaseException as e:
            self.result = e
            self.error_given = True
    def wait_done(self):
        """To be executed in the worker process"""
        while not self.result_given and not self.error_given:
            time.sleep(Command.WAIT_DONE)
        if self.result_given:
            return self.result
        if self.error_given:
            raise self.result

class CommandQueue:
    def __init__(self):
        self.queue = Queue()
    def put_func(self, func, args):
        c = Command(func, args)
        self.queue.put(c)
        return c
    def execute_all(self):
        size = self.queue.qsize()
        try:
            while size > 0:
                command:Command = self.queue.get(block=False)
                command.execute()
                size -= 1
        except Empty:
            pass

_COMMANDQUEUE = CommandQueue()

def remote(func, *args):
    c = _COMMANDQUEUE.put_func(func, args)
    return c.wait_done()

def remote_capable(func):
    def inner(*args):
        if threading.current_thread().name == 'MainThread':
            return func(*args)
        else:
            return remote(func, *args)
    return inner

def _on_closing():
    """Private method: cleans up internal values on window destruction"""
    global WINDOW, _EXIT_FLAG, LABELS
    _EXIT_FLAG = True
    WINDOW.destroy()
    WINDOW = None
    LABELS = {}


def start():
    """Open the telemetry window"""
    global WINDOW, _EXIT_FLAG
    _EXIT_FLAG = False
    if WINDOW is None:
        WINDOW = tk.Tk()
    WINDOW.protocol("WM_DELETE_WINDOW", _on_closing)
    update()


def isopen():
    """Determines if the telemtry window has been opened or closed"""
    return not _EXIT_FLAG


def resize(width=100, height=100):
    """Resize telemtry to a set width and height in pixels"""
    if WINDOW is None:
        return
    WINDOW.geometry("{}x{}".format(width, height))


def stop():
    """Closes telemtry window"""
    global WINDOW
    if WINDOW is not None:
        WINDOW.quit()
        WINDOW = None


class _Updater:
    UPDATE_DELAY = 0.01
    def __init__(self, func, obj, *args):
        self.thread = threading.Thread(target=self._listener, args=[obj]+list(args), daemon=True)
        self.func = func
        self.event = threading.Event()
        self.event.set()
    def start(self):
        self.thread.start()
    def stop(self):
        self.event.clear()
    def _listener(self, *args):
        while self.event.is_set():
            try:
                (self.func)(*args)
                time.sleep(_Updater.UPDATE_DELAY)
            except BaseException as e:
                print(e)
                break

class _Updatable:
    def set_updater(self, func, obj, *args):
        if hasattr(self, '_updater') and self._updater is not None:
            if not isinstance(self._updater, _Updater):
                return
            self._updater.stop()
        self._updater = _Updater(func, obj, *args)
        self._updater.start()
    def stop_updater(self):
        if hasattr(self, '_updater') and self._updater is not None and isinstance(self._updater, _Updater):
            self._updater.stop()

class _Slider(_Updatable):
    def __init__(self, lower, upper, value, func=None):
        self.s = Scale(WINDOW, from_=lower, to=upper, orient=HORIZONTAL)
        self.s.set(value)
        self.s.pack()

        if func is not None:
            self.set_updater(func, self)

    @remote_capable
    def get_value(self):
        return self.s.get()
    
    def __del__(self):
        self.stop_updater()


def create_slider(lower, upper=None, value=None, func=None):
    """Adds a slider to the telemetry window AND returns the slider object added
    
    create_slider(50) creates: 0<---25--->50
    create_slider(25, 50) creates: 25<---37--->50
    create_slider(-100, 100, 50) creates: -100<---50--->100
    """
    if upper is None:
        upper = lower
        lower = 0

    if value is None:
        value = lower

    if WINDOW is None or not isopen():
        return
    
    return _Slider(lower, upper, value, func)


class _Button(_Updatable):
    def __init__(self, name, func=None):
        self.b = TkButton(WINDOW, text=name)
        self.b.bind("<ButtonPress>", self._on_press)
        self.b.bind("<ButtonRelease>", self._on_release)
        self._is_pressed = False
        self.b.pack()

        if func is not None:
            self.set_updater(func, self)

    def _on_press(self, *args):
        self._is_pressed = True

    def _on_release(self, *args):
        self._is_pressed = False

    @remote_capable
    def is_pressed(self):
        return self._is_pressed

    def __del__(self):
        self.stop_updater()

def create_button(name, func=None):
    """Adds a button to the telemetry window AND returns the button object added"""
    if WINDOW is None or not isopen():
        return

    return _Button(name, func)

@remote_capable
def label(key, data, showkey=False):
    """Adds/Sets data by a key to the telemetry window"""
    add(key, data, showkey)


def add(key, data, showkey=False):
    """Adds/Sets data by a key to the telemetry window"""
    if WINDOW is None or not isopen():
        return
    key = str(key)
    data = str(data)
    if showkey:
        data = "{} : {}".format(key, data)
    if key in LABELS:
        LABELS[key][1].set(data)
    else:
        var = StringVar()
        var.set(data)
        LABELS[key] = (tk.Label(WINDOW, textvariable=var), var)
        LABELS[key][0].pack()


def update(retries=1):
    """Updates display with latest telemetry values"""
    global WINDOW
    if WINDOW is not None:
        try:
            ### Execute CommandQueue Operations ###
            _COMMANDQUEUE.execute_all()
            ### Execute CommandQueue Operations ###
            for i in range(retries):
                WINDOW.update()
        except TclError as e:
            err = str(e)
            if err == 'can\'t invoke "update" command: application has been destroyed':
                WINDOW = None


def clear():
    """Destroy and remove all LABELS of telemetry"""
    global LABELS
    for i, widget in LABELS.items():
        try:
            widget[0].destroy()
        except TclError:
            pass
    LABELS = {}


def mainloop():
    """Starts a while loop that calls update for you! 
    Usage of telemetry.update not needed when using this"""
    if WINDOW is not None and isopen():
        try:
            WINDOW.mainloop()
        except KeyboardInterrupt:
            return


if __name__ == '__main__':
    import time
    start()
    resize(500, 200)
    i = 0
    add("word", "heyo this is the start")
    update()
    while True:
        time.sleep(1)

        ### Test clearing window despite still updating ###
        if i == 10:
            clear()
            if not isopen():
                start()

        # Adding data
        add("color", "red", True)
        i = i + 2 if i < 40 else 0

        print(i, isopen())
        add("counter", "*"*i)

        # Must update window to see changes
        update()
