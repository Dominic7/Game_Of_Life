from Tkinter import *
import tkColorChooser
from copy import deepcopy
import math
import random

class node:

    def __init__(self, id, **stats):
        '''stats include : value, moveSpeed, hp, decayLife, str, defense,  '''
        
        self.id = id 
        self.alive = True
        self.stats = deepcopy(stats) #used for easy node copying

        self.value = stats.get("value", 1) #value/payload of node -- can be used as id or value linked with passed function in GameOfLife
        self.moveSpeed = stats.get('moveSpeed', 1) #speed(number of spaces) node can travel -- Default = 1
        self.hp = stats.get('hp', 1.0) #life points of node - used for when fights enabled -- Default = 1.0
        self.decayLife = stats.get('decayLife', 1) #number of turns needed to decay - used when decayRate is enabled -- Default = 1 turn
        self.str = stats.get('str', 1) #strength of node - used for when fights enabled -- Default = 1 damage
        self.defense = stats.get('defense', 1) #defense of node - used for when fights enabled -- Default = 1 damage resistance



class GameOfLife:
    
    def __init__(self, rows, columns, gui = None, **rules):
        ''' Rules include  -- liveRate, dieRate, decayRate, moveChance ,mapOb, fightRate, historyCount   '''
        self.state = [[None for j in range(columns)] for i in range(rows)]

        self.rows = rows
        self.columns = columns

        self.state_change = False #variable to control changes while transistioning states
        


        self.gui = gui # used to hold Tk() instance from gui class if being used with a gui

        self.random_generator = None # Set to None by default to use built in random generator

        self.historyCount = rules.get('historyCount', 10) #number of past states to keep -- Default 10
        self.current_history_count = 0
        self.history = {}

        self.rules = deepcopy(rules)
        self.continuous = rules.get('continuous', False)
        self.liveRate = rules.get('liveRate', 2)
        self.dieRate = rules.get('dieRate', 3)
        self.decayRate = rules.get('decayRate')
        self.moveChance = rules.get('moveChance')   #Enables the ability for nodes to move -- percent chance node will move at set node speed
        self.mapOb = rules.get('mapOP')             #Used for random GoL generation - percentage of map covered in opstacles
        self.fightRate = rules.get('fightRate')     #used to simulate fight chance - percent chance to fight adjacent neighbor 


    #----------------------- Option Functions---------------------------------#

    def update_size(self, rows, columns):
       
        if self.rows > rows:
            self.rows = rows
        if self.columns > columns:
            self.columns = columns

        new_state = [[None for j in range(columns)] for i in range(rows)]

        for i in range(self.rows):
            for j in range(self.columns):
                if self.state[i][j] is not None:
                    new_state[i][j] = deepcopy(self.state[i][j])

        self.state = deepcopy(new_state)
        self.rows = rows
        self.columns = columns




    def change_random_generator(self, random_gen):
        self.random_generator = random_gen


    def random_start(self, min_nodes, max_nodes, seed = None, random_gen = None, gui_funct = None):
        num_added = 0
        self.seed = seed
        random.seed(self.seed)
        trys = 0
        while num_added < max_nodes:
            x = random.randint(0,self.rows-1)
            y = random.randint(0,self.columns-1)

            if self.state[x][y] is None:
                self.state[x][y] = node(0)
                num_added += 1
            else:
                trys += 1
            if trys > 6 and num_added > min_nodes:
                break


        if gui_funct is not None:
            gui_funct()

        

    def change_state_rules(self, **rules):
        #self.rules = deepcopy(rules)
        #['liveRate', 'dieRate', 'decayRate', 'mapOP', 'fightRate'] 
        self.continuous = rules.get('continuous', False)
        self.liveRate = rules.get('liveRate', self.liveRate)
        self.dieRate = rules.get('dieRate', self.dieRate)
        self.decayRate = rules.get('decayRate')
        self.moveChance = rules.get('moveChance')
        self.fightRate = rules.get('fightRate')

    def set_default_node(self, **stats):
        
        #probably should put some validation here

        self.default_node_stats = stats


    def insert_node(self, x, y,n = None):
        if n is None:
            self.state[x][y] = node(0)
        else:
            self.state[x][y] = node(n.id, n.stats)
            
    def insert_obstacle(self, x,y):
        self.state[x][y] = -1

    def delete_node(self, x,y):
        self.state[x][y] = None

    #-------------------- GoL Sim Functions -------------------------------#

    def next_state(self, ticks = None, gui_funct = None):
        '''ticks = number of state loops
        gui_funct = function to run at the end of each state change'''
        if ticks is None:
            #sim one state change
            turns = 1
        else:
            turns = ticks

        for t in range(turns):
            self.next = deepcopy(self.state)

            for i in range(self.rows):
                for j in range(self.columns):
                    if self.state[i][j] is -1:
                        continue
                    neighbors = self.neighbor_count(i,j)

                        
                    if self.state[i][j] is None:
                        # Empty ---------> Live
                        if neighbors is self.liveRate: 
                            self.next[i][j] = node(0)
                    #---------------------------------------------------------------Edit for priority 
                    elif self.state[i][j] is not -1:
                        #Live ------------> Empty/Dead

                        if self.fightRate is not None:
                            k = random.randint(0, 100)
                            if k <= (self.fightRate*100):
                                x,y = self.find_random_neighbor(i,j)
                                
                                if x is not None and y is not None and self.state[x][y] is not None:
                                    if x < i or (i > x and y > j) or (i == x and y < j): #---------------------checking to see if the node has already been processed or not
                                        diff = self.state[i][j].str - self.next[x][y].defense
                                        if diff > 0:
                                            self.next[x][y].hp -= diff
                                        else:
                                            self.next[x][y].hp -= 1
                                        if self.next[x][y].hp <= 0:
                                            self.next[x][y] = None
                                    else:
                                        diff = self.state[i][j].str - self.state[x][y].defense
                                        if diff > 0:
                                            self.state[x][y].hp -= diff
                                        else:
                                            self.state[x][y].hp -= 1
                                        if self.state[x][y].hp <= 0:
                                            self.state[x][y] = None

                        if neighbors >= self.dieRate or self.state[i][j].alive is False:
                            if self.decayRate is None:
                                self.next[i][j] = None
                            else:
                                self.next[i][j].alive = False
                                self.next[i][j].decayLife -= 1
                                if self.next[i][j].decayLife <= 0:
                                    self.next[i][j] = None

                        if self.moveChance is not None:
                            k = random.randint(0,100)
                            if k <= self.moveChance*100:
                                x,y = self.find_random_open(i,j, )
                                if x is not None and y is not None:
                                    self.next[x][y] = self.state[i][j]
                                
            if gui_funct is not None:
                gui_funct()

            self.history[self.current_history_count % self.historyCount] = deepcopy(self.state)
            self.current_history_count += 1

            self.state = deepcopy(self.next)

    def find_random_open(self, i, j):
        found = False
        
        dist = self.state[i][j].moveSpeed

        while not found:
        
            x = random.randint(-dist, dist)
            y = random.randint(-dist,dist)

            if x is 0 and y is 0:
                continue
            if self.continuous:
                if self.next[(i+x) % self.rows][(j+y) % self.columns] is None:
                    if x > 0 and x > 0 and  self.state[(i+x) % self.rows][(j+y) % self.columns] is None: #<------------------------may need to check for correctness
                        return (i+x, j+y)
            else:
                try:
                    if self.next[i+x][j+y] is None:
                        return (i+x, j+y)
                except IndexError:
                    pass

    def find_random_neighbor(self, i, j):
        found = False
        
        while not found:
        
            x = random.randint(-1, 1)
            y = random.randint(-1,1)
            #---------------------------------------------------need to fix continuous logic
            if x is 0 and y is 0:
                continue

            if self.next[i+x][j+y] is not None and self.next[i+x][j+y] is not -1:
                return (i+x, j+y)

            if self.continuous:
                if self.next[(i+x) % self.rows][(j+y) % self.columns] is not None and self.next[(i+x) % self.rows][(j+y) % self.columns] is not - 1:    
                    return (i+x, j+y)
            else:
                try:
                    if self.next[i+x][j+y] is not None and self.next[i+x][j+y] is not -1:
                        return (i+x, j+y)
                except IndexError:
                    pass


    def neighbor_count(self, x,y, state = None):

        neighbor_c = 0

        if state is None:
            for i in range(-1,2):
                for j in range(-1,2):
                    try:
                        if self.state[i+x][j+y] is not None and self.state[i+x][j+y] is not -1 :
                            neighbor_c += 1
                    except IndexError:
                        pass
        else:
            for i in range(-1,2):
                for j in range(-1,2):
                    try:
                        if self.state[i+x][j+y] is not None and self.state[i+x][j+y] is not -1 :
                            neighbor_c += 1
                    except IndexError:
                        pass
        return neighbor_c






class GoLgui:
   
    def __init__(self): 
        self.root = Tk()
        self.root.geometry("800x600+200+200")
        #self.root.resizable(width = False, height = False)

        self.win_menu_width = 200
        self.win_height = 600
        
        self.entry_size = 10

        
        #------------------------Menu Options---------------------------------------#


        self.menu_window = Frame(self.root, width = self.win_menu_width, height = self.win_height)
        self.menu_window.pack(side = LEFT)

        self.label_names = ['Map Size x:', 'Map Size y:', 'Live Rate', 'Die Rate',"Decay Rate" ,'Move Chance', 'Map Obstacle Chance', 'Fight Chance', 'Past History Count']
        self.rule_names = [ None, None,'liveRate', 'dieRate', 'decayRate', 'moveChance', None, 'fightRate']
         #''' Rules include  -- liveRate, dieRate, decayRate, moveChance ,mapOb, fightRate, historyCount   '''
        self.var_list = [IntVar(), IntVar(), DoubleVar(), DoubleVar(), DoubleVar(), DoubleVar(), DoubleVar(), DoubleVar(), IntVar()]
        self.rule_set = {} # going to keep vals pull from var_list
        self.var_check_list = [BooleanVar() for i in range(len(self.label_names))]
        
        self.menu_dict = {}


        for i in range(len(self.label_names)):
            Label(self.menu_window, text=self.label_names[i]).grid(row = i, column = 0, sticky = W)
            Entry(self.menu_window, textvariable=self.var_list[i], width = self.entry_size).grid(row = i, column = 1)
            Checkbutton(self.menu_window, variable=self.var_check_list[i], onvalue=True, offvalue = False ).grid(row = i, column = 2)
            self.menu_dict[self.label_names[i]] = [self.var_list[i], self.var_check_list[i]]



        #-----------------------Menu Buttons--------------------------------------- Start at row 9-----------#

        butt_count = 9

        self.var_continuous = BooleanVar()
        self.check_continuous = Checkbutton(self.menu_window, text="Continuous Map", var = self.var_continuous, onvalue=True, offvalue=False)
        self.check_continuous.grid(row=butt_count, sticky=E)


        self.color_change_button = Button(self.menu_window, text="Change Colors")
        self.color_change_button.bind("<Button-1>", self.color_change_menu)
        self.color_change_button.grid(row = butt_count+1, sticky=W)

        self.button_nState = Button(self.menu_window, text="Go to nth state")
        self.button_nState.bind("<Button-1>", self.gol_run)
        self.button_nState.grid(row=butt_count+2, column=0, sticky=W)

        self.var_NthState = IntVar()
        self.entry_NthState = Entry(self.menu_window, textvariable=self.var_NthState, width = self.entry_size)
        self.var_NthState.set(1)
        self.entry_NthState.grid(row=butt_count+2, column=1)

        self.button_reset = Button(self.menu_window, text="Reset")
        self.button_reset.bind("<Button-1>", self.gol_reset)
        self.button_reset.grid(row=butt_count+3, column=0, sticky=W)

        self.button_next = Button(self.menu_window, text="Next State")
        self.button_next.bind("<Button-1>", self.gol_run)
        self.button_next.grid(row=butt_count+4, column=1)
        
        self.button_map_size = Button(self.menu_window, text="Map Size Update", command = self.redraw_grid)
        self.button_map_size.grid(row=butt_count+5, sticky=W)

        self.button_random_grid = Button(self.menu_window, text="Random Grid Config", command = self.random_grid)
        self.button_random_grid.grid(row=butt_count+6, sticky=W)
        
        self.var_max_rand_n = IntVar()
        self.entry_max_rand_nodes = Entry(self.menu_window, textvariable = self.var_max_rand_n, width=self.entry_size)
        self.entry_max_rand_nodes.grid(row=butt_count+6, column=1 , sticky=E)



        #---------------------------------Canvas-----------------------------------------#

        self.win_canvas_width = 600



        self.gol_win = Canvas(self.root, width = self.win_canvas_width, height = self.win_height)
        self.gol_win.pack(side = RIGHT ,expand=True, fill=BOTH)
        self.gol_win.bind("<Button-1>", self.gol_node_click)

        #-------------------------------- GOL variables ---------------------------------#

        self.nodes_x = 5#self.menu_dict["Map Size x:"][0].get() #used for reference on map size 
        self.nodes_y = 5#self.menu_dict["Map Size y:"][0].get() #used for reference on map size
        self.GOL = GameOfLife(self.nodes_x, self.nodes_y)

        self.node_color = 'black'
        self.obstacle_color = 'gray'
        self.empty_color = 'white'


        #-----------------------default canvas draw-----------------------------------#

        self.node_width = (self.win_canvas_width/self.nodes_x)
        self.node_height =(self.win_height/self.nodes_y)

        self.xy_to_coords = {}
        self.square_grid = []

        for i in range(self.node_width):
            self.square_grid.append([])
            for j in range(self.nodes_y):
                x1 = i*self.node_width #top left corner
                x2 = j*self.node_height 
                x3 = x1 + self.node_width
                x4 = x2 + self.node_height

                self.xy_to_coords[(i,j)] = (x1,x2,x3,x4)

                self.square_grid[i].append(self.gol_win.create_rectangle(x1,x2,x3,x4, fill="white"))

        
        self.root.mainloop()


    #-----------------------GUI Functions--------------------------------------------#

    def random_grid(self):
        try:
            self.nodes_x = self.var_list[0].get()
            self.nodes_y = self.var_list[1].get()

            self.node_width = (self.win_canvas_width/self.nodes_x)
            self.node_height = (self.win_height/self.nodes_y)


            self.GOL = GameOfLife(self.nodes_x, self.nodes_y)
        
            self.GOL.random_start(0, self.var_max_rand_n.get())#<----------------------------------need to get min and max num of nodes some how
            self.redraw_grid() 
        except ZeroDivisionError:
            pass

    def redraw_grid(self):

        self.gol_win.delete('all')

        self.nodes_x = self.var_list[0].get()
        self.nodes_y = self.var_list[1].get()

        self.node_width = (self.win_canvas_width/self.nodes_x)
        self.node_height =(self.win_height/self.nodes_y)

        self.xy_to_coords = {}
        self.square_grid = []

        for i in range(self.nodes_x):
            self.square_grid.append([])
            for j in range(self.nodes_y):
                x1 = i*self.node_width #top left corner
                x2 = j*self.node_height 
                x3 = x1 + self.node_width
                x4 = x2 + self.node_height

                self.xy_to_coords[(i,j)] = (x1,x2,x3,x4)

                self.square_grid[i].append(self.gol_win.create_rectangle(x1,x2,x3,x4, fill="white"))

        if self.GOL is not None:
            self.GOL.update_size(self.nodes_x, self.nodes_y)
            self.update_grid()



    def clear_grid(self):
        for i in range(self.nodes_x):
            for j in range(self.nodes_y):
                self.gol_win.itemconfig(self.square_grid[i][j], fill = 'white')

    def update_grid(self):
        refresh = False

        if self.nodes_x >= 50 or self.nodes_y >=50:
            refresh = True
            self.refresh_rate = max(self.nodes_x, self.nodes_y)/5 #<------------------------------------need to figure out best number/eq

        count = 0
        for i in range(self.nodes_x):
            for j in range(self.nodes_y):
                if self.GOL.state[i][j] is None:
                    self.gol_win.itemconfig(self.square_grid[i][j], fill = self.empty_color)
                elif self.GOL.state[i][j] is not -1:
                    self.gol_win.itemconfig(self.square_grid[i][j], fill = self.node_color)
                else:
                    self.gol_win.itemconfig(self.square_grid[i][j], fill = self.obstacle_color)

                
                if refresh:
                    count += 1
                    if count % self.refresh_rate is 0:
                        self.root.update_idletasks()

    def color_change_menu(self, event):
        color_menu = Tk()
        #color_menu = Frame(color_root, name="color change menu")

        node_color_butt = Button(color_menu, text="Change Node Color", command = self.colorSelectNode)
        obs_color_butt = Button(color_menu, text="Change Obstacle Color", command = self.colorSelectObs)
        empty_color_butt = Button(color_menu, text="Change Empty Color", command = self.colorSelectEmpty)
        node_color_butt.pack(side=LEFT)
        obs_color_butt.pack(side=LEFT)
        empty_color_butt.pack(side=LEFT)
    
    def colorSelectNode(self):
        rgb, hx = tkColorChooser.askcolor()
        self.node_color = hx

    def colorSelectObs(self):
        rgb, hx = tkColorChooser.askcolor()
        self.obstacle_color = hx

    def colorSelectEmpty(self):
        rgb, hx = tkColorChooser.askcolor()
        self.empty_color = hx

    def gol_node_click(self, event):
        self.click_x = event.x/self.node_width
        self.click_y = event.y/self.node_height


        self.clicked_node = self.GOL.state[self.click_x][self.click_y]

        self.node_edit_menu = Toplevel()
        #self.node_edit_menu.pack()
        '''stats include : value, moveSpeed, hp, decayLife, str, defense,  '''
        self.node_stat_labels = ["Value", "Move Speed", "Life", "Decay Life", "Strength", "Resistance"]
        self.node_stat_vars = [IntVar() for i in range(len(self.node_stat_labels))]

        for i in range(len(self.node_stat_labels)):
            Label(self.node_edit_menu, text=self.node_stat_labels[i]).grid(row=i, column=0, sticky=W)
            Entry(self.node_edit_menu, textvariable=self.node_stat_vars[i]).grid(row=i, column=1)

        if self.clicked_node is not None:
            if self.clicked_node.value is not None:
                self.node_stat_vars[0].set(self.clicked_node.value)
            if self.clicked_node.moveSpeed is not None:
                self.node_stat_vars[1].set(self.clicked_node.moveSpeed)
            if self.clicked_node.life is not None:
                self.node_stat_vars[2].set(self.clicked_node.life)
            if self.clicked_node.decayLife is not None:
                self.node_stat_vars[3].set(self.clicked_node.decayLife)
            if self.clicked_node.str is not None:
                self.node_stat_vars[4].set(self.clicked_node.str)
            if self.clicked_node.defense is not None:
                self.node_stat_vars[5].set(self.clicked_node.defense)


        self.edit_accept_butt = Button(self.node_edit_menu, text="Save Changes")
        self.edit_accept_butt.bind("<Button-1>", self.edit_node_button_click)
        self.edit_accept_butt.grid(row=6,column=0)

        self.edit_cancel_butt = Button(self.node_edit_menu, text="Cancel")
        self.edit_cancel_butt.bind("<Button-1>",self.edit_node_button_click)
        self.edit_cancel_butt.grid(row=6,column=1)

        self.delete_node_butt = Button(self.node_edit_menu, text="Remove Node")
        self.delete_node_butt.bind("<Button-1>", self.edit_node_button_click)
        self.delete_node_butt.grid(row=7, column = 0)
        
        self.obs_butt = Button(self.node_edit_menu, text="Make Obstacle")
        self.obs_butt.bind("<Button-1>", self.edit_node_button_click)
        self.obs_butt.grid(row=7, column=1)

    def edit_node_button_click(self, event):
        if event.widget is self.delete_node_butt:
            self.GOL.state[self.click_x][self.click_y] = None
            self.gol_win.itemconfig(self.square_grid[self.click_x][self.click_y], fill = self.empty_color)
        
        elif event.widget is self.obs_butt:
            self.GOL.state[self.click_x][self.click_y] = -1
            self.gol_win.itemconfig(self.square_grid[self.click_x][self.click_y], fill = self.obstacle_color)

        elif event.widget is self.edit_accept_butt:

            if self.clicked_node is None:
                self.GOL.state[self.click_x][self.click_y] = node(0)
                self.clicked_node = self.GOL.state[self.click_x][self.click_y]

            if self.node_stat_vars[0].get() is not None:
                self.clicked_node.value = self.node_stat_vars[0].get()
            if self.node_stat_vars[1].get() is not None:
                self.clicked_node.moveSpeed = self.node_stat_vars[1].get()
            if self.node_stat_vars[2].get() is not None:
                self.clicked_node.life = self.node_stat_vars[2].get()
            if self.node_stat_vars[3].get() is not None:
               self.clicked_node.decayLife = self.node_stat_vars[3].get()
            if self.node_stat_vars[4].get() is not None:
                self.clicked_node.str = self.node_stat_vars[4].get()
            if self.node_stat_vars[5].get() is not None:
                self.clicked_node.defense = self.node_stat_vars[5].get()

            self.gol_win.itemconfig(self.square_grid[self.click_x][self.click_y], fill = self.node_color)

        self.node_edit_menu.destroy()


    #-----------------------GoL Pass Through Functions-------------------------------#
    
    def check_rules(self):
        for i in range(len(self.rule_set)):
            if self.var_check_list[i].get() is True:
                if self.var_check_list[i].get() is not self.rule_set[i]:
                    return False
        return True

    def update_rules(self):
        for i in range(2, len(self.rule_set)):
            if self.var_check_list[i].get() is True and self.rule_names[i] is not None:
                self.rule_set[self.rule_names[i]] = self.var_list[i].get()
   

    def gol_run(self, event):
        if self.GOL is None: 
            #then first time setting up and randomizing

            self.GOL = GameOfLife(self.nodes_x, self.nodes_y)
            self.GOL.random_start(0, 15, None, None, self.update_grid) 
            

        if event.widget is self.button_next:
            if not self.check_rules():
                self.update_rules()
                self.GOL.change_state_rules(self.rule_set)
            self.GOL.next_state()
            self.update_grid()
        else:
            self.GOL.next_state(self.var_NthState.get(),self.update_grid)
            


    def gol_reset(self, event):
        self.GOL = None
        self.clear_grid()



if __name__=='__main__':
    g = GoLgui()



    #TO DO
    # - Previous button
    # - steady state checker 
    # - pattern recogition
