from __future__ import print_function

from PIL import Image,ImageDraw,ImageFont,ImageChops

import datetime as dt
import sched, time
import requests
import json
from lxml import html
import numpy as np

import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import logging



class InfoScreen:

    def __init__(self,test=False):
        """initilizes the screen and all functions needed"""

        # debugging and log file
        self.test = test

        logging.basicConfig(filename="logfile.log", level=logging.WARNING,
                            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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

        self.position = {
            'weather' : (10, 90)
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
                print('============================')

                logging.warning('screen cleared, ready to use')

            except:
                print('failed to initialize screen')
                logging.warning('failed to initialize screen')

        else:
            self.epd_width = 640
            self.epd_height = 384

            print('using debug mode')
            print('================')
            logging.warning('using debug mode')

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

        # start scheduler
        self.time_startup = time.time()
        self.s = sched.scheduler(time.time, time.sleep)



    def start_service(self, refresh = 60, time_end = 3600):
        """continuously updates screen"""

        self.epd.init()

        # print('updating content')
        res = self.assemble_basic_screen()
        self.draw(*res)

        # check if done
        if time_end < 0:

            if time.time() > self.time_startup + time_end:

                print('finished, timeout')

                return None

        else:

            self.epd.sleep()

            self.s.enter(refresh, time_end,
                         self.start_service, kwargs={'refresh': refresh, 'time_end': time_end})
            self.s.run()

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

        dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']

        try:
            weather_current = requests.get(link+"weather",params=params).json()
            weather_forecast= requests.get(link+"forecast",params=params).json()['list']


            current = (weather_current['weather'][0]['description'],
                       weather_current['main']['temp'] - 273.15,
                       self.weather_icon_table[weather_current['weather'][0]['icon']],
                       weather_current['wind']['speed'],
                       dirs[int(weather_current['wind']['deg']//45)])

            forecast = (weather_forecast[0]['weather'][0]['description'],
                       weather_forecast[0]['main']['temp'] - 273.15,
                       self.weather_icon_table[weather_forecast[0]['weather'][0]['icon']],
                       weather_forecast[0]['wind']['speed'],
                       dirs[int(weather_forecast[0]['wind']['deg']//45)])

            return (current, forecast)

        except:
            print('failed to fetch weather')

            return None

    def get_calendar(self):

        print('get calendar')

        now = dt.datetime.utcnow().isoformat() + 'Z'


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

                    offset = int(end[-6:-3])
                    end = dt.datetime.strptime(end[10:-6],'T%H:%M:%S+01:00')
                    end = dt.datetime.strftime(end, '%H:%M')

                else:
                    start = '.day'
                    end   = '.day'

                if day in days:
                    days[day].append((start,end, event['summary']))
                else:
                    days[day] = [(start,end, event['summary'])]

        for day in days.keys():

            days[day].sort(key=lambda tup: tup[0])

        return days

    def assemble_basic_screen(self):
        """displays basic information"""

        fonts = self.fonts
        logging.warning('updating content')
        print('\nupdating content\n' + '-'*16)

        HBlackimage = Image.new('1', (self.epd_width, self.epd_height), 255)
        HOrangeimage = Image.new('1', (self.epd_width, self.epd_height), 255)
        drawblack = ImageDraw.Draw(HBlackimage)
        draworange = ImageDraw.Draw(HOrangeimage)

        # background
        draworange.rectangle(((5,5,200,200)), fill=0)

        # draw time
        now = dt.datetime.now()

        drawblack.text((10, 10), now.strftime('%d %a'),
                       font=fonts['day'], fill=0)

        drawblack.text((10, 72), now.strftime('%B %Y'),
                       font=fonts['normal'], fill=0)
        # draw weather
        weather = self.get_weather()

        pos = self.position['weather']

        if weather:
            drawblack.text((pos[0], pos[1] + 10), weather[0][2],
                           font=fonts['weather'], fill=0)
            drawblack.text((pos[0]+40, pos[1]+5), weather[0][0],
                           font=fonts['normal'], fill=0)
            drawblack.text((pos[0]+40 ,pos[1]+20), '{:+5.1f}C  {:.1f}m/s ({})'
                           .format(weather[0][1], weather[0][3], weather[0][4]),
                           font=fonts['normal'], fill=0)

            drawblack.text((pos[0], pos[1] + 50), 'Forecast',
                           font=fonts['normal'], fill=0)
            drawblack.text((pos[0], pos[1] + 68), weather[1][2],
                           font=fonts['weather'], fill=0)
            drawblack.text((pos[0]+40, pos[1]+73), weather[1][0],
                           font=fonts['normal'], fill=0)
            drawblack.text((pos[0]+40, pos[1]+88), '{:+5.1f}C  {:.1f}m/s ({})'
                           .format(weather[1][1], weather[1][3], weather[1][4]),
                           font=fonts['normal'], fill=0)
        else:
            drawblack.text(pos, 'ERROR',
                           font=fonts['normal'], fill=0)

        # draw events
        events = self.get_calendar()

        pos_v = self.cal_pos_v
        pos = 5
        off_day = 25
        off_bar = (-5,-5,20)
        off_event = 20
        len_text = 51

        for day in sorted(events.keys()):
            pos += 5

            day_name = dt.datetime.strptime(day, '%Y-%m-%d')
            day_name = dt.datetime.strftime(day_name, '%A, %d %B')

            drawblack.text((pos_v-off_bar[0], pos), day_name,
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
