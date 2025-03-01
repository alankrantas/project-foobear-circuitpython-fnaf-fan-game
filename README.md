# Project Foobear: A FNAF Fan Game on CircuitPython and Wio Terminal

`Documentation working in progress`

## The Story

You are a programmer intern working in a AI startup, which develops a humanoid robot, codenamed "Foobear".

And you are ordered by your boss to stay up one night on watch, because apperently the security guy is sick. You also hear something about the robot would roam around after midnight.

The boss said: "Relax, it's not a big deal. Just don't let anyone enter the control room."

And when the clock hits 12:00 AM, you started to think maybe it is a mistake to stay after all.

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
- 2: Dev Office
- 3: Cafeteria
- 4: Meeting
- 5: Hallway
- 6: Servers
- 7: Restroom
- 8: Entrance
- 9: Control room (where you are; the door can be locked)
- 10: Air Vent (has a electric bug zapper)

Note:

- You cannot leave the control room. Stay alive until 6:00 AM.
- The lines in the floor plan indicate passage (the robot can move across).
- If the robot enters the control room, you die (game over).
- Use switch buttons to move focus to different rooms.
  - If SCAN shows up, press button 1 (leftmost top button) to scan the room. All rooms except the control room and air vent have scanners.
  - If a non-SCAN function shows, you can activate it (press button 3 or the rightmost top button).
  - You cannot activate a function if it's recharging (in cooldown).
- Listen for movements.

<details>
  <summary>Additional hints</summary>

- You might hear the robot when it's moving through room 5, 6 or 8 and the air vent.
- The robot will get more aggresive to get to you with each hour passed. (Each hour takes ~50 seconds.)
- The Bluetooth speaker distracts the robot - for most of the time.
- The door keeps the robot out.
- The air vent zapper also keeps the robot out and makes it run away.
- All controllable devices have cooldown time and consumes power. If you use too much, it will overload the system and force reboot.
- The robot will be more aggresive during the power outtage.

</details>

### Cheating Mode

Enable `ANOMALY_ALWAYS_SHOWN` and/or `ANOMALY_ACTION_LOG` to `True`.

`ANOMALY_ALWAYS_SHOWN` shows where the robot is, and `ANOMALY_ACTION_LOG` will print detailed game events in the console.

## Run the Game

### Hardware

This game is design for a the Wio Terminal, which is basically a SAMD51 microcontroller with 4 MB flash, a built-in 320x240 ILI9341 TFT and several buttons.

### Installation

1. Connect the device to USB port and flash the [CircuitPython 9.x firmware](https://github.com/alankrantas/project-foobear-circuitpython-fnaf-fan-game/blob/main/adafruit-circuitpython-seeeduino_wio_terminal-en_US-9.2.4.uf2) to the device. ([Instruction](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython))
2. After done, copy everything under `CIRCUITPY` to the `CIRCUITPY` drive representing the device storage.
3. Preset reset again and the game should start loading and running.

### Audio Output Wiring

Connect the DAC0 pin (pin 11 on Wio Terminal) and any GND pin (for example, pin 9) to a speaker or 3.5mm jack.

Personally I use a 3.5mm TRRS breakout board:

| Wio Terminal Pin | Wire |
| --- | --- |
| 11 (DAC0) | TIP |
| 9 (GND) | PING1 |

And I add a potentiometer between DAC0 and TIP so that the volumn can be reduced for earphones.

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
