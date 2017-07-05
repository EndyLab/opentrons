from tkinter import *

    
root = Tk()
frame = Frame(root, width=500, height=400, bd=1)
frame.pack()

# iframe5 = Frame(frame, bd=2, relief=RAISED)
# iframe5.pack(expand=1, fill=X, pady=10, padx=5)
c = Canvas(frame, bg='white', width=340, height=100)
c.pack()
for i in range(25):
    c.create_oval(5+(4*i),5+(3*i),(5*i)+60,(i)+60, fill='gray70')
c.create_text(260, 80, text='Canvas', font=('verdana', 10, 'bold'))
# iframe5.pack(expand=1, fill=X, pady=10, padx=5)
#root.option_add('*font', ('verdana', 10, 'bold'))
root.title('Tkinter Widgets')
root.mainloop()
           
       








