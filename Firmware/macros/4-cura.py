# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Adobe Illustrator for Mac

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                         # REQUIRED dict, must be named 'app'
    'type' : 'HID',
    'name' : 'Cura', # Application name
    'macros' : [
    
        (0x303000, ' ', ''),
        (0x101010, ' ', ''),
        (0x400000, ' ', ''),
        (0x400000, ' ', ''),
        (0x004000, 'Move', [Keycode.COMMAND, 'z']),
        (0x004000, 'Scale', [Keycode.COMMAND, 'Z']),
        (0x101010, 'Rotate', 'v'),
        (0x400000, 'Mirror', 'o'),
        (0x303000, ' ', ''),
        (0x101010, ' ', ''),
        (0x400000, ' ', ''),
        (0x400000, ' ', ''),
    ]
}
