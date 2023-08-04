from machine import UART, Pin, ADC
import _thread
from time import sleep
import gc

print('mem_free:',gc.mem_free())
print('loading keyboard firmware...')

tLock = _thread.allocate_lock()
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

KEY_CODES = {
    "NONE":0,
    "A":30,
    "B":48, 
    "C":46,
    "D":32,
    "E":18,
    "F":33,
    "G":34,
    "H":35,
    "I":23,
    "J":36,
    "K":37,
    "L":38,
    "M":50,
    "N":49,
    "O":24,
    "P":25,
    "Q":16,
    "R":19,
    "S":31,
    "T":20,
    "U":22,
    "V":47,
    "W":17,
    "X":45,
    "Y":21,
    "Z":44,
    "1":2,
    "2":3,
    "3":4,
    "4":5,
    "5":6,
    "6":7,
    "7":8,
    "8":9,
    "9":10,
    "0":11,
    "ENTER":28,
    "ESC":1,
    "BACKSPACE":14,
    "TAB":15,
    "SPACE":57,
    "MINUS":12,
    "EQUAL":13,
    "LEFTBRACE":26,
    "RIGHTBRACE":27,
    "BACKSLASH":43,
    "SEMICOLON":39,
    "APOSTROPHE":40,
    "GRAVE":41,
    "COMMA":51,
    "DOT":52,
    "SLASH":53,
    "CAPS":58,
    "F1":59,
    "F2":60,
    "F3":61,
    "F4":62,
    "F5":63,
    "F6":64,
    "F7":65,
    "F8":66,
    "F9":67,
    "F10":68,
    "F11":87,
    "F12":88,
    "HOME":102,
    "PAGEUP":104,
    "DELETE":111,
    "END":107,
    "PAGEDOWN":109,
    "RIGHT":106,
    "LEFT":105,
    "DOWN":108,
    "UP":103,
    "CTRL":97,
    "SHIFT":54,
    "ALT":100,
    "SUPER1":249,
    "SUPER2":250,
    "SUPER3":251,
    "M0":400,
    "M1":401,
    "M2":402,
    "M3":403,
    "M4":404,
    "M5":405,
    "M6":406,
    "M7":407,
    "M8":408,
    "M9":409,
    "M10":410,
    "M11":411,
    "M12":412,
    "M13":413,
    "M14":414,
    "M15":415,
    "M16":416,
    "M17":417,
    "M18":418,
    "M19":419,
    "M20":420,
    "M21":421,
    "M22":422,
    "M23":423,
    "M24":424,
    "M25":425,
    "M26":426,
    "M27":427,
    "M28":428,
    "M29":429,
    "M30":430,
    "M31":431,
    "M32":432,
    "M33":433,
    "M34":434,
    "M35":435
    }

mod_map=("SUPER1","SUPER2","SUPER3","ALT","CTRL","SHIFT")

key_map0=(("A","B","C","D","E","ESC"),\
         ("F","G","H","I","J","BACKSPACE"),\
         ("K","L","M","N","O","DELETE"),\
         ("P","Q","R","S","T","TAB"),\
         ("U","V","W","X","UP","ENTER"),\
         ("Y","Z","SPACE","LEFT","DOWN","RIGHT"))

key_map1=(("1","2","3","4","5","ESC"),\
         ("6","7","8","9","0","BACKSPACE"),\
         ("GRAVE","LEFTBRACE","RIGHTBRACE","BACKSLASH","SEMICOLON","DELETE"),\
         ("APOSTROPHE","COMMA","DOT","SLASH","MINUS","TAB"),\
         ("EQUAL","F1","F2","F3","UP","ENTER"),\
         ("F4","CAPS","SPACE","LEFT","DOWN","RIGHT"))

key_map2=(("M0","M1","M2","M3","M4","M5"),\
         ("M6","M7","M8","M9","M10","M11"),\
         ("M12","M13","M14","M15","M16","M17"),\
         ("M18","M19","M20","M21","M22","M23"),\
         ("M24","M25","M26","M27","M28","M29"),\
         ("M30","M31","M32","M33","M34","M35"))

class Power:
    def __init__(self):
        self.signal = Pin(22, Pin.OUT, Pin.PULL_UP)
        self.adc = ADC(2)
        self.voltage = 4.20
        self.voltage_flag = False
        self.last_voltage = 4.20


    def read_voltage(self):
        self.signal.value(1)
        while True:
            #read_adc = round((self.adc.read_u16()*3.13*10/65535),2)
            self.voltage = round(self.adc.read_u16()/2070,2)
            
            if self.voltage < 3.4:
                self.signal.value(0)
            
            tLock.acquire()
            self.voltage_flag = True
            tLock.release()
            
            gc.collect()
            sleep(10)
    
    def send_voltage(self):
        if  self.voltage != self.last_voltage:
            if self.voltage_flag == True:
                print(self.voltage)
                tLock.acquire()
                self.last_voltage = self.voltage
                self.voltage_flag = False
                tLock.release()
                sleep(0.02)
            
class Keypad:
    
    def __init__(self):
        self.cols=[10,9,5,2,18,19]
        self.rows=[11,6,8,3,4,7]
        self.mods=[12,13,14,15,16,17]
        self.result=[]
        self.key_map = key_map0
        self.cur_mod = 'NONE'
        self.cur_key = 'NONE'
        self.key_pressed = False
        self.mod_pressed = False
        self.cycles = 0
        
    def matrix_init(self):
        
        #setup rows in matrix
        for x in range(0,6):
            self.rows[x]=Pin(self.rows[x], Pin.OUT)
            self.rows[x].value(1)
        
        #setup columns in matrix
        for x in range(0,6):
            self.cols[x] = Pin(self.cols[x], Pin.IN, Pin.PULL_UP)
        
        #setup mods    
        for x in range(0,6):
            self.mods[x] = Pin(self.mods[x], Pin.IN, Pin.PULL_UP)

    def mods_read(self):
        mod_sum = 0
        for mod in self.mods:
            mod.value(1)
            if mod.value() == 0:
                mod_sum += 1
                self.cur_mod = mod_map[int(self.mods.index(mod))]
                mod.value(1)
            mod.value(1)
        
        if self.cur_mod == "SUPER1" or self.cur_mod == "SUPER2":
            self.key_map = key_map1
        elif self.cur_mod == "SUPER3":
            self.key_map = key_map2
        else:
            self.key_map = key_map0

        if mod_sum == 0:
            if self.mod_pressed == True:
                self.cur_mod = "NONE"
                self.mod_pressed = False
                print('3',self.mod_pressed, self.cur_mod)
        else:
            if self.mod_pressed == False:
                self.mod_pressed = True
                uart.write(f'{KEY_CODES[self.cur_mod]},{KEY_CODES[self.cur_key]},{core2.voltage}\n')
                sleep(0.02)
                print('2',self.mod_pressed, self.cur_mod)
                self.mod_key = "NONE"
            
    def matrix_read(self):
        
        key_sum = 0
        
        for switch in self.rows:
            switch.value(0)
            self.result=[self.cols[0].value(),self.cols[1].value(),self.cols[2].value(),self.cols[3].value(),self.cols[4].value(),self.cols[5].value()]
            key_sum += sum(self.result)
            if min(self.result) == 0:
                self.cur_key = self.key_map[int(self.rows.index(switch))][int(self.result.index(0))]
                switch.value(1)
            switch.value(1)
        
        if key_sum == 36:
            self.cycles = 0
            if self.key_pressed == True:
                self.cur_key = "NONE"
                self.key_pressed = False
                print('0',self.key_pressed, self.cur_key)
        else:
            if self.key_pressed == False:
                self.cycles += 1
                self.key_pressed = True
                uart.write(f'{KEY_CODES[self.cur_mod]},{KEY_CODES[self.cur_key]},{core2.voltage}\n')
                if self.cur_key == "M35":
                    core2.signal.value(0)
                print('1',self.key_pressed, self.cur_key)
                self.cur_key = "NONE"
            if self.key_pressed == True:
                self.cycles += 1
                if self.cycles > 34:
                    uart.write(f'{KEY_CODES[self.cur_mod]},{KEY_CODES[self.cur_key]},{core2.voltage}\n')
                    print('3',self.key_pressed, self.cur_key)
                    sleep(0.026)

kp = Keypad()
kp.matrix_init()
core2 = Power()
_thread.start_new_thread(core2.read_voltage, ())

print('keyboard firmware loaded!')
print('mem_free:',gc.mem_free())

while True:
    gc.collect()
    core2.send_voltage()
    kp.mods_read()
    kp.matrix_read()
    sleep(0.02)
