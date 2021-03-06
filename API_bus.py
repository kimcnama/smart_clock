import requests
import json
import time

class API_bus:
    def __init__(self, num):
        self.stop_num = num
        self.url = "https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid={}&format=json".format(self.stop_num)
        self.time_stamp_last_call = time.time()
        self.bus_info = []

    def make_api_call(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            json_response = json.loads(response.content.decode('utf-8'))
            if json_response:
                # time in seconds
                self.bus_info = []
                self.time_stamp_last_call = time.time()
                results = json_response['results']
                for bus in results:
                    self.bus_info.append("{} in {} mins".format(bus['route'], bus['duetime']))
                for bus in self.bus_info:
                    print(bus + '\n')

if __name__ == '__main__':
    bus = API_bus("184")
    bus.make_api_call()