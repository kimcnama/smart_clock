from tkinter import *
from PIL import Image, ImageTk, ImageFont, ImageDraw
import os
import datetime
import random
from API_bus import API_bus
from API_weather import API_weather

image_dir = 'images'
font_path = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
colour_map = {'black':(0, 0, 0),
              'white':(255, 255, 255)}
time_font = 100
window_width = 1000
window_height = 780

class Display(object):
    def __init__(self):
        self.root = Tk()
        self.bus = API_bus("184")
        self.weather = API_weather()
        self.refresh_time = 1000
        self.root.title('Smart Clock')
        self.canvas = Canvas(width=window_width, height=window_height, bg='white')
        self.canvas.pack()

        self.photo = self.generate_image()
        self.img = self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

        self.root.after(self.refresh_time, self.change_photo)
        self.root.mainloop()

    def change_photo(self):
        self.photo = self.generate_image()
        self.canvas.itemconfig(self.img, image=self.photo, anchor=NW)
        self.root.after(self.refresh_time, self.change_photo)

    def generate_image(self):
        # load an image with Pillow's [Image]
        images = os.listdir(image_dir)
        loaded_image = Image.open(os.path.join(image_dir, images[random.randrange(0, len(images))]))
        loaded_image = loaded_image.resize((window_width, window_height), resample=Image.BICUBIC)
        draw = ImageDraw.Draw(loaded_image)

        # clock
        font = ImageFont.truetype(font_path, 100)
        draw.text((loaded_image.size[0] / 3, loaded_image.size[1] / 3), self.get_time(), colour_map['black'], font=font)

        # bus
        font = ImageFont.truetype(font_path, 68)
        bus_str = ""
        now = datetime.datetime.now()
        if now.second % self.bus.frequency_of_call == 0 and now.hour > 5:
            self.bus.make_api_call()
        elif self.bus.empty_msg not in self.bus.bus_info and now.hour <= 5:
            self.bus.make_api_call()
        for i in range(len(self.bus.bus_info)):
            if not bus_str:
                bus_str = "{}".format(self.bus.bus_info[i])
            else:
                bus_str = "{}\n{}".format(bus_str, self.bus.bus_info[i])
            if i > 4:
                break
        draw.text((0, 0), bus_str, colour_map['black'], font=font)

        if now.minute == 1 or not self.weather.hourly_forecast:
            self.weather.make_api_call()
        weather_str = ""
        for i, hour in enumerate(self.weather.hourly_forecast):
            if not weather_str:
                weather_str = "{} {} {}C".format(hour.hour, hour.day_time_symbol, hour.temp)
            else:
                weather_str = "{}\n{} {} {}C".format(weather_str, hour.hour, hour.day_time_symbol, hour.temp)
            if i > 12:
                break
        font_weather = ImageFont.truetype(font_path, 40)
        draw.text((600, 0), weather_str, colour_map['black'], font=font_weather)

        # convert loaded_image with Pillow's [ImageTK]
        return ImageTk.PhotoImage(loaded_image)

    def get_time(self):
        now = datetime.datetime.now()
        if now.hour < 10:
            hour = "0{}".format(now.hour)
        else:
            hour = now.hour
        if now.minute < 10:
            minute = "0{}".format(now.minute)
        else:
            minute = now.minute
        if now.second % 2:
            return "{}:{}".format(hour, minute)
        else:
            return "{} {}".format(hour, minute)

if __name__ == "__main__":
    gui = Display()