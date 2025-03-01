# Project Foobear: A FNAF Fan Game on CircuitPython and Wio Terminal

`Documentation working in progress`

## The Story

You are a programmer intern working in a AI startup, which develops a humanoid robot, codenamed "Foobear".

And you are ordered by your boss to stay up one night on watch, because apperently the security guy is sick. You also hear something about the robot would roam around after midnight.

The boss said: "Relax, it's not a big deal. We are debugging that thing, nothing to worry about. Just don't let anyone or anything enter the control room."

As the clock hits 12:00 AM, you started to feel that this will be the longest night of your life - or maybe the shortest one.

### Rules

```
Floor plan

1----2----3
|    |    |
4----5----6--|
|    |       10
7----8---[9]-|
```

- 1: Demo Room (has a Bluetooth speaker)
- 2: Developers' Office
- 3: Cafeteria
- 4: Meeting room
- 5: Main hallway
- 6: Server room
- 7: Restroom
- 8: Entrance
- 9: Control room (where you are; the door can be locked)
- 10: Air Vent (has a electric bug zapper)

Note:

- You cannot leave the control room. Stay alive until 6:00 AM.
- The control has a door to room 8, connects to the air vent, and has a mesh window to room 6 (you may hear things moving in there if any).
- The lines in the floor plan indicate passage, in which the robot can move from room to room or the air vent.
- If the robot enters the control room, you die (game over).
- Use switch buttons to move focus to different rooms.
  - If SCAN shows up, press button 1 (leftmost top button) to scan the room. All rooms except the control room and air vent have scanners.
  - If a non-SCAN function shows, you can activate it (press button 3 or the rightmost top button).
  - You cannot activate a function if it's recharging (in cooldown).

<details>
  <summary>Additional hints</summary>

- The robot will get more aggresive to get to you with each hour passed. (Each hour takes ~50 seconds.)
- The Bluetooth speaker distracts the robot - for most of the time.
- The door keeps the robot out.
- The air vent zapper also keeps the robot out.
- All controllable devices have cooldown time and consumes power. If you use too much, it will overload the system and force reboot.
- The robot will be more aggresive during the power outtage.

</details>

<details>
  <summary>Even more hints!</summary>

- Enable `ANOMALY_ALWAYS_SHOWN` and/or `ANOMALY_ACTION_LOG` to `True` to cheat.
- Being blocked by the door or zapped in the air vent may cause the robot to "run away" to the farthest corner for a short while.
- You don't need to scan every room - just the room closest to the door and air vent. And listen to the sound clue.

</details>

## Run the Game

### Hardware

This game is design for a the Wio Terminal, which is basically a SAMD51 microcontroller with 4 MB flash, a built-in 320x240 ILI9341 TFT and several buttons.

You may try to migrate this game to other platforms with the display and buttons attached, but bear in mind the text and audio files require almost 4 MB storage.

### Installation

1. Connect the device to USB port and flash the [CircuitPython 9.x firmware](https://github.com/alankrantas/project-foobear-circuitpython-fnaf-fan-game/blob/main/adafruit-circuitpython-seeeduino_wio_terminal-en_US-9.2.4.uf2) to the device. ([Instruction](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython))
2. After done, copy everything under `CIRCUITPY` to the `CIRCUITPY` drive representing the device storage.
3. Press reset again and the game should start loading and running.

### Audio Output Wiring

![pinout](https://github.com/alankrantas/project-foobear-circuitpython-fnaf-fan-game/blob/main/WioT-Pinout.jpg)

Connect the DAC0 pin (pin 11 on Wio Terminal) and any GND pin (for example, pin 9) to a speaker or 3.5mm jack.

Personally I use a 3.5mm TRRS breakout board:

| Wio Terminal Pin | Wire |
| --- | --- |
| 11 (DAC0) | TIP |
| 9 (GND) | PING1 |

And I add a potentiometer between DAC0 and TIP so that the volumn can be reduced for earphones.

## About This Project

This was conceived some years ago, with the primary coding completed in the summer of 2022. The original plan was to build a physical model control room in front of the Wio Terminal (which is the "tablet" you're using) - the serve-controlled door actually opens and closes, and the RGB LEDs shows scanner and zapper light, etc.

In the end, I just couldn't find enough motivate to finish it; it's more difficult and simply not immersive enough. The code can run complete without all the external devices, and so I decided to leave it as it is.

## References

Hardware/firmware/driver:

- [Get Started with Wio Terminal](https://wiki.seeedstudio.com/Wio-Terminal-Getting-Started/)
- [Seeeduino Wio Terminal (Circuit firmware)](https://circuitpython.org/board/seeeduino_wio_terminal/)
- [Adafruit CircuitPython Library Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle)

CircuitPython:

- [Seeed Wio Terminal Circuitpython Modules](https://gist.github.com/stonehippo/03677c206bf68846328f151ee8322193)
- [Buttons and Switch](https://learn.adafruit.com/sensor-plotting-with-mu-and-circuitpython/buttons-and-switch)
- Display:
  - [Display Support Using displayio](https://learn.adafruit.com/circuitpython-display-support-using-displayio/ui-quickstart)
  - [Display Text](https://learn.adafruit.com/circuitpython-display-support-using-displayio/text)
  - [displayio](https://docs.circuitpython.org/en/latest/shared-bindings/displayio/index.html)
  - [adafruit_display_shapes](https://docs.circuitpython.org/projects/display-shapes/en/latest/index.html)
  - [adafruit_display_text](https://docs.circuitpython.org/projects/display_text/en/latest/index.html)
  - [adafruit_progressbar](https://docs.circuitpython.org/projects/progressbar/en/latest/index.html)
  - [Adafruit_CircuitPython_Bitmap_Font](https://github.com/adafruit/Adafruit_CircuitPython_Bitmap_Font/tree/main/examples/fonts)
  - [Convert a font in BDF format to PCF format for use with CircuitPython](https://adafruit.github.io/web-bdftopcf/)
- Audio:
  - [CircuitPython Audio Out](https://learn.adafruit.com/circuitpython-essentials/circuitpython-audio-out)
  - [audioio](https://docs.circuitpython.org/en/latest/shared-bindings/audioio/index.html)
  - [audiomixer](https://docs.circuitpython.org/en/latest/shared-bindings/audiomixer/index.html)
  - [Convert Sound Files in Audacity](https://learn.adafruit.com/microcontroller-compatible-audio-file-conversion)
  - Audio files of [FNAF 1](https://downloads.khinsider.com/game-soundtracks/album/five-nights-at-freddy-s-fnaf) and [FNAF 2](https://downloads.khinsider.com/game-soundtracks/album/five-nights-at-freddy-s-fnaf-2-sfx)
