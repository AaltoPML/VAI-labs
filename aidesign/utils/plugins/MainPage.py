import tkinter as tk
import os
from PIL import Image, ImageTk

from tkinter.filedialog import askopenfilename, askdirectory
import pandas as pd

from aidesign.utils.plugins.dataLoader import dataLoader

_PLUGIN_CLASS_NAME = "MainPage"
_PLUGIN_CLASS_DESCRIPTION = "Splash and Menu page used as GUI entry-point"
_PLUGIN_READABLE_NAMES = {"main":"default","main page":"alias","launch page":"alias"}
_PLUGIN_MODULE_OPTIONS = {"layer_priority": 1,"required_children": ['aidCanvas', 'pluginCanvas']}
_PLUGIN_REQUIRED_SETTINGS = {}
_PLUGIN_OPTIONAL_SETTINGS = {}
class MainPage(tk.Frame):

    def __init__(self, parent, controller, config:dict):
        " Here we define the main frame displayed upon opening the program."
        " This leads to the different methods to provide feedback."
        super().__init__(parent, bg = parent['bg'])
        self.controller = controller
        self.controller.title('AI Assisted Framework Design')
        
        self.bg = parent['bg']
        
        script_dir = os.path.dirname(__file__)
        self.my_img1 = ImageTk.PhotoImage(
                            Image.open(
                                os.path.join(
                                    script_dir,
                                    'resources',
                                    'Assets',
                                    'AIFRED.png')
                                    ).resize((600, 300))
                                )
        
        self.grid_rowconfigure(tuple(range(3)), weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        frame1 = tk.Frame(self, bg = self.bg)
        frame2 = tk.Frame(self, bg = self.bg)
        frame3 = tk.Frame(self, bg = self.bg)
        
        self.my_label = tk.Label(frame1, 
                                    image = self.my_img1,
                                    bg = parent['bg'])

        self.my_label.grid(column = 0,
                            row = 0,
                            rowspan = 10,
                            columnspan = 4,
                            pady = 10,
                            sticky = tk.NE)
        
        my_label = tk.Label(frame2, 
                                text = 
                                'Indicate the data folder and define the pipeline.',
                                pady= 10,
                                font = controller.title_font,
                                bg = parent['bg'],
                                fg = 'white')
        my_label.grid(column = 0,
                            row = 11,
                            columnspan = 4)
        
        tk.Button(frame3,
                    text = 'Data file',
                    fg = 'white',
                    font = controller.title_font, 
                    bg = parent['bg'],
                    height = 3,
                    width = 20, 
                    command = self.upload_data_file,
                    ).grid(column = 0, row = 12)
        tk.Button(frame3,
                    text = 'Data folder',
                    fg = 'white',
                    font = controller.title_font, 
                    bg = parent['bg'],
                    height = 3,
                    width = 20, 
                    command = self.upload_data_folder,
                    ).grid(column = 1, row = 12)
        self.controller.Datalabel = tk.Label(frame3, 
                                text = 'Incomplete',
                                pady= 10,
                                padx= 10,
                                font = controller.title_font,
                                bg = parent['bg'],
                                fg = 'white')
        self.controller.Datalabel.grid(column = 2,
                            row = 12)
        
        self.interactButton = tk.Button(frame3,
                    text = 'Interact with canvas',
                    fg = 'white',
                    font = controller.title_font,
                    bg = parent['bg'],
                    height = 3,
                    width = 20, 
                    state = tk.DISABLED, 
                    command = lambda: self.canvas("aidCanvas")
                    )
        self.interactButton.grid(column = 0, row = 13)

        self. uploadButton = tk.Button(frame3,
                    text = 'Upload XML file',
                    fg = 'white',
                    font = controller.title_font, 
                    bg = parent['bg'],
                    height = 3,
                    width = 20, 
                    state = tk.DISABLED, 
                    command = self.upload_xml,
                    )
        self. uploadButton.grid(column = 1, row = 13)
        
        self.controller.XMLlabel = tk.Label(frame3, 
                                text = 'Incomplete',
                                pady= 10,
                                padx= 10,
                                font = controller.title_font,
                                bg = parent['bg'],
                                fg = 'white')
        self.controller.XMLlabel.grid(column = 2,
                            row = 13)
        self.PluginButton = tk.Button(frame3,
                    text = 'Modules plugins',
                    fg = 'white',
                    font = controller.title_font, 
                    bg = parent['bg'],
                    height = 3,
                    width = 20, 
                    state = tk.DISABLED,
                    command = lambda: self.canvas("pluginCanvas"),
                    )
        self.PluginButton.grid(column = 0, row = 14)
        self.RunButton = tk.Button(frame3,
                    text = 'Run Pipeline',
                    fg = 'white',
                    font = controller.title_font, 
                    bg = parent['bg'],
                    height = 3,
                    width = 20, 
                    state = tk.DISABLED,
                    command = self.controller.destroy,
                    )
        self.RunButton.grid(column = 1, row = 14)
        
        self.controller.XML = tk.IntVar()
        self.controller.Data = tk.IntVar()
        self.controller.Plugin = tk.IntVar()
        self.controller.XML.set(False)
        self.controller.Data.set(False)
        self.controller.Plugin.set(False)
        
        self.controller.XML.trace('w', self.trace_XML)
        self.controller.Data.trace('w', self.trace_Data)
        self.controller.Plugin.trace('w', self.trace_Plugin)
        
        frame1.grid(column=0, row=0, sticky="n")
        frame2.grid(column=0, row=1, sticky="n")
        frame3.grid(column=0, row=2, sticky="n")
        
    def set_data_in(self, _):
        pass

    def trace_XML(self,*args):
        """ Checks if XML variable has been updated
        """
        if self.controller.XML.get():
            self.controller.XMLlabel.config(text = 'Done!', fg = 'green')
            # if self.controller.Data.get():
            self.PluginButton.config(state = 'normal')
            if self.controller.Plugin.get():
                self.RunButton.config(state = 'normal')

    def trace_Data(self,*args):
        """ Checks if Data variable has been updated
        """
        if self.controller.Data.get():
            self.controller.Datalabel.config(text = 'Done!', fg = 'green')
            self.interactButton.config(state = 'normal')
            self.uploadButton.config(state = 'normal')
            # if self.controller.XML.get():
                # self.PluginButton.config(state = 'normal')
            # if self.controller.Plugin.get():
            #     self.RunButton.config(state = 'normal')


    def trace_Plugin(self,*args):
        """ Checks if Plugin variable has been updated
        """
        if self.controller.Plugin.get():
            self.RunButton.config(state = 'normal')

    def canvas(self,name: str):
        """ Shows the canvas frame.
        :param name: string type of name of desired canvas.
        """
        self.controller._show_frame(name)

    def upload_xml(self):
        """ Indicates the XML file containng the desired pipeline """
        filename = askopenfilename(initialdir = os.getcwd(), 
                                   title = 'Select a file', 
                                   defaultextension = '.xml', 
                                   filetypes = [('XML file', '.xml'), 
                                                ('All Files', '*.*')])
        if filename is not None and len(filename) > 0:
            self.controller._append_to_output("xml_filename",filename)
            self.controller.XML.set(True)

    def upload_data_file(self):
        """ Loads a data file containing the data required for the pipeline """
        
        self.newWindow = tk.Toplevel(self.controller)
        # Window options
        self.newWindow.title('Data upload')
        script_dir = os.path.dirname(__file__)
        self.tk.call('wm','iconphoto', self.newWindow, ImageTk.PhotoImage(
            file = os.path.join(os.path.join(
                script_dir, 
                'resources', 
                'Assets', 
                'AIDIcon.ico'))))
        self.newWindow.geometry("600x200")
        
        frame1 = tk.Frame(self.newWindow)
        self.label_list = []
        self.var = ['X', 'Y', 'X test', 'Y test']
        for r,v in enumerate(self.var):
            v = v + '*' if r == 0 else v
            tk.Label(frame1, text = v,
                                    pady= 10,
                                    padx= 10,
                                    fg = 'black'
                                    ).grid(column = 0, row = r)
            tk.Button(frame1, 
                      text="Browse", 
                      command = lambda a = r: self.upload_file(a)
                      ).grid(column = 1, row = r)
            self.label_list.append(tk.Label(frame1, text = '',
                                    pady= 10,
                                    padx= 10,
                                    fg = 'black'
                                    ))
            self.label_list[-1].grid(column = 2, row = r)
        frame2 = tk.Frame(self.newWindow)
        tk.Label(frame2, text = '* This data file is mandatory.',
                                pady= 10,
                                padx= 10,
                                fg = 'black'
                                ).pack(side = tk.LEFT)
        tk.Button(frame2, 
                      text="Done", 
                      command = self.start_dataloader
                      ).pack(side = tk.RIGHT)
        frame1.grid(column=0, row=0, sticky="nsew")
        frame2.grid(column=0, row=1, sticky="nsew")

    def upload_file(self, r):
        filename = askopenfilename(initialdir = os.getcwd(), 
                                   title = 'Select a file', 
                                   defaultextension = '.csv', 
                                   filetypes = [('CSV', '.csv'), 
                                                ('All Files', '*.*')])
        self.label_list[r].config(text = filename)
        # if filename is not None and len(filename) > 0 and r == 0:
        #     if filename.lower().endswith(('.csv')):
        #         data = loadmat(filename)
        #         dL = dataLoader(self.controller, data, filename)
        #         self.controller.Data = dL.controller.Data

    def start_dataloader(self):
        """ Reads all the selected files, loads the data and passes it to 
        dataLoader."""
        data = {}
        if len(self.label_list[0].cget("text")) > 0:
            for i,label in enumerate(self.label_list):
                filename = label.cget("text")
                variable = self.var[i]
                if filename is not None and len(filename) > 0:
                    if filename.lower().endswith(('.csv')):
                        data[variable] = pd.read_csv(filename) #Infers by default, should it be None?
                        self.controller._append_to_output("data_"+variable+"_filename",filename)
            self.newWindow.destroy()
            dL = dataLoader(self.controller, data)
            self.controller.Data = dL.controller.Data
        else:
            tk.messagebox.showwarning(title = 'Error - X not specified',
                                      message = 'You need to specify X before proceeding.')


    def upload_data_folder(self):
        """ Stores the directory containing the data that will be later loaded 
        """
        folder = askdirectory(initialdir = os.getcwd(),
                                    title = 'Select a folder',
                                    mustexist = True)
        onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        self.upload_data_file()
        for file in onlyfiles:
            name = file.lower()
            filename = os.path.join(folder, file)
            if name.endswith(('.csv')):
                name = ''.join(ch for ch in name if ch.isalnum())
                if 'test' in name or 'tst' in name:
                    if name[0] == 'x':
                        # data = self.checkFile(filename,data,'X test')
                        self.label_list[2].config(text = filename)
                    elif name[0] == 'y':
                        # data = self.checkFile(filename,data,'Y test')
                        self.label_list[3].config(text = filename)
                else:
                    if name[0] == 'x':
                        # data = self.checkFile(filename,data,'X')
                        self.label_list[0].config(text = filename)
                        self.controller.Data.set(True)
                    elif name[0] == 'y':
                        # data = self.checkFile(filename,data,'Y')
                        self.label_list[1].config(text = filename)
