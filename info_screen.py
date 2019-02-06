import epd7in5b
from PIL import Image,ImageDraw,ImageFont

import datetime
import traceback
import asyncio
import requests
import json

# read settings
with open('settings.json') as f:
    settings = json.load(f)

API_weather_key  = settings['weather_api']
API_weather_city = settings['city_id']

# initialize the display
epd = epd7in5b.EPD()
epd.init()
epd.Clear(0xFF)
print('Clear done')


# define fonts
font = ImageFont.truetype('fonts/FFFFORWA.TTF', 12)
font_large = ImageFont.truetype('fonts/FFFFORWA.TTF', 24)
font_weather = ImageFont.truetype('fonts/artill_clean_icons.otf', 12)

def display_basic_screen(end_time, loop):
    """displays basic information
    """

    print('updating basic screen')
    HBlackimage = Image.new('1', (epd7in5b.EPD_WIDTH, epd7in5b.EPD_HEIGHT), 255)
    HOrangeimage = Image.new('1', (epd7in5b.EPD_WIDTH, epd7in5b.EPD_HEIGHT), 255)
    drawblack = ImageDraw.Draw(HBlackimage)
    draworange = ImageDraw.Draw(HOrangeimage)

    current_time = datetime.datetime.now().strftime('%a, %d-%m-%Y %H:%M')
    drawblack.text((10, 10), current_time, font = font, fill = 0)

    print('get weather')
    try:
        weather_response = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"appid":API_weather_key, "id":API_weather_city}).json()
        forecast_response = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={"appid":API_weather_key, "id":API_weather_city}).json()

        icon_link = 'http://openweathermap.org/img/w/{}.png'.format(
                    weather_response['weather'][0]['icon'])
        name = weather_response['weather'][0]['description']
        temperature = weather_response['main']['temp'] - 273.15

        drawblack.text((10, 30), name + '{:+5.1f}C'.format(temperature),
            font = font, fill = 0)

    except:
        print('ERROR: fetching weather failed')

    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HOrangeimage))

    if (loop.time() + 1.0) < end_time:
        loop.call_later(5, display_basic_screen, end_time, loop)

    else:
        epd.Clear(0xFF)
        loop.stop()

def turn_off():
    epd.Clear(0xFF)
    epd.sleep()

# start event loop
loop = asyncio.get_event_loop()
end_time = loop.time() + 600.0
loop.call_soon(display_basic_screen, end_time, loop)

try:
    loop.run_forever()
finally:
    loop.close()
