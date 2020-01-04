import datetime
import time
import requests
from xml.etree import ElementTree
import xmltodict

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
                self.hourly_forecast[i].t_from = weather_pt.time_from

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

if __name__ == '__main__':
    weather = API_weather()
    weather.make_api_call()