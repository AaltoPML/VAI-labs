import tkinter as tk                # python 3
import os
from PIL import Image, ImageTk
from tkinter import messagebox, ttk
from tkinter.filedialog import asksaveasfile, askopenfile, askopenfilename
import numpy as np
import pandas as pd
import math


class PageManual(tk.Frame):
    
    

    def __init__(self, parent, controller):
            
        super().__init__(parent, bg = parent['bg'])
        self.controller = controller
        self.parent = parent
        
        self.dirpath = os.getcwd()
        self.assets_path = os.path.join(self.dirpath, 'modules', 'UI', 
                                        'resources', 'Assets')

        self.class_list = ['Atelectasis', 'Cardiomelagy', 'Effusion', 
                           'Infiltration', 'Mass', 'Nodule', 'Pneumonia', 
                           'Pneumothorax'
                           ]
        
        pixels = 500
        path = os.path.join(self.dirpath, 'modules', 'UI', 'resources', 
                            'example_radiography_images')
        self.N = len(os.listdir(path))
        
        # Create a list with all the available (I have tried reading the file when placing it but wasn't able to)
        self.image_list = []
        for f in os.listdir(path):
            self.image_list.append(
                ImageTk.PhotoImage(self.expand2square(
                    Image.open(os.path.join(path, f)), 
                    (0, 0, 0)).resize((pixels, pixels)))) # (0, 0, 0) is the padding colour
        
        # Status bar in the lower part of the window
        status = tk.Label(self, text='Image 1 of '+str(self.N), bd = 1, 
                          relief = tk.SUNKEN, anchor = tk.E, fg = 'white', 
                          bg = parent['bg'])
        status.grid(row=20, column=0, columnspan=4, pady = 10, 
                    sticky = tk.W+tk.E)
        
        # Inital window
        self.my_label = tk.Label(self, image = self.image_list[0], 
                                 bg = parent['bg'])
        self.my_label.grid(column = 0, row = 0, rowspan = 10, columnspan = 3)
    
        # Buttons initialisation
        self.back_img = ImageTk.PhotoImage(Image.open(
            os.path.join(self.assets_path,'back_arrow.png')).resize((150, 50)))
        self.forw_img = ImageTk.PhotoImage(Image.open(
            os.path.join(self.assets_path,'forw_arrow.png')).resize((150, 50)))
        self.button_back = tk.Button(
            self, image = self.back_img, bg = parent['bg'], 
            state = tk.DISABLED).grid(column = 0,row = 19)
        self.button_save = tk.Button(
            self, text = 'Save', fg = 'white', bg = parent['bg'], height = 3, 
            width = 20, command = self.save_file).grid(column = 1,row = 19)
        self.button_forw = tk.Button(
            self, image = self.forw_img, bg = parent['bg'], 
            command = lambda: self.forward_back(2)).grid(column = 2,row = 19)
        
        button_main = tk.Button(
            self, text="Go to the main page", 
            fg = 'white', bg = parent['bg'], height = 3, width = 20, 
            command = self.check_quit).grid(column = 4,row = 19)
        
        self.out_data = np.zeros((self.N, len(self.class_list)))
        self.button_cl = {}
        
        self.var = {}
        for i,cl in enumerate(self.class_list):
            self.var[0,i] = tk.IntVar(value=self.out_data[0,i])
            self.button_cl[cl] = tk.Checkbutton(
                self, text = cl, fg = 'white', bg = parent['bg'], 
                selectcolor = 'black', height = 3, width = 20, 
                variable = self.var[0,i], 
                command=(lambda i=i: self.onPress(0,i)))
            self.button_cl[cl].grid(column = 4,row = i)
        
        #Tree defintion. Output display
        style = ttk.Style()
        style.configure(
            "Treeview", background = 'white', foreground = 'white', 
            rowheight = 25, fieldbackground = 'white', 
            font = self.controller.pages_font)
        style.configure("Treeview.Heading", font = self.controller.pages_font)
        style.map('Treeview', background = [('selected', 'grey')])
        
        tree_frame = tk.Frame(self)
        tree_frame.grid(row = 0, column = 5, columnspan = 4, rowspan = 10)
        
        tree_scrollx = tk.Scrollbar(tree_frame, orient = 'horizontal')
        tree_scrollx.pack(side = tk.BOTTOM, fill = tk.X)
        tree_scrolly = tk.Scrollbar(tree_frame)
        tree_scrolly.pack(side = tk.RIGHT, fill = tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, 
                                 yscrollcommand = tree_scrolly.set, 
                                 xscrollcommand = tree_scrollx.set)
        self.tree.pack()
        
        tree_scrollx.config(command = self.tree.xview)
        tree_scrolly.config(command = self.tree.yview)
        
        self.tree['columns'] = self.class_list
        
        # Format columns
        self.tree.column("#0", width = 50)
        for n, cl in enumerate(self.class_list):
            self.tree.column(
                cl, width = int(self.controller.pages_font.measure(str(cl)))+20, 
                minwidth = 50, anchor = tk.CENTER)
        # Headings
        self.tree.heading("#0", text = "Image", anchor = tk.CENTER)
        for cl in self.class_list:
            self.tree.heading(cl, text = cl, anchor = tk.CENTER)
        self.tree.tag_configure('odd', foreground = 'white', 
                                background='#E8E8E8')
        self.tree.tag_configure('even', foreground = 'white', 
                                background='#DFDFDF')
        # Add data
        for n, sample in enumerate(self.out_data):
            if n%2 == 0:
                self.tree.insert(parent = '', index = 'end', iid = n, text = n+1, 
                                 values = tuple(sample.astype(int)), tags = ('even',))
            else:
                self.tree.insert(parent = '', index = 'end', iid = n, text = n+1, 
                                 values = tuple(sample.astype(int)), tags = ('odd',))
        
        # Select the current row
        self.tree.selection_set(str(int(0)))
        
        # Define double-click on row action
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        
        self.save_path = ''
        self.saved = True
        
    def expand2square(self, pil_img, background_color):
        
        " Adds padding to make the image a square."
        width, height = pil_img.size
        if width == height:
            return pil_img
        elif width > height:
            result = Image.new(pil_img.mode, (width, width), background_color)
            result.paste(pil_img, (0, (width - height) // 2))
            return result
        else:
            result = Image.new(pil_img.mode, (height, height), 
                               background_color)
            result.paste(pil_img, ((height - width) // 2, 0))
            return result

    def check_quit(self):
        
        if not self.saved:
            response = messagebox.askokcancel(
                "Are you sure you want to leave?", 
                "Do you want to leave the program without saving?")
            if response:
                self.controller.show_frame("StartPage")
        else:
            self.controller.show_frame("StartPage")
    
    def open_file(self):
        
        self.save_path = askopenfile(mode='r+')
        if self.save_path is not None:
            t = self.save_path.read()
            # textentry.delete('0.0', 'end')
            # textentry.insert('0.0', t)
            # textentry.focus()
            
    def save_file_as(self):
        
        self.save_path = asksaveasfile(mode='w')
        self.save_file()
        
    def save_file(self):
        
        if self.save_path == '':
            self.save_path = asksaveasfile(defaultextension = '.txt', 
                                      filetypes = [('Text file', '.txt'), 
                                                   ('CSV file', '.csv'), 
                                                   ('All Files', '*.*')])
        if self.save_path is not None: # asksaveasfile return `None` if dialog closed with "cancel".
            filedata = pd.DataFrame(
                self.out_data, columns = self.class_list).to_string()
            self.save_path.seek(0) # Move to the first row to overwrite it
            self.save_path.write(filedata)
            self.save_path.flush() # Save without closing
            # typically the above line would do. however this is used to ensure that the file is written
            os.fsync(self.save_path.fileno())
            self.saved = True
            
    def forward_back(self, image_number):
        
        " Forward button to continue to the next image in the folder."
        
        self.tree.selection_set(str(int(image_number-1)))
        # Print the corresponding image
        self.my_label.grid_forget()
        self.my_label = tk.Label(self, image=self.image_list[image_number-1])
        
        # Update button commands
        self.button_forw = tk.Button(
            self, image = self.forw_img, bg = self.parent['bg'], 
            command = lambda: self.forward_back(
                image_number+1)).grid(column = 2,row = 19)
        self.button_back = tk.Button(
            self, image = self.back_img, bg = self.parent['bg'], 
            command = lambda: self.forward_back(
                image_number-1)).grid(column = 0,row = 19)
        if image_number == self.N:
            self.button_forw = tk.Button(
                self, image = self.forw_img, bg = self.parent['bg'], 
                state = tk.DISABLED).grid(column = 2,row = 19)
        if image_number == 1:
            self.button_back = tk.Button(
                self, image = self.back_img, bg = self.parent['bg'], 
                state = tk.DISABLED).grid(column = 0,row = 19)
            
        self.my_label.grid(column=0, row=0, rowspan = 10, columnspan=3)
        
        # Classes buttons
        # var = {}
        for i,cl in enumerate(self.class_list):
            # print(out_data[image_number-1,i])
            self.var[image_number-1,i] = tk.IntVar(
                value = int(self.out_data[image_number-1,i]))
            # var[i] = tk.IntVar(value = int(self.out_data[image_number-1,i]))
            # I can not make this be selected when going backwards or forward 
            # if it was previously selected.
            self.button_cl[cl] = tk.Checkbutton(
                self, text = cl, fg = 'white', bg = self.parent['bg'], 
                selectcolor = 'black', height = 3, width = 20, 
                variable = self.var[image_number-1,i], 
                command=(lambda i=i: self.onPress(image_number-1,i)))
            self.button_cl[cl].grid(column = 4,row = i)

        # Status bar    
        status = tk.Label(
            self, text='Image ' + str(image_number) + ' of '+str(self.N), 
            bd = 1, relief = tk.SUNKEN, anchor = tk.E, fg = 'white', 
            bg = self.parent['bg'])
        status.grid(row=20, column=0, columnspan=4, pady = 10, 
                    sticky = tk.W+tk.E)
            
    def onPress(self, n,i):
        
        "Updates the stored values on clicking the checkbutton."
        
        self.out_data[n,i] = not self.out_data[n,i]
        self.tree.item(self.tree.get_children()[n], text = n+1, 
                       values = tuple(self.out_data[n,:].astype(int)))
        self.saved = False
        
    def OnDoubleClick(self, event):
        
        "Moves to the image corresponding to the row clicked on the tree."
        
        item = self.tree.selection()[0]
        self.forward_back(self.tree.item(item,"text"))
