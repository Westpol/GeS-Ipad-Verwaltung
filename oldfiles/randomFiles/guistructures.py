import tkinter as tk
import time


class Frontend:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("{}x{}".format(960, 540))
        self.root.minsize(960, 540)
        self.root.maxsize(960, 540)
        self.root.bind("<KeyPress>", self.print_keys)
        self.keyPresses = []
        #self.root.config(bg="red")

    def choose(self, guiselect: str):

        match guiselect:
            case "1":
                self.welcome_screen()
            case _:
                pass

        self.root.mainloop()

    def destroy_wigets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def welcome_screen(self):

        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        subMenu = tk.Menu()

        menu.add_cascade(label="file", menu=subMenu)

        subMenu.add_cascade(label="Import Database")
        subMenu.add_cascade(label="Export Database")
        subMenu.add_cascade(label="New Database")
        subMenu.add_cascade(label="Export .xlsx")

        welcome_screen = tk.Label(self.root, text="Scan Ipad to see Information...", font=("Arial", 30))
        welcome_screen.place(relx=.5, rely=.4, anchor=tk.CENTER)
        manual_search = tk.Button(self.root, text="Manual Search (in Progress...)", font=("Arial", 15))
        manual_search.pack(anchor="w", side="bottom")

    def print_keys(self, event):
        self.keyPresses.append((event.char, time.time()))
        lasti = self.keyPresses[0][1]
        for i in self.keyPresses:
            print("delta: " + str(i[1]-lasti))
            lasti = i[1]


frontend = Frontend()
frontend.choose(input("which gui to show?"))
print([ m for m in dir(frontend) if not m.startswith('__')])
