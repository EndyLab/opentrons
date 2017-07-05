from tkinter import *

class FixedRatio(Frame):
    def __init__(self, master, width, height):
        Frame.__init__(self, master)
        self.grid(sticky=N+S+E+W)
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        self._create_widgets()
        self.bind('<Configure>', self._resize)
        self.winfo_toplevel().minsize(150, 150)

    def _create_widgets(self):
        self.content = Frame(self, bg='blue')
        # self.content = Frame(self, bd=1, relief=SUNKEN)
        self.content.grid(row=0, column=1, sticky=N+S+E+W)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

    def _resize(self, event):
        '''Modify padding when window is resized.'''
        w, h = event.width, event.height
        w1, h1 = self.content.winfo_width(), self.content.winfo_height()
        print(w1, h1)  # should be equal
        if w > h:
            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=0)
            self.columnconfigure(1, weight=h)
            self.columnconfigure(2, weight=w - h)
        elif w < h:
            self.rowconfigure(0, weight=w)
            self.rowconfigure(1, weight=h - w)
            self.columnconfigure(1, weight=1)
            self.columnconfigure(2, weight=0)
        else:
            # width = height
            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=0)
            self.rowconfigure(0, weight=1)
            self.columnconfigure(2, weight=0)

root = Tk()
app = FixedRatio(master=root, width=100, height=100)
root.mainloop()