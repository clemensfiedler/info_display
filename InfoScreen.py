from __future__ import print_function

from PIL import Image,ImageDraw,ImageFont,ImageChops

import datetime as dt
import asyncio
import requests
import json
from lxml import html
import numpy as np

import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class InfoScreen:

    def __init__(self,test=False):

        # read settings
        with open('settings.json') as f:
            settings = json.load(f)

        self.API_weather_key = settings['weather_api']
        self.API_weather_city = settings['city_id']

        # load fonts
        self.fonts = {
            'normal' : ImageFont.truetype('fonts/tahoma.ttf', 12),
            'large'  : ImageFont.truetype('fonts/tahoma.ttf', 24),
            'day'    : ImageFont.truetype('fonts/tahoma.ttf', 40),
            'weather': ImageFont.truetype('fonts/meteocons.ttf', 32)
        }

        # load conversion of weather icons
        with open('fonts/weather_icons.json') as f:
            self.weather_icon_table = json.load(f)

        # set offsets
        self.cal_pos_v = 250

        # initialize the screen
        if not test:
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

        else:
            self.epd_width = 640
            self.epd_height = 384

        # set up google calendar:
        self.calendar_list = settings['calendars']

        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

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

        im = HOrangeimage
        im = im.convert('RGBA')

        data = np.array(im)  # "data" is a height x width x 4 numpy array
        red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

        # Replace white with red... (leaves alpha values alone...)
        white_areas = (red == 0) & (blue == 0) & (green == 0)
        data[..., :-1][white_areas.T] = (243, 199, 87)

        im2 = Image.fromarray(data)

        im3 = HBlackimage
        im3 = im3.convert('RGBA')

        final = ImageChops.multiply(im3,im2)
        final.show()


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

    def get_calendar(self):

        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

        now = dt.datetime.utcnow().isoformat() + 'Z'
        print('Getting the upcoming 10 events')

        days = {}
        for calendarId in self.calendar_list:

            events_result = self.service\
                .events().list(calendarId=calendarId, timeMin=now,
                               maxResults=10, singleEvents=True,
                               orderBy='startTime').execute()

            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')


            for event in events:

                start = event['start'].get('dateTime',
                                           event['start'].get('date'))
                end = event['end'].get('dateTime',
                                           event['start'].get('date'))
                day = start[0:10]

                if len(start)>10:
                    start = dt.datetime.strptime(start[10:],'T%H:%M:%S+01:00')
                    start = dt.datetime.strftime(start,'%H:%M')

                    end = dt.datetime.strptime(end[10:],'T%H:%M:%S+01:00')
                    end = dt.datetime.strftime(end, '%H:%M')

                else:
                    start = '.day'
                    end   = '.day'

                if day in days:
                    days[day].append((start,end, event['summary']))
                else:
                    days[day] = [(start,end, event['summary'])]

            print(event['end'])
            for day in days:
                days[day].sort(key=lambda tup: tup[0])

            # Sort
        sorted_days = {}
        for key in sorted(days.keys()):

            day = key
            day = dt.datetime.strptime(day, '%Y-%m-%d')
            day = dt.datetime.strftime(day, '%d %B')
            sorted_days[day] = days[key]

        return sorted_days

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
        now = dt.datetime.now()

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
        # text_sport = self.get_sports()
        #
        # if len(text_sport)>0:
        #     drawblack.text((10, 170), text_sport,
        #                    font=fonts['normal'], fill=0)
        #
        # else:
        #     drawblack.text((10, 170), 'no sports',
        #                    font=fonts['normal'], fill=0)

        #draw events
        events = self.get_calendar()

        pos_v = self.cal_pos_v
        pos = 5
        off_day = 25
        off_bar = (-5,-5,20)
        off_event = 20
        len_text = 51

        for day in events:
            pos += 5

            drawblack.text((pos_v-off_bar[0], pos), day,
                           font=fonts['normal'], fill=0)

            draworange.rectangle(((pos_v, pos+off_bar[1],
                                   self.epd_width,pos+off_bar[2])), fill=0)
            pos += off_day

            for event in events[day]:

                if not event[0]=='.day':
                    drawblack.text((pos_v+10, pos), event[0] + ' - ' + event[1],
                                   font=fonts['normal'], fill=0)

                if len(event[2])>len_text:

                    text_parts = event[2].split(' ')
                    text = text_parts[0]
                    length = 0

                    for t in text_parts[1:]:
                        if length + len(t)< len_text:
                            text += ' ' + t
                            length += len(t)
                        else:
                            break

                else:
                    text = event[2]

                drawblack.text((pos_v+110, pos), text,
                               font=fonts['normal'], fill=0)

                pos += off_event

                if pos > self.epd_height-off_day:
                    break

            if pos > self.epd_height-40:
                break

        return (HBlackimage,HOrangeimage)