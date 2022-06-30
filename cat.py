from tkinter import *

from ApplicationServices import kCGEventKeyDown, kCGEventKeyUp, CGEventMaskBit, CGEventTapCreate, \
    kCGSessionEventTap, kCGHeadInsertEventTap, CFMachPortCreateRunLoopSource, kCFAllocatorDefault, CFRunLoopAddSource, \
    CFRunLoopGetCurrent, kCFRunLoopCommonModes, CGEventTapEnable, kCGKeyboardEventKeycode, CGEventGetIntegerValueField, \
    kCGKeyboardEventAutorepeat
from PIL import ImageTk, Image
from PIL.Image import Resampling

##############################################################################


root = Tk()
root.title("Cat")
root.geometry("400x225")
root.wm_attributes("-topmost", True)


class Cat(Frame):
    def __init__(self, master, *pargs):
        Frame.__init__(self, master, *pargs)

        self.keys_map = {
            0xc: ["left", 2],
            0xd: ["left", 1],
            0x1f: ["right", 2],
            0x23: ["right", 1],
        }

        self.width = 400
        self.height = 225

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
        self.resized_images = {}

        self.new_width = self.width
        self.new_height = self.height

        self.cat = "base"
        self.left_paw = None
        self.right_paw = None

        self.paw_positions = {
            "left": 0,
            "right": 0,
        }

        self.resize_images()
        self.change_positions()

        self.canvas = Canvas(self.master, width=self.width, height=self.height)
        self.canvas.pack(fill=BOTH, expand=True)

        self.canvas_images = {
            "cat": self.canvas.create_image(0, 0, image=self.resized_images[self.cat], anchor='nw'),
            "left_paw": self.canvas.create_image(0, 0, image=self.resized_images[self.left_paw], anchor='nw'),
            "right_paw": self.canvas.create_image(0, 0, image=self.resized_images[self.right_paw], anchor='nw'),
        }

        self.canvas.bind('<Configure>', self.window_resized)

        self.redraw_all()

        self.init_keyloger()

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
            self.resize_images()
            self.redraw_all()

    def redraw_all(self):
        self.canvas.itemconfig(self.canvas_images["cat"], image=self.resized_images[self.cat])
        self.redraw_paws()

    def redraw_paws(self):
        self.canvas.itemconfig(self.canvas_images["left_paw"], image=self.resized_images[self.left_paw])
        self.canvas.itemconfig(self.canvas_images["right_paw"], image=self.resized_images[self.right_paw])

    def key_pressed(self, proxy, event_type, event, refcon):
        key_code = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)

        if CGEventGetIntegerValueField(event, kCGKeyboardEventAutorepeat):
            return event

        print(hex(key_code), "down" if event_type == kCGEventKeyDown else "up")

        need_redraw = False

        if key_code in self.keys_map:
            need_redraw = True
            if event_type == kCGEventKeyDown:
                self.paw_positions[self.keys_map[key_code][0]] += self.keys_map[key_code][1]
            elif event_type == kCGEventKeyUp:
                self.paw_positions[self.keys_map[key_code][0]] -= self.keys_map[key_code][1]

        if need_redraw:
            self.change_positions()
            print(self.left_paw, self.right_paw)
            self.redraw_all()

        return event

    def init_keyloger(self):
        event_mask = (CGEventMaskBit(kCGEventKeyDown) | CGEventMaskBit(kCGEventKeyUp))
        event_tap = CGEventTapCreate(kCGSessionEventTap, kCGHeadInsertEventTap, 0, event_mask, self.key_pressed, 0)

        if not event_tap:
            print("ERROR: Unable to create event tap.")
            exit(-1)

        run_loop_source = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, event_tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), run_loop_source, kCFRunLoopCommonModes)
        CGEventTapEnable(event_tap, True)

    def change_positions(self):
        self.left_paw = "left_" + bin(self.paw_positions["left"])[2:].zfill(2)
        self.right_paw = "right_" + bin(self.paw_positions["right"])[2:].zfill(2)


cat = Cat(root)
cat.pack(fill=BOTH, expand=YES)

root.mainloop()
