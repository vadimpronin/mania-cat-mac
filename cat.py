from tkinter import *

import keyboard
from PIL import ImageTk, Image
from PIL.Image import Resampling


##############################################################################

class Cat(Frame):
    def __init__(self, master, *pargs):
        Frame.__init__(self, master, *pargs)

        self.keys_map = {
            "q": ["left", 1],
            "w": ["left", 0],
            "o": ["right", 1],
            "p": ["right", 0],
        }

        self.width = 1189
        self.height = 669

        self.images = {
            "base": Image.open("images/base.png"),

            "right_00": Image.open("images/base_right.png"),
            "right_01": Image.open("images/base_0001.png"),
            "right_10": Image.open("images/base_0010.png"),
            "right_11": Image.open("images/base_0011.png"),

            "left_00": Image.open("images/base_left.png"),
            "left_01": Image.open("images/base_0100.png"),
            "left_10": Image.open("images/base_1000.png"),
            "left_11": Image.open("images/base_1100.png"),
        }

        self.master = master
        self.new_width = self.width
        self.new_height = self.height
        self.cat = "base"
        self.left_paw = None
        self.right_paw = None

        self.paw_positions = {
            "left": 0,
            "right": 0,
        }

        self.resized_images = {}

        self.resize_images()
        self.update_positions()

        self.canvas = Canvas(self.master, width=self.width, height=self.height)
        self.canvas.pack(fill=BOTH, expand=True)

        self.canvas_images = {
            "cat": self.canvas.create_image(0, 0, image=self.resized_images[self.cat], anchor='nw'),
            "left_paw": self.canvas.create_image(0, 0, image=self.resized_images[self.left_paw], anchor='nw'),
            "right_paw": self.canvas.create_image(0, 0, image=self.resized_images[self.right_paw], anchor='nw'),
        }

        self.master.bind('<Configure>', self.window_resized)

        self.redraw_all()

        keyboard.hook(self.process_key_event, False, self.process_key_event)

    def resize_images(self):
        self.resized_images = {}

        for key, image in self.images.items():
            resized_image = image.resize((self.width, self.height), Resampling.BILINEAR)
            self.resized_images[key] = ImageTk.PhotoImage(resized_image)

    def window_resized(self, event):
        if 1 != event.width != self.new_width != 1 or 1 != event.height != self.new_height:
            self.new_width = event.width
            self.new_height = event.height
            self.master.after(50, self.delayed_resize)

    def delayed_resize(self):
        if self.new_width != self.width or self.new_height != self.height:
            self.width = self.new_width
            self.height = self.new_height
            self.canvas.config(width=self.width, height=self.height)
            self.resize_images()
            self.redraw_all()

    def redraw_all(self):
        self.canvas.itemconfig(self.canvas_images["cat"], image=self.resized_images[self.cat])
        self.redraw_paws()

    def redraw_paws(self):
        self.canvas.itemconfig(self.canvas_images["left_paw"], image=self.resized_images[self.left_paw])
        self.canvas.itemconfig(self.canvas_images["right_paw"], image=self.resized_images[self.right_paw])

    def process_key_event(self, event: keyboard.KeyboardEvent):
        key_event = event.event_type
        key_name = event.name
        # print(key_name, key_event)

        need_redraw = False

        if key_name in self.keys_map:
            key_config = self.keys_map[key_name]
            new_position = self.paw_positions[key_config[0]]

            if key_event == "down":
                new_position = self.paw_positions[key_config[0]] | (1 << key_config[1])
            elif key_event == "up":
                new_position = self.paw_positions[key_config[0]] & ~(1 << key_config[1])

            if new_position != self.paw_positions[key_config[0]]:
                self.paw_positions[key_config[0]] = new_position
                need_redraw = True

        if need_redraw:
            self.update_positions()
            # print(self.left_paw, self.right_paw)
            self.redraw_all()

    def update_positions(self):
        self.left_paw = "left_" + bin(self.paw_positions["left"])[2:].zfill(2)
        self.right_paw = "right_" + bin(self.paw_positions["right"])[2:].zfill(2)


root = Tk()
root.title("Cat")
root.geometry("400x225")
root.wm_attributes("-topmost", True)

cat = Cat(root)
cat.pack(fill=BOTH, expand=YES)

root.mainloop()
