
# a wrapper for the crickit neopixels library to make it more like the other class i'm using
import logging
import time
from adafruit_crickit import crickit
from adafruit_seesaw.neopixel import NeoPixel



colors = {
    'off': (0,0,0),
    'white': (180,180,180),
    'red': (255,0,0),
    'green': (0,255,0),
    'blue': (0,0,255),
    'yellow': (255, 150, 0),
    'cyan': (0, 255,255),
    'purple': (180, 0, 255)
}

############
def get(obj, name, default):
    result = default
    if name in obj:
        result = obj[name]
    return result
############
def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

class MyNeoPixels:
    def __init__(self, n, seesaw=crickit.seesaw, pin=20, bpp=3, brightness=1.0, auto_write=True, pixel_order=None):
        self.numPixels=n
        self.pixels= NeoPixel(seesaw, pin, n, auto_write=False)#, bpp, brightness, auto_write, pixel_order)
        self.pixels.brightness = 0.5

    def setPixelColor(self, idx, color):
        self.pixels[idx] = color

    def show(self):
        self.pixels.show()
        return

    def fill(self, color):
        self.pixels.fill(color)

    # Define functions which animate LEDs in various ways.
    def colorWipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.numPixels):
            self.setPixelColor(i, color)
            self.show()
            time.sleep(wait_ms/1000.0)


    def theaterChase(self, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.numPixels, 3):
                    self.setPixelColor(i+q, color)
                self.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.numPixels, 3):
                    self.setPixelColor(i+q, 0)

    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):
            for i in range(self.numPixels):
                self.setPixelColor(i, wheel((i+j) & 255))
            self.show()
            time.sleep(wait_ms/1000.0)

    def rainbowCycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(self.numPixels):
                self.setPixelColor(i, wheel((int(i * 256 / self.numPixels) + j) & 255))
            self.show()
            time.sleep(wait_ms/1000.0)

    def theaterChaseRainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.numPixels, 3):
                    self.setPixelColor(i+q, wheel((i+j) % 255))
                self.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.numPixels, 3):
                    self.setPixelColor(i+q, 0)

    def set_neopixels(self, color, count):
        if count > self.numPixels:
            count = self.numPixels
        logging.info("setting %d pixesl to %s" % (count, color))
        for i in range(0, self.numPixels):
            if i < count:
                self.setPixelColor(i, color)
            else:
                self.setPixelColor(i, colors['off'])
        self.show()

    # health will be a setting of 10 pixels, and the number will be out of 100
    def health(self, color, health, tip = 'off', wait_ms=50):
        self.set_neopixels(color, health)
        time.sleep(0.002)
        self.setPixelColor(self.numPixels-1, colors[tip])
        self.show()

    ##############
    operations = {
        # custom = has A, B, C, D
        #'magic_item': magic_item,
        # needs colour and count
        'set': set_neopixels,
        'health': health,
        #needs colour
        'colourwipe': colorWipe,
        'theatrechase': theaterChase,
        #no colour option
        'rainbow': rainbow,
        'rainbow_cycle': rainbowCycle,
    }
    ###############
    def play(self, payload = {}):
        operationname = get(payload, 'operation', 'colourwipe')
        operation = get(MyNeoPixels.operations, operationname, MyNeoPixels.operations['colourwipe'])
        logging.info("playing %s" % operationname)

        if operationname == 'magic_item':
            operation(self, payload)
            return

        if operationname == 'rainbow' or operationname == 'rainbow_cycle':
            operation(self)
            return

        colourname = get(payload, 'colour', 'off')
        colour = get(colors, colourname, colors['off'])
        # TODO: maybe change to using HTML colors #000000 style?
        if operationname == 'colourwipe' or operationname == 'theatrechase':
            operation(self, colour)
            return

        count = get(payload, 'count', 10)
        operation(self, colour, count)


