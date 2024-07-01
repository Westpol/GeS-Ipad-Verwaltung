import json
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import time
import copy

# TODO
'''
Backend is ONLY used as the json Interface
in the beninging, the data is stored in a dict variable, and saved when saved button is pressed 

- Decision if adding new Ipads makes sense (it doesn't)
    -> Backend().addNew needs to be updated to output database conform output
- add functionality to newITNum (ipad not found prompt)
- refine manualSearch (autocomplete via Tab)
- uncomment backend __init__ line
- manual searching leads to the same it num shown in every following scan (check fix in School)
'''


class Backend:

    def __init__(self):
        self.dictPath = "Data/database.json"
        with open(self.dictPath, "r") as jsonfile:      # loading json file and storing it globally, to save in the end
            self.device_dict = json.load(jsonfile)
        #self.device_dict["opendate"] = int(time.time())

    def addNew(self, itnum: str, version: str, surname: str, name: str, classNum, subClass: str):      # creating a dict with new info and adding it to the existing dict
        data = {itnum: {"moddate": int(time.time()), "version": version, "surname": surname, "name": name, "class": classNum, "subclass": subClass, 'repair': False, 'repairdate': 0, 'dosys': False, 'comments': ''}}
        self.device_dict["Ipads"].update(data)

    def save(self):
        with open(self.dictPath, "w") as file:
            json.dump(self.device_dict, file, indent=4)

    def inList(self, itnum: str):       # returns true or false if the given IT number is in dict or not
        if itnum in self.device_dict["Ipads"]:
            return True
        return False

    def getIpad(self, itnum: str):      # returns dict with the Information stored about the Ipad
        if self.inList(itnum):
            return copy.deepcopy(self.device_dict["Ipads"][itnum])
        raise "given IT-number not in system, bofore requesting directly, please check with inlist()"

    def delete_ipad(self, itnum: str):
        del self.device_dict["Ipads"][itnum]


class Frontend:

    def __init__(self):
        self.backend = Backend()

        self.keyData = []
        self.accept_scan = False
        self.itnum = ""

        self.root = tk.Tk()
        self.root.geometry("{}x{}".format(960, 540))
        self.root.minsize(960, 540)
        self.root.maxsize(960, 540)
        self.root.bind("<KeyPress>", self.keylogger)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)

        self.clear(self.root, True)
        self.welcomeScreen()

        self.itList = []
        for i in self.backend.device_dict["Ipads"]:
            self.itList.append((i, self.backend.device_dict["Ipads"][i]["userInfo"]["surname"], self.backend.device_dict["Ipads"][i]["userInfo"]["name"], self.backend.device_dict["Ipads"][i]["deviceInfo"]["SNr"]))

    def exit(self):

        def yesPressed():
            self.keyData = []
            self.accept_scan = False
            self.itnum = ""
            self.welcomeScreen()
            childWindow.destroy()
            self.root.destroy()

        def noPressed():
            childWindow.destroy()

        childWindow = tk.Toplevel(self.root)
        shureLabel = tk.Label(childWindow, text="Sacher, dass du das Programm beenden willst? Jeglicher ungespeicherte Daten gehen verloren!")
        yesButton = tk.Button(childWindow, text="Ja", command=lambda: yesPressed())
        noButton = tk.Button(childWindow, text="Nein", command=lambda: noPressed())
        shureLabel.pack()
        yesButton.pack()
        noButton.pack()

    def begin(self):
        self.root.mainloop()
        self.backend.save()

    def clear(self, window, recomputeDropdown: bool):
        for widget in window.winfo_children():
            widget.destroy()
        if recomputeDropdown:
            self.dropdownMenu()

    def dropdownMenu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        sub_menu = tk.Menu()

        menu.add_cascade(label="file", menu=sub_menu)

        sub_menu.add_cascade(label="Import Database")
        sub_menu.add_cascade(label="Export Database")
        sub_menu.add_cascade(label="New Database")
        sub_menu.add_cascade(label="Export .xlsx")

    def welcomeScreen(self):
        self.accept_scan = True

        self.clear(self.root, True)

        welcome_screen = tk.Label(self.root, text="Scan Ipad to see Information...", font=("Arial", 30))
        welcome_screen.place(relx=.5, rely=.4, anchor=tk.CENTER)
        manual_search = tk.Button(self.root, text="Manual Search", font=("Arial", 15), command=lambda: self.manualSearch())
        manual_search.pack(anchor="w", side="bottom")

    def manualSearch(self):
        self.accept_scan = False
        self.clear(self.root, True)

        def searchPressed(*args):
            itnum_local = inputText.get()

            if len(str(listVar.get()).split("\n")) == 2:
                self.clear(self.root, True)
                print(str(listVar.get()).split(",")[0])
                self.showData(self.backend.getIpad(str(listVar.get()).split(",")[0]), str(listVar.get()).split(",")[0])

            if not self.backend.inList(itnum_local):
                warningVariable.set("IT-Number not in Database!")
            else:
                self.clear(self.root, True)
                print(itnum_local)
                self.showData(self.backend.getIpad(itnum_local), itnum_local)

        def narrowList(event):
            writtenSoFar = inputText.get()
            searchResult = ""
            for i in self.itList:
                if str(writtenSoFar).lower() in i[0].lower() or str(writtenSoFar) == "" or str(writtenSoFar).lower() in i[1].lower() or str(writtenSoFar).lower() in i[2].lower() or str(writtenSoFar).lower() in i[3].lower():
                    searchResult += "{0}, {1} {2}, {3}\n".format(i[0], i[1], i[2], i[3])
            listVar.set(searchResult)

        self.root.bind('<Return>', lambda *args: searchPressed(*args))
        self.root.bind('<KeyPress>', lambda *args: narrowList(*args))

        inputText = tk.StringVar()
        warningVariable = tk.StringVar()
        listVar = tk.StringVar()

        searchFrame = tk.Frame(self.root)

        entryBox = tk.Entry(searchFrame, textvariable=inputText)
        searchButton = tk.Button(searchFrame, text="Search", command=lambda: searchPressed())
        errorMessage = tk.Label(searchFrame, textvariable=warningVariable)
        inListText = tk.Label(searchFrame, textvariable=listVar)

        entryBox.grid(column=0, row=0)
        searchButton.grid(column=1, row=0)
        errorMessage.grid(column=0, row=1)
        inListText.grid(column=0, row=2)
        searchFrame.pack()

        narrowList(None)

    def showData(self, infos: dict, itnum: str):
        print(infos)
        self.accept_scan = False

        self.clear(self.root, True)

        def setStatus():
            if infos["status"] == 1:
                statusVar.set("Status:  In Reperatur")
            elif infos["status"] == 2:
                statusVar.set("Status:  Bei Dosys eingesendet")
            else:
                statusVar.set("Status:  Standard")

        def editUserWindow():
            childWindow = tk.Toplevel(self.root)

        def repairWindow():

            def beginRepairPrompt1():

                repairReason = tk.StringVar()
                repairReason.set("Auswählen")  # default value

                exitButton = tk.Button(childWindow, text="Exit", command=childWindow.destroy)
                saveButton = tk.Button(childWindow, text="Save", command=lambda: saveRepair(repairReason, ""))

                w = tk.OptionMenu(childWindow, repairReason, "Wlan-problem", "Passwort vergessen", "Pencil kaputt", "Display kaputt", "Sonstiges (bitte eintragen)")

                pleaseChoose = tk.Label(childWindow, text="Please Choose a problem")

                pleaseChoose.pack()
                w.pack()
                exitButton.pack(anchor="e", side="bottom")
                saveButton.pack(anchor="w", side="bottom")

            def saveRepair(repReas, comments: str):
                reason: int = 0
                if str(repReas.get()) == "Auswählen":
                    reason = 0
                if str(repReas.get()) == "Wlan-problem":
                    reason = 1
                if str(repReas.get()) == "Passwort vergessen":
                    reason = 2
                if str(repReas.get()) == "Pencil kaputt":
                    reason = 3
                if str(repReas.get()) == "Display kaputt":
                    reason = 4
                if str(repReas.get()) == "Sonstiges (bitte eintragen)":
                    reason = 5

                repairCounter = 1

                for i in infos["repairHistory"]:
                    repairCounter += 1

                repairDict = {"repair" + str(repairCounter): {"active": True, "status": 1, "reason": reason, "repairBegin": int(time.time()), "repairEnd": 0, "comments": comments}}
                infos["repairHistory"].update(repairDict)
                infos["status"] = 1
                print(infos)

                childWindow.destroy()
                self.showData(infos, itnum)

            def setStatusLocal():
                if infos["status"] == 1:
                    statusVariable.set("In Reperatur")
                    button_text.set("Dosys einsenden")
                elif infos["status"] == 2:
                    statusVariable.set("Bei Dosys eingesendet")
                    button_text.set("Reperatur beenden")
                else:
                    statusVariable.set("Derzeit keine Reperatur")
                    button_text.set("Reperatur beginnen")

            def changeStatusLocal():
                if infos["status"] == 1:
                    infos["status"] = 2
                elif infos["status"] == 2:
                    infos["status"] = 0
                else:
                    infos["status"] = 1
                setStatusLocal()

            if infos["status"] == 0:
                childWindow = tk.Toplevel(self.root)
                childWindow.geometry("{}x{}".format(960, 540))
                childWindow.minsize(320, 250)
                childWindow.maxsize(320, 250)
                beginRepairPrompt1()
            else:
                childWindow = tk.Toplevel(self.root)

                statusVariable = tk.StringVar()
                button_text = tk.StringVar()
                repairStatus = tk.Label(childWindow, textvariable=statusVariable, font=("Arial", 25))
                setStatusLocal()

                repairStatus.pack()

                changeStatusButton = tk.Button(childWindow, textvariable=button_text, command=changeStatusLocal)
                exitButton = tk.Button(childWindow, text="Exit", command=childWindow.destroy)
                saveButton = tk.Button(childWindow, text="Save")

                exitButton.pack()
                saveButton.pack()
                changeStatusButton.pack()

                repairReason = tk.StringVar()
                repairReason.set("Auswählen")  # default value

                w = tk.OptionMenu(childWindow, repairReason, "Wlan-problem", "Passwort vergessen", "Pencil kaputt", "Display kaputt", "Sonstiges (bitte eintragen)")
                w.pack()

        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure((1, 2, 3), weight=1)

        notes = tk.Label(self.root, text="Anmerkungen:", font=("Arial", 15))
        textfield = ScrolledText(self.root)
        textfield.insert("1.0", str(infos["comments"]))

        user = tk.Label(self.root, text="Besitzer:", font=("Arial", 15))
        name = tk.Label(self.root, text=str("Name:  " + infos["userInfo"]["surname"] + " " + infos["userInfo"]["name"]))

        if infos["userInfo"]["subclass"] is not None:
            classs = tk.Label(self.root, text=str("Klasse:  " + str(infos["userInfo"]["class"]) + "." + str(infos["userInfo"]["subclass"])))
        else:
            classs = tk.Label(self.root, text=str("Klasse:  " + str(infos["userInfo"]["class"])))

        besitzer_bearbeiten = tk.Button(self.root, text="Bearbeiten", command=editUserWindow)

        device = tk.Label(self.root, text="Gerät:", font=("Arial", 15))

        statusVar = tk.StringVar(self.root, "")
        setStatus()

        status = tk.Label(self.root, textvariable=statusVar)

        serialNum = tk.Label(self.root, text=str("Seriennummer: " + infos["deviceInfo"]["SNr"]))

        if infos["status"] == 0:
            history = tk.Button(self.root, text="Reperatur beginnen", command=lambda: repairWindow())
        else:
            history = tk.Button(self.root, text="Reperatur bearbeiten", command=lambda: repairWindow())

        save_button = tk.Button(self.root, text="Save", command=lambda: self.saveData(infos, textfield.get("1.0", "end"), itnum))
        save_exit_button = tk.Button(self.root, text="Save + Exit", command=lambda: self.saveAndExit(infos, textfield.get("1.0", "end"), itnum))
        exit_button = tk.Button(self.root, text="Exit", command=lambda: self.exitShowData(True))

        textfield.grid(row=1, column=0, rowspan=7, padx="20")
        notes.grid(row=0, column=0, sticky="w")
        user.grid(row=0, column=1, columnspan=3, sticky="w")
        name.grid(row=1, column=1, columnspan=3, sticky="w")
        classs.grid(row=2, column=1, columnspan=3, sticky="w")
        besitzer_bearbeiten.grid(row=3, column=3, sticky="w")
        device.grid(row=4, column=1, columnspan=3, sticky="w")
        serialNum.grid(row=5, column=1, columnspan=3, sticky="w")
        status.grid(row=6, column=1, columnspan=3, sticky="w")
        history.grid(row=7, column=1, columnspan=3, sticky="w")
        save_button.grid(row=8, column=1)
        save_exit_button.grid(row=8, column=2)
        exit_button.grid(row=8, column=3)
    
    def newITNum(self, itnum: str):
        self.accept_scan = True

        self.clear(self.root, True)

        addITNum = tk.Label(self.root, text="Do you want to add {0}".format(itnum), font=("Arial", 30))
        yesButton = tk.Button(self.root, text="Yes", command=lambda: self.addIpad(itnum))
        noButton = tk.Button(self.root, text="No", command=lambda: self.welcomeScreen())
        addITNum.pack()
        yesButton.pack()
        noButton.pack()
        
    def addIpad(self, itnum: str):
        self.clear(self.root, True)
        print("Ipad added: {0}".format(itnum))

    def exitShowData(self, displayWarning: bool):

        def yesPressed():
            self.keyData = []
            self.accept_scan = False
            self.itnum = ""
            self.welcomeScreen()
            childWindow.destroy()#

        def noPressed():
            childWindow.destroy()

        if displayWarning:
            childWindow = tk.Toplevel(self.root)
            shureLabel = tk.Label(childWindow, text="Sicher, dass beendet wird ohne dass gespeichert wird?")
            yesButton = tk.Button(childWindow, text="Ja", command=lambda: yesPressed())
            noButton = tk.Button(childWindow, text="Nein", command=lambda: noPressed())
            shureLabel.pack()
            yesButton.pack()
            noButton.pack()
        else:
            self.keyData = []
            self.accept_scan = False
            self.itnum = ""
            self.welcomeScreen()

    def saveAndExit(self, infos: dict, textbox: str, itnum: str):
        self.saveData(infos, textbox, itnum)
        self.exitShowData(False)

    def saveData(self, infos: dict, textbox: str, itnum: str):
        infos["comments"] = textbox[0:len(textbox)-1:1]
        self.backend.device_dict["Ipads"][itnum] = infos
        self.backend.save()

    def getScan(self):     # returns itnum
        self.itnum = ""
        time_delta = self.keyData[len(self.keyData) - 1][1]
        temp_string = ""

        for i in reversed(range(0, len(self.keyData) - 1)):
            if 0.005 < time_delta - self.keyData[i][1] < 0.025:
                temp_string += self.keyData[i][0]
            else:
                if time_delta - self.keyData[i][1] > 0.01:
                    break
                else:
                    if self.keyData[i][0] != "":
                        temp_string += self.keyData[i][0]
            time_delta = self.keyData[i][1]

        self.itnum = temp_string[::-1]
        self.keyData = []

        if self.itnum != "":
            return self.itnum
        else:
            return None

    def keylogger(self, event):
        if self.accept_scan:
            if event.keysym == "Return":
                self.keyData.append(("\n", time.time()))
                itnum = self.getScan()
                if itnum is not None:
                    if self.backend.inList(itnum) is True:
                        print(itnum)
                        self.showData(self.backend.getIpad(itnum), itnum)
                    else:
                        self.newITNum(itnum)
            else:
                self.keyData.append((event.char, time.time()))


if __name__ == "__main__":
    frontend = Frontend()
    frontend.begin()
