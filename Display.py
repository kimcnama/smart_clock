from tkinter import *
from PIL import Image, ImageTk, ImageFont, ImageDraw
import os
import datetime

image_dir = 'images'
font_path = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
colour_map = {'black':(0, 0, 0),
              'white':(255, 255, 255)}
time_font = 100
window_width = 1000
window_height = 780

def get_time():
    now = datetime.datetime.now()
    if now.second % 2:
        return "{}:{}".format(now.hour, now.minute)
    else:
        return "{} {}".format(now.hour, now.minute)

def generate_image():
    # load an image with Pillow's [Image]
    loaded_image = Image.open(os.path.join(image_dir, 'sunny.jpg'))

    draw = ImageDraw.Draw(loaded_image)

    font = ImageFont.truetype(font_path, 100)

    draw.text((loaded_image.size[0] / 3, loaded_image.size[1] / 3), get_time(), colour_map['black'], font=font)

    # convert loaded_image with Pillow's [ImageTK]
    return ImageTk.PhotoImage(loaded_image)

class myGUI(object):
    def __init__(self):
        self.root = Tk()
        self.root.title('Smart Clock')
        self.canvas = Canvas(width=window_width, height=window_height, bg='white')
        self.canvas.pack()

        self.photo = generate_image()
        self.img = self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

        self.root.after(1000, self.change_photo)
        self.root.mainloop()

    def change_photo(self):
        print("Changing Photo")
        image = generate_image()
        self.photo = image
        self.canvas.itemconfig(self.img, image=self.photo, anchor=NW)

if __name__ == "__main__":
    gui = myGUI()