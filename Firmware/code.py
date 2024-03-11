import board
import busio
import time
import terminalio
import displayio
import digitalio
import os
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_display_text import label
from adafruit_st7789 import ST7789
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.mouse import Mouse
from websockets import Session
import rotaryio
import keypad
import usb_hid
from adafruit_debouncer import Debouncer
import asyncio
import rtc
import socketpool
import wifi
import adafruit_ntp
import adafruit_requests as requests
import neopixel
import binascii
import json
import adafruit_hashlib as hashlib

online=False
#FIRST INIT RUN ONCE
def get_secrets():
    try:
        from secrets import secrets
    except ImportError:
        print("secrets.py import error")
        raise
    else:
        return secrets
secrets = get_secrets()    
def tftinit():
    tft_cs=board.IO34
    tft_dc=board.IO35
    tft_bl=board.IO38
    tft_sck=board.IO36
    tft_mosi=board.IO37
    #RELEASE DISPLAYS------------------------------------------------------------------------------------------------------------------------
    displayio.release_displays()


    #INIT DISPLAY----------------------------------------------------------------------------------------------------------------------------
    displaysize =(320,170)
    spi = busio.SPI(tft_sck, MOSI=tft_mosi)
    display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
    display = ST7789(
        display_bus,
        width=displaysize[0],
        height=displaysize[1],
        rowstart=0,
        colstart=35,
        backlight_pin=tft_bl,
        rotation=90+180,
    )
    return display
def wifi_conect():
    global online, secrets
    print('Conecting to WIFI')
    try:
        wifi.radio.connect(secrets["ssid"], secrets["password"])
    except ConnectionError:
        print('Conection problems')
        return None
        raise
    else:
        pool = socketpool.SocketPool(wifi.radio)
        ssl_context = ssl.create_default_context()
        online=True
        print('We are online')
        return (pool,ssl_context,None)
def get_time(pool,utc):
        print('updating time and date')
        try:
            ntp = adafruit_ntp.NTP(pool, tz_offset=utc, server='ntp0.ntp-servers.net')
        except:
            print('something going wrong with time')
        rtc.RTC().datetime = ntp.datetime
        print("Current time",time.localtime().tm_hour,":",time.localtime().tm_min)    
def base64(input):
    tmp = binascii.b2a_base64(input)
    return tmp[:-1]
class obsws:
    def __init__(self, host=None, port=4455, password=""):
        self.id = 0
        # self.thread_recv = None
        # self.eventmanager = EventManager()
        # self.answers = {}
        self.host = host
        self.port = port
        self.password = password
        self.ws = None

    def connect(self):
        global pool, ssl_context, iface
        URL = "ws://{}:{}".format(self.host, self.port)
        session = Session(pool, ssl=ssl_context, iface=iface)
        self.ws = session.client(URL)
        self._auth(self.password)

    def _auth(self, password):
        self.id += 1
        #auth_payload = {"request-type": "GetAuthRequired", "message-id": str(self.id)}
        #self.ws.send(json.dumps(auth_payload))
        result = json.loads(self.ws.recv())
        print("obsws result:", result)
        identify_message = {'op': 1, 'd': {}}
        identify_message['d']['rpcVersion'] = 1
        if result["op"]==0:
            secret = base64(
                hashlib.sha256((password + result['d']['authentication']["salt"]).encode("utf-8")).digest()
            )
            auth = base64(
                hashlib.sha256(secret + result['d']['authentication']["challenge"].encode("utf-8")).digest()
            ).decode("utf-8")
            identify_message['d']['authentication'] = auth
            self.ws.send(json.dumps(identify_message))
            result = json.loads(self.ws.recv())
            print ('ident result',result)
            if result["op"] != 2:
                raise ConnectionFailure(result["error"])

    def recv(self):
        self.ws.settimeout(0.1)
        try:
            rec = self.ws.recv()
            if rec.strip() != "":
                result = json.loads(rec)
            else:
                result = {}
            return result
        except OSError as err:
            # timeout
            if err.args[0] == 110 or err.args[0] == 116:
                return None
            else:
                raise err

    def send(self, payload):
        self.id += 1
        payload["message-id"] = str(self.id)
        self.ws.settimeout(None)
        self.ws.send(json.dumps(payload))
        # NOTE: il envoie "replay starting" "replay started" first
        # donc il ne faut pas attendre de recv() un status ok
        # result = json.loads(self.ws.recv())
        # return result
        return self.id
class Scr_state:
    def __init__(self,screen_index=0,app_index=0,last_position=0,menu_position=1,wstring='weather',timeupd=99,weather_updated=False,w_last_update=0.0) -> None:
        self.screen_index=screen_index
        self.app_index=app_index
        self.last_position=last_position
        self.menu_position=menu_position
        self.wstring=wstring
        self.timeupd=timeupd
        self.weather_updated=weather_updated
        self.w_last_update=w_last_update
class Screen:
    def __init__(self) -> None:
        statusbar = displayio.Group()
        statusbar.append(Rect(0, 0, display.width, 20, fill=0x484848))
        statusbar.append(label.Label(terminalio.FONT, text=str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min), color=0xFFFFFF, anchored_position=(2, 2), anchor_point=(0.0, 0.0)))
        statusbar.append(label.Label(terminalio.FONT, text="weather", color=0xFFFFFF, anchored_position=(display.width//2, 2), anchor_point=(0.5, 0.0)))
        statusbar.append(label.Label(terminalio.FONT, text=str(time.localtime().tm_mday)+' '+month[time.localtime().tm_mon-1], color=0xFFFFFF, anchored_position=(display.width-2, 2), anchor_point=(1.0, 0.0)))
        main_scr = displayio.Group()
        group = displayio.Group()
        header = displayio.Group()
        keysgroup=displayio.Group()
        header.append(Rect(0, 21, display.width, 20, fill=0x252525))
        header.append(label.Label(terminalio.FONT, text="", color=0xFFFFFF, anchored_position=(display.width//2, 25), anchor_point=(0.5, 0.0)))
        for key_index in range(12):
            xpos = key_index % 4
            ypos = key_index // 4
            keysgroup.append(RoundRect(x=xpos*80+5,y=ypos*36+50,width=72,height=35,r=3,fill=0x000000,outline=0x484848, stroke=2))
            group.append(label.Label(terminalio.FONT, text='', color=0xFFFFFF, anchored_position=((display.width - 1) * xpos / 4 + 41,display.height - 1 -(3 - ypos) * 36 +15),anchor_point=(0.5, 1.0)))
        main_scr.append(header)
        main_scr.append(keysgroup)
        main_scr.append(group)
        self.statusbar=statusbar
        self.main_scr=main_scr
    def update(self):
        global display,rootgroup
        if len(rootgroup)==0:          
            rootgroup.append(self.statusbar)
            rootgroup.append(self.main_scr)
        display.show(rootgroup)
        display.refresh()

"""    screen items position
statusbar scrgroup[0]
        rectangle       scrgroup[0][0]
        time            scrgroup[0][1]  left
        weather         scrgroup[0][2]  center
        date            scrgroup[0][3]  right

mainscr   scrgroup[1]

        ===macro===
    header              scrgroup[1][0]
        rectangle       scrgroup[1][0][0]
        macro name      scrgroup[1][0][1]
    keys outlines       scrgroup[1][1]
        outline         scrgroup[1][1][0:11]
    keys labels         scrgroup[1][2]
        labels          scrgroup[1][2][0:11]

        ===settings===

"""

#---------------------------------------------------SETUP--------------------------------------
encoder_pins =(board.IO2, board.IO3)
nav_pins = (board.IO1,board.IO16,board.IO21,board.IO33,board.IO18)
pixel = neopixel.NeoPixel(board.IO5, 20, brightness=1, auto_write=False)
month = ('jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec')
longpress=2 # long press in seconds
keyboard =Keyboard(usb_hid.devices)
consumer_control = ConsumerControl(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)       
obs = None
MACRO_FOLDER = '/macros'
display =tftinit()
pool,ssl_context,iface=wifi_conect()
mqtt = None
ssl_context = ssl.create_default_context()
buttons=[]
for pin in nav_pins:
    btn=digitalio.DigitalInOut(pin)
    btn.direction=digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    dbtn= Debouncer(btn)
    buttons.append(dbtn)
display.auto_refresh = False
pixel.auto_write = False
mcol=[board.IO9,board.IO10,board.IO11,board.IO12]
mrow=[board.IO6,board.IO7,board.IO8]
keys = keypad.KeyMatrix(row_pins=mrow,column_pins=mcol,columns_to_anodes=True)
rootgroup=displayio.Group()
screen = Screen()
screen.update()



def init_mqtt(pool,broker,user,key,port):
    mqtt_client = MQTT.MQTT(
    broker=broker,
    port=port,
    username=user,
    password=key,
    socket_pool=pool,
    ssl_context=ssl_context,)
    return mqtt_client
if online:
    get_time(pool,secrets["timezone"])
    #mqtt=init_mqtt(pool=pool,broker=secrets["mqtt_broker"],user=secrets["mqtt_user"],key=secrets["mqtt_pass"],port=secrets["mqtt_port"])

last_encoder_switch = False

scrmenu =('Exit','BLE connect','Status','Settings')


# MACRO APP
class App:      
    def __init__(self, appdata):
        self.type = appdata['type']
        self.name = appdata['name']
        self.macros = appdata['macros']

    def switch(self,scr_state:Scr_state):
        global screen
        if scr_state.screen_index==0:
            
            screen.main_scr[0][1].text = self.name   # Application name
            for i in range(12):
                if i < len(self.macros): # Key in use, set label + LED color
                    pixel[i] = self.macros[i][0]                    #set key glow
                    screen.main_scr[1][i].outline = self.macros[i][0]   #set key outline
                    screen.main_scr[2][i].text = self.macros[i][1]    #set key label
                else:  # Key not in use, no label or LED
                    pixel[i] = self.macros[i][0]
                    screen.main_scr[1][i].text = ''
            screen.update()
        keyboard.release_all()
        consumer_control.release()
        mouse.release_all()
        pixel.show()
def get_apps():
    apps = []
    files = os.listdir(MACRO_FOLDER)
    files.sort()
    for filename in files:
        if filename.endswith('.py') and not filename.startswith('._'):
            try:
                module = __import__(MACRO_FOLDER + '/' + filename[:-3])
                apps.append(App(module.app))
            except (SyntaxError, ImportError, AttributeError, KeyError, NameError,
                    IndexError, TypeError) as err:
                print("ERROR in", filename)
                import traceback
                traceback.print_exception(err, err, err.__traceback__)

    if not apps:
        group[13].text = 'NO MACRO FILES FOUND'
        display.refresh()
        while True:
            pass
    return apps
def sideled_notyfy(type,col,val):
    if type =="blink":
        pixel[12::]=[col]*8
        pixel.show()
        time.sleep(1)
        pixel[12::]=[0x000000]*8
        pixel.show()
    pass
def obs_notify(msg={}):
    if msg['op']==5:
        if msg['d']['eventIntent']==8:
            print (msg['d']['eventData'])
            sideled_notyfy("blink",0x152500,0)
            
    elif msg['op']==3:
        print ('reauth req')
    else:
        print (msg)

#SCREEN AND MENU
def menu_update(pressed):
    global screen_index
    if not pressed:
        if menu_position==0:
            scrgroup[0][3][3].text=''
            scrgroup[0][3][4].text=scrmenu[menu_position]
            scrgroup[0][3][5].text=scrmenu[menu_position+1]
        elif menu_position==len(scrmenu)-1:
            scrgroup[0][3][3].text=scrmenu[menu_position-1]
            scrgroup[0][3][4].text=scrmenu[menu_position]
            scrgroup[0][3][5].text=''
        else:    
            scrgroup[0][3][3].text=scrmenu[menu_position-1]
            scrgroup[0][3][4].text=scrmenu[menu_position]
            scrgroup[0][3][5].text=scrmenu[menu_position+1]
        display.refresh()
    else:
        if menu_position==0:
            screen_index=0
            set_scr()
        else:
            screen_index=0
            set_scr()
"""def set_scr():  #TODO update other apps
    if scrgroup:
        del scrgroup[0:]
    global timeupd
    statusbar = displayio.Group()
    statusbar.append(Rect(0, 0, display.width, 20, fill=0x484848))
    statusbar.append(label.Label(terminalio.FONT, text=str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min), color=0xFFFFFF, anchored_position=(2, 2), anchor_point=(0.0, 0.0)))
    statusbar.append(label.Label(terminalio.FONT, text=wstring, color=0xFFFFFF, anchored_position=(display.width//2, 2), anchor_point=(0.5, 0.0)))
    statusbar.append(label.Label(terminalio.FONT, text=str(time.localtime().tm_mday)+' '+month[time.localtime().tm_mon-1], color=0xFFFFFF, anchored_position=(display.width-2, 2), anchor_point=(1.0, 0.0)))
    scrgroup.append(statusbar)
    timeupd = time.localtime().tm_min
    if screen_index==0: #MACRO        
        maingroup = displayio.Group()
        group = displayio.Group()
        header = displayio.Group()
        keysgroup=displayio.Group()
        header.append(Rect(0, 21, display.width, 20, fill=0x252525))
        header.append(label.Label(terminalio.FONT, text="", color=0xFFFFFF, anchored_position=(display.width//2, 25), anchor_point=(0.5, 0.0)))
        for key_index in range(12):
            xpos = key_index % 4
            ypos = key_index // 4
            keysgroup.append(RoundRect(x=xpos*80+5,y=ypos*36+50,width=72,height=35,r=3,fill=0x000000,outline=0x484848, stroke=2))
            group.append(label.Label(terminalio.FONT, text='', color=0xFFFFFF, anchored_position=((display.width - 1) * xpos / 4 + 41,display.height - 1 -(3 - ypos) * 36 +15),anchor_point=(0.5, 1.0)))
        maingroup.append(header)
        maingroup.append(keysgroup)
        maingroup.append(group)
        scrgroup.append(maingroup)
        apps[app_index].switch()
        display.refresh()

    elif screen_index ==-1:  #Settings
        maingroup = displayio.Group()
        group_items = displayio.Group()
        group_status = displayio.Group()
        maingroup.append(Rect(0, 0, display.width, 20, fill=0x484848))
        maingroup.append(label.Label(terminalio.FONT, text='Setting', color=0xFFFFFF, anchored_position=(display.width//2, 2), anchor_point=(0.5, 0.0)))
        group_items.append(Rect(x=120,y=30,width=200,height=35,fill=0xbbbbbb))
        group_items.append(Rect(x=100,y=75,width=200,height=40,fill=0xffffff))
        group_items.append(Rect(x=120,y=125,width=200,height=35,fill=0xbbbbbb))
        group_items.append(label.Label(terminalio.FONT, text='1', color=0xFFFFFF, anchored_position=(165, 40), anchor_point=(0.5, 0.0)))
        group_items.append(label.Label(terminalio.FONT, text='2', color=0x000000, anchored_position=(145, 88), anchor_point=(0.5, 0.0)))
        group_items.append(label.Label(terminalio.FONT, text='3', color=0xFFFFFF, anchored_position=(165, 135), anchor_point=(0.5, 0.0)))
        group_status.append(label.Label(terminalio.FONT, text='status', color=0xFFFFFF, anchored_position=(10, 80), anchor_point=(0.0, 0.0)))
        maingroup.append(group_status)
        maingroup.append(group_items)
        scrgroup.append(maingroup)
        display.refresh()
    elif screen_index >0:  #OTHER
        if scrgroup:
            del scrgroup[0]
        
        scrgroup.append(maingroup)
        display.refresh()
"""
#set_scr()

def connectobs(obsws_ip,obsws_port,obsws_pass):
    global obs
    try:
        obs = obsws(obsws_ip, int(obsws_port),obsws_pass)
        obs.connect()
    except Exception as Ex:
        print("Exception")
        print(Ex)
        raise Ex
    try:
            if obs==None:
                connectobs()
            elif obs!=None:
                print ('obs conected')
    except Exception as Ex:
        obs = None
        print("Exception")
        print(Ex)
if online and secrets["use_obsws"]=="yes":
    connectobs(secrets["obsws_ip"],secrets["obsws_port"],secrets["obsws_secret"])
#ASYNC WORKERS
async def ws_update():
    global obs
    while True:
        if obs!=None:
            try:
                msg = json.loads(obs.ws.recv())
                obs_notify(msg)
            except:
                obs=None
            
        await asyncio.sleep(0)
async def monitor_nav(buttons,scr_state:Scr_state,apps):                                # navigation cross controll
    while True:
        for i in range(len(buttons)):
            buttons[i].update()
        if buttons[1].fell:
            print('screenindex+=1')
            pass
        elif buttons[3].fell:
            print('screen_index-=1')
            pass
        if scr_state.screen_index == -1:      # SETTINGS
            pass
        elif scr_state.screen_index == 0:     #MACRO
            if buttons[4].fell:
                if scr_state.app_index < len(apps)-1:
                    scr_state.app_index += 1
                    apps[scr_state.app_index].switch(scr_state)
                else:
                    scr_state.app_index = 0
                    apps[scr_state.app_index].switch(scr_state)
                pass
            if buttons[2].fell:
                if scr_state.app_index > 0:
                    scr_state.app_index -= 1
                    apps[scr_state.app_index].switch(scr_state)
                else:
                    scr_state.app_index = len(apps)-1
                    apps[scr_state.app_index].switch(scr_state)
                pass
        elif scr_state.screen_index == 1:     #TIME

            pass
        else:
            pass
        await asyncio.sleep(0)
async def get_weather(pool,scr_state:Scr_state,secrets):                                    # check and update weather
    if online:
        request=requests.Session(pool)
        while True: 
            print ("geting weather")
            if not scr_state.weather_updated or time.monotonic()-scr_state.w_last_update>3600.0:

                DATA_SOURCE = "http://api.openweathermap.org/data/2.5/weather?q="+secrets['city']+"&units=metric"
                DATA_SOURCE += "&appid="+secrets['openweather_token']
                try:
                    wjson=request.get(DATA_SOURCE).json()
                except:
                    print ('something wrong with weather')
                    raise
                else:
                    city=wjson['name']
                    if wjson['main']['temp']>0:
                        temp='+'+ str(int(wjson['main']['temp']))+'C'
                    elif wjson['main']['temp']<0:
                        temp= str(int(wjson['main']['temp']))+'C'
                    else:
                        temp="0C"
                    #temp=wjson['main']['temp']
                    hum=wjson['main']['humidity']
                    wind=wjson['wind']['speed']
                    icon=wjson['weather'][0]['icon']
                    weather=wjson['weather'][0]['description']
                    print(city,temp,hum,wind,icon,weather)
                    scr_state.wstring = city+' '+temp+ ' '+ weather
                    wjson={}
                    scr_state.weather_updated=True
                    scr_state.w_last_update=time.monotonic()
            await asyncio.sleep(3600)
async def monitor_enc(encoder_pins,scr_state:Scr_state): #TODO add enc actions
    with  rotaryio.IncrementalEncoder(encoder_pins[1],encoder_pins[0],2) as encoder: #if encoder inverted swap pins
        while True:
            if scr_state.screen_index==-1:            # SETTINGS
                if encoder.position>scr_state.last_position:
                    print('enc+')
                elif encoder.position<scr_state.last_position:
                    print('enc-')
                pass
            elif scr_state.screen_index==0:           # MACRO
                if encoder.position>scr_state.last_position:
                    print('enc+')
                elif encoder.position<scr_state.last_position:
                    print('enc-')
                pass
            elif scr_state.screen_index==1:           # TIME
                if encoder.position>scr_state.last_position:
                    print('enc+')
                elif encoder.position<scr_state.last_position:
                    print('enc-')
                pass
            else:                           # ELSE
                pass
            scr_state.last_position=encoder.position
            await asyncio.sleep(0)
async def mqtt_upd():#TODO add apis updates
    pass
async def monitor_matrix(scr_atate:Scr_state,apps):#TODO add apis updates
    while True:
        event = keys.events.get()
        if not event:
            await asyncio.sleep(0)
            
        else:
            key_number = event.key_number
            if event.pressed:
                print('key',key_number,"pressed")
#-------------------------------------------------------HID-------------------------------------------------------------
                if apps[scr_atate.app_index].type=='HID':
                    sequence = apps[scr_atate.app_index].macros[key_number][2]
                    for item in sequence:
                        if isinstance(item, int):
                            if item >= 0:
                                keyboard.press(item)
                            else:
                                keyboard.release(-item)
                        elif isinstance(item, float):
                            time.sleep(item)
                        elif isinstance(item, str):
                            keyboard_layout.write(item)
                        elif isinstance(item, list):
                            for code in item:
                                if isinstance(code, int):
                                    consumer_control.release()
                                    consumer_control.press(code)
                                    consumer_control.release()
                                if isinstance(code, float):
                                    time.sleep(code)
                        elif isinstance(item, dict):
                            if 'buttons' in item:
                                if item['buttons'] >= 0:
                                    mouse.press(item['buttons'])
                                else:
                                    mouse.release(-item['buttons'])
                            mouse.move(item['x'] if 'x' in item else 0,
                                                item['y'] if 'y' in item else 0,
                                                item['wheel'] if 'wheel' in item else 0)
        #-------------------------------------------------------MQTT-------------------------------------------------------------
                elif apps[scr_atate.app_index].type=='MQTT':
                    pass
                await asyncio.sleep(0)    
            else:
                for item in sequence:
                    if isinstance(item, int):
                        if item >= 0:
                            keyboard.release(item)
                    elif isinstance(item, dict):
                        if 'buttons' in item:
                            if item['buttons'] >= 0:
                                mouse.release(item['buttons'])
                        elif 'tone' in item:
                            consumer_control.release()
                await asyncio.sleep(0)
async def update_statusscr(scr_state:Scr_state,screen:Screen):
    while True:
        if time.localtime().tm_min!= scr_state.timeupd:
            screen.statusbar[1].text=str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)    #time
            screen.statusbar[2].text=scr_state.wstring
            screen.statusbar[3].text=str(time.localtime().tm_mday)+' '+month[time.localtime().tm_mon-1]
            scr_state.timeupd=time.localtime().tm_min
            screen.update()
        await asyncio.sleep(0)   
async def set_notification():
    while True:
        notify=1
        await asyncio.sleep(0)
async def main():
    apps = get_apps()
    global secrets, screen
    scr_state= Scr_state()
    apps[scr_state.app_index].switch(scr_state)

    #-----------------ASYNC TASKS-------------------------------------
    obs_task = asyncio.create_task(ws_update())
    weather_task = asyncio.create_task(get_weather(pool,scr_state,secrets))
    enc_task = asyncio.create_task(monitor_enc(encoder_pins,scr_state))
    matrix_task = asyncio.create_task(monitor_matrix(scr_state,apps))
    status_task =asyncio.create_task(update_statusscr(scr_state,screen))
    nav_task = asyncio.create_task(monitor_nav(buttons,scr_state,apps))
    await asyncio.gather(obs_task,enc_task,matrix_task,status_task,nav_task,weather_task)
asyncio.run(main())

