# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Consumer Control codes (media keys)

# The syntax for Consumer Control macros is a little peculiar, in order to
# maintain backward compatibility with the original keycode-only macro files.
# The third item for each macro is a list in brackets, and each value within
# is normally an integer (Keycode), float (delay) or string (typed literally).
# Consumer Control codes are distinguished by enclosing them in a list within
# the list, which is why you'll see double brackets [[ ]] below.
# Like Keycodes, Consumer Control codes can be positive (press) or negative
# (release), and float values can be inserted for pauses.

# To reference Consumer Control codes, import ConsumerControlCode like so...
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid import keycode
# You can still import Keycode as well if a macro file mixes types!
# See other macro files for typical Keycode examples.
micmute = keycode.Keycode(0x21b)

app = {               # REQUIRED dict, must be named 'app'
    'type' : 'HID',
    'name' : 'Media', # Application name
    'macros' : [
        (0x200000, 'Mute', [[ConsumerControlCode.MUTE]]),
        (0x000020, 'Vol+', [[ConsumerControlCode.VOLUME_INCREMENT]]),
        (0x000000, 'mic', [micmute]),
        (0x202020, 'Bright+', [[ConsumerControlCode.BRIGHTNESS_INCREMENT]]),
        (0x202000, '<<', [[ConsumerControlCode.SCAN_PREVIOUS_TRACK]]),
        (0x002000, 'Play/Pause', [[ConsumerControlCode.PLAY_PAUSE]]),
        (0x202000, '>>', [[ConsumerControlCode.SCAN_NEXT_TRACK]]),
        (0x202020, 'Bright-', [[ConsumerControlCode.BRIGHTNESS_DECREMENT]]),
        (0x000000, '', []),
        (0x000020, 'Vol-', [[ConsumerControlCode.VOLUME_DECREMENT]]),
        (0x000000, '', []),
        (0x000000, '', []),
        #(0x000000, '', [])
    ]
}
