# Project FooBear: A FNAF Fan Game on CircuitPython and Wio Terminal - with Full Sound Effects!

> Photo and video to be added later.

## The Story

You are an intern working in a AI startup, which develops a humanoid robot codenamed "Foobear". (Because, you know, "foo" and "bar".)

And one day you are ordered to stay in the company for the night, because apperently the security guy disappeared previous day for no reason. A big demo is scheduled tomorrow, and the company cannot afford to have no one on watch.

You also hear something about the robot may roam around the empty office after midnight.

You asked the boss, and he said: "Relax, we are testing that thing. Reinforcement learning stuff, nothing to worry about. Just don't let anyone enter the control room. You can lock yourself in if you have to, but under _NO_ circumstances overload the power system!"

As the clock hits 12:00 AM, alone in the security room, you started to feel that this may be the longest night of your life - or the shortest one.

### Floor Plan

```
0(b)-1----2
|    |    |
3----4----5--|
|    |    w  9(z)
6----7--d[8]-|
```

| Label | Description |
| --- | --- |
| `0` | Demo Room (has a Bluetooth speaker in there) |
| `1` | Developers' Office |
| `2` | Cafeteria |
| `3` | Meeting room |
| `4` | Main hallway |
| `5` | Server room |
| `6` | Restroom |
| `7` | Lobby |
| `8` | Control room (where you are; power usage is shown and the security door can be locked) |
| `9` | Air Vent (has a electric bug zapper installed) |
| `b` | Bluetooth speaker |
| `d` | Security door |
| `w` | Window |
| `z` | Bug zapper |

All rooms but control room and air vent has scanner installed.

### Rules

- You cannot leave the control room nor the company. Stay alive until 6:00 AM. (Each hour is ~1 minute).
- Stop anything enters the control room.
- The control room has a door to lobby, connects the air vent with the server room, and has a mesh window between it and the server room (so you may hear things moving in there if any).
- The lines in the floor plan indicate passages, in which anyone can move from room to room.
- Speaking of which, the air vent is also big enough to crawl through...
- Use switch buttons to move focus to different rooms. The focused room will be highlighted.
  - Use the scan button to scan "anomaly" in the focused room.
  - If a non-`SCAN` special action is available, you can activate with the special action button.
  - You cannot activate a function if it's recharging (in cooldown).
- The right side of the control room icon shows the current power load. Scan and special actions consume power for recharging. If you cause too much power load at a point, the system will shut down and undergo emergency reboot. You will not to be able to see or do anything in the meantime...

<details>
  <summary>Additional hints</summary>

- The Bluetooth speaker distracts `FooBear` - for most of the time.
- The door keeps `FooBear` out, but keep the door closed will gradually increase power load.
- The air vent zapper also keeps `FooBear` out. This usually will scare the robot away for a while.
- `FooBear` will get more aggresive to hunt you with each hour passed.
- When `FooBear` is in hunting mode, it will try to enter from either the door or the air vent.
- When `FooBear` is in hunting mode and get blocked at the door or zapped in the air vent, it may run away for a while (more likely when zapped) or change the hunting direction.
- `FooBear` will not try to enter the control room when it's not hunting (simply roaming).
- `FooBear` will very likely to hunt you more actively and move more quickly during the power outtage.
- If you try to activate an action but it wouldn't work, it's either the action is in cooldown, or...your time is numbered.

</details>

<details>
  <summary>Even more hints!</summary>

- Cheats and configuration by modifying `code.py`:
  - Set `ANOMALY_ALWAYS_SHOWN` to `True` to show where `FooBear` is.
  - Set `ANOMALY_ACTION_LOG` to `True` to print game event and action logs in the console.
  - Set `ANOMALY_NOT_MOVING` to `True` to make the robot not moving at all. (You will never fail the game).
  - Set `SKIP_TITLE_ANIMATION` to `True` to skip the title animation after game booting up.
- You don't need to scan every room - just the room closest to the door and air vent. And listen to the sound clue:
  - `FooBear` laughs when it is moving in hunting mode.
  - You would hear `FooBear` walking when it enters room 4, 5 or 7 (the nearest to the control room).
  - You would hear clanging sound when `FooBear` crawls into the air vent.
  - `FooBear` also laughs and can be heard of walking at the same time when it enters the control room...

</details>

### Buttons

![btns](https://github.com/alankrantas/project-foobear-circuitpython-fnaf-fan-game/blob/main/WioT_Btns.png)

| Button | Function |
| --- | --- |
| Up, down, left, right | Move room focus |
| C | Scan (if available) |
| A | Special action (if available) |

---

## Run the Game

### Hardware

This game is design for a the [Wio Terminal](https://wiki.seeedstudio.com/Wio-Terminal-Getting-Started/), which is basically a SAMD51 microcontroller (which has DAC pins to play audio) with 512 KB RAM, 4 MB flash, a built-in 320x240 ILI9341 TFT and several buttons.

You may try to migrate this game to other SAMD51 boards with the display and buttons attached, but bear in mind that the code uses ~80% RAM and the text and audio files require ~3.7 MB storage.

### Installation

1. Connect the device to USB port and flash the [CircuitPython 9.x firmware](https://github.com/alankrantas/project-foobear-circuitpython-fnaf-fan-game/blob/main/adafruit-circuitpython-seeeduino_wio_terminal-en_US-9.2.4.uf2) to the device. ([Instruction](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython))
2. After done, copy everything under `CIRCUITPY` to the `CIRCUITPY` drive representing the device storage.
3. Press reset again and the game should start loading and running.

### Audio Output

**This game can be played without audio - but it will be less fun and harder to play.**

Connect the `DAC0` pin (pin 11 on Wio Terminal) and any `GND` pin (for example, pin 9) to a speaker or 3.5mm jack. Check CircuitPython's [instruction](https://learn.adafruit.com/circuitpython-essentials/circuitpython-audio-out) of how to connect a 3.5mm jack (ignore the button).

Personally I use a 3.5mm TRRS breakout board:

| Wio Terminal Pin | Wire |
| --- | --- |
| 11 (DAC0) | TIP |
| 9 (GND) | PING1 |

![pinout](https://github.com/alankrantas/project-foobear-circuitpython-fnaf-fan-game/blob/main/WioT-Pinout.jpg)

And I add a potentiometer between `DAC0` and `TIP` so that the volumn can be reduced for earphones.

---

## About This Project

This FNAF ([_Five Nights at Freddy's_](https://en.wikipedia.org/wiki/Five_Nights_at_Freddy%27s)) fan game was conceived some years ago, with the primary coding completed between 2021 and 2022. The code, more than 1,000 lines long, is built around a complex synchronous process runtime in which I can add behaviors and control them in the ways and intervals I want.

One of eariler concepts was to recreate the "It's a UNIX system, I know this" moment in _Jurassic Park_, where you have to defend yourself against a velociraptor by operating on a text-based system.

Of course, I had to re-invent the gameplay and rules since it's not possible to recreate and include all game mechanics of FNAF 1 or 2; but the inspiron is still there. I also can't help to "borrow" many of the FNAF sound effects (I did considered to use _Half Life_ sound effects instead. From the file names of FNAF sound effects, they are probably not original too). This game utilizes CircuitPython's audiomixer to play multiple audio files at the same time (including the looping background ambience sound) asynchronously, which works surprising well.

### What It Should Have Been

The original plan was to build a "table-top arcade game", with a physical, decorated model room built in front of the Wio Terminal (the "tablet" you're using) as the control room itself. The serve-controlled door on the left actually opens and closes (with a blue LED lights up when it is "locked"), and 5 RGB LEDs representing the room interior/scanner/zapper lights. It should feel like you are actually sitting in the control room, and observe things happening around you. You can see the scanner light shines white or red dependint on the results adjacent to the control room. Finally, all LEDs will light up in red when you are dead, and in green when you survived.

A large translucent "window" is installed at the far end of the control room looking into the server room; my plan was to install a Freddy-like silhouette standing behind the window, and put two LEDs in front of it and at the back. When the "anomaly" is in the server room and being "scanned", the back LED lights up in red, and if not, the front LED lights up in white (so you won't see the silhouette). No moving parts required! That was the theory anyway. This game would have to be played in near-blackness so that you won't see the silhouette exposed by external illumination.

I did connect and test all the electronic parts as a completed system:
- A SG-90 servo
- A blue LED
- 5 NeoPixel modules (1 RGB LED each)
- One analog joystick module
- Two push buttons

All of them were powered directly from the Wio Termainl (which is connected to 5V 2A DC input with its USB Type-C cable). Power them from an external source did not work that well.

But in the end, I just couldn't find enough motivattion and satisfaction to finish it; it's more difficult for me to build, and I found it simply not immersive enough. The game can run completely without all the external devices anyway - the room is just an augmented extension of the game itself - so eventually I decided to leave it as it is.

---

## References and Resources

CircuitPython

- Firmware/driver:
  - [Seeeduino Wio Terminal (Circuit firmware)](https://circuitpython.org/board/seeeduino_wio_terminal/)
  - [Adafruit CircuitPython Library Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle)
- General:
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

Audio files are from [FNAF 1](https://downloads.khinsider.com/game-soundtracks/album/five-nights-at-freddy-s-fnaf) and [FNAF 2](https://downloads.khinsider.com/game-soundtracks/album/five-nights-at-freddy-s-fnaf-2-sfx) with minor modifications. This project is not intended to be commercialized anyway.

And lastly, thank you, Markiplier; I do not play scary games at all, but I watched all the FNAF videos from the very beginning. It was really fun indeed.
