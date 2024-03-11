# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Safari web browser for Mac

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                    # REQUIRED dict, must be named 'app'
    'type' : 'HID',
    'name' : 'F13', # Application name
    'macros' : [           # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x004000, 'F13', [Keycode.F13]),
        (0x004000, 'F14', [Keycode.F14]),
        (0x400000, 'F15', [Keycode.F15]), 
        (0x202000, 'F16', [Keycode.F16]),
        (0x202000, 'F17', [Keycode.F17]),
        (0x400000, 'F18', [Keycode.F18]),     
        (0x000040, 'F19', [Keycode.F19]),
        (0x000040, 'F20', [Keycode.F20]),
        (0x000040, 'F21', [Keycode.F21]),
        (0x000000, 'F22', [Keycode.F22]),
        (0x800000, 'F23', [Keycode.F23]),
        (0x101010, 'F24', [Keycode.F24]),
    ]
}
