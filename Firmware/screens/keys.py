

import terminalio
import displayio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
display_width=240
display_height=135

maingroup = displayio.Group()
group = displayio.Group()
keysgroup=displayio.Group()
for key_index in range(12):
    xpos = key_index % 4
    ypos = key_index // 4
    keysgroup.append(RoundRect(x=xpos*60,y=ypos*36+25,width=58,height=35,r=3,fill=0x000000,outline=0x484848, stroke=2))
    group.append(label.Label(terminalio.FONT, text='', color=0xFFFFFF, anchored_position=((display_width - 1) * xpos / 4 + 30,display_height - 1 -(3 - ypos) * 36 +20),anchor_point=(0.5, 1.0)))
group.append(Rect(0, 0, display_width, 20, fill=0x484848))
group.append(label.Label(terminalio.FONT, text='', color=0xFFFFFF, anchored_position=(display_width//2, 2), anchor_point=(0.5, 0.0)))
maingroup.append(keysgroup)
maingroup.append(group)


screen = {
    'name': 'keys',
    'scr': maingroup
}