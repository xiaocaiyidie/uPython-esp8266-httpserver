# Micropython Http Temperature Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

class Display():
    def __init__(self):
        self.d = None
        self.text = ''
        try:
            import ssd1306
            from machine import I2C, Pin
            i2c = I2C(sda=Pin(4), scl=Pin(5))
            self.d = ssd1306.SSD1306_I2C(64, 48, i2c, 60)
            print ("Open display")
        except Exception as e:
            print(e)
            print ("Cannot open display")
            self.d = None
            pass

    def texting(self, text1):
        if text1 == self.text:
            return
        self.text = text1
        if self.d != None:
            #self.d.fill(1)
            #self.d.show()
            self.d.fill(0)
            self.d.text(text1,0, 10, 1)
            self.d.show()

display = Display()
