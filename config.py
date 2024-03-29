from tkinter import *
import random, os

class GUI:
    def __init__(self, game):
        db = game.db.db
        self.game = game
        self.setting = self.game.setting
        self.master = Tk()
        self.master.title('Elma AI Config')
        self.master.bind("<KeyRelease>", self.keyup)
        # works but makes double clicking episodes or seed start training   
        #self.master.bind('<Double-Button-1>', self.dblclick)
        self.top = Frame(self.master)
        self.top.pack(side=TOP)
        self.rightFrame = Frame(self.top)
        self.rightFrame.pack(side=LEFT)


        self.levWidget = Listbox(self.top, exportselection=0)
        self.levWidget.insert(END, 'ribotAI0.lev')
        self.levWidget.insert(END, 'ribotAI1.lev')
        self.levWidget.insert(END, 'ribotAI2.lev')
        self.levWidget.insert(END, 'wu.lev')
        self.levWidget.insert(END, 'ft.lev')
        self.levWidget.insert(END, 'tp.lev')
        self.levWidget.insert(END, 'ou.lev')
        self.levWidget.insert(END, 'ub.lev')
        self.levWidget.insert(END, 'ml.lev')
        self.levWidget.insert(END, 'ai.lev')
        self.levWidget.select_set(self.setting['level'].int_value or 0)
        self.levWidget.pack(side=LEFT)
        self.levWidget.bind('<Double-Button-1>', self.dblclick)

        self.agentWidget = Listbox(self.top, exportselection=0)
        self.agentWidget.insert(END, 'ribot algorithm')
        self.agentWidget.insert(END, 'Benchmark')
        self.agentWidget.insert(END, 'CEM')
        self.agentWidget.select_set(self.setting['agent'].int_value or 0)
        self.agentWidget.pack(side=LEFT)
        self.agentWidget.bind('<Double-Button-1>', self.dblclick)

        self.actionsWidget = Listbox(self.top, exportselection=0, selectmode=MULTIPLE)
        self.actionsWidget.insert(END, 'accelerate')
        self.actionsWidget.insert(END, 'brake')
        self.actionsWidget.insert(END, 'left')
        self.actionsWidget.insert(END, 'right')
        self.actionsWidget.insert(END, 'turn')
        self.actionsWidget.insert(END, 'supervolt')
        for value in self.setting['actions'].int_values or [0]:
            self.actionsWidget.select_set(value)
        self.actionsWidget.pack(side=LEFT)
        self.actionsWidget.bind('<Double-Button-1>', self.dblclick)
        self.actionsWidget.bind('<Button-3>', self.rclick)

        self.episodesLabel = Label(self.rightFrame, text="Episodes")
        self.episodesLabel.pack(anchor="w")
        self.episodesEntry = Entry(self.rightFrame)
        self.episodesEntry.insert(0, self.setting['episodes'].int_value or 5000 )
        self.episodesEntry.pack(anchor="w")

        self.fpsLabel = Label(self.rightFrame, text="FPS")
        self.fpsLabel.pack(anchor="w")
        self.fpsEntry = Entry(self.rightFrame)
        self.fpsEntry.insert(0, self.setting['fps'].int_value or 80)
        self.fpsEntry.pack(anchor="w")

        self.seedLabel = Label(self.rightFrame, text="Seed")
        self.seedLabel.pack(anchor="w")
        self.seedEntry = Entry(self.rightFrame)
        self.seedEntry.insert(0, self.setting['seed'].int_value or 752958)
        self.seedEntry.pack(anchor="w")
        self.seedButton = Button(self.rightFrame, text="Generate", command=lambda: self.seedEntry.delete(0, END) == 0 or self.seedEntry.insert(0, random.randint(0,999999)))
        self.seedButton.pack(anchor="w")

        self.arg_man = IntVar( self.rightFrame, self.setting['man'].int_value )
        self.arg_render = IntVar( self.rightFrame, self.setting['render'].int_value )
        self.arg_framebyframe = IntVar( self.rightFrame, self.setting['framebyframe'].int_value )
        self.arg_test = IntVar( self.rightFrame, self.setting['test'].int_value )
        self.arg_eol = IntVar( self.rightFrame, self.setting['eol'].int_value )
        self.manCheckbutton = Checkbutton(self.rightFrame, text="Play Manually", variable=self.arg_man)
        self.renderCheckbutton = Checkbutton(self.rightFrame, text="Render", variable=self.arg_render)
        self.framebyframeCheckbutton = Checkbutton(self.rightFrame, text="Frame by Frame", variable=self.arg_framebyframe)
        self.testCheckbutton = Checkbutton(self.rightFrame, text="Test (don't train)", variable=self.arg_test)
        self.eolCheckbutton = Checkbutton(self.rightFrame, text="Play EOL", variable=self.arg_eol)
        self.manCheckbutton.pack(anchor="w")
        self.renderCheckbutton.pack(anchor="w")
        self.framebyframeCheckbutton.pack(anchor="w")
        self.testCheckbutton.pack(anchor="w")
        self.eolCheckbutton.pack(anchor="w")

        self.loadWidget = Listbox(self.master, exportselection=0, width=100)
        self.loadWidget.insert(END, '')
        #for filename in os.listdir('keras_models'):
        #    #self.loadWidget.insert(END, '00x786_194_ribotAI0.rec_seed88148_observations17_actionsA_lr0.010000_gamma0.990000_softmax_rmsprop_sparse_categorical_crossentropy')
        #    self.loadWidget.insert(END, filename)
        self.loadWidgetRows = db( db.sequence.id > 0).select(orderby=db.sequence.hiscore)
        for row in self.loadWidgetRows:
            self.loadWidget.insert(END, "%s - score: %.2f, ep: %d, seed: %d" % (row.level.filename, row.hiscore, row.episodes, row.seed))
        self.loadWidget.select_set(self.setting['load'].int_value or 0)
        self.loadWidget.pack()
        self.loadWidget.bind('<Double-Button-1>', self.dblclick)
        #self.loadWidget.bind("<<ListboxSelect>>", self.on_loadWidget_select)

        self.infoText = Message(self.master, text="Right click an action to select all actions. Double click an action to deselect all other actions. Double click another list to automatically START.")
        self.infoText.pack(fill=BOTH)

        self.doneButton = Button(self.master, text="START", height=10, command=self.start, background="#999")
        self.doneButton.pack(fill=BOTH)

        # handle closing window so that game will not proceed if closing (rather than pressing start button)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.mainloop()

    def on_close(self):
        #filehandler = open("config.pickle","wb")
        #pickle.dump(self, filehandler)
        #filehandler.close()
        self.master.destroy()
        import sys
        sys.exit()

    def keyup(self, e):
        #print(e)
        # <KeyRelease event state=Mod1 keysym=Return keycode=13 char='\r' x=796 y=86>
        if e.keysym == 'Return':
            self.start()
        elif e.keysym == 'Escape':
            self.on_close()

    def dblclick(self, e):
        #print(e, e.widget)
        # <ButtonPress event state=Mod1 num=1 x=39 y=91>
        if e.widget == self.actionsWidget:
        # [accelerate, brake, left, right, turn, supervolt]
            #for action in self.game.input:
            #for value in self.setting['actions'].int_values or [0]:
            #    self.actionsWidget.select_set(value)
            self.actionsWidget.selection_clear(0, END)
            self.actionsWidget.selection_set(ACTIVE)
        else:
            self.start()

    def rclick(self, e):
        # self.actionsWidget.bind('<Button-3>', self.rclick)
        if e.widget == self.actionsWidget:
            self.actionsWidget.selection_set(0, END)
        #print(e)

    def noop(self, e):
        pass

    def start(self):
        # this setup of vars might contain some legacy of old command line usage
        selected_level_index = self.levWidget.curselection()[0]
        selected_level_name = self.levWidget.get(selected_level_index)
        self.setting['level'].update_record( int_value=selected_level_index, str_value=selected_level_name )

        # load_ids are the row ids to select from in the load widget
        # including 0 which means no selection
        # whereas the selected index references which of those load_ids to load
        selected_load_index = self.loadWidget.curselection()[0]
        selected_load_name = self.loadWidget.get(selected_load_index)
        load_ids = [0] + [row.id for row in self.loadWidgetRows]
        self.setting['load'].update_record( int_value=selected_load_index, str_value=selected_load_name, int_values=load_ids )

        # set before loading
        seed = self.seedEntry.get().strip()
        seed = int(seed) if seed.isnumeric() else 0
        # set seed in run.py
        #if seed != self.game.seed:
        #    self.game.set_seed( seed )
        self.setting['seed'].update_record( int_value=seed )

        """
        # only update db here, and load settings in run
        #self.game.arg_load = True if self.loadWidget.curselection()[0] > 0 else False
        if self.loadWidget.curselection()[0] > 0:
            selected_model_index = self.loadWidget.curselection()[0]
            self.game.load = self.loadWidget.get(selected_model_index)
            # when loading model, use same seed as that model
            selected_model_seed_index = self.game.load.find('seed')
            seed_str = ""
            for char in self.game.load[selected_model_seed_index+4:]:
                if char.isnumeric():
                    seed_str += char 
                else:
                    break
            #print(seed_str)
            self.game.set_seed( int(seed_str) )
            #print(self.game.load)
        """

        n_episodes = self.episodesEntry.get()
        self.setting['episodes'].update_record( int_value=int(n_episodes) )

        fps = self.fpsEntry.get()
        fps = int(fps) if fps.isnumeric() and int(fps) >= 30 else 80
        self.setting['fps'].update_record( int_value=fps )


        #self.game.n_episodes = self.episodesEntry.get() # set below
        self.game.args.append( self.episodesEntry.get() )
        #print(self.game.args)
        self.setting['man'].update_record( int_value=self.arg_man.get() )
        self.setting['render'].update_record( int_value=self.arg_render.get() )
        self.setting['framebyframe'].update_record( int_value=self.arg_framebyframe.get() )
        self.setting['test'].update_record( int_value=self.arg_test.get() )
        self.setting['eol'].update_record( int_value=self.arg_eol.get() )

        selected_agent_index = self.agentWidget.curselection()[0]
        selected_agent_name = self.agentWidget.get(selected_agent_index)
        #print("agent: %d % s" % (selected_agent_index, selected_agent_name))
        self.setting['agent'].update_record( int_value=selected_agent_index, str_value=selected_agent_name )

        self.setting['actions'].update_record( int_value=None, int_values=self.actionsWidget.curselection() )

        self.game.db.db.commit()
        self.master.destroy()


if __name__ == "__main__":
    import game
    game = game.Game()
    config = GUI(game)




# not working, and makes terminal colors not work
#from pypsi import shell, wizard
#from pypsi.completers import choice_completer

"""
# https://pythonhosted.org/pypsi/pypsi.wizard.html#pypsi.wizard.WizardStep
sh = shell.Shell()
# https://github.com/ameily/pypsi
# https://github.com/ameily/pypsi/issues/49
def tab_complete():
    #from pypsi.completers import command_completer
    #return completions = command_completer(self.parser, shell, args, prefix)
    return choice_completer(['ribotAI0.lev', 'ribotAI1.lev', 'ft.lev'])

wiz = wizard.PromptWizard(
    name="Elma AI",
    description="Welcome",

    steps=(
        # WizardStep(id, name, help, default=None, completer=None, validators=None)
        wizard.WizardStep(
            id = "level",
            name = "Level",
            help = "",
            #completer = choice_completer(['ribotAI0.lev', 'ribotAI1.lev', 'ft.lev']),
            completer = tab_complete,
            default = "ribotAI0.lev"
        ),
        wizard.WizardStep(
            id = "step2",
            name = "Step 2",
            help = "",
            completer = choice_completer([1, 2, 3]),
            default = 2
        ),
    )
)

#argz = wiz.run(sh)
#print(argz.level, argz.step2)
#sys.exit()"""