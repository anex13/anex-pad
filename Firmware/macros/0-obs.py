from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'type' : 'HID',
    'name' : 'obs', # Application name
    'macros' : [              # List of button macros...
        # 1st row ----------
        (0x004000, '< Back', [Keycode.ALT, Keycode.LEFT_ARROW]),
        (0x004000, 'Fwd >', [Keycode.CONTROL, Keycode.RIGHT_ARROW]),
        (0x400000, 'Up', [Keycode.SHIFT, ' ']),
        (0x400000, 'Down', ' '),
        (0x202000, '< Tab', [Keycode.CONTROL, Keycode.SHIFT, Keycode.TAB]),
        (0x202000, 'Tab >', [Keycode.CONTROL, Keycode.TAB]),
        (0x000040, 'Reload', [Keycode.CONTROL, 'r']),
        (0x000040, 'History', [Keycode.CONTROL, 'h']),
        (0x000040, 'Private', [Keycode.CONTROL, Keycode.SHIFT, 'p']),
        (0x101010, 'Reddit', [Keycode.CONTROL, 't', -Keycode.CONTROL,'www.reddit.com\n']),
        (0x000040, 'Dev Mode', [Keycode.F12]),
        (0x101010, 'Twitch', [Keycode.CONTROL, 't', -Keycode.CONTROL,'twitch.com\n']),
        (0x000000, '', [Keycode.CONTROL, 'w'])
    ]
}
