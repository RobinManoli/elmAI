from tkinter import *

class GUI:
    def __init__(self, game):
        self.game = game
        self.master = Tk()
        self.master.title('Elma AI Config')
        self.top = Frame(self.master)
        self.top.pack(side=TOP)
        self.rightFrame = Frame(self.top)
        self.rightFrame.pack(side=LEFT)


        self.levWidget = Listbox(self.top, exportselection=0)
        self.levWidget.insert(END, 'ribotAI0.lev')
        self.levWidget.insert(END, 'ribotAI1.lev')
        self.levWidget.insert(END, 'ft.lev')
        self.levWidget.select_set(0)
        self.levWidget.pack(side=LEFT)

        self.fpsWidget = Listbox(self.top, exportselection=0)
        self.fpsWidget.insert(END, '30 fps')
        self.fpsWidget.insert(END, '80 fps')
        self.fpsWidget.insert(END, '500 fps')
        self.fpsWidget.insert(END, '1000 fps')
        self.fpsWidget.select_set(1)
        self.fpsWidget.pack(side=LEFT)

        self.agentWidget = Listbox(self.top, exportselection=0)
        self.agentWidget.insert(END, 'CEM')
        self.agentWidget.select_set(0)
        self.agentWidget.pack(side=LEFT)

        self.actionsWidget = Listbox(self.top, exportselection=0, selectmode=MULTIPLE)
        self.actionsWidget.insert(END, 'accelerate')
        self.actionsWidget.insert(END, 'brake')
        self.actionsWidget.insert(END, 'left')
        self.actionsWidget.insert(END, 'right')
        self.actionsWidget.insert(END, 'turn')
        self.actionsWidget.insert(END, 'supervolt')
        self.actionsWidget.select_set(0)
        self.actionsWidget.pack(side=LEFT)

        self.episodesLabel = Label(self.rightFrame, text="Episodes")
        self.episodesLabel.pack(anchor="w")
        self.episodesEntry = Entry(self.rightFrame)
        self.episodesEntry.insert(0, 200)
        self.episodesEntry.pack(anchor="w")

        self.arg_man = IntVar()
        self.arg_render = IntVar()
        self.arg_test = IntVar()
        self.manCheckbutton = Checkbutton(self.rightFrame, text="Play Manually", variable=self.arg_man)
        self.renderCheckbutton = Checkbutton(self.rightFrame, text="Render", variable=self.arg_render)
        self.testCheckbutton = Checkbutton(self.rightFrame, text="Test (don't train)", variable=self.arg_test)
        self.manCheckbutton.deselect()
        self.renderCheckbutton.select()
        self.testCheckbutton.deselect()
        self.manCheckbutton.pack(anchor="w")
        self.renderCheckbutton.pack(anchor="w")
        self.testCheckbutton.pack(anchor="w")

        self.loadWidget = Listbox(self.master, exportselection=0, width=100)
        self.loadWidget.insert(END, '')
        self.loadWidget.insert(END, '00x786_194_ribotai0.recseed43364_observations19_actionsA_lr0.010000_gamma0.990000_softmax_rmsprop_sparse_categorical_crossentropy')
        self.loadWidget.insert(END, '00x794_184_ribotai0.recseed43364_observations19_actionsA_lr0.010000_gamma0.990000_softmax_rmsprop_sparse_categorical_crossentropy')
        self.loadWidget.select_set(0)
        self.loadWidget.pack()

        self.doneButton = Button(self.master, text="START", height=10, command=self.start)
        self.doneButton.pack(fill=BOTH)

        # handle closing window so that game will not proceed if closing (rather than pressing start button)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.mainloop()

    def on_close(self):
        self.master.destroy()
        import sys
        sys.exit()

    def start(self):
        # this setup of vars keep the possibility of having command line args intact
        selected_level_index = self.levWidget.curselection()[0]
        selected_level_name = self.levWidget.get(selected_level_index)
        self.game.args.append(selected_level_name)

        self.game.arg_fps30 = True if self.fpsWidget.curselection()[0] == 0 else False
        # default fps 80 not handled here as it is default
        self.game.arg_fps500 = True if self.fpsWidget.curselection()[0] == 2 else False
        self.game.arg_fps1000 = True if self.fpsWidget.curselection()[0] == 3 else False

        #self.game.arg_load = True if self.loadWidget.curselection()[0] > 0 else False
        if self.loadWidget.curselection()[0] > 0:
            selected_model_index = self.loadWidget.curselection()[0]
            self.game.load = self.loadWidget.get(selected_model_index)
            #print(self.game.load)

        #self.game.n_episodes = self.episodesEntry.get() # set below
        self.game.args.append( self.episodesEntry.get() )
        self.game.arg_man = self.arg_man.get() == 1
        self.game.arg_render = self.arg_render.get() == 1 or self.game.arg_man
        self.game.arg_test = self.arg_test.get() == 1
        #print(self.game.args)

        self.game.arg_cem = True if not self.game.arg_man and self.agentWidget.curselection()[0] == 0 else False
        self.game.arg_ddpg = False
        self.game.arg_rltf = False

        # [accelerate, brake, left, right, turn, supervolt]
        for selected_action in self.actionsWidget.curselection():
            self.game.n_actions += 1
            elmainputs = [0, 0, 0, 0, 0, 0]
            elmainputs[selected_action] = 1
            self.game.actions.append(elmainputs)
            action_name = self.actionsWidget.get(selected_action)
            self.game.actions_str += action_name[0].upper()
        #print(self.game.n_actions, self.game.actions, self.game.actions_str)
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