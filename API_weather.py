import datetime
import time
import requests
import xmltodict
from Display import colour_map
import random
import os

font_colours_dict = {
    'day_cloud1':{'font':'black', 'weather':'white'},
    'day_cloud2':{'font':'yellow', 'weather':'yellow'},
    'day_cloud3':{'font':'black', 'weather':'white'},
    'day_cloud4':{'font':'black', 'weather':'black'},
    'day_cloud5':{'font':'yellow', 'weather':'white'},
    'day_cloud6':{'font':'black', 'weather':'yellow'},

    'day_rain1':{'font':'yellow', 'weather':'yellow'},
    'day_rain2':{'font':'dr', 'weather':'yellow'},
    'day_rain3':{'font':'yellow', 'weather':'yellow'},
    'day_rain5':{'font':'black', 'weather':'black'},
    'day_rain6':{'font':'black', 'weather':'green'},

    'day_sun1':{'font':'black', 'weather':'dr'},
    'day_sun2':{'font':'black', 'weather':'yellow'},
    'day_sun3':{'font':'yellow', 'weather':'yellow'},
    'day_sun5':{'font':'yellow', 'weather':'yellow'},
    'day_sun6':{'font':'yellow', 'weather':'black'},
    'day_sun7':{'font':'black', 'weather':'yellow'},

    'day_wind1':{'font':'dr', 'weather':'black'},
    'day_wind2':{'font':'black', 'weather':'black'},
    'day_wind3':{'font':'black', 'weather':'black'},
    'day_wind4':{'font':'black', 'weather':'black'},

    'night_cloud1':{'font':'yellow', 'weather':'yellow'},
    'night_cloud2':{'font':'green', 'weather':'green'},
    'night_cloud3':{'font':'yellow', 'weather':'yellow'},
    'night_cloud4':{'font':'yellow', 'weather':'yellow'},
    'night_cloud5':{'font':'yellow', 'weather':'yellow'},

    'night_rain1':{'font':'yellow', 'weather':'yellow'},
    'night_rain2':{'font':'white', 'weather':'yellow'},
    'night_rain3':{'font':'yellow', 'weather':'yellow'},
    'night_rain4':{'font':'yellow', 'weather':'yellow'},
    'night_rain5':{'font':'green', 'weather':'yellow'},

    'night_sky1':{'font':'yellow', 'weather':'yellow'},
    'night_sky2':{'font':'white', 'weather':'white'},
    'night_sky3':{'font':'yellow', 'weather':'yellow'},
    'night_sky4':{'font':'yellow', 'weather':'yellow'},
    'night_sky6':{'font':'green', 'weather':'green'},

    'snow1':{'font':'black', 'weather':'black'},
    'snow2':{'font':'teal', 'weather':'teal'},
    'snow3':{'font':'black', 'weather':'white'}
}

# Stephens Green
latitude = "53.343242"
longitude = "-6.255160"
tomorrow_hour = "20"


def get_hour_from_time_stamp(time_stamp):
    ind = time_stamp.find('T')
    return int(time_stamp[ind + 1] + time_stamp[ind + 2])

class Weather_hour:
    def __init__(self, t_from='', t_to='', symbol='', wind='', rain='', temp=''):
        self.time_from = t_from
        self.time_to = t_to
        self.day_time_symbol = symbol
        self.rain = rain
        self.wind = wind
        self.temp = temp
        self.hour = get_hour_from_time_stamp(self.time_from)

class API_weather:
    def __init__(self, latitde=latitude, lngitde=longitude):
        self.wind_threshold = 4
        self.time_stamp_last_call = time.time()
        self.lat = latitde
        self.lng = lngitde
        self.url = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast?" \
                   "lat={0};long={1};from={2}-{3}-{4}T{5}:00;to={6}-{7}-{8}T{9}:00"
        self.hourly_forecast = []

    def make_api_call(self):
        url = self.generate_url()
        response = requests.get(url)
        if response.status_code == 200:
            self.time_stamp_last_call = datetime.datetime.now()
            xml_response = xmltodict.parse(response.content.decode('utf-8'))
            self.parse_xml(xml_response)
        else:
            print("Error calling Weather API")

    def check_if_time_captured(self, t_to):
        for i, data in enumerate(self.hourly_forecast):
            if data.time_to == t_to.time_to:
                return i
        return -1

    def parse_xml(self, xml):
        xml = xml['weatherdata']['product']['time']
        for data in xml:
            weather_pt = Weather_hour(data['@from'], data['@to'])
            if self.check_if_time_captured(weather_pt) == -1:
                weather_pt.temp = data['location']['temperature']['@value']
                weather_pt.wind = data['location']['windSpeed']['@beaufort']
                self.hourly_forecast.append(weather_pt)
            else:
                i = self.check_if_time_captured(weather_pt)
                self.hourly_forecast[i].rain = data['location']['precipitation']['@value']
                self.hourly_forecast[i].day_time_symbol = data['location']['symbol']['@id']
                self.hourly_forecast[i].time_from = weather_pt.time_from

    def generate_url(self):
        now = datetime.datetime.now()
        year = str(now.year)
        month = now.month
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        day = now.day
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        hour = now.hour
        if hour < 10:
            hour = '0' + str(hour)
        else:
            hour = str(hour)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_year = str(tomorrow.year)
        tomorrow_month = tomorrow.month
        if tomorrow_month < 10:
            tomorrow_month = '0' + str(tomorrow_month)
        else:
            tomorrow_month = str(tomorrow_month)
        tomorrow_day = tomorrow.day
        if tomorrow_day < 10:
            tomorrow_day = '0' + str(tomorrow_day)
        else:
            tomorrow_day = str(tomorrow_day)
        return self.url.format(self.lat, self.lng, year, month, day, hour, tomorrow_year, tomorrow_month, tomorrow_day,
                               tomorrow_hour)

    def night_time(self):
        now = datetime.datetime.now()
        if now.hour > 21 or now.hour < 7:
            return True
        else:
            return False

    def get_font_colour(self, full_path):
        for pict in font_colours_dict.keys():
            if pict in full_path:
                pic = pict
                break
        return font_colours_dict[pic]['font'], font_colours_dict[pic]['weather']

    # return random path to background depending on weather
    def get_background_path(self, day_time_symbol=None, wind=None, test=None):
        if test:
            dir_path = 'images/backgrounds/' + test
            files = os.listdir(dir_path)
            full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
            while 'temp' in full_path:
                full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
            return full_path
        wind = int(wind)
        day_time_symbol = day_time_symbol.lower()
        if wind > self.wind_threshold:
            dir_path = 'images/backgrounds/day_wind'
            files = os.listdir(dir_path)
            full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
            font_colour, weather_font_colour = self.get_font_colour(full_path)
            return full_path, font_colour, weather_font_colour
        elif 'rain' in day_time_symbol:
            if self.night_time():
                dir_path = 'images/backgrounds/night_rain'
                files = os.listdir(dir_path)
                full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
                font_colour, weather_font_colour = self.get_font_colour(full_path)
                return full_path, font_colour, weather_font_colour
            else:
                dir_path = 'images/backgrounds/day_rain'
                files = os.listdir(dir_path)
                full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
                font_colour, weather_font_colour = self.get_font_colour(full_path)
                return full_path, font_colour, weather_font_colour
        elif 'snow' in day_time_symbol or 'sleet' in day_time_symbol:
            dir_path = 'images/backgrounds/snow'
            files = os.listdir(dir_path)
            full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
            font_colour, weather_font_colour = self.get_font_colour(full_path)
            return full_path, font_colour, weather_font_colour
        elif 'cloud' in day_time_symbol and 'sun' in day_time_symbol and not self.night_time():
            if random.randrange(0, 2) == 1:
                dir_path = 'images/backgrounds/day_cloud'
            else:
                dir_path = 'images/backgrounds/day_sun'
            files = os.listdir(dir_path)
            full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
            font_colour, weather_font_colour = self.get_font_colour(full_path)
            return full_path, font_colour, weather_font_colour
        elif 'cloud' in day_time_symbol:
            if self.night_time():
                dir_path = 'images/backgrounds/night_cloud'
                files = os.listdir(dir_path)
                full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
                font_colour, weather_font_colour = self.get_font_colour(full_path)
                return full_path, font_colour, weather_font_colour
            else:
                dir_path = 'images/backgrounds/day_cloud'
                files = os.listdir(dir_path)
                full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
                font_colour, weather_font_colour = self.get_font_colour(full_path)
                return full_path, font_colour, weather_font_colour
        elif 'sun' in day_time_symbol:
            if self.night_time():
                dir_path = 'images/backgrounds/night_sun'
                files = os.listdir(dir_path)
                full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
                font_colour, weather_font_colour = self.get_font_colour(full_path)
                return full_path, font_colour, weather_font_colour
            else:
                dir_path = 'images/backgrounds/day_sun'
                files = os.listdir(dir_path)
                full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
                font_colour, weather_font_colour = self.get_font_colour(full_path)
                return full_path, font_colour, weather_font_colour
        else:
            if self.night_time():
                dir_path = 'images/backgrounds/night_cloud'
                files = os.listdir(dir_path)
                full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
                font_colour, weather_font_colour = self.get_font_colour(full_path)
                return full_path, font_colour, weather_font_colour
            else:
                dir_path = 'images/backgrounds/day_cloud'
                files = os.listdir(dir_path)
                full_path = os.path.join(dir_path, files[random.randrange(0, len(files))])
                font_colour, weather_font_colour = self.get_font_colour(full_path)
                return full_path, font_colour, weather_font_colour

    def get_icon_path(self, day_time_symbol, wind):
        wind = int(wind)
        day_time_symbol = day_time_symbol.lower()
        if 'rain' in day_time_symbol and 'sun' in day_time_symbol:
            if 'dark' in day_time_symbol or self.night_time():
                return 'images/icon_night_rain.png'
            else:
                return "images/icon_rainsuncloud.png"
        elif 'rain' in day_time_symbol and wind > self.wind_threshold:
            if 'dark' in day_time_symbol or self.night_time():
                return 'images/wind_rain.jpeg'
            else:
                return "images/wind_rain.png"
        elif 'rain' in day_time_symbol:
            if 'dark' in day_time_symbol or self.night_time():
                return 'images/icon_night_rain.png'
            else:
                return "images/icon_rain.png"
        elif 'cloud' in day_time_symbol and 'sun' in day_time_symbol:
            if 'dark' in day_time_symbol or self.night_time():
                return "images/icon_night_cloud.png"
            else:
                return "images/icon_suncloud.png"
        elif 'cloud' in day_time_symbol:
            if 'dark' in day_time_symbol or self.night_time():
                return "images/icon_night_cloud.png"
            else:
                return "images/icon_cloudy.png"
        if 'rain' not in day_time_symbol and wind > self.wind_threshold:
            if 'dark' in day_time_symbol or self.night_time():
                return "images/icon_night_wind.png"
            else:
                return "images/icon_wind.png"
        elif 'sun' in day_time_symbol and 'cloud' in day_time_symbol:
            if 'dark' in day_time_symbol or self.night_time():
                return "images/icon_night_cloud.png"
            else:
                return "images/icon_suncloud.png"
        elif 'sun' in day_time_symbol:
            if 'dark' in day_time_symbol or self.night_time():
                return "images/icon_night_sun.png"
            else:
                return "images/icon_sun.png"
        elif 'snow' in day_time_symbol:
            return "images/icon_snow.png"
        else:
            return "images/icon_cloudy.png"

if __name__ == '__main__':
    weather = API_weather()
    weather.make_api_call()
    for hour in weather.hourly_forecast:
        print(str(hour.hour) + " " + hour.day_time_symbol + " " + hour.temp + " C")