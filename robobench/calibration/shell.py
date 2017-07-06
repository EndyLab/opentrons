from tkinter import *
import collections
from opentrons import robot, instruments

# from mess import FixedRatio

INCR = 2

# ports = robot.get_serial_ports_list()
# print(ports)
# robot.connect(ports[0])

# simulator
robot.connect('Virtual Smoothie')
robot.home(now=True)

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

def mouse_callback(event):
    msg.set("clicked at " + str(event.x) + " " + str(event.y))
    move_to(float(event.x), float(event.y), 100)
    print(msg.get())

def move_axis_by(axis, incr):
    msg.set("moving axis: " + str(axis) + " by " + str(incr) + " amount")
    print(msg.get())

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
    # pos_str.set("x: " + str(coords.x) + "\ny: " + str(coords.y) + "\nz: " + str(coords.z))

def move_to(x, y, z):
    robot.move_head(x=x, y=y, z=z)
    print("moving robot to: x= ",x," y= ",y, " z= ",z, sep='')
    pos_str.set("x: " + str(x) + "\ny: " + str(y) + "\nz: " + str(z))

PIPETTE_AXIS = 'a'

# "active pipette: \nplunger pos: \npipette a:\n pipette b:"
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
    msg.set("axis: " + axis + " selected")
    update_pipette_str("axis", axis)
    # pipette_str.set("active pipette: " + axis + "\nplunger pos: \npipette a:\npipette b:")


def depress_pipette(incr):
    # moves A axis to position 5
    if PIPETTE_AXIS == 'a':
        robot._driver.move_plunger(mode='absolute', a=incr)
        update_pipette_str("pos_a", str(incr),"pos_active", str(incr))
    elif PIPETTE_AXIS == 'b':
        robot._driver.move_plunger(mode='absolute', b=incr)
        update_pipette_str("pos_b", str(incr),"pos_active", str(incr)) 

    msg.set("pipette "+PIPETTE_AXIS+" plunger pos changed by "+str(incr))

def key_to_cmd(event):
    key_dict_robot = {
        'Up': ('y', INCR), 
        'Down': ('y', -1*INCR), 
        'Left': ('x', -1*INCR), 
        'Right': ('x', INCR), 
        'Return': ('z', INCR), 
        'Shift_R': ('z', -1*INCR)
    }

    key_dict_pipette = {
        'w': (depress_pipette, INCR), 
        's': (depress_pipette, -1*INCR), 
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


#Create & Configure root 
win = Tk()

Grid.rowconfigure(win, 0, weight=1)

Grid.columnconfigure(win, 0, weight=1)
Grid.columnconfigure(win, 1, weight=1)    
Grid.columnconfigure(win, 2, weight=1)           

# status bar message
msg = StringVar()
msg.set("status message...")

pos_str = StringVar()
pos_str.set("x: \ny: \nz:")

pipette_str = StringVar()
pip_desc = {
    "active pipette: "  : "",
    "\nplunger pos: "   : "",
    "\npipette a: "      : "",
    "\npipette b: "      : ""
}

def dict_to_str(strdict):
    res = ""
    for key in strdict.keys():
        res += (key + strdict[key])
    pipette_str.set(res)

dict_to_str(pip_desc)
# keyboard focus
win.focus_set()
win.bind('<Key>', key_to_cmd)

# control buttons
left_frame = Frame(win, bd=1)
left_frame.grid(row=0, column=0, sticky=N)

# canvas grid
# mouse bind event
mid_frame = Frame(win, bd=1, relief=SUNKEN, width=200, height=200)
mid_frame.grid(row=0, column=1, sticky=N+S+E+W)
# mid_frame = FixedRatio(master=win, width=200, height=200)
# mid_frame.bind("<Button-1>", mouse_callback)
# mid_frame.bind('<Configure>', mid_frame._resize)
c = Canvas(mid_frame, bg="white", width=200, height=200)
c.pack()
c.bind("<Button-1>", mouse_callback)

#cross
def draw_cross(x, y, len, thickness):
    c.create_line(x-len, y, x+len, y, fill="#476042", width=thickness)
    c.create_line(x, y-len, x, y+len, fill="#476042", width=thickness)

step=50
for x in range(0,200,step):
    for y in range(0,200,step):
        draw_cross(x,y,5,3)
        # print("x:",x,"y:",y)  

# pos stats
right_frame = Frame(win, bd=1)
right_frame.grid(row=0, column=2, sticky=N)

# error message
bottom_frame = Frame(win)
bottom_frame.grid(row=1, column=0, columnspan=3, sticky=S+W)

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

# incr slider
ticks = [1,2,5,10,20]
def slider_set(value):
    new_value = min(ticks, key=lambda x:abs(x-float(value)))
    slider.set(new_value)
    global INCR 
    INCR = int(float(new_value))

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


# status message
status = Label(bottom_frame, textvariable=msg, bd=1, relief=SUNKEN, anchor=W)
status.grid(row=0,column=0, sticky=W)

win.mainloop()