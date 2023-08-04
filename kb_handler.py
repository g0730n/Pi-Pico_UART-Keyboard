import os
import serial
import keyboard
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

class Keypad:
    def __init__(self):
        self.ser = serial.Serial("/dev/serial0", 9600) #Open port with baud rate
        self.s_keys = (54,97,100,249,250,251) #54=shift, 97=control, 100= alt, 249=super1, 250=super2, 251=super3
        self.cur_key = 0
        self.cur_mod = 0
        self.voltage = 0.0
        self.max_voltage = 4.0
        self.min_voltage = 3.0
        self.volt_file = "/home/gordon/ramdisk/.voltage"
        self.prev_mod = 0
        self.buffer = []
        self.macros = {
            400: "ls -a",
            401: "cd ..",
            402: "pwd",
            403: "python3",
            404: "clear",
            405: "sudo apt update",
            406: "sudo apt upgrade",
            407: "lsblk",
            408: "cd ..",
            409: "ps",
            410: "410",
            411: "411",
            412: "412",
            413: "413",
            414: "414",
            415: "415",
            416: "416",
            417: "417",
            418: "418",
            419: "grep",
            420: "420",
            421: "421",
            422: "tmux",
            423: "423",
            424: "424",
            425:(97,48,46),  #ctrl+B C
            426:(97,48,49),  #ctrl+B N
            427:(97,48,26),  #ctrl+B [
            428:(97,48,54,8), #ctrl+B &
            429: "429",
            430: "backlight down",
            431: "backlight up",
            433: "433",
            432: "backlight off",   
            434: "434",
            435: "shut down"
            }
        self.bl = GPIO.PWM(18, 64)
        self.bl_lvl = 100
        self.loop_cycles = 0
    
    def volt_log(self,v):
        bat_percent = int((v-self.min_voltage)/(self.max_voltage-self.min_voltage)*100)
        if bat_percent > 100:
            bat_percent = 100
        with open(self.volt_file, "w") as f:
            f.write(f'{bat_percent}%')

    def mod_key(self):
        if self.cur_mod == 249:
            if self.cur_key == 103: #up
                self.cur_key = 104   #page_up
            if self.cur_key == 108: #down
                self.cur_key = 109   #page_down
            if self.cur_key == 105: #left
                self.cur_key = 102   #home
            if self.cur_key == 106: #right
                self.cur_key = 107   #end
            keyboard.send(self.cur_key)
        else:
            if self.cur_mod == 250:
                self.cur_mod = 54
            keyboard.press(self.cur_mod)
            keyboard.send(self.cur_key)
            keyboard.release(self.cur_mod)


    def bl_control(self, cmd):
        if cmd == 'off':
            if self.bl_lvl != 0:
                self.bl_lvl = 0
            else:
                self.bl_lvl = 50
            self.bl.start(self.bl_lvl)
        if cmd == 'up':
            if self.bl_lvl < 91:
                self.bl_lvl += 10
                self.bl.start(self.bl_lvl)
        if cmd == 'down':
            if self.bl_lvl > 9:
                self.bl_lvl -= 10
                self.bl.start(self.bl_lvl)
    
    def macro_key(self,m_key):
        if type(self.macros[m_key]) == str:
                if m_key == 430:
                    self.bl_control('down')
                if m_key == 431:
                    self.bl_control('up')
                elif m_key == 432:
                    self.bl_control('off')
                else:
                    #pass
                    keyboard.write(self.macros[m_key])
                    keyboard.send('enter')

kp = Keypad()
kp.bl.start(100)
kp.macro_key(422)
kp.cur_key = 0
sleep(0.2)

while True:
    received_data = kp.ser.readline()
    try:
        key_string = str(received_data, encoding='utf8').strip()
        kp.buffer = key_string.split(",")
        kp.cur_mod = int(kp.buffer[0])
        kp.cur_key = int(kp.buffer[1])
        kp.voltage = float(kp.buffer[2])
        #print(kp.buffer)
    except Exception as error:
        os.system('echo serial read error')

    if kp.loop_cycles > 10:
        kp.loop_cycles = 0
        kp.volt_log(kp.voltage)
    else:
        kp.loop_cycles += 1
    
    if kp.cur_key > 399 and kp.cur_key < 436:
        kp.macro_key(kp.cur_key)
    elif kp.cur_mod in kp.s_keys:
        kp.mod_key()
    else:
        keyboard.send(kp.cur_key)    

#kp.bl_control('off')
