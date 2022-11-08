#!/usr/bin/env python3
"""
Module for creating and generating sine wave based sound. 
Includes Frequency modulation and Amplitude modulation.

Authors: Ryan Au and Younes Boubekaur
"""

from typing import Callable, Iterable, SupportsIndex, Tuple, Union
import time
import os
import pickle
import simpleaudio as sa
import math
import functools
import array

LIMIT_MAX_VOLUME = True


def change_volume(percentage):
    vol = abs(int(percentage))
    vol = min(100, max(0, vol))
    try:
        command = f'sudo amixer cset numid=1 {vol}%'
        os.system(command)
    except OSError:
        return


@functools.lru_cache()
def sin(x: float) -> float:
    return math.sin(x)


def cos(x: float) -> float:
    return math.cos(x)


def clip(x: float, bot: float, top: float, nomax=False) -> float:
    # Ensures that x is no lesser than bot and no greater than top
    return max(x, bot) if nomax else max(min(x, top), bot)


def _amp_to_db(p0: float, p1: float) -> float:
    """Converts the relative amplitude to decibels.
    p0 is the reference amplitude, p1 is the next value
    """
    return 20 * math.log10(p1/p0)


def db_to_amp(db: float, ref_amp: float) -> float:
    """Converts decibels to a next amplitude.
    ref_amp is the reference amplitude to start at.
    """
    return 10**(db/20) * ref_amp


HIGHEST_VOLUME = 100  # Custom value. Could be 100, 1.0, 50, doesn't matter.
_LOWEST_AMPLITUDE = 0.0001  # must be non-zero, but low
_HIGHEST_AMPLITUDE = 1.0  # acts as a scalar factor, should be 0 to 1
_HIGHEST_DECIBEL = _amp_to_db(_LOWEST_AMPLITUDE, _HIGHEST_AMPLITUDE)


def vol_to_amp(vol: float) -> float:
    """Converts a volume level to an amplitude scalar factor.
    Input would range from 0 to HIGHEST_VOLUME (default:100).
    Output ranges from 0 to 1

    Furthermore, the output behaves similarly to the volume on a listening device,
    when setting the volume. If the max is 100% level, then 50% feels half as loud.

    Note: 0 is not absolutely silent, it is just extremely quiet, and is audible.
    Note 2: this volume is dependent on the system volume.
        Loudness = program volume * system volume (if in percentage)
    """
    db = clip(vol, 0, HIGHEST_VOLUME, nomax=LIMIT_MAX_VOLUME) * \
        _HIGHEST_DECIBEL / HIGHEST_VOLUME
    amp = db_to_amp(db, _LOWEST_AMPLITUDE)
    return clip(amp, 0, _HIGHEST_AMPLITUDE, nomax=LIMIT_MAX_VOLUME)


def _parse_freq(value: Union[str, float]):
    if type(value) == str:
        if value in NOTES:
            return NOTES[value]
    if type(value) == int or type(value) == float:
        return float(value)
    return 0


def gen_wave(duration=1, volume=40, pitch: Union[str, float] = "A4", mod_f: Union[str, float] = 0, mod_k=0, amp_f: Union[str, float] = 0, amp_ka=0, amp_ac=1, cutoff=0.01, fs=8000):
    # Process frequencies, factors
    pitch = _parse_freq(pitch)
    mod_f = _parse_freq(mod_f)
    amp_f = _parse_freq(amp_f)

    # Convert volume using decibel underneath
    volume = vol_to_amp(volume)

    return _gen_wave(duration, volume, pitch, mod_f, mod_k, amp_f, amp_ka, amp_ac, cutoff, fs)


def _gen_wave(duration, volume, pitch, mod_f, mod_k, amp_f, amp_ka, amp_ac, cutoff, fs):
    n = int(duration * fs)
    t = [0 for i in range(n)]  # comprehension faster than append
    maximum = -2**31
    for i in range(0, n):
        x = i / fs
        # create carrier wave (float division is faster)
        c = (2 * math.pi * x * pitch)
        # frequncy modulate
        m = mod_k * sin(2 * math.pi * mod_f * x)
        y = cos(c + m)
        # amplitude modulate
        a = amp_ac * (1 + (amp_ka * sin(2 * math.pi * amp_f * x)))
        y = y * a
        if maximum < (_abs := abs(y)):
            maximum = _abs
        # no append (which is marginally slow)
        t[i] = y

    # do volume and cutoff calculation
    max16 = (2**15 - 1)
    cutoff = min(int(n/2), int(fs * cutoff))
    k = (1/3) * (1/math.log(2))
    for i in range(len(t)):
        # apply volume
        y = t[i] * volume

        # # apply cutoff
        if 0 <= i and i < cutoff:
            y *= math.log(i / cutoff * 7 + 1) * k
        elif n - cutoff <= i and i < n:
            j = n - i - 1
            y *= math.log(j / cutoff * 7 + 1) * k

        # pull down value to int16
        t[i] = clip(int(y * max16 / maximum), -32768, 32767, nomax=False)

    return array.array('h', t)


class Sound:
    def __init__(self, duration=1, volume=40, pitch="A4", mod_f=0, mod_k=0, amp_f=0, amp_ka=0, amp_ac=1, cutoff=0.01, fs=8000):
        self.player = None
        self._fs = fs  # needs a default value
        self.set_volume(volume)
        self.set_pitch(pitch)
        self.set_cutoff(cutoff)
        self.set_frequency_modulation(mod_f, mod_k)
        self.set_amplitude_modulation(amp_f, amp_ka, amp_ac)
        self.update_duration(duration, fs)

    def reset(self):
        """Fully resets the underlying audio of this Sound object.
        The sound must be stopped, or this will give unexpected behavior

        see Sound.reset_audio
        """
        return self.reset_audio()

    def reset_audio(self):
        """Fully resets the underlying audio data of this Sound object.
        The sound must be stopped, or this will give unexpected behavior
        """
        return self.update_audio(True)

    def append(self, other, spacing=0):
        """Takes the underlying audio data of another Sound object, other, and appends all of it
        to the underlying audio data of this Sound object.

        This does not alter any base attributes of this Sound object, and a 'reset' will undo these appends

        see Sound.append_sound
        """
        return self.append_sound(other, spacing)

    def append_sound(self, other, spacing=0):
        """Takes the underlying audio data of another Sound object, other, and appends all of it
        to the underlying audio data of this Sound object.

        This does not alter any base attributes of this Sound object, and a 'reset' will undo these appends
        """
        spacing = float(spacing)
        if spacing < 0:
            spacing = 0
        spacing_n = int(spacing * self._fs)

        if not self.is_playing():
            src = list(self.audio)
            dst = list(other.audio)
            spacer = [0 for i in range(spacing_n)]

            self.audio = array.array('h', src + spacer + dst)
        else:
            raise RuntimeError(
                "Cannot alter this sound object for repetition while playing this sound.")
        return self

    def repeat_sound(self, repeat_times=1, repeat_interval=0):
        """Alters the underlying audio data of this Sound object, such that the main sound will:
        - repeat equal to the value of repeat_times. It should be an integer value.
        - each time the original sound is repeated, there will be an interval of silence for 'repeat_interval' seconds.
            Expects either int or float value, of seconds for the interval. Default is 0 seconds.

        Explanation of Potential Usage:
        You may utilize the concept of BPM or "beats per minute" to help you with creating a tempo for your songs.
            If you want a sound repeated at 120bpm, that would be 2 times/sec, 0.5 seconds per sound played.
            If the original sound has duration 0.1 seconds, then the silence spacing would have to be 0.4 seconds, such that
            every sound starts playing every 0.5 seconds, matching 120bpm. The end of this repeated Sound object will be a 
            sound playing for 0.1 seconds, and then no silence spacing afterwards. This is desired behavior. You can then perform 
            a time.sleep(0.4) seconds before replaying this Sound object. BUT there is sometimes latency in "starting" a sound, 
            so the time sleep may need to be smaller, such as 0.35 seconds instead.
        """
        repeat_times = int(
            repeat_times)  # This can cause an error, which is desired
        if repeat_times < 1:
            repeat_times = 1

        repeat_interval = float(repeat_interval)
        if repeat_times < 0:
            repeat_times = 0

        fs = self._fs
        interval_n = int(fs * repeat_interval)

        if not self.is_playing():
            src = list(self.audio)
            src_n = len(src)
            end_n = src_n * repeat_times + (repeat_times - 1) * interval_n
            spacer = [0 for i in range(interval_n)]
            n = src_n + interval_n
            arr = []
            tmp = src + spacer
            for i in range(end_n):
                arr.append(tmp[i % n])
            self.audio = array.array('h', arr)
        else:
            raise RuntimeError(
                "Cannot alter this sound object for repetition while playing this sound.")
        return self

    def set_volume(self, volume):
        """Set the volume level of this sound.
        **Must use Sound.update_audio() to apply all changes**

        Enter a value from (0-100).
        """
        self.volume = volume
        return self

    def set_pitch(self, pitch: Union[str, float]):
        """Set the pitch or frequency of this sound.
        **Must use Sound.update_audio() to apply all changes**

        Enter a Hertz value within audible human range:
            minimum: 0
            maximum: ~7500
        """
        self.pitch = pitch
        return self

    def set_cutoff(self, cutoff):
        """Set the 'cutoff', the duration of the lead-in and fade-out for each sound wave.
        **Must use Sound.update_audio() to apply all changes**

        Enter a value in seconds, default: 0.01s

        Notable Effects:
        a value of 0s may lead to a 'pop/crackle' noise at the beginning and end of a sound.
        a value greater than or equal to the duration (also <1s) may lead to a pulse-like noise.
        a value greater than or equal to duration (also >1s) may lead to a 'coming and going' feeling.
        """
        self.cutoff = cutoff
        return self

    def set_frequency_modulation(self, mod_f: Union[str, float], mod_k):
        """Set the frequency(mod_f) and strength(mod_k) of Frequency Modulation.
        This modulation gives special effects to your sounds.
        **Must use Sound.update_audio() to apply all changes**

        Enter a value of frequency for mod_f
        Enter any positive integer for mod_k, a multiplication factor

        Notable Effects:
        mod_f=0, mod_k=0 - no modulation. This is default settings.
        mod_f=(1-10Hz), mod_k=(1-10) - mild modulation, sounding wavy, possibly crackly.
        mod_f='A4', mod_k=(1-50) - increasing levels of graininess observed, with increasing k factor.

        *Swapping mod_f and the pitch leads to new effects*
        mod_f=pitch, pitch=1, mod_k=1 - Sounds like a pipe organ, where mod_f becomes the new pitch setting.
        """
        self.mod_f = mod_f
        self.mod_k = mod_k
        return self

    def set_amplitude_modulation(self, amp_f: Union[str, float], amp_ka, amp_ac):
        """Set the frequency(amp_f), ka factor(amp_ka), and ac factor(amp_ac) of Amplitude Modulation.
        Effect is most similar to 'vibrato' altering the volume in a wobbling sense.
        **Must use Sound.update_audio() to apply all changes**

        amp_ka - wobbling factor. 0 is no wobble. >0 provides wobble.
        amp_ac - factor to change strength of wobble overall. See Notable Effects to understand this.

        Constraints:
        (resultant volume is % of the set volume of this Sound object)
        highest % of volume = amp_ac * (1 + amp_ka)
        lowest  % of volume = amp_ac * (1 - amp_ka)

        Notable Effects:
        amp_f=1Hz - wobbles 1 time per second
        amp_f=10Hz - wobbles 10 times per second

        amp_ka=0, amp_ac=1 - no wobble. The default settings.
        amp_ka=1, amp_ac=0.5 - alternates volume from 100% to 0% according to amp_f frequency.
        amp_ka=0.5, amp_ac=0.5 - alternates volume from 25% to 75% according to amp_f frequency.
        """
        self.amp_f = amp_f
        self.amp_ka = amp_ka
        self.amp_ac = amp_ac
        return self

    def update_duration(self, duration, fs: int = None):
        """Change the duration of this Sound (seconds).
        Cannot change duration of currently playing sounds.

        Only affects the next played sound.

        fs - Sample rate of sound wave. Default 8000 as lowest.
            Increased 'quality' with higher rate.
        """
        if fs is not None:
            self._fs = fs
        self._duration = duration

        if not self.is_playing():
            self.update_audio(True)
        else:
            raise RuntimeError(
                "Cannot change duration or sample rate while playing sound.")
        return self

    def update_audio(self, overwrite: bool = False):
        """Updates the audio to be played, based on current Sound attributes.

        - if overwrite=False and is_playing()==True, the playing audio will be updated
        - if overwrite=True and is_playing()==True, changes are present only in next play()
        """
        arr = gen_wave(self._duration, self.volume, self.pitch, self.mod_f,
                       self.mod_k, self.amp_f, self.amp_ka, self.amp_ac, self.cutoff, self._fs)
        if not overwrite:
            for i in range(min(len(self.audio), len(arr))):
                self.audio[i] = arr[i]
        else:
            self.audio = arr
        return self

    def alter_wave(self, func: Callable[[float, int], int]):
        """Apply a function to change the currently playing/prepared audio wave.

        func is of the format: func(x:float, y:int16) -> y:int16

        Given an xy-coordinate plane with the sound wave being centered on y=0,
        x is time in seconds, and y is amplitude in the range [-32768, 32767]


        """
        for i in range(len(self.audio)):
            # func(x:float, y:int16) -> y:int16
            self.audio[i] = clip(
                func(i/self._fs, self.audio[i]), -32768, 32767)
        return self

    def play(self):
        self.stop()
        self.player = sa.play_buffer(self.audio, 1, 2, self._fs)
        return self

    def stop(self):
        if self.is_playing():
            self.player.stop()
        return self

    def is_playing(self) -> bool:
        return self.player is not None and self.player.is_playing()

    def wait_done(self):
        if self.is_playing():
            self.player.wait_done()
        return self

    def __repr__(self):
        return f'Sound({self.pitch}, {self._duration}secs, {self.volume}%, {self.mod_f}mod)'


class Song(list):
    """Creates a special player object, that can play Sound objects
     quickly for long periods of time.

    Example Usage:

    s0 = Song.create_silence(seconds=0.5)
    s1 = Sound(duration=1, pitch="A4")
    s2 = Sound(duration=1, pitch="B4")

    song = Song([s1, s0, s2, s0])
    song *= 4 # repeat the song 4 times over

    song.compile() # Slow process, several seconds latency

    song.play() # Faster, ~0.7 seconds latency
    time.sleep(song.duration)
    song.stop()
    """
    MIN_VOLUME, MAX_VOLUME = -32_767, +32_767

    @staticmethod
    def create_silence(seconds=1):
        """A helper method to create a special Sound object 
        containing silence of given duration.
        """

        core = Sound(duration=1)
        core.audio = array.array(
            'h', [0 for i in range(int(core._fs*seconds))])

        return core

    def __init__(self, sounds=()):
        """Creates a Song with that plays silence for 1 second by default.

        Can be initialized with a list of existing sounds.
        This is optional.

        Sounds can be added with Song.append(sound)
        """
        super().__init__()
        self.core = self.create_silence(1)  # Default silence
        self.duration = self.core._duration

        self.extend(sounds)

    def append(self, obj):
        """Add a Sound object to this Song.

        Must be of type Sound."""
        if not isinstance(obj, Sound):
            raise ValueError("Cannot append objects that are not type Sound")
        super().append(obj)

    def extend(self, ls):
        """Adds all the Sounds of ls to this Song. 
        This can work for lists of Sounds, any iterable containing Sounds, 
        or another Song.

        Ignores non-Sound objects.
        """
        for el in ls:
            if isinstance(el, Sound):
                self.append(el)

    def compile(self):
        """Compiles the appended sounds to create the song.

        After this is set, then it can be played using Song.play()
        """
        sounds = [s for s in self if isinstance(s, Sound)]
        self.duration = sum([s._duration for s in sounds])
        self._samples = sum([len(s.audio) for s in sounds])
        self.core = Sound(duration=1)
        self.core.audio = array.array(
            'h', [0 for i in range(int(self._samples))])
        ptr = 0
        for s in sounds:
            n = len(s.audio)
            for i in range(n):
                self.core.audio[min(ptr, self._samples-1)] = s.audio[i]
                ptr += 1

    def play(self):
        """Starts the Song. It plays silence by default.

        Has latency on startup. Will stop by itself after the 
            Song duration has ended (defined in init)

        If Song.play_sound(s1) was done already, then Song.start()
            will play the given sound s1 to begin with.
        """
        self.core.play()

    def stop(self):
        """Stops the Song. Keeps the last sound that was 
        used in Song.play_sound(s1)

        """
        self.core.stop()

    def is_playing(self):
        """Returns True if the Song is active.

        Active means that it would play sound, when the 
            Song.play_sound(s1) function is called.
        """
        return self.core.is_playing()

    def wait_done(self):
        """Uses a while-loop to keep checking until the song is done playing.

        Reliable, un-interruptible.
        """
        while self.is_playing():
            time.sleep(0.01)

    def sleep_done(self):
        """Uses a time.sleep to wait for the duration of the song.

        Interruptable, less reliable.
        """
        time.sleep(self.duration)

    def __del__(self):
        self.stop()


NOTES = {
    "C0": 16.35,
    "D0": 18.35,
    "E0": 20.60,
    "F0": 21.83,
    "G0": 24.50,
    "A0": 27.50,
    "B0": 30.87,
    "C1": 32.70,
    "D1": 36.71,
    "E1": 41.20,
    "F1": 43.65,
    "G1": 49.00,
    "A1": 55.00,
    "B1": 61.74,
    "C2": 65.41,
    "D2": 73.42,
    "E2": 82.41,
    "F2": 87.31,
    "G2": 98.00,
    "A2": 110.00,
    "B2": 123.47,
    "C3": 130.81,
    "D3": 146.83,
    "E3": 164.81,
    "F3": 174.61,
    "G3": 196.00,
    "A3": 220.00,
    "B3": 246.94,
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25,
    "D5": 587.33,
    "E5": 659.25,
    "F5": 698.46,
    "G5": 783.99,
    "A5": 880.00,
    "B5": 987.77,
    "C6": 1046.50,
    "D6": 1174.66,
    "E6": 1318.51,
    "F6": 1396.91,
    "G6": 1567.98,
    "A6": 1760.00,
    "B6": 1975.53,
    "C7": 2093.00,
    "D7": 2349.32,
    "E7": 2637.02,
    "F7": 2793.83,
    "G7": 3135.96,
    "A7": 3520.00,
    "B7": 3951.07,
    "C8": 4186.01,
    "D8": 4698.63,
    "E8": 5274.04,
    "F8": 5587.65,
    "G8": 6271.93,
    "A8": 7040.00,
    "B8": 7902.13,
    "C#0": 17.32,
    "Db0": 17.32,
    "D#0": 19.45,
    "Eb0": 19.45,
    "F#0": 23.12,
    "Gb0": 23.12,
    "G#0": 25.96,
    "Ab0": 25.96,
    "A#0": 29.14,
    "Bb0": 29.14,
    "C#1": 34.65,
    "Db1": 34.65,
    "D#1": 38.89,
    "Eb1": 38.89,
    "F#1": 46.25,
    "Gb1": 46.25,
    "G#1": 51.91,
    "Ab1": 51.91,
    "A#1": 58.27,
    "Bb1": 58.27,
    "C#2": 69.30,
    "Db2": 69.30,
    "D#2": 77.78,
    "Eb2": 77.78,
    "F#2": 92.50,
    "Gb2": 92.50,
    "G#2": 103.83,
    "Ab2": 103.83,
    "A#2": 116.54,
    "Bb2": 116.54,
    "C#3": 138.59,
    "Db3": 138.59,
    "D#3": 155.56,
    "Eb3": 155.56,
    "F#3": 185.00,
    "Gb3": 185.00,
    "G#3": 207.65,
    "Ab3": 207.65,
    "A#3": 233.08,
    "Bb3": 233.08,
    "C#4": 277.18,
    "Db4": 277.18,
    "D#4": 311.13,
    "Eb4": 311.13,
    "F#4": 369.99,
    "Gb4": 369.99,
    "G#4": 415.30,
    "Ab4": 415.30,
    "A#4": 466.16,
    "Bb4": 466.16,
    "C#5": 554.37,
    "Db5": 554.37,
    "D#5": 622.25,
    "Eb5": 622.25,
    "F#5": 739.99,
    "Gb5": 739.99,
    "G#5": 830.61,
    "Ab5": 830.61,
    "A#5": 932.33,
    "Bb5": 932.33,
    "C#6": 1108.73,
    "Db6": 1108.73,
    "D#6": 1244.51,
    "Eb6": 1244.51,
    "F#6": 1479.98,
    "Gb6": 1479.98,
    "G#6": 1661.22,
    "Ab6": 1661.22,
    "A#6": 1864.66,
    "Bb6": 1864.66,
    "C#7": 2217.46,
    "Db7": 2217.46,
    "D#7": 2489.02,
    "Eb7": 2489.02,
    "F#7": 2959.96,
    "Gb7": 2959.96,
    "G#7": 3322.44,
    "Ab7": 3322.44,
    "A#7": 3729.31,
    "Bb7": 3729.31,
    "C#8": 4434.92,
    "Db8": 4434.92,
    "D#8": 4978.03,
    "Eb8": 4978.03,
    "F#8": 5919.91,
    "Gb8": 5919.91,
    "G#8": 6644.88,
    "Ab8": 6644.88,
    "A#8": 7458.62,
    "Bb8": 7458.62,
}

_note_order = {
    'b': 'x', '': 'y', '#': 'z',
    'C': '0', 'D': '1', 'E': '2', 'F': '3', 'G': '4', 'A': '5', 'B': '6', }

NOTE_NAMES = sorted(list(
    NOTES.keys()), key=lambda x: x[-1] + _note_order[x[0]] + _note_order[x[1:-1]])


def preload_all_pitches(duration=1, volume=40, mod_f=0, mod_k=0, amp_f=0, amp_ka=0, amp_ac=1, cutoff=0.01, fs=8000):
    return {key: Sound(pitch=key, duration=duration, volume=volume, mod_f=mod_f, mod_k=mod_k, amp_f=amp_f, amp_ka=amp_ka, amp_ac=amp_ac, cutoff=cutoff, fs=fs) for key in NOTE_NAMES}


def save_all_pitches_file(sounds, filename="sounds"):
    path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), str(filename) + ".pickle")
    with open(path, "rb") as f:
        pickle.dump(sounds, f)


def load_all_pitches_file(filename="sounds"):
    path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), str(filename) + ".pickle")
    with open(path, "rb") as f:
        return pickle.load(f)


SAMPLE_RATES = [
    8000,
    11025,
    16000,
    22050,
    24000,
    32000,
    44100,
    48000,
    88200,
    96000,
    192000,
]


def _test1():
    a = Sound()  # Basic 1sec A4 Note at 20% vol
    a.play()
    input("Press any button to continue to new pitch...")
    b = Sound(pitch="C4")  # Now a C4 note
    b.play()
    input("Press any button to continue to reuse and play two notes...")
    a.play()
    b.play()
    input("Press any button to continue to play strange notes...")
    c = Sound(mod_f=10, mod_k=10)
    c.play()
    input("Press any button to continue to play a different basic sound...")
    # swap mod_f and pitch for new effect
    d = Sound(mod_f="A4", mod_k=1, pitch=1)
    d.play()
    input("Press any button to continue to stop...")


def _test_vol1():
    Sound(volume=.001).play().wait_done()
    while (ans := input("Enter volume (100-0): ")) and ans.count('.') <= 1 and ans.replace('.', '').isnumeric():
        Sound(volume=float(ans)).play().wait_done()


if __name__ == '__main__':
    _test_vol1()
