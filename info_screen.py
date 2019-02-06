import epd7in5b
from PIL import Image,ImageDraw,ImageFont

import datetime
import traceback
import asyncio

# initialize the display
epd = epd7in5b.EPD()
epd.init()
epd.Clear(0xFF)
print('Clear done')


# define fonts
font = ImageFont.truetype('fonts/FFFFORWA.TTF', 24)
font_large = ImageFont.truetype('fonts/FFFFORWA.TTF', 48)

def display_basic_screen(end_time, loop):
    """displays basic information
    """

    HBlackimage = Image.new('1', (epd7in5b.EPD_WIDTH, epd7in5b.EPD_HEIGHT), 255)
    HOrangeimage = Image.new('1', (epd7in5b.EPD_WIDTH, epd7in5b.EPD_HEIGHT), 255)
    drawblack = ImageDraw.Draw(HBlackimage)
    draworange = ImageDraw.Draw(HOrangeimage)

    current_time = datetime.datetime.now().strftime('%a, %d-%m-%Y %H:%M')
    drawblack.text((10, 10), current_time, font = font, fill = 0)

    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HOrangeimage))

    if (loop.time() + 1.0) < end_time:
        loop.call_later(5, display_date, end_time, loop)

    else:
        epd.Clear(0xFF)
        loop.stop()

def turn_off():
    epd.Clear(0xFF)
    epd.sleep()

# start event loop
loop = asyncio.get_event_loop()
end_time = loop.time() + 60.0
loop.call_soon(display_date, end_time, loop)

try:
    loop.run_forever()
finally:
    loop.close()
