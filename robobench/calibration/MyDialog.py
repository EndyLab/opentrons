'''
Directly adapted from http://effbot.org/tkinterbook/listbox.htm
'''

from tkinter import *
import tkSimpleDialog

class MyDialog(tkSimpleDialog.Dialog):

    def body(self, master):

        Label(master, text="Name:").grid(row=0)
        Label(master, text="Type:").grid(row=1)
        Label(master, text="Slot:").grid(row=2)

        self.e1 = Entry(master)
        self.e2 = Entry(master)
        self.e3 = Entry(master)

        # default values for testing
        self.e1.insert(END, 'plate1')
        self.e2.insert(END, '96-PCR-flat')
        self.e3.insert(END, 'A1')

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        return self.e1 # initial focus

    def validate(self):
        try:
        	# Add actual verification
            self.name = self.e1.get()
            self.container_type = self.e2.get()
            self.slot = self.e3.get()
            return 1
        except ValueError:
            print('Bad input')
            return 0

