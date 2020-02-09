from tkinter import *
from PIL import Image, ImageTk, ImageFont, ImageDraw
import datetime
from API_bus import API_bus
import API_weather

image_dir = 'images'
clock_font_sz = 210
weather_font_sz = 20
bus_font_sz = 50
font_path = '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'
font_bold_path = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
colour_map = {'black':(0, 0, 0),
              'white':(255, 255, 255),
              'grey':(160, 160, 160),
              'yellow':(255, 255, 102),
              'green':(0, 255, 0),
              'pink':(255, 102, 255),
              'red':(255, 0, 0),
              'dr':(153, 0, 0),
              'teal':(0, 102, 102)}
font_colour = colour_map['black']

time_font = 100
window_width = 1050
window_height = 540

class Display(object):
    def __init__(self):
        self.root = Tk()
        self.bus = API_bus("184")
        self.bus.make_api_call()
        self.weather = API_weather.API_weather()
        self.weather.make_api_call()
        self.refresh_time = 900
        self.root.title('Smart Clock')
        self.clock_font = ImageFont.truetype(font_bold_path, clock_font_sz)
        self.clock_font_colour = colour_map['black']
        self.bus_font = ImageFont.truetype(font_path, bus_font_sz)
        self.weather_font = ImageFont.truetype(font_bold_path, weather_font_sz)
        self.weather_font_colour = colour_map['black']
        self.canvas = Canvas(width=window_width, height=window_height, bg='white')
        self.canvas.pack()
        self.weather_hours_displayed = 12
        self.weather_icon_dim = int(window_width / self.weather_hours_displayed)
        self.background_second_change = 10
        self.loaded_image = None
        self.img_path = None

        self.photo = self.generate_image()
        self.img = self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.root.after(self.refresh_time, self.change_photo)
        self.root.mainloop()

    def change_photo(self):
        self.photo = self.generate_image()
        self.canvas.itemconfig(self.img, image=self.photo, anchor=NW)
        # Open Lexis surface plot, trim whitespace, paste into canvas
        self.root.after(self.refresh_time, self.change_photo)

    def generate_image(self):
        # load an image with Pillow's [Image]
        if self.loaded_image is None or datetime.datetime.now().second % self.background_second_change == 0:
            self.img_path, c_font, w_font = self.weather.get_background_path(
                self.weather.hourly_forecast[0].day_time_symbol, self.img_path, self.weather.hourly_forecast[0].wind)
            self.clock_font_colour = colour_map[c_font]
            self.weather_font_colour = colour_map[w_font]

        self.loaded_image = None
        self.loaded_image = Image.open(self.img_path)
        self.loaded_image = self.loaded_image.resize((window_width, window_height), resample=Image.BICUBIC)

        # Weather icons
        for i in range(self.weather_hours_displayed):
            icon = Image.open(self.weather.get_icon_path(self.weather.hourly_forecast[i].day_time_symbol,
                                                         self.weather.hourly_forecast[i].wind))
            icon = icon.resize((self.weather_icon_dim, self.weather_icon_dim), resample=Image.BICUBIC)
            try:
                self.loaded_image.paste(icon, (self.weather_icon_dim * i, window_height - self.weather_icon_dim), icon)
            except:
                self.loaded_image.paste(icon, (self.weather_icon_dim * i, window_height - self.weather_icon_dim))
        draw = ImageDraw.Draw(self.loaded_image)

        # clock
        draw.text(((self.loaded_image.size[0] / 3) + 50, (self.loaded_image.size[1] / 3) - 50), self.get_time(),
                  self.clock_font_colour, font=self.clock_font)

        # bus
        bus_str = ""
        now = datetime.datetime.now()
        if now.second % self.bus.frequency_of_call == 0 and now.hour > 5:
            self.bus.make_api_call()
        elif self.bus.empty_msg not in self.bus.bus_info and now.hour <= 5:
            self.bus.make_api_call()
        for i in range(len(self.bus.bus_info)):
            bus_str = "{}\n{}".format(bus_str, self.bus.bus_info[i])
            if i > 5:
                break
        draw.text((0, 0), bus_str, self.clock_font_colour, font=self.bus_font)

        # Weather
        if (now.minute == 1 and now.second == 3) or not self.weather.hourly_forecast:
            self.weather.make_api_call()

        for i, hour in enumerate(self.weather.hourly_forecast):
            weather_str = "{}h\n{}°".format(hour.hour, hour.temp)
            draw.text((int(self.weather_icon_dim/2)-12+self.weather_icon_dim*i, window_height - self.weather_icon_dim - 25)
                      ,weather_str, self.weather_font_colour, font=self.weather_font)

        # convert loaded_image with Pillow's [ImageTK]
        return ImageTk.PhotoImage(self.loaded_image)

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