from tkinter import *
from PIL import Image, ImageTk, ImageFont, ImageDraw
import os
import datetime
import random

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
        loaded_image = loaded_image.resize((window_width, window_height),resample=Image.BICUBIC)
        draw = ImageDraw.Draw(loaded_image)

        font = ImageFont.truetype(font_path, 100)

        draw.text((loaded_image.size[0] / 3, loaded_image.size[1] / 3), self.get_time(), colour_map['black'], font=font)

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