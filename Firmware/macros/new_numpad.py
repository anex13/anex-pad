# SPDX-FileCopyrightText: 2021 Emma Humphries for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Universal Numpad

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                # REQUIRED dict, must be named 'app'
    'type' : 'HID',
    'name' : 'Numpad', # Application name
    'macros' : [       # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x202000, '7', ['7']),
        (0x202000, '8', ['8']),
        (0x202000, '9', ['9']),
        (0x202000, '4', ['4']),
        # 2nd row ----------
        (0x202000, '5', ['5']),
        (0x202000, '6', ['6']),
        (0x202000, '1', ['1']),
        (0x202000, '2', ['2']),
        # 3rd row ----------
        (0x202000, '3', ['3']),
        (0x101010, '*', ['*']),
        (0x800000, '0', ['0']),
        (0x101010, '#', ['#']),
        # Encoder ----------
        (0x000000, '', [Keycode.BACKSPACE]), #but
        (0x800000, '0', ['0']), #enc+
        (0x101010, '#', ['#']) #enc-
    ]
}
"""
-------------------EXAMPLES---------------------------------


app = {                # REQUIRED dict, must be named 'app'
    'type' : 'MQTT',
    'name' : 'lights', # Application name
    'macros' : [       # List of button macros...
        # COLOR    NAME    ['TOPIC','TYPE','VALUE']
        # 1st row ----------
        (0x202000, 'togle light' , ['light1', 'on/off','']),
        (0x202000, 'color +', ['light2', 'RGB+',10]),
        (0x202000, 'color -', ['light2', 'RGB-',10]),
        (0x202000, 'vol+', ['vol','Vol+','10']),
        # 2nd row ----------
        (0x000000, '', ['']),
        (0x000000, '', ['']),
        (0x000000, '', ['']),
        (0x000000, 'vol-', ['vol','Vol-','10']),
        # 3th row ----------
        (0x000000, '', ['']),        
        (0x000000, '', ['']),
        (0x800000, '', ['']),
        (0x101010, '', ['']),
        # Encoder -----------
        (0x000000, '', [Keycode.BACKSPACE]),
        (0x800000, '0', ['0']),  #enc+
        (0x101010, '#', ['#'])   #enc-
    ]
}

app = {                # REQUIRED dict, must be named 'app'
    'type' : 'HTTPAPI',
    'name' : 'lights', # Application name
    'macros' : [       # List of button macros...
        # COLOR    URI    VALUE
        # 1st row ----------
        (0x202000, 'light1', 'on/off'),
        (0x202000, 'light2', 'RGB+'),
        (0x202000, 'light2', 'RGB-'),
        (0x202000, 'vol', ['Vol+','10']),
        # 2nd row ----------
        (0x000000, '', ['']),
        (0x000000, '', ['']),
        (0x000000, '', ['']),
        (0x000000, 'vol', ['Vol-','10']),
        # 3th row ----------
        (0x000000, '', ['']),        
        (0x000000, '', ['']),
        (0x800000, '', ['']),
        (0x101010, '', ['']),
        # Encoder -----------
        (0x000000, '', [Keycode.BACKSPACE]),
        (0x800000, '0', ['0']),  #enc+
        (0x101010, '#', ['#'])   #enc-
    ]
}


"""