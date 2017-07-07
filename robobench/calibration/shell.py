""" TODO:
        [x] canvas graphical indication DONE
        [ ] out of bounds handling
        [ ] robot disconnect command
        [ ] gui shell input (commands)
        [ ] link buttons to commands
"""

from tkinter import *
import collections
from opentrons import robot, instruments
import warnings

# treat warnings like errors
warnings.filterwarnings("error")

def opentrons_connect():
    try:
        # physical robot
        ports = robot.get_serial_ports_list()
        print(ports)
        robot.connect(ports[0])
    except IndexError:
        # simulator
        robot.connect('Virtual Smoothie')
        # robot.home(now=True)

    # robot.home('xyzab')
    pipette = instruments.Pipette(axis='a')

def get_coords():
    Point = collections.namedtuple('Point', ['x', 'y', 'z'])
    curr_coords = robot._driver.get_head_position()
    curr_x = curr_coords['current'].coordinates.x
    curr_y = curr_coords['current'].coordinates.y
    curr_z = curr_coords['current'].coordinates.z
    pos = Point(curr_x, curr_y, curr_z)
    # print("robot coords are: x= ",pos.x, " y= ", pos.y, " z= ", pos.z, sep='')
    return pos

def in_bounds(x,y,z):
    return (x > 0 and x < 310) and (y > -145 and y < 400)

def mouse_callback(event):
    status_str.set("clicked at " + str(event.x) + " " + str(event.y))
    pos = c.coords(marker)

    # cant use move_marker bc mouse y coords are not flipped like the robot coords are
    x1 = pos[0]
    y1 = pos[1]
    x2 = event.x
    y2 = event.y
    dx = x2 - x1 
    dy = y2 - y1
    print("x1:",x1,"y1:",y1,"x2:",x2,"y2:",y2,"dx:",dx,"dy:",dy)
    c.move(marker, dx, dy)
    x = x2
    y = y2*-1
    z = get_coords().z
    # if in_bounds(x,y,z):
    robot.move_head(x=x, y=y, z=z)
    print("moving robot to: x= ",x," y= ",y, " z= ",z, sep='')
    pos_str.set("x: " + str(x) + "\ny: " + str(y) + "\nz: " + str(z))
    print(status_str.get())


def move_axis_by(axis, increment):
    status_str.set("moving axis: " + str(axis) + " by " + str(increment) + " amount")
    # print(status_str.get())

    axis_dict = {
        'x': 0,
        'y': 1,
        'z': 2
    }
    coords = get_coords()
    pos = [coords.x, coords.y, coords.z]
    pos[axis_dict[str(axis)]] = coords[axis_dict[str(axis)]]+increment
    if in_bounds(pos[0], pos[1], pos[2]):
        move_to(pos[0], pos[1], pos[2])

# box dimensions
# x: 0, 310
# y: -145, 400
def move_marker(x1, y1, x2, y2):
    dx = x2 - x1 
    dy = (y2 - y1)*-1
    print("x1:",x1,"y1:",y1,"x2:",x2,"y2:",y2,"dx:",dx,"dy:",dy)
    c.move(marker, dx, dy)

def move_to(x, y, z):
    # try: 
    old_x = get_coords().x
    old_y = get_coords().y
    move_marker(old_x, old_y, x, y)
    robot.move_head(x=x, y=y, z=z)
    print("moving robot to: x= ",x," y= ",y, " z= ",z, sep='')
    pos_str.set("x: " + str(x) + "\ny: " + str(y) + "\nz: " + str(z))
    # except RuntimeWarning:
        # print("about to crash pls move in the opposite direction")
    # except RuntimeError:
        # print("rip")
 

# arg format: (arg type, arg, ...)
# pip_desc = {
#     "active pipette: ": "",
#     "\nplunger pos: " : "",
#     "\npipette a: "   : "",
#     "\npipette b: "   : ""
# }
def update_pipette_str(*arg):
    key = ""
    res = pipette_str.get()
    for j in range(0, len(arg),2):
        if arg[j] == "axis":
            key = "active pipette: "
        elif arg[j] == "pos_active":
            key = "\nplunger pos: "
        elif arg[j] == "pos_a":
            key = "\npipette a: "
        elif arg[j] == "pos_b":
            key = "\npipette b: "
        else:
            print("error: not valid pipette var")

        pip_desc[key] = arg[j+1]

    dict_to_str(pip_desc)

def pipette_select(axis):
    global PIPETTE_AXIS
    PIPETTE_AXIS = axis
    status_str.set("axis: " + axis + " selected")
    update_pipette_str("axis", axis)
    # pipette_str.set("active pipette: " + axis + "\nplunger pos: \npipette a:\npipette b:")

def depress_pipette(increment):
    # moves A axis to position 5
    if PIPETTE_AXIS == 'a':
        robot._driver.move_plunger(mode='relative', a=increment)
        update_pipette_str("pos_a", str(increment),"pos_active", str(increment))
    elif PIPETTE_AXIS == 'b':
        robot._driver.move_plunger(mode='relative', b=increment)
        update_pipette_str("pos_b", str(increment),"pos_active", str(increment)) 

    status_str.set("pipette "+PIPETTE_AXIS+" plunger pos changed by "+str(increment))

# translates keyboard input into robot commands
def key_to_cmd(event):
    key_dict_robot = {
        'Up': ('y', increment), 
        'Down': ('y', -1*increment), 
        'Left': ('x', -1*increment), 
        'Right': ('x', increment), 
        'Return': ('z', increment), 
        'Shift_R': ('z', -1*increment)
    }

    key_dict_pipette = {
        'w': (depress_pipette, -1*increment), 
        's': (depress_pipette, 1*increment), 
        'a': (pipette_select, 'a'), 
        'd': (pipette_select, 'b'), 
    }
    
    for key in key_dict_robot.keys():
        if event.keysym == key:
            move_axis_by(key_dict_robot[key][0], key_dict_robot[key][1])
            break

    for key in key_dict_pipette.keys():
        if event.keysym == key:
            key_dict_pipette[key][0](key_dict_pipette[key][1])
            break

    # robot.home()

#Create & Configure root 
win = Tk()

####################
# INIT GLOBAL VARS #
####################
# increment for pipette and xyz movement
increment = 10
marker_size = 10

PIPETTE_AXIS = 'a'

# status bar message
status_str = StringVar()
status_str.set("status message...")

# shell input
shell_input = StringVar()
shell_input.set(">")

# xyz pos message
pos_str = StringVar()
pos_str.set("x: \ny: \nz:")

# pipette pos/info message
pipette_str = StringVar()
pip_desc = {
    "active pipette: "  : "",
    "\nplunger pos: "   : "",
    "\npipette a: "     : "",
    "\npipette b: "     : ""
}

def dict_to_str(strdict):
    res = ""
    for key in strdict.keys():
        res += (key + strdict[key])
    pipette_str.set(res)

dict_to_str(pip_desc)
##########################
# END OF GLOBAL VAR INIT #

# frames
# left_frame()
# mid_frame()
# right_frame()
# bottom_frame()

##############
# LEFT FRAME #
##############
# def left_frame():
left_frame = Frame(win, bd=1)
left_frame.grid(row=0, column=0, sticky=N)

# wasd
button_w = Button(left_frame, text="W", height=1, width=2).grid(row=0, column=1)
button_a = Button(left_frame, text="A", height=1, width=2).grid(row=1, column=0)
button_s = Button(left_frame, text="S", height=1, width=2).grid(row=1, column=1)
button_d = Button(left_frame, text="D", height=1, width=2).grid(row=1, column=2)

# arrow keys
button_up = Button(left_frame, text="^", height=1, width=2).grid(row=4, column=1)
button_left = Button(left_frame, text="<", height=1, width=2).grid(row=5, column=0)
button_down = Button(left_frame, text="|", height=1, width=2).grid(row=5, column=1)
button_right = Button(left_frame, text=">", height=1, width=2).grid(row=5, column=2)

# shift and enter
def robot_stats():
    print(robot.versions())

button_enter = Button(left_frame, text="Enter", height=1, command=robot_stats).grid(row=6, column=0, columnspan=3)
# button_shift = Button(left_frame, text="Shift", height=1).grid(row=7, column=0, columnspan=3)

button_home = Button(left_frame, text="home", height=1, command=lambda: robot.home('xyzab')).grid(row=7, column=0, columnspan=3)

#############
# MID FRAME #
#############
# def mid_frame():
# x: 0, 310
# y: -145, 400
x_dim = 310 + 2*marker_size
y_dim = 545 + 2*marker_size
mid_frame = Frame(win, bd=1, relief=SUNKEN, width=x_dim, height=y_dim)
mid_frame.grid(row=0, column=1, sticky=N+S+E+W)
c = Canvas(mid_frame, bg="white", width=x_dim, height=y_dim)
c.pack()
c.bind("<Button-1>", mouse_callback)

#cross
def draw_cross(x, y, len, thickness):
    c.create_line(x-len, y, x+len, y, fill="#476042", width=thickness)
    c.create_line(x, y-len, x, y+len, fill="#476042", width=thickness)

step=50
for x in range(0,x_dim,step):
    for y in range(0,y_dim,step):
        draw_cross(x,y,5,3)
        # print("x:",x,"y:",y) 

# marker initialize
marker = c.create_rectangle(0,0,marker_size,marker_size, fill="blue")
    
###############
# RIGHT FRAME #
###############
# def right_frame():
# pos stats
right_frame = Frame(win, bd=1)
right_frame.grid(row=0, column=2, sticky=N)

# enter coords
l1 = Label(right_frame, text = "x: ").grid(row=0, sticky=E)
l2 = Label(right_frame, text = "y: ").grid(row=1, sticky=E)
l3 = Label(right_frame, text = "z: ").grid(row=2, sticky=E)
x_entry = DoubleVar()
y_entry = DoubleVar()
z_entry = DoubleVar()
entry = []
entry_vars = [x_entry, y_entry, z_entry]
for j in range(0,3):
    entry.append(Entry(right_frame, textvariable=entry_vars[j]).grid(row=j,column=1))
move_button = Button(right_frame, text = "Move", command = lambda: move_to(x_entry.get(), y_entry.get(), z_entry.get())).grid(columnspan=2)

# increment slider
ticks = [1,2,5,10,20]
def slider_set(value):
    new_value = min(ticks, key=lambda x:abs(x-float(value)))
    slider.set(new_value)
    global increment 
    increment = int(float(new_value))

slider = Scale(right_frame, from_=1, to=20, orient=HORIZONTAL, command=slider_set)
slider.grid(columnspan=2)

# pos stats text
coords = get_coords()
pos_txt = Label(right_frame, textvariable=pos_str)
pos_txt.grid(columnspan=2, sticky=W)
pos_txt.config(justify=LEFT)

# pipette stats text
pipette_txt = Label(right_frame, textvariable=pipette_str)
pipette_txt.grid(columnspan=2, sticky=W)
pipette_txt.config(justify=LEFT)

################
# BOTTOM FRAME #
################
# def bottom_frame():
# error message
bottom_frame = Frame(win)
bottom_frame.grid(row=1, column=0, columnspan=3, sticky=S+W)

# status message
status = Label(bottom_frame, textvariable=status_str, bd=1, relief=SUNKEN, anchor=W)
status.grid(row=0,column=0, sticky=W)

# shell input
shell = Entry(bottom_frame, textvariable=shell_input).grid(row=1,column=0, sticky=W)

# connect to robot
opentrons_connect()

# gui loop
# keyboard focus to app
def handle_events(event):
    # widget = win.winfo_containing(event.x_root, event.y_root)
    if win.focus_get() == shell:
        print("shell has focus")
    else:
        print(shell)
        print("root is:", win.focus_get())
    # print("type", type(win.focus_get()))

win.focus_set()
win.bind('<Key>', key_to_cmd)
# win.bind('<Key>', handle_events)
# win.bind_all("<B1-Motion>", handle_events)

# configure app window
Grid.rowconfigure(win, 0, weight=1)
Grid.columnconfigure(win, 0, weight=1)
Grid.columnconfigure(win, 1, weight=1)    
Grid.columnconfigure(win, 2, weight=1)   

win.mainloop()