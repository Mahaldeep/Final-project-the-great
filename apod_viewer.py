import inspect
import os
import sqlite3
import tkinter
from datetime import date
from tkinter import *
from tkinter import ttk
from tkcalendar import *
import apod_desktop
from PIL import Image, ImageTk
import image_lib

# Determine the path and parent directory of this script

script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
script_dir = os.path.dirname(script_path)

# Initialize the image cache
apod_desktop.init_apod_cache(script_dir)

# TODO: Create the GUI
root = Tk()
root.geometry('600x400')
root.title('Astronomy Picture of the Day Viewer')
image = Image.open('icon.png')
icon = ImageTk.PhotoImage(image)
root.iconphoto(True, icon)

# Add frames to window
frm_top = ttk.Frame(root)
frm_top.grid(row=0, column=0, sticky='nsew', columnspan=2, padx=10, pady=10)
frm_btm_left = ttk.LabelFrame(root, text='View Cached Image', borderwidth=4, relief='ridge')
frm_btm_left.grid(row=1, column=0, sticky='nsew')
frm_btm_right = ttk.LabelFrame(root, text='Get More Images', borderwidth=10, relief='ridge')
frm_btm_right.grid(row=1, column=1, sticky='nsew')

# Add widgets to top frame
photo = ImageTk.PhotoImage(image.resize((600, 300)))
lbl_img = ttk.Label(frm_top, image=photo)
lbl_img.grid(row=0, column=0, sticky='nsew',columnspan=2)
img_description = ttk.Label(frm_top,wraplength=600,justify='center')
img_description.grid(row=1, column=0, sticky='nsew',columnspan=2)

# Define a callback function to resize the text widget when the frame size changes
def resize_frm(event):
    frame_width = frm_top.winfo_width()
    frame_height = frm_top.winfo_height()
    img_description.config(wraplength=frame_width)

# Bind the callback function to the <Configure> event of the frame
frm_top.bind("<Configure>", resize_frm)

#function to decide enable/disbale of button 'Set Desktop'
def on_select(value):
    if value:
        btn_set_desktop.config(state=tkinter.NORMAL)
    else:
        btn_set_desktop.config(state=tkinter.DISABLED)


def dwnld_img():
    input_date = date.fromisoformat(str(drop_cal.get_date()))
    apod_id = apod_desktop.add_apod_to_cache(input_date)
    #update list of titles of images in cache
    new_lst_title = apod_desktop.get_all_apod_titles()
    optn_img['menu'].delete(0, 'end')
    for option in new_lst_title:
        optn_img['menu'].add_command(label=option, command=tkinter._setit(lst, option))


def setdesktop():
    img_title = lst.get()
    with sqlite3.connect(apod_desktop.image_cache_db) as conn:
        c = conn.cursor()
        c.execute("SELECT title, explanation, image_path FROM apod_cache WHERE title=?", (img_title,))
        row = c.fetchone()
        # TODO: Put information into a dictionary
        if row:
            apod_info = {
                'title': row[0],
                'explanation': row[1],
                'file_path': row[2],
            }
            print(row[2])
    img_description.config(text=apod_info['explanation'])
    new_image = Image.open(apod_info['file_path'])
    new_photo = ImageTk.PhotoImage(new_image.resize(((600,100))))
    lbl_img.config(image=new_photo, justify='center')
    lbl_img.image = new_photo
    image_lib.set_desktop_background_image(apod_info['file_path'])


# Add widgets to bottom right frame
lbl_cal = ttk.Label(frm_btm_right, text='Select Date:')
lbl_cal.grid(row=0, column=0, sticky='nsew')
drop_cal = DateEntry(frm_btm_right, min_date=date(1995, 6, 16), max_date=date.today(), selectmode="day",
                     date_pattern='yyyy-mm-dd')
drop_cal.grid(row=0, column=1, sticky='nsew')
btn_download = ttk.Button(frm_btm_right, text='Download Image', command=dwnld_img)
btn_download.grid(row=0, column=2, sticky='nsew')

# Add widgets to bottom left frame
lbl_img_drop = ttk.Label(frm_btm_left, text='Select Image:')
lbl_img_drop.grid(row=0, column=0, sticky='nsew')
lst = tkinter.StringVar(frm_btm_left)
lst.trace('w', lambda *args: on_select(lst.get()))
old_lst_title = apod_desktop.get_all_apod_titles()
optn_img = ttk.OptionMenu(frm_btm_left, lst, 'Select title', *old_lst_title)
optn_img.grid(row=0, column=1, sticky='nsew')
btn_set_desktop = ttk.Button(frm_btm_left, text='Set as Desktop', command=setdesktop, state=DISABLED)
btn_set_desktop.grid(row=0, column=2, sticky='nsew')

# configure the column and row weights to control resizing
root.grid_columnconfigure(0, weight=2)
root.grid_columnconfigure(1, weight=2)
root.grid_rowconfigure(0, weight=2)
root.grid_rowconfigure(1, weight=2)
frm_btm_left.grid_rowconfigure(0,weight=1)
frm_btm_left.grid_columnconfigure(0,weight=1)
frm_btm_left.grid_columnconfigure(1,weight=1)
frm_btm_left.grid_columnconfigure(2,weight=1)
frm_btm_right.grid_rowconfigure(0,weight=1)
frm_btm_right.grid_columnconfigure(0,weight=1)
frm_btm_right.grid_columnconfigure(1,weight=1)
frm_btm_right.grid_columnconfigure(2,weight=1)

root.mainloop()
