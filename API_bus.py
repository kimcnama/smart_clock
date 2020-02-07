import requests
import json
import time

class API_bus:
    def __init__(self, stop_num):
        self.stop_num = stop_num
        self.url = "https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid={}&format=json".format(self.stop_num)
        self.time_stamp_last_call = time.time()
        self.bus_info = []
        # seconds
        self.frequency_of_call = 20
        self.empty_msg = "No RTPI Info"

    def make_api_call(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                json_response = json.loads(response.content.decode('utf-8'))
                if json_response:
                    # time in seconds
                    self.bus_info = []
                    self.time_stamp_last_call = time.time()
                    results = json_response['results']
                    for bus in results:
                        if 'Due' in bus['duetime']:
                            self.bus_info.append("{} in {}".format(bus['route'], bus['duetime']))
                        else:
                            self.bus_info.append("{} in {}mins".format(bus['route'], bus['duetime']))
                    if not self.bus_info:
                        self.bus_info = [self.empty_msg]
            else:
                print("Error calling Bus API stop: {}".format(self.stop_num))
        except:
            print("Error calling Bus API stop: {}".format(self.stop_num))
            self.bus_info = [self.empty_msg]

if __name__ == '__main__':
    bus = API_bus("184")
    bus.make_api_call()
    for i in bus.bus_info:
        print(i)