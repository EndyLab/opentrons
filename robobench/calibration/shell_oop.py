from tkinter import *
import collections
from opentrons import robot, instruments

class Point:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def printPoint(self):
        print("x:", self.x,"y:",self.y,"z:",self.z)

    def equals(self, p2):
        return bool(self.x == p2.x and self.y == p2.y and self.z == p2.z)

    def deltaEquals(self, p2, tolerance):
        delta_x = abs(self.x-p2.x)
        delta_y = abs(self.y-p2.y)
        delta_z = abs(self.z-p2.z)
        return bool(delta_x<tolerance and delta_y<tolerance and delta_z<tolerance)

status_msg = StringVar()
    coords_str = StringVar()
    coords = Point()
    incr = 10

def init_global_vars():
    global status_msg
    global coords_str 
    global mcoords 
    global incr
    global_app_data = {
        'status': status_msg,
        'coords': coords,
        'coords_str': coords_str,
        'incr': incr
    }
    return global_app_data

def get_coords():
    # Point = collections.namedtuple('Point', ['x', 'y', 'z'])
    pos = robot._driver.get_head_position()
    x = pos['current'].coordinates.x
    y = pos['current'].coordinates.y
    z = pos['current'].coordinates.z
    coords = Point(x, y, z)
    # print("robot coords are: x= ",coords.x, " y= ", coords.y, " z= ", coords.z, sep='')
    return coords

# for more accurate moving
# def move_incr(currPos, incr):
def move_axis_by(axis, incr):
        # msg.set("moving axis: " + str(axis) + " by " + str(incr) + " amount")
        # print(self.msg.get())

        axis_dict = {
            'x': 0,
            'y': 1,
            'z': 2
        }
        coords = get_coords()
        pos = [coords.x, coords.y, coords.z]
        pos[axis_dict[str(axis)]] = coords[axis_dict[str(axis)]]+incr
        move_to(pos[0], pos[1], pos[2])
        # robot.move_head(x=pos[0], y=pos[1], z=pos[2])
        # print("moving robot to: x= ",pos[0]," y= ",pos[1], " z= ",pos[2], sep='')
        # self.pos_str.set("x: " + str(coords.x) + "\ny: " + str(coords.y) + "\nz: " + str(coords.z))

    # def move_to(self, x, y, z):
    #     robot.move_head(x=x, y=y, z=z)
    #     print("moving robot to: x= ",x," y= ",y, " z= ",z, sep='')
    #     self.pos_str.set("x: " + str(x) + "\ny: " + str(y) + "\nz: " + str(z))

def move_to(x, y, z):
    robot.move_head(x=x, y=y, z=z)

    # precision to 1mm
    # tolerance = 1
    # target = Point(x,y,z)
    # while currPos.deltaEquals(target, tolerance) == False: 
    #     delta_x = x-currPos.x
    #     delta_y = y-currPos.y
    #     delta_z = z-currPos.z
    #     # print("delta x:",delta_x,"delta y:", delta_y, "delta z:", delta_z)
    #     if abs(delta_x) > tolerance:
    #         robot.move_head(x=currPos.x+delta_x,y=y, z=z)
    #     if abs(delta_y) > tolerance:
    #         robot.move_head(x=x,y=y+delta_y, z=z)
    #     if abs(delta_z) > tolerance:
    #         robot.move_head(x=x,y=y, z=z+delta_z)

    #     currPos = get_coords()

    # currPos = get_coords()
    # print(type(currPos))
    # currPos.printPoint()
    print("moving robot to: x= ",x," y= ",y, " z= ",z, sep='')
    # pos_str.set("x: " + str(x) + "\ny: " + str(y) + "\nz: " + str(z))

def key_to_cmd(self, event):
        key_dict_robot = {
            'Up': ('y', INCR), 
            'Down': ('y', -1*INCR), 
            'Left': ('x', -1*INCR), 
            'Right': ('x', INCR), 
            'Return': ('z', INCR), 
            'Shift_R': ('z', -1*INCR)
        }

        key_dict_pipette = {
            'w': ('plunger', INCR), 
            's': ('plunger', -1*INCR), 
            'a': ('pip choice',-1*INCR), 
            'd': ('pip choice', INCR), 
        }
        # motor.speed(speed)
        # motor.move(destination)
        
        for key in key_dict_robot.keys():
            if event.keysym == key:
                move_axis_by(key_dict_robot[key][0], key_dict_robot[key][1])
                break

        # for key in key_dict_pipette.keys():
        #     if event.keysym == key:
        #         # motor.move()
        #     break

class LeftFrame(Frame):
    def __init__(self, master):
        # fram init
        Frame.__init__(self, master, bd=1)
        self.master = master
        self.widgets()

    def widgets(self):
        # wasd
        self.button_w = Button(self, text="W", height=1, width=2).grid(row=0, column=1)
        self.button_a = Button(self, text="A", height=1, width=2).grid(row=1, column=0)
        self.button_s = Button(self, text="S", height=1, width=2).grid(row=1, column=1)
        self.button_d = Button(self, text="D", height=1, width=2).grid(row=1, column=2)

        # arrow keys
        self.button_up = Button(self, text="^", height=1, width=2).grid(row=4, column=1)
        self.button_left = Button(self, text="<", height=1, width=2).grid(row=5, column=0)
        self.button_down = Button(self, text="|", height=1, width=2).grid(row=5, column=1)
        self.button_right = Button(self, text=">", height=1, width=2).grid(row=5, column=2)

        # shift and enter
        self.button_enter = Button(self, text="Enter", height=1).grid(row=6, column=0, columnspan=3)
        self.button_shift = Button(self, text="Shift", height=1).grid(row=7, column=0, columnspan=3)

class MidFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bd=1, relief=SUNKEN, width=200, height=200)
        self.master = master
        self.widgets()

    def widgets(self):
        def mouse_callback(event):
            self.msg.set("clicked at " + str(event.x) + " " + str(event.y))
            move_to(float(event.x), float(event.y), 100)
            # print(self.msg.get())

        def draw_cross(x, y, len, thickness):
            self.c.create_line(x-len, y, x+len, y, fill="#476042", width=thickness)
            self.c.create_line(x, y-len, x, y+len, fill="#476042", width=thickness)

        # canvas grid
        self.c = Canvas(self, bg="white", width=200, height=200)
        self.c.pack()
        self.c.bind("<Button-1>", mouse_callback)
        
        for x in range(0,200,50):
            for y in range(0,200,50):
                draw_cross(x,y,5,3)

class RightFrame(Frame):
    def __init__(self, master, global_app_data):
        Frame.__init__(self, master, bd=1)
        self.master = master
        self.app_data = global_app_data
        self.widgets()

    def widgets(self):
        # enter coords
        self.l1 = Label(self, text = "x: ").grid(row=0, sticky=E)
        self.l2 = Label(self, text = "y: ").grid(row=1, sticky=E)
        self.l3 = Label(self, text = "z: ").grid(row=2, sticky=E)
        x_entry = DoubleVar()
        y_entry = DoubleVar()
        z_entry = DoubleVar()

        # user input entries
        self.entry = []
        entry_vars = [x_entry, y_entry, z_entry]
        self.entry_vars = entry_vars
        for j in range(0,3):
            self.entry.append(Entry(self, textvariable=entry_vars[j]).grid(row=j,column=1))

        # move button
        x_target = self.entry_vars[0].get()
        y_target = self.entry_vars[1].get()
        z_target = self.entry_vars[2].get()
        self.move_button = Button(self, text="Move", command = lambda: move_to(x_target, y_target, z_target)).grid(columnspan=2)
        coords = self.app_data['coords']
        coords = get_coords()
        print("coords are:")
        coords.printPoint()
        pos_str = self.app_data['coords_str']
        pos_str.set('x:' + str(coords.x) + '\ny:' + str(coords.y) + '\nz:' + str(coords.z))
        self.pos_lbl=Label(self, textvariable=pos_str)
        self.pos_lbl.grid(columnspan=2, sticky=W)
        self.pos_lbl.config(justify=LEFT)

        # incr slider
        self.ticks = [1,2,5,10,20]
        def slider_set(value):
            # new_value = min(self.ticks, key=lambda x:abs(x-float(value)))
            # slider.set(new_value)
            # global INCR 
            INCR = int(float(value))
            # print(value, INCR)

        self.slider = Scale(self, from_=1, to=20, orient=HORIZONTAL, command=slider_set)
        self.slider.grid(row=5, columnspan=2)

    def update(self):
        # enter coords
        # self.l1 = Label(self, text = "x: ").grid(row=0, sticky=E)
        # self.l2 = Label(self, text = "y: ").grid(row=1, sticky=E)
        # self.l3 = Label(self, text = "z: ").grid(row=2, sticky=E)
        # x_entry = DoubleVar()
        # y_entry = DoubleVar()
        # z_entry = DoubleVar()

        # user input entries
        # self.entry = []
        # entry_vars = [x_entry, y_entry, z_entry]
        # for j in range(0,3):
        #     self.entry.append(Entry(self, textvariable=entry_vars[j]).grid(row=j,column=1))
       

        # move button
        coords = self.app_data['coords']
        self.move_button.configure()
        coords = get_coords()
        print("coords are:")
        coords.printPoint()
        # def testprint():
        #     print(x_entry.get(), y_entry.get(), z_entry.get())
        # self.move_button = Button(self, text="Move", command=testprint).grid(columnspan=2)

        # def print_diff(*args):
        #     print("point changed!")
        # coords display area
        # pos_str = self.app_data['coords_str']
        pos_str = 'x:' + str(coords.x) + '\ny:' + str(coords.y) + '\nz:' + str(coords.z)
        self.pos_lbl.config(text=pos_str)

        # incr slider
        self.ticks = [1,2,5,10,20]
        def slider_set(value):
            # new_value = min(self.ticks, key=lambda x:abs(x-float(value)))
            # slider.set(new_value)
            # global INCR 
            INCR = int(float(value))
            # print(value, INCR)

        self.slider = Scale(self, from_=1, to=20, orient=HORIZONTAL, command=slider_set)
        self.slider.grid(row=5, columnspan=2)


class BottomFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bd=1, relief=SUNKEN, width=200, height=200)
        self.master = master
        self.widgets()

    def widgets(self):
        # status message
        self.status = Label(self, text="status message...", bd=1, relief=SUNKEN, anchor=W)
        self.status.grid(row=0,column=0, sticky=W)

class App(Tk):
    def __init__(self, master):
        Tk.__init__(self, master)
        self.master = master

        # app variables
        self.opentronsConnect()
        # self.initGlobalVars()

        # frames
        self.app_data = init_global_vars()
        self.mainWidgets()

        # print(get_coords().y)

    def opentronsConnect(self):  
        # ports = robot.get_serial_ports_list()
        # print(ports)
        # robot.connect(ports[0])

        # simulator
        robot.connect('Virtual Smoothie')
        robot.home(now=True)
        pipette = instruments.Pipette(axis='a')

    # def initGlobalVars(self):
    #     status_msg = StringVar()
    #     coords_str = StringVar()
    #     coords = Point()
    #     incr = 0
    #     global_app_data = {
    #         'status': status_msg,
    #         'coords': coords,
    #         'coords_str': coords_str,
    #         'incr': incr
    #     }
    #     self.app_data = global_app_data

    def mainWidgets(self):
        self.left_frame = LeftFrame(self)
        self.left_frame.grid(row=0, column=0, sticky=N)

        self.mid_frame = MidFrame(self)
        self.mid_frame.grid(row=0, column=1, sticky=N+S+E+W)

        self.right_frame = RightFrame(self, self.app_data)
        self.right_frame.grid(row=0, column=2, sticky=N)

        self.bottom_frame = BottomFrame(self)
        self.bottom_frame.grid(row=1, column=0, columnspan=3, sticky=S+W)


# class CalibrationGUI:
#     INCR = 10
#     STEP = 50

#     def __init__(self, master):
#         self.master = master
#         master.title("Calibration GUI")
#         self.opentronsConnect()
#         self._gui_init()

#     def _status_bar_init(self):
#         # status bar message
#         self.msg = StringVar()
#         self.msg.set("status message...")

#         self.pos_str = StringVar()
#         self.pos_str.set("x: \ny: \nz:")

#     def _left_fr_init(self):
#         # fram init
#         self.left_frame = Frame(self, bd=1)
#         self.left_frame.grid(row=0, column=0, sticky=N)

#         # wasd
#         self.button_w = Button(self.left_frame, text="W", height=1, width=2).grid(row=0, column=1)
#         self.button_a = Button(self.left_frame, text="A", height=1, width=2).grid(row=1, column=0)
#         self.button_s = Button(self.left_frame, text="S", height=1, width=2).grid(row=1, column=1)
#         self.button_d = Button(self.left_frame, text="D", height=1, width=2).grid(row=1, column=2)

#         # arrow keys
#         self.button_up = Button(self.left_frame, text="^", height=1, width=2).grid(row=4, column=1)
#         self.button_left = Button(self.left_frame, text="<", height=1, width=2).grid(row=5, column=0)
#         self.button_down = Button(self.left_frame, text="|", height=1, width=2).grid(row=5, column=1)
#         self.button_right = Button(self.left_frame, text=">", height=1, width=2).grid(row=5, column=2)


#     def _mid_fr_init(self):
#         # canvas grid
#         # mouse bind event
#         self.mid_frame = Frame(self, bd=1, relief=SUNKEN, width=200, height=200)
#         self.mid_frame.grid(row=0, column=1, sticky=N+S+E+W)
#         self.c = Canvas(self.mid_frame, bg="white", width=200, height=200)
#         self.c.pack()
#         self.c.bind("<Button-1>", mouse_callback)

#         #cross
#         def draw_cross(x, y, len, thickness):
#             self.c.create_line(x-len, y, x+len, y, fill="#476042", width=thickness)
#             self.c.create_line(x, y-len, x, y+len, fill="#476042", width=thickness)

#         for x in range(0,200,STEP):
#             for y in range(0,200,STEP):
#                 draw_cross(x,y,5,3)
#                 # print("x:",x,"y:",y)  

#     def _right_fr_init(self):
#         # pos stats
#         self.right_frame = Frame(self, bd=1)
#         self.right_frame.grid(row=0, column=2, sticky=N)

#         # enter coords
#         self.l1 = Label(self.right_frame, text = "x: ").grid(row=0, sticky=E)
#         self.l2 = Label(self.right_frame, text = "y: ").grid(row=1, sticky=E)
#         self.l3 = Label(self.right_frame, text = "z: ").grid(row=2, sticky=E)
#         self.x_entry = DoubleVar()
#         self.y_entry = DoubleVar()
#         self.z_entry = DoubleVar()
#         self.entry = []
#         self.entry_vars = [x_entry, y_entry, z_entry]
#         for j in range(0,3):
#             self.entry.append(Entry(self.right_frame, textvariable=entry_vars[j]).grid(row=j,column=1))
#         self.move_button = Button(self.right_frame, text = "Move", command = lambda: move_to(x_entry.get(), y_entry.get(), z_entry.get())).grid(columnspan=2)

#         # coords display area
#         self.coords = get_coords()
#         self.pos_lbl = Label(self.right_frame, textvariable=self.pos_str)
#         self.pos_lbl.grid(columnspan=2, sticky=W)
#         self.pos_lbl.config(justify=LEFT)

#         # incr slider
#         self.ticks = [1,2,5,10,20]
#         def slider_set(value):
#             new_value = min(ticks, key=lambda x:abs(x-float(value)))
#             slider.set(new_value)
#             global INCR 
#             INCR = int(float(new_value))

#         self.slider = Scale(self.right_frame, from_=1, to=20, orient=HORIZONTAL, command=slider_set)
#         self.slider.grid(row=5, columnspan=2)


#     def _bottom_frame_init(self):
#         # error message
#         self.bottom_frame = Frame(self)
#         self.bottom_frame.grid(row=1, column=0, columnspan=3, sticky=S+W)

#         # status message
#         self.status = Label(self.bottom_frame, textvariable=self.msg, bd=1, relief=SUNKEN, anchor=W)
#         self.status.grid(row=0,column=0, sticky=W)


#     def _gui_init(self):
#         self.Grid.rowconfigure(self, 0, weight=1)
#         self.Grid.columnconfigure(self, 0, weight=1)
#         self.Grid.columnconfigure(self, 1, weight=1)    
#         self.Grid.columnconfigure(self, 2, weight=1) 

#         # status bar init
#         self._status_bar_init()

#         # keyboard focus
#         self.focus_set()
#         self.bind('<Key>', key_to_cmd)

#         # left frame init
#         self._left_fr_init()

#         # mid frame init
#         self._mid_fr_init()

#         # right frame init
#         self._right_fr_init()

#         # bottom frame init
#         self._bottom_fr_init()

       
#     def opentronsConnect(self):  
#         # ports = robot.get_serial_ports_list()
#         # print(ports)
#         # robot.connect(ports[0])

#         # simulator
#         robot.connect('Virtual Smoothie')
#         robot.home(now=True)
#         pipette = instruments.Pipette(axis='a')

#     def get_coords(self):
#         Point = collections.namedtuple('Point', ['x', 'y', 'z'])
#         curr_coords = robot._driver.get_head_position()
#         curr_x = curr_coords['current'].coordinates.x
#         curr_y = curr_coords['current'].coordinates.y
#         curr_z = curr_coords['current'].coordinates.z
#         pos = Point(curr_x, curr_y, curr_z)
#         # print("robot coords are: x= ",pos.x, " y= ", pos.y, " z= ", pos.z, sep='')
#         return pos

#     def mouse_callback(self, event):
#         self.msg.set("clicked at " + str(event.x) + " " + str(event.y))
#         move_to(float(event.x), float(event.y), 100)
#         print(self.msg.get())

#     def move_axis_by(self, axis, incr):
#         self.msg.set("moving axis: " + str(axis) + " by " + str(incr) + " amount")
#         print(self.msg.get())

#         axis_dict = {
#             'x': 0,
#             'y': 1,
#             'z': 2
#         }
#         coords = get_coords()
#         pos = [coords.x, coords.y, coords.z]
#         pos[axis_dict[str(axis)]] = coords[axis_dict[str(axis)]]+incr
#         move_to(pos[0], pos[1], pos[2])
#         # robot.move_head(x=pos[0], y=pos[1], z=pos[2])
#         # print("moving robot to: x= ",pos[0]," y= ",pos[1], " z= ",pos[2], sep='')
#         # self.pos_str.set("x: " + str(coords.x) + "\ny: " + str(coords.y) + "\nz: " + str(coords.z))

#     def move_to(self, x, y, z):
#         robot.move_head(x=x, y=y, z=z)
#         print("moving robot to: x= ",x," y= ",y, " z= ",z, sep='')
#         self.pos_str.set("x: " + str(x) + "\ny: " + str(y) + "\nz: " + str(z))

#     def key_to_cmd(self, event):
#         key_dict_robot = {
#             'Up': ('y', INCR), 
#             'Down': ('y', -1*INCR), 
#             'Left': ('x', -1*INCR), 
#             'Right': ('x', INCR), 
#             'Return': ('z', INCR), 
#             'Shift_R': ('z', -1*INCR)
#         }

#         key_dict_pipette = {
#             'w': ('plunger', INCR), 
#             's': ('plunger', -1*INCR), 
#             'a': ('pip choice',-1*INCR), 
#             'd': ('pip choice', INCR), 
#         }
#         # motor.speed(speed)
#         # motor.move(destination)
        
#         for key in key_dict_robot.keys():
#             if event.keysym == key:
#                 move_axis_by(key_dict_robot[key][0], key_dict_robot[key][1])
#                 break

#         # for key in key_dict_pipette.keys():
#         #     if event.keysym == key:
#         #         # motor.move()
#         #     break


#Create & Configure root 
if __name__=="__main__":
    app = App(None)
    app.mainloop()