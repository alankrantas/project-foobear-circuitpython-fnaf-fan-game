'''
Project Foobear: A FNAF Fan Game on CircuitPython and Wio Terminal

https://github.com/alankrantas/project-foobear-circuitpython-fnaf-fan-game
'''


# ===== import built-in modules =====

import random, time, os, sys, gc
import board, digitalio, analogio, pwmio, displayio, audioio, audiocore, audiomixer
from micropython import const

gc.enable()
gc.collect()
mem_limit = gc.mem_free()


# ===== import external modules =====

try:
    from adafruit_display_text.label import Label
    from adafruit_display_shapes.line import Line
    from adafruit_display_shapes.rect import Rect
    from adafruit_display_shapes.circle import Circle
    from adafruit_display_shapes.triangle import Triangle
    from adafruit_progressbar.verticalprogressbar import VerticalProgressBar
    from adafruit_bitmap_font import bitmap_font
except Exception as e:
    print(f'import library error: {e}')
    
print('Loading packages...ok')


# ===== game logic - config =====

ANOMALY_NAME = 'FooBear'
TITLE = f'Project\n{ANOMALY_NAME}'

# for debugging or cheating purposes
ANOMALY_ALWAYS_SHOWN = True
ANOMALY_ACTION_LOG = True
ANOMALY_NOT_MOVING = False
SKIP_TITLE_ANIMATION = False

# game parameters (all interval and countdown time values are seconds * 10)
AI_START_LEVEL = const(10)  # 1-100
AI_FINAL_LEVEL = const(90)  # 1-100
HOUR_INTERVAL = const(400)
MOVE_INTERVAL = const(40)
MOVE_MODE_RESET_CHANCE = const(33)
MOVE_MODE_MORE_ACTIVE_CHANCE = const(66)
LURED_CHANCE = const(75)
SCAN_COOLDOWN = const(15)
AUDIO_COOLDOWN = const(600)
ZAP_COOLDOWN = const(150)
POWER_LIMIT = const(100)
DOOR_POWER_CHANGE_LEVEL = const(5)
SCAN_POWER_CHANGE_LEVEL = const(15)
AUDIO_POWER_CHANGE_LEVEL = const(30)
ZAP_POWER_CHANGE_LEVEL = const(50)
POWER_REBOOT_INTERNAL = const(160)
WHITE = const(0xFFFFFF)
BLACK = const(0x000000)


# ===== game logic - rooms =====

'''
0(b)-1----2
|    |    |
3----4----5--|
|    |    w  9(z)
6----7--d[8]-|

0: Demo Room (has a Bluetooth speaker in there)
1: Developers' Office
2: Cafeteria
3: Meeting room
4: Main hallway
5: Server room
6: Restroom
7: Lobby
8: Control room (where you are; power usage is shown and the security door can be locked)
9: Air Vent (has a electric bug zapper installed)

b: Bluetooth speaker
d: Security door
w: Window
z: Bug zapper
'''

ROOM_NAMES = {
    0: 'Demo Room',
    1: 'Dev Office',
    2: 'Cafeteria',
    3: 'Meeting',
    4: 'Hallway',
    5: 'Servers',
    6: 'Restroom',
    7: 'Lobby',
    8: 'Control',  # target
    9: 'Air Vent'
}

RESET_ROOMS = (0, 1, 3)
SCANNABLE_ROOMS = (0, 1, 2, 3, 4, 5, 6, 7)
WALK_SOUND_ROOMS = (4, 5, 7)
TARGET_ROOM = const(8)
AIR_VENT_ROOM = const(9)
AUDIO_ROOM = const(0)
DOOR_ROOM = const(7)
WINDOW_ROOM = const(5)
CENTER_ROOM = const(4)

MOVE_PERF = {  # anamony's move mode
    'Normal': {  # roaming; not hunting
        0: (1, 3),
        1: (2, 4),
        2: (1, 5),
        3: (4, 6),
        4: (3, 5, 7),
        5: (4,),
        6: (3, 7),
        7: (4,),
        8: [],
        9: (5,),
    },
    'Door': {  # go to the door; hunting
        0: (3,),
        1: (4,),
        2: (1, 5),
        3: (4, 6),
        4: (7,),
        5: (4,),
        6: (7,),
        7: (8,),
        8: [],
        9: (5,),
    },
    'Air Vent': {  # go to the air vent: hunting
        0: (1, 3),
        1: (2, 4),
        2: (5,),
        3: (0, 4),
        4: (5,),
        5: (9,),
        6: (3, 7),
        7: (4,),
        8: [],
        9: (8,),
    },
    'Escape': {  # escape from being blocked
        0: (1, 3),
        1: (0,),
        2: (1,),
        3: (0,),
        4: (1, 3,),
        5: (2, 4),
        6: (3,),
        7: (4,),
        8: [],
        9: (5,),
    },
    'Lure': {  # lured by audio
        0: [],
        1: (0,),
        2: (1,),
        3: (0,),
        4: (1, 3,),
        5: (2, 4,),
        6: (3,),
        7: (4, 6),
        8: [],
        9: (5,),
    },
}


# ===== game logic - internal variables =====

AI = 0
gameStatus = ''
hour = 0
anomalyRoom = 0
selectedRoom = TARGET_ROOM
detectionRoom = 0
moveMode = ''
pressedKey = ''
doorClosed = False
systemPower = 0
powerOut = False
justLaughed = 0


# ===== pin and device config ===== https://wiki.seeedstudio.com/Wio-Terminal-IO-Overview/

pin_audio = board.DAC0
pin_door_servo = board.A2
pin_btn_special = board.BUTTON_1
pin_btn_scan = board.BUTTON_3
pin_btn_up = board.SWITCH_UP
pin_btn_down = board.SWITCH_DOWN
pin_btn_left = board.SWITCH_LEFT
pin_btn_right = board.SWITCH_RIGHT


# ===== buttons =====

def btnFactory(pin):
    btn = digitalio.DigitalInOut(pin)
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    return btn

btns = {
    'Special': {
        'btn': btnFactory(pin_btn_special),
        'action': 'PlayerAction',
    },
    'Scan': {
        'btn': btnFactory(pin_btn_scan),
        'action': 'PlayerAction',
    },
    'Up': {
        'btn': btnFactory(pin_btn_up),
        'action': 'SelectRoom',
    },
    'Down': {
        'btn': btnFactory(pin_btn_down),
        'action': 'SelectRoom',
    },
    'Left': {
        'btn': btnFactory(pin_btn_left),
        'action': 'SelectRoom',
    },
    'Right': {
        'btn': btnFactory(pin_btn_right),
        'action': 'SelectRoom',
    },
}

def detectKeyPress():
    global pressedKey
    for key, item in btns.items():
        if not item['btn'].value:
            pressedKey = key
            invokeCallbackAndCountdown(item['action'])
            return

print('Configuring buttons...ok')


# ===== font ===== https://github.com/Tecate/bitmap-fonts/tree/master/bitmap/terminus-font-4.39

try:
    font_12 = bitmap_font.load_font('./font/ter-u12b.pcf')
    font_22 = bitmap_font.load_font('./font/ter-u22b.pcf')
except Exception as e:
    print(f'Font load error: {e}')
    sys.exit()

print('Loading fonts...ok')


# ===== audio =====

VOICE_BACKGROUND = const(0)
VOICE_PLAYER_ACTION = const(1)
VOICE_PLAYER_EFFECT = const(2)
VOICE_PLAYER_EFFECT_2 = const(3)
VOICE_ANOMALY_ACTION = const(4)
VOICE_ANOMALY_LAUGH = const(5)

audioLibrary = {}

# add all audio files in ./audio
# all audio files are 22.5 KHz 16 bit mono WAVs
for filename in os.listdir('audio'):
    if not filename.endswith('.wav'):
        continue
    try:
        audioLibrary[filename.replace('.wav', '')] = audiocore.WaveFile(f'./audio/{filename}')
    except Exception as e:
        print(f'Audio load error: {e}')
        sys.exit()
        
print('Loading audio library...ok')

audio = audioio.AudioOut(pin_audio)
mixer = audiomixer.Mixer(
    channel_count=1,
    voice_count=6,
    buffer_size=2048,
    bits_per_sample=16,
    sample_rate=22050,
    samples_signed=True)
audio.play(mixer)

def playAudio(voice, name):
    mixer.voice[voice].play(audioLibrary[name])

def isVoicePlaying(voice):
    return mixer.voice[voice].playing

def playBackgroundAudio():
    if not powerOut and not isVoicePlaying(VOICE_BACKGROUND):
        playAudio(VOICE_BACKGROUND, 'ambience')

print('Configuring audio mixer...ok')


# ===== main screen config =====

display = board.DISPLAY
display.root_group = None
display.brightness = 1.0
display.auto_refresh = False

splashMain = displayio.Group()
splashTitle = displayio.Group()

SCREEN_W = display.width
SCREEN_H = display.height
ROOM_W = const(65)
ROOM_H = const(40)
ROOM_INTERVAL = const(15)
LEFT_PAD = const(25)
TOP_PAD = const(75)
ICON_DEFAULT_X = const(-ROOM_INTERVAL*2)
ICON_DEFAULT_Y = const(-ROOM_INTERVAL*2)

ROOM_BORDER_COLOR = const(0xFFF5EE)
ROOM_BORDER_CONTROL_COLOR = const(0x00BFFF)
ROOM_WINDOW_COLOR = const(0x00BFFF)
ROOM_SELECTED_COLOR = const(0x708090)
ROOM_SCAN_CLEAR_COLOR = const(0xAFEEEE)
ROOM_SCAN_DANGER_COLOR = const(0xFF1493)

ROOM_LABEL_COLOR = const(0x808080)
ROOM_LABEL_SELECTED_COLOR = const(0xFFF8DC)
DOOR_OPEN_LABEL_COLOR = const(0x7CFC00)
DOOR_CLOSED_LABEL_COLOR = const(0xDC143C)
SCAN_LABEL_COLOR = const(0x1E90FF)
DISABLED_LABEL_COLOR = const(0x696969)
AUDIO_LABEL_COLOR = const(0xEE82EE)
ZAP_LABEL_COLOR = const(0xFF7F50)
HOUR_LABEL_TEXT_COLOR = const(0x00FFFF)

COOLDOWN_BAR_COLOR = const(0xADFF2F)
COOLDOWN_BAR_COLOR_2 = const(0x87CEFA)

ANOMALY_ICON_COLOR = const(0xDC143C)
AUDIO_ICON_COLOR = const(0xDAA520)
ZAP_ICON_COLOR = const(0x00BFFF)

CORRIDOR_COLOR = const(0xE9967A)
AIR_VENT_TUNNEL_COLOR = const(0xA0522D)
CONTROL_HIGHLIGHT_COLOR = const(0x000080)

LABEL_TITLE_COLOR = (const(0xF08080), const(0xCD5C5C), const(0xFA8072))
LABEL_MSG_COLOR = const(0xD3D3D3)
LABEL_MSG_BOX_COLOR = const(0x3CB371)
MSG_PAD = const(20)


# ===== display - main =====

drawRooms = []

for j in range(3):
    for i in range(3):
        drawRooms.append(
            Rect(
                x=LEFT_PAD+(ROOM_W+ROOM_INTERVAL)*i,
                y=TOP_PAD+(ROOM_H+ROOM_INTERVAL)*j,
                width=ROOM_W,
                height=ROOM_H,
                outline=ROOM_BORDER_COLOR))

drawRooms.append(
    Rect(
        x=drawRooms[WINDOW_ROOM].x+drawRooms[WINDOW_ROOM].width+round(ROOM_INTERVAL*1.5),
        y=drawRooms[WINDOW_ROOM].y+round(drawRooms[WINDOW_ROOM].height/4),
        width=round(ROOM_W/3),
        height=round(ROOM_H*1.5)+ROOM_INTERVAL,
        outline=ROOM_BORDER_COLOR))

drawRooms[TARGET_ROOM].outline = ROOM_BORDER_CONTROL_COLOR

roomLabels = [
    Label(
        font=font_12,
        text=ROOM_NAMES[i],
        x=drawRooms[i].x,
        y=drawRooms[i].y+6,
        color=ROOM_LABEL_COLOR)
    for i in range(9)
]

roomLabels.append(
    Label(
        font=font_12,
        text=ROOM_NAMES[AIR_VENT_ROOM],
        x=drawRooms[AIR_VENT_ROOM].x,
        y=drawRooms[AIR_VENT_ROOM].y-12,
        color=ROOM_LABEL_COLOR))


for i in (0, 1, 3, 4, 6, 7):
    splashMain.append(
        Line(
            x0=drawRooms[i].x+drawRooms[i].width,
            y0=drawRooms[i].y+round(drawRooms[i].height/2),
            x1=drawRooms[i].x+drawRooms[i].width+ROOM_INTERVAL,
            y1=drawRooms[i].y+round(drawRooms[i].height/2),
            color=CORRIDOR_COLOR))

for i in range(5):
    splashMain.append(
        Line(
            x0=drawRooms[i].x+round(drawRooms[i].width/2),
            y0=drawRooms[i].y+drawRooms[i].height,
            x1=drawRooms[i].x+round(drawRooms[i].width/2),
            y1=drawRooms[i].y+drawRooms[i].height+ROOM_INTERVAL,
            color=CORRIDOR_COLOR))

for i in (5, 8):
    splashMain.append(
        Line(
            x0=drawRooms[i].x+drawRooms[i].width,
            y0=drawRooms[i].y+round(drawRooms[i].height/2),
            x1=drawRooms[AIR_VENT_ROOM].x,
            y1=drawRooms[i].y+round(drawRooms[i].height/2),
            color=CORRIDOR_COLOR))

for r in drawRooms:
    splashMain.append(r)

for i, l in enumerate(roomLabels):
    l.x = drawRooms[i].x+round(drawRooms[i].width/2 - l.width/2)
    splashMain.append(l)
        
door = Rect(
            x=drawRooms[TARGET_ROOM].x-round(ROOM_INTERVAL/4),
            y=drawRooms[TARGET_ROOM].y+round(drawRooms[TARGET_ROOM].height/8),
            width=round(ROOM_INTERVAL/2),
            height=round(drawRooms[TARGET_ROOM].height*3/4),
            fill=DOOR_OPEN_LABEL_COLOR)

window = Rect(
            x=drawRooms[TARGET_ROOM].x+round(drawRooms[TARGET_ROOM].width/8),
            y=drawRooms[TARGET_ROOM].y-round(ROOM_INTERVAL*3/4),
            width=round(drawRooms[TARGET_ROOM].width*3/4),
            height=round(ROOM_INTERVAL/2),
            fill=ROOM_WINDOW_COLOR)

scanBtnLabel = Label(
            font=font_22,
            text='Scan',
            x=drawRooms[0].x,
            y=drawRooms[0].y-ROOM_INTERVAL*2,
            color=BLACK,
            background_color=BLACK,
            padding_top=4,
            padding_bottom=4,
            padding_left=4,
            padding_right=4)
scanBtnLabel.x = drawRooms[0].x + round(drawRooms[0].width/2 - scanBtnLabel.width/2)

actionBtnLabel = Label(
            font=font_22,
            text='Action',
            x=drawRooms[2].x,
            y=drawRooms[2].y-ROOM_INTERVAL*2,
            color=BLACK,
            background_color=BLACK,
            padding_top=4,
            padding_bottom=4,
            padding_left=4,
            padding_right=4)
actionBtnLabel.x = drawRooms[2].x + round(drawRooms[2].width/2 - actionBtnLabel.width/2)

hourLabel = Label(
            font=font_22,
            text='0 AM',
            x=drawRooms[1].x,
            y=drawRooms[1].y-ROOM_INTERVAL*2,
            color=HOUR_LABEL_TEXT_COLOR,
            background_color=BLACK,
            padding_top=4,
            padding_bottom=4,
            padding_left=4,
            padding_right=4)
hourLabel.x = drawRooms[1].x + round(drawRooms[1].width/2 - hourLabel.width/2)

scanCooldownBar = VerticalProgressBar(
            position=(
                drawRooms[0].x-ROOM_INTERVAL,
                round(scanBtnLabel.y-scanBtnLabel.height/2)),
            size=(round(ROOM_INTERVAL/2), scanBtnLabel.height),
            min_value=0,
            max_value=SCAN_COOLDOWN,
            value=0,
            bar_color=COOLDOWN_BAR_COLOR_2,
            outline_color=BLACK,
            fill_color=BLACK)

audioCooldownBar = VerticalProgressBar(
            position=(
                drawRooms[AUDIO_ROOM].x-ROOM_INTERVAL,
                drawRooms[AUDIO_ROOM].y),
            size=(round(ROOM_INTERVAL/2), ROOM_H),
            min_value=0,
            max_value=AUDIO_COOLDOWN,
            value=0,
            bar_color=COOLDOWN_BAR_COLOR,
            outline_color=BLACK,
            fill_color=BLACK)

zapCooldownBar = VerticalProgressBar(
            position=(
                drawRooms[AIR_VENT_ROOM].x+drawRooms[AIR_VENT_ROOM].width+round(ROOM_INTERVAL/2),
                drawRooms[AIR_VENT_ROOM].y+round(drawRooms[AIR_VENT_ROOM].height/4)),
            size=(round(ROOM_INTERVAL/2), round(drawRooms[AIR_VENT_ROOM].height/2)),
            min_value=0,
            max_value=ZAP_COOLDOWN,
            value=0,
            bar_color=COOLDOWN_BAR_COLOR,
            outline_color=BLACK,
            fill_color=BLACK)

systemPowerBar = VerticalProgressBar(
            position=(
                drawRooms[TARGET_ROOM].x+drawRooms[TARGET_ROOM].width-round(ROOM_INTERVAL/2),
                drawRooms[TARGET_ROOM].y),
            size=(round(ROOM_INTERVAL/2), drawRooms[TARGET_ROOM].height),
            min_value=0,
            max_value=POWER_LIMIT,
            value=0,
            bar_color=COOLDOWN_BAR_COLOR,
            outline_color=ROOM_BORDER_CONTROL_COLOR,
            fill_color=BLACK)

anomalyIcon = Circle(
            x0=ICON_DEFAULT_X,
            y0=ICON_DEFAULT_Y,
            r=round(ROOM_INTERVAL/2),
            fill=ANOMALY_ICON_COLOR)

anomalyLabel = Label(
            font=font_12,
            text='!',
            x=anomalyIcon.x0,
            y=anomalyIcon.y0,
            color=WHITE)

TRI_BASE = ROOM_INTERVAL
TRI_H = round(TRI_BASE * (3 ** 0.5) / 2)
TRI_CEN_TO_BASE = round(TRI_BASE * (3 ** 0.5) / 6)

audioIcon = Triangle(
            x0=drawRooms[AUDIO_ROOM].x-TRI_CEN_TO_BASE,
            y0=drawRooms[AUDIO_ROOM].y+round(drawRooms[AUDIO_ROOM].height/2)-round(TRI_BASE/2),
            x1=drawRooms[AUDIO_ROOM].x-TRI_CEN_TO_BASE,
            y1=drawRooms[AUDIO_ROOM].y+round(drawRooms[AUDIO_ROOM].height/2)+round(TRI_BASE/2),
            x2=drawRooms[AUDIO_ROOM].x+TRI_CEN_TO_BASE,
            y2=drawRooms[AUDIO_ROOM].y+round(drawRooms[AUDIO_ROOM].height/2),
            fill=AUDIO_ICON_COLOR)
audioIcon.fill = None

zapIcon = Triangle(
            x0=drawRooms[AIR_VENT_ROOM].x+drawRooms[AIR_VENT_ROOM].width+TRI_CEN_TO_BASE,
            y0=drawRooms[AIR_VENT_ROOM].y+round(drawRooms[AIR_VENT_ROOM].height/2)-round(TRI_BASE/2),
            x1=drawRooms[AIR_VENT_ROOM].x+drawRooms[AIR_VENT_ROOM].width+TRI_CEN_TO_BASE,
            y1=drawRooms[AIR_VENT_ROOM].y+round(drawRooms[AIR_VENT_ROOM].height/2)+round(TRI_BASE/2),
            x2=drawRooms[AIR_VENT_ROOM].x+drawRooms[AIR_VENT_ROOM].width-(TRI_H-TRI_CEN_TO_BASE),
            y2=drawRooms[AIR_VENT_ROOM].y+round(drawRooms[AIR_VENT_ROOM].height/2),
            fill=ZAP_ICON_COLOR)
zapIcon.fill = None

splashMain.append(door)
splashMain.append(window)
splashMain.append(scanBtnLabel)
splashMain.append(actionBtnLabel)
splashMain.append(hourLabel)
splashMain.append(scanCooldownBar)
splashMain.append(audioCooldownBar)
splashMain.append(zapCooldownBar)
splashMain.append(systemPowerBar)
splashMain.append(anomalyIcon)
splashMain.append(anomalyLabel)
splashMain.append(audioIcon)
splashMain.append(zapIcon)
print('Loading main screen layers...ok')

def showIcon(icon):
    if icon == 'anomaly':
        anomalyIcon.x0 = drawRooms[anomalyRoom].x + round(drawRooms[anomalyRoom].width/2)
        anomalyIcon.y0 = drawRooms[anomalyRoom].y + round(drawRooms[anomalyRoom].height/2)
        anomalyLabel.x = anomalyIcon.x0 - round(anomalyLabel.width/2)
        anomalyLabel.y = anomalyIcon.y0
    elif icon == 'audio':
        audioIcon.fill = AUDIO_ICON_COLOR
    elif icon == 'zap':
        zapIcon.fill = ZAP_ICON_COLOR

def hideIcon(icon):
    if icon == 'anomaly' or icon == 'all':
        anomalyIcon.x0 = ICON_DEFAULT_X
        anomalyIcon.y0 = ICON_DEFAULT_Y
        anomalyLabel.x = anomalyIcon.x
        anomalyLabel.y = anomalyIcon.y
    if icon == 'audio' or icon == 'all':
        audioIcon.fill = None
    if icon == 'zap' or icon == 'all':
        zapIcon.fill = None

def startMainScreen():
    global splashTitle
    display.root_group = None
    splashTitle = None
    gc.collect()
    display.root_group = splashMain


# ===== power out screen =====

powerOutLabel = None

def startMainScreenPowerOut():
    global splashTitle, powerOutLabel
    print('Loading power out screen...')
    display.root_group = None
    splashTitle = None
    powerOutLabel = None
    gc.collect()
    splashTitle = displayio.Group()
    powerOutLabel = Label(
                    font=font_22,
                    text='Power overloaded.\n\nEmergency\nrebooting...',
                    x=round(SCREEN_W/2),
                    y=round(SCREEN_H/2),
                    color=BLACK)
    powerOutLabel.x = round(SCREEN_W/2 - powerOutLabel.width/2)
    powerOutLabel.y = round(SCREEN_H/2 - powerOutLabel.height/2)
    splashTitle.append(powerOutLabel)
    display.root_group = splashTitle


# ===== title screen =====

def startTitleScreen():
    global splashTitle, firstTimeRunning
    print('Loading title screen...')
    print(f'First time playing: {firstTimeRunning}')
    splashTitle = displayio.Group()
    labelTitle = Label(
            font=font_22,
            text=TITLE,
            scale=2,
            x=round(SCREEN_W/2),
            y=round(SCREEN_H/4),
            color=BLACK)
    labelTitle.x = round(SCREEN_W/2 - labelTitle.width)
    labelMsg = Label(
            font=font_22,
            text='System booting ',
            x=MSG_PAD,
            y=SCREEN_H-MSG_PAD*2,
            color=BLACK)
    labelMsgBox = Rect(
            x=labelMsg.x+labelMsg.width,
            y=labelMsg.y-round(labelMsg.height/2),
            width=round(labelMsg.height/2),
            height=labelMsg.height,
            fill=BLACK)
    splashTitle.append(labelTitle)
    splashTitle.append(labelMsg)
    splashTitle.append(labelMsgBox)
    display.root_group = splashTitle
    gc.collect()
    if firstTimeRunning and not SKIP_TITLE_ANIMATION:
        time.sleep(1)
        labelMsg.color = LABEL_MSG_COLOR
        display.refresh()
        labelMsgBox.fill = LABEL_MSG_BOX_COLOR
        for i in range(3):
            if i == 0:
                labelMsgBox.fill = LABEL_MSG_BOX_COLOR
            labelMsg.text = labelMsg.text + '. '
            labelMsgBox.x = labelMsg.x + labelMsg.width
            playAudio(VOICE_BACKGROUND, 'beep')
            display.refresh()
            time.sleep(1)
        firstTimeRunning = False
    labelTitle.color = BLACK
    labelMsg.color = BLACK
    splashTitle.remove(labelMsgBox)
    del labelMsgBox
    gc.collect()
    display.refresh()
    time.sleep(1)
    labelTitle.color = LABEL_TITLE_COLOR[0]
    labelMsg.text = 'Press any key'
    labelMsg.color = LABEL_MSG_COLOR
    labelMsg.x = round(SCREEN_W/2 - labelMsg.width/2)
    labelMsg.y = SCREEN_H - MSG_PAD*2
    display.refresh()
    exitFlag = False
    msgFlash = False
    msgFlashCountdown = 5
    start = time.monotonic_ns()
    while not exitFlag:
        playBackgroundAudio()
        for item in btns.values():
            if not item['btn'].value:
                exitFlag = True
                break
        if (time.monotonic_ns() - start) >= 100000000:  # 100 ms
            start = time.monotonic_ns()
            if random.randint(1, 100) <= 5:
                labelTitle.x = labelTitle.x + random.randint(-5, 5)
            else:
                labelTitle.x = round(SCREEN_W/2 - labelTitle.width)
            if random.randint(1, 100) <= 5:
                labelTitle.y = labelTitle.y + random.randint(-5, 5)
            else:
                labelTitle.y = round(SCREEN_H/4)
            if random.randint(1, 100) <= 10:
                labelTitle.color = LABEL_TITLE_COLOR[random.randint(0, len(LABEL_TITLE_COLOR)-1)]
            if msgFlashCountdown == 0:
                msgFlash = not msgFlash
                msgFlashCountdown = 5
            else:
                msgFlashCountdown -= 1
            labelMsg.color = LABEL_MSG_COLOR if msgFlash else BLACK
            display.refresh()
    print('The player pressed start')
    labelTitle.color = BLACK
    labelMsg.color = BLACK
    display.refresh()
    playAudio(VOICE_PLAYER_EFFECT_2, 'gamestart')
    time.sleep(0.1)
    if SKIP_TITLE_ANIMATION:
        return
    t = 'Survive until 6 AM.'
    labelMsg.text = t
    labelMsg.x = round(SCREEN_W/2 - labelMsg.width/2)
    labelMsg.y = round(SCREEN_H/2)
    labelMsg.color = LABEL_MSG_COLOR
    for i in range(len(t)+1):
        labelMsg.text = t[:i]
        display.refresh()
        time.sleep(0.05)
    time.sleep(1)
    t = 'Watch out for anomaly.'
    labelMsg.text = t
    labelMsg.x = round(SCREEN_W/2 - labelMsg.width/2)
    for i in range(len(t)+1):
        labelMsg.text = t[:i]
        display.refresh()
        time.sleep(0.05)
    time.sleep(2)
    labelMsg.color = BLACK
    display.refresh()
    time.sleep(1)
    display.root_group = None
    splashTitle = None
    gc.collect()


# ===== end title screen =====

def startEndTitleScreen():
    global splashTitle
    print('Loding end title screen...')
    time.sleep(1)
    splashTitle = displayio.Group()
    labelMsg = Label(
            font=font_22,
            text='',
            x=0,
            y=0,
            color=BLACK)
    t = ''
    if gameStatus == 'Died':
        t = 'Y O U  D I E D'
        labelMsg.color = LABEL_TITLE_COLOR[0]
    else:
        t = 'You survived! :)'
        labelMsg.color = LABEL_MSG_COLOR
    labelMsg.text = t
    labelMsg.x = round(SCREEN_W/2 - labelMsg.width/2)
    labelMsg.y = round(SCREEN_H/2 - labelMsg.height/2)
    splashTitle.append(labelMsg)
    display.root_group = splashTitle
    gc.collect()
    if gameStatus == 'Died':
        playAudio(VOICE_BACKGROUND, 'jumpscare')
        for _ in range(20):
            labelMsg.color = LABEL_TITLE_COLOR[random.randint(0, len(LABEL_TITLE_COLOR)-1)]
            display.refresh()
            time.sleep(0.1)
    else:
        playAudio(VOICE_BACKGROUND, 'survived')
        for i in range(len(t)+1):
            labelMsg.text = t[:i]
            display.refresh()
            time.sleep(0.25)
    time.sleep(5)
    display.root_group = None
    splashTitle = None
    gc.collect()


# ===== game logic - countdowns and callbacks =====

countdownTable = {
    'GC': {
        'mode': 'continuous',
        'interval': const(7),
    },
    'Hour': {
        'mode': 'continuous',
        'interval': HOUR_INTERVAL,
    },
    'Move': {
        'mode': 'continuous',
        'interval': MOVE_INTERVAL,
    },
    'PowerMonitor': {
        'mode': 'continuous',
        'interval': const(10),
    },
    'PowerReboot': {
        'mode': 'stepping',
        'interval': POWER_REBOOT_INTERNAL,
    },
    'SelectRoom': {
        'mode': 'once',
        'interval': const(3),
    },
    'PlayerAction': {
        'mode': 'once',
        'interval': const(5),
    },
    'Door': {
        'mode': 'stepping',
        'interval': const(8),
    },
    'Scan': {
        'mode': 'stepping',
        'interval': const(10),
        'cooldown': 'ScanCooldown',
    },
    'Audio': {
        'mode': 'stepping',
        'interval': const(10),
        'cooldown': 'AudioCooldown',
    },
    'Zap': {
        'mode': 'stepping',
        'interval': const(10),
        'cooldown': 'ZapCooldown',
    },
    'ScanCooldown': {
        'mode': 'stepping',
        'interval': SCAN_COOLDOWN,
    },
    'AudioCooldown': {
        'mode': 'stepping',
        'interval': AUDIO_COOLDOWN,
    },
    'ZapCooldown': {
        'mode': 'stepping',
        'interval': ZAP_COOLDOWN,
    },
    'ShowAnomaly': {
        'mode': 'stepping' if not ANOMALY_ALWAYS_SHOWN else 'continuous',
        'interval': const(25) if not ANOMALY_ALWAYS_SHOWN else const(3),
    },
}

# helpers

def chance(threshold):
    return random.randint(1, 100) <= threshold

def setMoveMode(modes):
    global moveMode
    moveMode = modes[random.randint(0, len(modes)-1)]
    if ANOMALY_ALWAYS_SHOWN and ANOMALY_ACTION_LOG:
        print(f'{ANOMALY_NAME} switchs to move mode: {moveMode}')

def moveModeChange():
    if powerOut and moveMode in ('Normal', 'Lure', 'Escape'):
        setMoveMode(('Door', 'Air Vent'))
    elif ((moveMode == 'Lure' and anomalyRoom == AUDIO_ROOM) or (moveMode == 'Escape' and anomalyRoom in RESET_ROOMS)) \
            and chance(MOVE_MODE_RESET_CHANCE):
        setMoveMode(('Normal',))
        return True
    elif moveMode == 'Normal' and anomalyRoom not in (WINDOW_ROOM, DOOR_ROOM, AIR_VENT_ROOM) \
            and chance(MOVE_MODE_MORE_ACTIVE_CHANCE):
        setMoveMode(('Door', 'Air Vent'))

def setLabelsAndColors():
    countdown, _ = getCountdownAndInterval('ScanCooldown')
    if selectedRoom in SCANNABLE_ROOMS:
        scanBtnLabel.background_color = SCAN_LABEL_COLOR if countdown == 0 else DISABLED_LABEL_COLOR
    else:
        scanBtnLabel.background_color = BLACK
    if selectedRoom == TARGET_ROOM:
        actionBtnLabel.text = 'Door'
        actionBtnLabel.background_color = DOOR_CLOSED_LABEL_COLOR if doorClosed else DOOR_OPEN_LABEL_COLOR
    elif selectedRoom == AUDIO_ROOM:
        countdown, _ = getCountdownAndInterval('AudioCooldown')
        actionBtnLabel.text = 'Audio'
        actionBtnLabel.background_color = AUDIO_LABEL_COLOR if countdown == 0 else DISABLED_LABEL_COLOR
    elif selectedRoom == AIR_VENT_ROOM:
        countdown, _ = getCountdownAndInterval('ZapCooldown')
        actionBtnLabel.text = 'Zap'
        actionBtnLabel.background_color = ZAP_LABEL_COLOR if countdown == 0 else DISABLED_LABEL_COLOR
    else:
        actionBtnLabel.background_color = BLACK
    actionBtnLabel.x = drawRooms[2].x + round(drawRooms[2].width/2 - actionBtnLabel.width/2)
    door.fill = DOOR_CLOSED_LABEL_COLOR if doorClosed else DOOR_OPEN_LABEL_COLOR

def setHourLabel():
    hourLabel.text = f'{hour} AM'
    hourLabel.x = drawRooms[1].x + round(drawRooms[1].width/2 - hourLabel.width/2)

def getCountdownAndInterval(key):
    return countdownTable[key]['countpool'], countdownTable[key]['interval']

def resetCountDown(key, value=0):
    countdownTable[key]['countpool'] = value

# callbacks

def GC():
    gc.collect()

def Hour():
    global hour, AI, gameStatus
    if hour == 6:
        return
    hour += 1
    if hour == 6:
        gameStatus = 'Survived'
        return
    setHourLabel()
    AI = min(100, AI + round((AI_FINAL_LEVEL - AI_START_LEVEL) / 5))
    print(f'Time: {hour} AM, AI level: {AI}/100')

def Move():
    global anomalyRoom, moveMode, gameStatus, justLaughed
    if ANOMALY_NOT_MOVING:
        return
    if anomalyRoom == TARGET_ROOM and gameStatus != 'Died':
        gameStatus = 'Died'
        return
    if (not powerOut or moveMode not in ('Escape', 'Lure') or anomalyRoom not in (DOOR_ROOM, AIR_VENT_ROOM)) \
           and not chance(AI):
        return
    moveModeChange()
    ConnectedRooms = MOVE_PERF[moveMode].get(anomalyRoom, [])
    if len(ConnectedRooms) == 0:
        return
    newDirection = ConnectedRooms[random.randint(0, len(ConnectedRooms)-1)]
    if moveMode == 'Door' and anomalyRoom == DOOR_ROOM and newDirection == TARGET_ROOM and doorClosed:
        print(f'{ANOMALY_NAME} is blocked by the security door! (knocking sound heard)')
        playAudio(VOICE_ANOMALY_ACTION, 'knock')
        setMoveMode(('Normal', 'Air Vent', 'Escape'))
        return
    anomalyRoom = newDirection
    if ANOMALY_ACTION_LOG and anomalyRoom != TARGET_ROOM:
        print(f'{ANOMALY_NAME} moves to {ROOM_NAMES[anomalyRoom]} (room {anomalyRoom}), mode: {moveMode}')
    if anomalyRoom == TARGET_ROOM:
        playAudio(VOICE_ANOMALY_LAUGH, f'laugh{random.randint(1, 2)}')
        playAudio(VOICE_ANOMALY_ACTION, 'walk')
        if ANOMALY_ACTION_LOG:
            print(f'Help me, Markimoo, you are my only hope... ({ANOMALY_NAME} has reached the target)')
    elif anomalyRoom in WALK_SOUND_ROOMS:
        playAudio(VOICE_ANOMALY_ACTION, 'walk')
        print(f'{ANOMALY_NAME} walking sound heard')
    elif anomalyRoom == AIR_VENT_ROOM:
        playAudio(VOICE_ANOMALY_ACTION, 'airvent')
        print(f'{ANOMALY_NAME} crawling in the air vent heard')
    if anomalyRoom in SCANNABLE_ROOMS and moveMode in ('Door', 'Air Vent'):
        if (time.monotonic_ns() - justLaughed) >= 700000000:
            playAudio(VOICE_ANOMALY_LAUGH, f'laugh{random.randint(1, 2)}')
            print(f'{ANOMALY_NAME} laughing sound heard')
            justLaughed = time.monotonic_ns()

def PowerMonitor():
    global systemPower, powerOut, doorClosed
    if powerOut:
        return
    if doorClosed:
        systemPower += DOOR_POWER_CHANGE_LEVEL
    else:
        systemPower -= DOOR_POWER_CHANGE_LEVEL
    systemPower = max(0, min(POWER_LIMIT, systemPower))
    systemPowerBar.value = systemPower
    systemPowerBar.bar_color = \
        DOOR_CLOSED_LABEL_COLOR if (POWER_LIMIT - systemPower <= POWER_LIMIT * 0.3) else DOOR_OPEN_LABEL_COLOR
    if not powerOut and systemPower == POWER_LIMIT:
        print('Power out!')
        startMainScreenPowerOut()
        playAudio(VOICE_PLAYER_EFFECT_2, 'door')
        playAudio(VOICE_BACKGROUND, 'powerdown')
        powerOut = True
        systemPower = 0
        systemPowerBar.value = 0
        doorClosed = False
        if moveMode not in ('Door', 'Air Vent'):
            setMoveMode(('Door', 'Air Vent'))
        invokeCallbackAndCountdown('PowerReboot')

def PowerReboot():
    global powerOut
    powerOutLabel.color = LABEL_TITLE_COLOR[random.randint(0, len(LABEL_TITLE_COLOR)-1)]
    if random.randint(1, 100) <= 20:
        powerOutLabel.x = powerOutLabel.x + random.randint(-SCREEN_W, SCREEN_W) - round(powerOutLabel.width/2)
    else:
        powerOutLabel.x = round(SCREEN_W/2 - powerOutLabel.width/2)
    if random.randint(1, 100) <= 20:
        powerOutLabel.y = powerOutLabel.y + random.randint(-SCREEN_H, SCREEN_H) - round(powerOutLabel.height/2)
    else:
        powerOutLabel.y = round(SCREEN_H/2 - powerOutLabel.height/2)
    countdown, _ = getCountdownAndInterval('PowerReboot')
    if ANOMALY_ACTION_LOG and countdown % 10 == 0:
        print(f'Power reboot countdown: {int(countdown/10)}')
    if countdown == 0:
        powerOut = False
        playBackgroundAudio()
        setLabelsAndColors()
        startMainScreen()

def SelectRoom():
    global selectedRoom, pressedKey
    newRoom = selectedRoom
    if pressedKey == 'Up':
        roomChanged = True
        if selectedRoom in (3, 4, 5, 6, 7, 8):
            newRoom -= 3
        elif selectedRoom == 9:
            newRoom = 5
    elif pressedKey == 'Down':
        roomChanged = True
        if selectedRoom in (0, 1, 2, 3, 4, 5):
            newRoom += 3
    elif pressedKey == 'Left':
        roomChanged = True
        if selectedRoom in (1, 2, 4, 5, 7, 8):
            newRoom -=1
        elif selectedRoom == 9:
            newRoom = 8
    elif pressedKey == 'Right':
        roomChanged = True
        if selectedRoom in (0, 1, 3, 4, 6, 7, 8):
            newRoom += 1
        elif selectedRoom == 5:
            newRoom = 9
    if newRoom != selectedRoom:
        drawRooms[selectedRoom].fill = BLACK
        drawRooms[newRoom].fill = ROOM_SELECTED_COLOR
        roomLabels[selectedRoom].color = ROOM_LABEL_COLOR
        roomLabels[newRoom].color = ROOM_LABEL_SELECTED_COLOR
        selectedRoom = newRoom
        setLabelsAndColors()
        pressedKey = ''
        playAudio(VOICE_PLAYER_ACTION, 'tap')

def PlayerAction():
    global pressedKey, detectionRoom
    if powerOut or anomalyRoom == TARGET_ROOM:
        playAudio(VOICE_PLAYER_EFFECT, 'error')
    elif pressedKey == 'Special':
        if selectedRoom == TARGET_ROOM:
            invokeCallbackAndCountdown('Door')
        elif selectedRoom == AIR_VENT_ROOM:
            invokeCallbackAndCountdown('Zap')
        elif selectedRoom == AUDIO_ROOM:
            invokeCallbackAndCountdown('Audio')
    elif pressedKey == 'Scan':
        if selectedRoom in SCANNABLE_ROOMS:
            detectionRoom = selectedRoom
            invokeCallbackAndCountdown('Scan')
    pressedKey = ''

def Door():
    global doorClosed
    if powerOut:
        resetCountDown('Door')
    countdown, maxCountDown = getCountdownAndInterval('Door')
    if countdown == maxCountDown-2:
        doorClosed = not doorClosed
        playAudio(VOICE_PLAYER_EFFECT_2, 'door')
        setLabelsAndColors()

def Scan():
    global detectionRoom, systemPower
    if powerOut:
        resetCountDown('Scan')
    countdown, maxCountDown = getCountdownAndInterval('Scan')
    detected = (anomalyRoom == detectionRoom)
    if countdown == maxCountDown:
        if detected:
            invokeCallbackAndCountdown('ShowAnomaly')
    elif countdown == maxCountDown-2:
        if detected:
            playAudio(VOICE_PLAYER_EFFECT_2, 'windowscare')
        playAudio(VOICE_PLAYER_EFFECT, 'scan')
        systemPower += SCAN_POWER_CHANGE_LEVEL
    if countdown == 0:
        detectionRoom = -1
        drawRooms[detectionRoom].fill = BLACK
    elif countdown in (maxCountDown-2, maxCountDown-4, maxCountDown-6):
        drawRooms[detectionRoom].fill = ROOM_SCAN_DANGER_COLOR if detected else ROOM_SCAN_CLEAR_COLOR
    elif countdown in (maxCountDown-3, maxCountDown-5, maxCountDown-7):
        drawRooms[detectionRoom].fill = ROOM_SELECTED_COLOR if selectedRoom == detectionRoom else BLACK
        
def Audio():
    global anomalyRoom, systemPower
    if powerOut:
        resetCountDown('Audio')
        hideIcon('audio')
    countdown, maxCountDown = getCountdownAndInterval('Audio')
    if countdown == maxCountDown-2:
        playAudio(VOICE_PLAYER_EFFECT_2, f'lure{random.randint(1, 3)}')
        print('Lure audio played')
        if anomalyRoom not in (TARGET_ROOM, 9):
            if chance(LURED_CHANCE):
                setMoveMode(('Lure',))
                if ANOMALY_ACTION_LOG:
                    print(f'{ANOMALY_NAME} is attracted by the audio lure!')
        systemPower += AUDIO_POWER_CHANGE_LEVEL
    if countdown in (maxCountDown, maxCountDown-6):
        showIcon('audio')
    elif countdown in (maxCountDown-5, 1):
        hideIcon('audio')

def Zap():
    global anomalyRoom, systemPower
    if powerOut:
        resetCountDown('Zap')
        hideIcon('zap')
    countdown, maxCountDown = getCountdownAndInterval('Zap')
    if countdown == maxCountDown-2:
        playAudio(VOICE_PLAYER_EFFECT_2, 'zap')
        if anomalyRoom == AIR_VENT_ROOM:
            playAudio(VOICE_ANOMALY_ACTION, 'zapscream')
            anomalyRoom = WINDOW_ROOM
            setMoveMode(('Escape', 'Door'))
            if ANOMALY_ACTION_LOG:
                print(f'{ANOMALY_NAME} get zapped in the air vent!')
        systemPower += ZAP_POWER_CHANGE_LEVEL
    if countdown in (maxCountDown, maxCountDown-6):
        showIcon('zap')
    elif countdown in (maxCountDown-5, 1):
        hideIcon('zap')

def ScanCooldown():
    if powerOut:
        resetCountDown('ScanCooldown')
    countdown, maxCountDown = getCountdownAndInterval('ScanCooldown')
    scanCooldownBar.value = countdown
    if countdown == maxCountDown or countdown == 0:
        setLabelsAndColors()

def AudioCooldown():
    if powerOut:
        resetCountDown('AudioCooldown')
    countdown, maxCountDown = getCountdownAndInterval('AudioCooldown')
    audioCooldownBar.value = countdown
    if countdown == maxCountDown or countdown == 0:
        setLabelsAndColors()

def ZapCooldown():
    if powerOut:
        resetCountDown('ZapCooldown')
    countdown, maxCountDown = getCountdownAndInterval('ZapCooldown')
    zapCooldownBar.value = countdown
    if countdown == maxCountDown or countdown == 0:
        setLabelsAndColors()
    
def ShowAnomaly():
    if ANOMALY_ALWAYS_SHOWN:
        showIcon('anomaly')
    else:
        if powerOut:
            resetCountDown('ShowAnomaly')
        countdown, maxCountDown = getCountdownAndInterval('ShowAnomaly')
        if countdown == maxCountDown:
            showIcon('anomaly')
        elif countdown == 0:
            hideIcon('anomaly')

# add callbacks to countdownTable
for key, item in countdownTable.items():
    try:
        func = globals()[key]
        if callable(func):
            item['callback'] = func
    except:
        print(f'error: cannot find callback function {key}')
        sys.exit()
print('Callback functions loaded')

def invokeCallbackAndCountdown(key):
    item = countdownTable[key]
    if item['countpool'] == 0:
        if countdownTable.get(item.get('cooldown', None), {}).get('countpool', 0) > 0:
            playAudio(VOICE_PLAYER_ACTION, 'error')
        else:
            item['countpool'] = item['interval']
            if item['mode'] != 'onceAtEnd':
                item['callback']()
            
def countdownProcess():
    for key, item in countdownTable.items():
        if item['countpool'] == 0 and item['mode'] == 'continuous':
            invokeCallbackAndCountdown(key)
        elif item['countpool'] > 0:
            item['countpool'] -= 1
            if item['mode'] == 'stepping':
                item['callback']()
            if item['countpool'] == 0:
                if item['mode'] == 'onceAtEnd':
                    item['callback']()
                if item.get('cooldown', None):
                    invokeCallbackAndCountdown(item['cooldown'])

# ===== game logic - reset functions =====

def resetConfig():
    global AI, gameStatus, hour, power, selectedRoom, detectionRoom, moveMode, pressedKey, doorClosed, powerOut, systemPower
    AI = max(0, AI_START_LEVEL + (AI_FINAL_LEVEL - AI_START_LEVEL - round((AI_FINAL_LEVEL - AI_START_LEVEL) / 5) * 5))
    gameStatus = 'Ongoing'
    hour = 0
    selectedRoom = TARGET_ROOM
    detectionRoom = -1
    moveMode = 'Normal'
    pressedKey = ''
    doorClosed = False
    powerOut = False
    systemPower = 0

def resetCountdown():
    for item in countdownTable.values():
        item['countpool'] = item['interval'] if item['mode'] == 'continuous' else 0
    scanCooldownBar.value = 0
    audioCooldownBar.value = 0
    zapCooldownBar.value = 0
    systemPowerBar.value = 0

def resetRoom():
    global anomalyRoom, selectedRoom
    selectedRoom = TARGET_ROOM
    anomalyRoom = RESET_ROOMS[random.randint(0, len(RESET_ROOMS)-1)]
    roomLabels[selectedRoom].color = ROOM_LABEL_SELECTED_COLOR
    for idx in range(len(drawRooms)):
        drawRooms[idx].fill = ROOM_SELECTED_COLOR if idx == selectedRoom else BLACK

def resetGame():
    resetConfig()
    resetCountdown()
    resetRoom()
    hideIcon('all')
    setLabelsAndColors()
    setHourLabel()
    

# ===== runtime loop =====

print('Loading game logic and runtime...ok')
firstTimeRunning = True
gc.collect()
print(f'Memory used: {100 - round(gc.mem_free() / mem_limit * 100, 1)}%')

while True:
    
    # ===== reset game =====
    resetGame()
    
    # ===== start title screen =====
    startTitleScreen()
    
    # ===== start main screen =====
    startMainScreen()
    
    print('Game started')
    print(f'Time: {hour} AM, AI level: {AI}')
    if ANOMALY_ACTION_LOG:
        print(f'{ANOMALY_NAME} starts in {ROOM_NAMES[anomalyRoom]} (mode: {moveMode})')
    
    nxtTime = time.monotonic_ns()
    
    # ===== main loop =====
    while gameStatus == 'Ongoing':
    
        playBackgroundAudio()
    
        if (time.monotonic_ns() - nxtTime) < 100000000:  # 100 ms
            continue
        nxtTime = time.monotonic_ns()

        detectKeyPress()
        countdownProcess()
        display.refresh()

    # ===== end game =====
    print(f'Game orver; you {gameStatus.lower()}!')
    startEndTitleScreen()

    time.sleep(2)
