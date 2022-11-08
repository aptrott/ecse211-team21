"""sample_sound

This file shows you how you can use the sound helper code.

Author: Ryan Au
Date: Feb 2nd, 2022
"""

### This file should be moved to the project/ folder if you want to run it ###

from utils.sound import Sound
import time


"""We first generate a Sound object.

This is a 'slow process' so do it at the beginning of your file.

duration - in seconds.
volume   - 0.0 to 100.0 but be careful when going to 100%
pitch    - Either a note name such as 'A3', 'C#5', or 'Gb4'
           OR a frequency number in Hertz: 440, 200, 1, 150.5
"""
tone1 = Sound(duration=1.0, volume=80, pitch="A3")

tone2 = Sound(duration=2.0, volume=80, pitch="A4")

"""Now we can use the sound after creation."""


tone1.play() # Starts the tone1 playing on the speaker
tone1.wait_done() # Will wait until tone1 is done playing

""" Play two notes simultaneously! """
tone1.play() # Starts tone1 playing on the speaker
tone2.play() # Starts tone2 playing
tone2.wait_done() # Will wait until tone2 is done playing (2 seconds)

""" Restart the same note! May cause static when done quickly. """
tone1.play() # Starts tone1 playing on the speaker
tone1.play() # Stops tone1, then restarts it very quickly
tone1.play() # Does it again
tone1.wait_done() # Will wait until tone1 is done playing or not making noise

""" Restart the same note! Use time.sleep to avoid making static. """
tone1.play() # Starts tone1 playing on the speaker
time.sleep(0.5)
tone1.play() # Stops tone1, then restarts it
time.sleep(0.5)
tone1.play() # Does it again
tone1.wait_done() # Will wait until tone1 is done playing or not making noise


""" And here's a shortcut for playing and waiting... """
tone2.play().wait_done()

########################
### Different Sounds ###
########################
"""Frequency Modulation. Uses another frequency to change your sound wave.

mod_f - frequency of modulation
mod_k - strength of modulation
"""

# We can make an alien-like tone by setting mod_f=10 and mod_k=10
alien_sound = Sound(duration=2.0, volume=80, pitch="A4", mod_f=10, mod_k=10)
alien_sound.play()
alien_sound.wait_done()

# We can make a pipe organ-like tone by setting pitch=1, mod_k=1 and
# instead use mod_f to have the desired pitch of our tone
organ_tone = Sound(duration=2.0, volume=80, pitch=1, mod_f="A4", mod_k=1)
organ_tone.play()
organ_tone.wait_done()

"""We don't know what different modulations exist, so experiment for yourself!"""

#########################
### Volume alteration ###
#########################

tone3 = Sound(duration=5.0, volume=80, pitch="A4")
tone3.play()
time.sleep(1) # wait

tone3.set_volume(60) # quieter
tone3.update_audio()
time.sleep(1)

tone3.set_volume(40) # and quieter
tone3.update_audio()
time.sleep(1)

tone3.set_volume(80) # and loud again!
tone3.update_audio()
