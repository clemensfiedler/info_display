from PIL import Image,ImageDraw,ImageFont

import datetime
import asyncio
import requests
import json
from lxml import html

class InfoScreen:

    def __init__(self):

        # read settings
        with open('settings.json') as f:
            settings = json.load(f)

        self.API_weather_key = settings['weather_api']
        self.API_weather_city = settings['city_id']

        # load fonts
        self.fonts = {
            'normal' : ImageFont.truetype('fonts/FFFFORWA.TTF', 12),
            'large'  : ImageFont.truetype('fonts/FFFFORWA.TTF', 24),
            'day'    : ImageFont.truetype('fonts/FFFFORWA.TTF', 40),
            'weather': ImageFont.truetype('fonts/meteocons.ttf', 32)
        }

        # load conversion of weather icons
        with open('fonts/weather_icons.json') as f:
            self.weather_icon_table = json.load(f)

        # initialize the screen
        try:
            import epd7in5b
            self.epd = epd7in5b.EPD()
            self.epd.init()
            self.epd.Clear(0xFF)
            self.epd_width = epd7in5b.EPD_WIDTH  # 640
            self.epd_height = epd7in5b.EPD_HEIGHT  # 384
            print('screen cleared, ready to use')

        except:
            print('failed to initialize screen')
            self.epd_width = 640
            self.epd_height = 384

    def draw(self, HBlackimage, HOrangeimage):
        """ takes the two layers and displays them"""
        epd = self.epd

        epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HOrangeimage))

    def clear(self):
        """Clears the screen"""

        self.epd.Clear(0xFF)
        print('Cleared')

    def draw_test(self, HBlackimage, HOrangeimage):
        """ takes the two layers and displays them for testing"""
        HBlackimage.show()
        HOrangeimage.show()

    def get_weather(self):
        """ downloads information on weather"""
        print('get weather')
        link = "http://api.openweathermap.org/data/2.5/"
        params ={"appid": self.API_weather_key, "id": self.API_weather_city}

        try:
            weather_current = requests.get(link+"weather",params=params).json()
            weather_forecast= requests.get(link+"forecast",params=params).json()

            name = weather_current['weather'][0]['description']
            temp = weather_current['main']['temp'] - 273.15
            icon = weather_current['weather'][0]['icon']
            icon = self.weather_icon_table[icon]

            return (name,temp,icon)

        except:
            print('failed to fetch weather')

            return None

    def get_sports(self):
        """ get information on sports schedule"""
        print('fetching sports schedule')
        link_swimming = 'https://www.sportintilburg.nl/accommodaties/drieburcht/openingstijden'

        selector = '//*[@id="content"]/div[2]/section[2]/div/div[1]/div[1]/div[2]/a'

        sports = ''

        try:
            swimming = []
            data = requests.get(link_swimming).content
            html_code = html.fromstring(data)
            res = html_code.xpath(selector)

            for i in res:
                if i[0][1].text == 'Banenzwemmen (Sportbad)':
                   swimming.append(i[0][0].text)

        except:
            print('error: get swimming times')

        if len(swimming)>0:
            sports += 'Swimming\n' + '\n'.join(swimming)


        return sports


    def assemble_basic_screen(self):
        """displays basic information"""

        fonts = self.fonts

        print('updating basic screen')

        HBlackimage = Image.new('1', (self.epd_width, self.epd_height), 255)
        HOrangeimage = Image.new('1', (self.epd_width, self.epd_height), 255)
        drawblack = ImageDraw.Draw(HBlackimage)
        draworange = ImageDraw.Draw(HOrangeimage)

        # background #todo how to write this?
        draworange.rectangle(((0,0,200,165)), fill=0)

        # draw time
        now = datetime.datetime.now()

        drawblack.text((10, 10), now.strftime('%d %a'),
                       font=fonts['day'], fill=0)

        drawblack.text((10, 72), now.strftime('%B %Y'),
                       font=fonts['normal'], fill=0)
        # draw weather
        weather = self.get_weather()

        if weather:
            drawblack.text((10, 90), weather[0] + '{:+5.1f}C'.format(weather[1]),
                           font=fonts['normal'], fill=0)
            drawblack.text((10, 120), weather[2],
                           font=fonts['weather'], fill=0)
        else:
            drawblack.text((10, 90), 'ERROR',
                           font=fonts['normal'], fill=0)

        #draw sports
        text_sport = self.get_sports()

        if len(text_sport)>0:
            drawblack.text((10, 170), text_sport,
                           font=fonts['normal'], fill=0)

        else:
            drawblack.text((10, 170), 'no sports',
                           font=fonts['normal'], fill=0)

        return (HBlackimage,HOrangeimage)