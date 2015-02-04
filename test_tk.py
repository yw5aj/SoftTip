# -*- coding: utf-8 -*-
"""
Created on Tue Feb 03 16:33:38 2015

@author: Administrator
"""

import Tkinter as tk
import ttk


class Application(ttk.Frame):

    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.grid()
        self.init_ui()
        return

    def init_ui(self):
        
        return

root = tk.Tk()
root.title('Manual displ control interface')
app = Application(root)
root.mainloop()
