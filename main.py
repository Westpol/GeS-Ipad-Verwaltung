import os
import json
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
import time
import copy
import requests

version = "v1.2.2"
latestVersion = ""


# TODO
'''
Backend is ONLY used as the json Interface
in the beninging, the data is stored in a dict variable, and saved when saved button is pressed 

- refine manualSearch (autocomplete via Tab)
- manual searching leads to the same it num shown in every following scan (check fix in School)
'''


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Backend:

    def __init__(self):

        default_dict = {
            "activeFilepath": "",
            "recentFiles": []
        }

        dir_list = os.path.dirname(os.path.realpath(__file__)).split("/")[1:]
        dir_config = "/" + dir_list[0] + "/" + dir_list[1] + "/" + ".config" + "/ipadverwaltung"
        self.file_config = dir_config + "/config.json"
        if not os.path.exists(dir_config):
            os.mkdir(dir_config)
        if not os.path.exists(self.file_config):
            with open(self.file_config, "w") as configfile:
                configfile.write(json.dumps(default_dict, indent=4))
        if os.path.exists(self.file_config):
            with open(self.file_config, "r") as configfile:
                self.config_dict = json.load(configfile)
        else:
            Exception(AttributeError)

        self.dictPath = self.config_dict["activeFilepath"]
        if self.dictPath != "":
            with open(self.dictPath, "r") as jsonfile:      # loading json file and storing it globally, to save in the end
                self.device_dict = json.load(jsonfile)
            self.device_dict["opendate"] = int(time.time())

    def setDictPath(self, fp: str):
        if "/" in fp:
            with open(self.file_config, "w") as configfile:
                self.config_dict["activeFilepath"] = fp
                configfile.write(json.dumps(self.config_dict, indent=4))

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


class Frontend:
    def __init__(self):
        self.hasDatabase = False
        self.backend = Backend()

        self.root = tk.Tk()
        self.root.geometry("{}x{}".format(960, 540))
        self.root.minsize(960, 540)
        self.root.maxsize(960, 540)
        self.root.bind("<KeyPress>", self.keylogger)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)

        self.clear(self.root, True)

        if os.path.exists(self.backend.dictPath):
            self.hasDatabase = True
            self.keyData = []
            self.accept_scan = False
            self.itnum = ""
            self.itnumDict = {}

            self.welcomeScreen()

            self.itList = []
            for i in self.backend.device_dict["Ipads"]:
                self.itList.append((i, self.backend.device_dict["Ipads"][i]["userInfo"]["surname"],
                                    self.backend.device_dict["Ipads"][i]["userInfo"]["name"],
                                    self.backend.device_dict["Ipads"][i]["deviceInfo"]["SNr"]))
            self.repairList = []
        else:
            self.chooseFile()

    def exit(self):

        def yesPressed():
            self.keyData = []
            self.accept_scan = False
            self.itnum = ""
            self.welcomeScreen()
            childWindow.destroy()
            self.root.destroy()
            exit()

        def notChanged():
            self.keyData = []
            self.accept_scan = False
            self.itnum = ""
            self.welcomeScreen()
            self.root.destroy()
            exit()

        def noPressed():
            childWindow.destroy()

        if all(item in self.backend.device_dict["Ipads"].items() for item in {self.itnum: self.itnumDict}.items()) or self.itnumDict == {}:
            notChanged()

        childWindow = tk.Toplevel(self.root)
        shureLabel = tk.Label(childWindow, text="Sacher, dass du das Programm beenden willst? Jeglicher ungespeicherte Daten gehen verloren!")
        yesButton = tk.Button(childWindow, text="Ja", command=lambda: yesPressed())
        noButton = tk.Button(childWindow, text="Nein", command=lambda: noPressed())
        shureLabel.pack()
        yesButton.pack()
        noButton.pack()

    def begin(self):
        self.root.mainloop()

    def chooseFile(self):
        curr_dir = os.path.dirname(os.path.realpath(__file__)).split("/")[1:]
        filename = tk.filedialog.askopenfilename(initialdir="/{0}/{1}/".format(curr_dir[0], curr_dir[1]), title="Select a File", filetypes=(("JSON files", "*.json*"), ("all files", "*.*")))
        self.changeFile(filename)
        self.root.destroy()

    def changeFile(self, fn: str):
        self.backend.setDictPath(fn)

    def dropdownMenu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        sub_menu = tk.Menu()

        menu.add_cascade(label="File", menu=sub_menu)

        recent_files = tk.Menu(sub_menu)
        files = self.backend.config_dict["recentFiles"]
        for i in range(len(self.backend.config_dict["recentFiles"])):
            recent_files.add_command(label=files[i].split("/")[-1], command=lambda: print(files[i]))

        sub_menu.add_command(label="Open Database", command=self.chooseFile)
        sub_menu.add_cascade(label="Recent Files", menu=recent_files)
        sub_menu.add_cascade(label="Export .xlsx")
        sub_menu.add_separator()
        sub_menu.add_command(label="Exit", command=self.exit)

    def clear(self, window, recomputeDropdown: bool):
        for widget in window.winfo_children():
            widget.destroy()
        if recomputeDropdown:
            self.dropdownMenu()

    def welcomeScreen(self):
        self.accept_scan = True

        self.clear(self.root, True)

        welcome_screen = tk.Label(self.root, text="Scan Ipad to see Information...", font=("Arial", 30))
        welcome_screen.place(relx=.5, rely=.4, anchor=tk.CENTER)
        database_directory = tk.Label(self.root, text=self.backend.dictPath)
        database_directory.pack(anchor="e", side="bottom")
        manual_search = tk.Button(self.root, text="Manual Search", font=("Arial", 15), command=lambda: self.manualSearch())
        manual_search.pack(anchor="w", side="bottom")
        list_repairs = tk.Button(self.root, text="List Repairs", font=("Arial", 15), command=lambda: self.listActiveRepairs())
        list_repairs.pack(anchor="w", side="bottom")

    def manualSearch(self):
        self.accept_scan = False
        self.clear(self.root, True)

        def searchPressed(*args):
            itnum_local = inputText.get()

            if len(str(listVar.get()).split("\n")) == 2:
                self.clear(self.root, True)
                print(str(listVar.get()).split(",")[0])
                self.itnumDict = self.backend.getIpad(str(listVar.get()).split(",")[0])
                self.itnum = str(listVar.get()).split(",")[0]
                self.showData()

            if not self.backend.inList(itnum_local):
                warningVariable.set("IT-Number not in Database!")
            else:
                self.clear(self.root, True)
                print(itnum_local)
                self.itnumDict = self.backend.getIpad(itnum_local)
                self.itnum = itnum_local
                self.showData()

        def narrowList(event):
            writtenSoFar = inputText.get().split()
            if len(writtenSoFar) == 0:
                writtenSoFar = [""]
            searchResult = ""
            temporaryITList = []

            for i in self.itList:
                if str(writtenSoFar[0]).lower() in i[0].lower() or str(writtenSoFar[0]) == "" or str(writtenSoFar[0]).lower() in i[1].lower() or str(writtenSoFar[0]).lower() in i[2].lower() or str(writtenSoFar[0]).lower() in i[3].lower():
                    temporaryITList.append(i)

            for f in range(1, len(writtenSoFar)):
                newTemporaryITList = []
                for i in temporaryITList:
                    if str(writtenSoFar[f]).lower() in i[0].lower() or str(writtenSoFar[f]) == "" or str(writtenSoFar[f]).lower() in i[1].lower() or str(writtenSoFar[f]).lower() in i[2].lower() or str(writtenSoFar[f]).lower() in i[3].lower():
                        newTemporaryITList.append(i)
                temporaryITList = newTemporaryITList

            for i in temporaryITList:
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

    def listActiveRepairs(self):
        self.accept_scan = False
        self.clear(self.root, True)

        self.repairList = []
        temporaryRepairList = {"Ipads": {}}
        for i in list(self.backend.device_dict["Ipads"].keys()):
            if self.backend.device_dict["Ipads"][i]["status"] != 0:
                temporaryRepairList["Ipads"].update({str(i): {}})
                temporaryRepairList["Ipads"][str(i)].update(self.backend.device_dict["Ipads"][i])

        for i in temporaryRepairList["Ipads"]:
            self.repairList.append((i, self.backend.device_dict["Ipads"][i]["userInfo"]["surname"],
                                    self.backend.device_dict["Ipads"][i]["userInfo"]["name"],
                                    self.backend.device_dict["Ipads"][i]["deviceInfo"]["SNr"]))
        print(self.repairList)

        def searchPressed(*args):
            itnum_local = inputText.get()

            if len(str(listVar.get()).split("\n")) == 2:
                self.clear(self.root, True)
                print(str(listVar.get()).split(",")[0])
                self.itnumDict = self.backend.getIpad(str(listVar.get()).split(",")[0])
                self.itnum = str(listVar.get()).split(",")[0]
                self.showData()

            if not self.backend.inList(itnum_local):
                warningVariable.set("IT-Number not in Repair!")
            else:
                self.clear(self.root, True)
                print(itnum_local)
                self.itnumDict = self.backend.getIpad(itnum_local)
                self.itnum = itnum_local
                self.showData()

        def narrowList(event):
            writtenSoFar = inputText.get().split()
            if len(writtenSoFar) == 0:
                writtenSoFar = [""]
            searchResult = ""
            temporaryITList = []

            for i in self.repairList:
                if str(writtenSoFar[0]).lower() in i[0].lower() or str(writtenSoFar[0]) == "" or str(writtenSoFar[0]).lower() in i[1].lower() or str(writtenSoFar[0]).lower() in i[2].lower() or str(writtenSoFar[0]).lower() in i[3].lower():
                    temporaryITList.append(i)

            for f in range(1, len(writtenSoFar)):
                newTemporaryITList = []
                for i in temporaryITList:
                    if str(writtenSoFar[f]).lower() in i[0].lower() or str(writtenSoFar[f]) == "" or str(writtenSoFar[f]).lower() in i[1].lower() or str(writtenSoFar[f]).lower() in i[2].lower() or str(writtenSoFar[f]).lower() in i[3].lower():
                        newTemporaryITList.append(i)
                temporaryITList = newTemporaryITList

            for i in temporaryITList:
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

    def showData(self):
        print(self.itnumDict)
        self.accept_scan = False

        self.clear(self.root, True)

        def setStatus():
            if self.itnumDict["status"] == 1:
                statusVar.set("Status:  In Reperatur")
            elif self.itnumDict["status"] == 2:
                statusVar.set("Status:  Bei Dosys eingesendet")
            else:
                statusVar.set("Status:  Standard")

        def repairWindow():
            repairReasonList = ["Wlan-problem", "Passwort vergessen", "Pencil kaputt", "Display kaputt", "Sonstiges (bitte eintragen)"]

            def beginRepairPrompt1():

                repairReason = tk.StringVar()
                repairReason.set("Auswählen")  # default value

                exitButton = tk.Button(childWindow, text="Exit", command=childWindow.destroy)
                saveButton = tk.Button(childWindow, text="Save", command=lambda: saveRepair(repairReason, ""))
                nextButton = tk.Button(childWindow, text="Next", command=lambda: beginRepairPrompt2(repairReason))

                repairReasonDropdown = tk.OptionMenu(childWindow, repairReason, *repairReasonList)

                pleaseChoose = tk.Label(childWindow, text="Please Choose a problem")

                childWindow.rowconfigure(1, weight=1)
                childWindow.columnconfigure(1, weight=1)

                pleaseChoose.grid(row=0, column=1)
                repairReasonDropdown.grid(row=1, column=1)
                exitButton.grid(row=2, column=0)
                saveButton.grid(row=2, column=1)
                nextButton.grid(row=2, column=2)

            def beginRepairPrompt2(repReason):
                self.clear(childWindow, False)
                comments = ScrolledText(childWindow, width=30, height=10)
                exitButton2 = tk.Button(childWindow, text="Exit", command=childWindow.destroy)
                saveButton2 = tk.Button(childWindow, text="Save", command=lambda: saveRepair(repReason, comments.get("1.0", "end")))
                childWindow.rowconfigure(0, weight=1)
                comments.grid(row=0, column=1)
                exitButton2.grid(row=1, column=0)
                saveButton2.grid(row=1, column=2)

            def saveRepair(repReas, comments: str):
                reason: int = repairReasonList.index(repReas.get())
                repairCounter = 1

                for i in self.itnumDict["repairHistory"]:
                    repairCounter += 1

                repairDict = {"repair" + str(repairCounter): {"active": True, "status": 1, "reason": reason, "repairBegin": int(time.time()), "repairEnd": 0, "comments": comments}}
                self.itnumDict["repairHistory"].update(repairDict)
                self.itnumDict["status"] = 1

                childWindow.destroy()
                # saveData(self.itnumDict["comments"])
                self.showData()

            def setStatusLocal():
                if activeRepairDict["status"] == 1:
                    statusVariable.set("In Reperatur")
                    button_text.set("Dosys einsenden")
                elif activeRepairDict["status"] == 2:
                    statusVariable.set("Bei Dosys\neingesendet")
                    button_text.set("Reperatur beenden")
                else:
                    statusVariable.set("Derzeit keine\nReperatur")
                    button_text.set("Reperatur beginnen")

            def changeStatusLocal():
                if activeRepairDict["status"] == 1:
                    activeRepairDict["status"] = 2
                elif activeRepairDict["status"] == 2:
                    activeRepairDict["status"] = 0
                else:
                    activeRepairDict["status"] = 1
                setStatusLocal()

            def saveChangedRepair(repairDict: dict, repairNum: str):
                self.itnumDict["repairHistory"][repairNum] = repairDict
                if repairDict["status"] == 0 or repairDict["status"] == 2:
                    self.itnumDict["repairHistory"][repairNum]["active"] = False
                    self.itnumDict["repairHistory"][repairNum]["repairEnd"] = int(time.time())
                    self.itnumDict["status"] = 0
                self.showData()
                childWindow.destroy()

            if self.itnumDict["status"] == 0:
                childWindow = tk.Toplevel(self.root)
                childWindow.geometry("{}x{}".format(960, 540))
                childWindow.minsize(320, 250)
                childWindow.maxsize(320, 250)
                beginRepairPrompt1()
            else:

                hasActiveRepair = False
                for i in self.itnumDict["repairHistory"]:
                    if self.itnumDict["repairHistory"][i]["active"]:
                        print(i)
                        activeRepairNum = i
                        activeRepairDict = copy.deepcopy(self.itnumDict["repairHistory"][activeRepairNum])       # IMPORTANT, in the following function, only use activeRepairDict for information about the repair
                        hasActiveRepair = True

                if hasActiveRepair:
                    childWindow = tk.Toplevel(self.root)
                    childWindow.geometry("{}x{}".format(960, 540))
                    childWindow.minsize(480, 375)
                    childWindow.maxsize(480, 375)

                    statusVariable = tk.StringVar()
                    button_text = tk.StringVar()
                    repairStatus = tk.Label(childWindow, textvariable=statusVariable, font=("Arial", 25))
                    setStatusLocal()

                    changeStatusButton = tk.Button(childWindow, textvariable=button_text, command=changeStatusLocal)
                    exitButton = tk.Button(childWindow, text="Exit", command=childWindow.destroy)
                    saveButton = tk.Button(childWindow, text="Save", command=lambda: saveChangedRepair(activeRepairDict, activeRepairNum))

                    repairReason = tk.StringVar()
                    repairReason.set(repairReasonList[int(activeRepairDict["reason"]) - 1])  # default value

                    w = tk.OptionMenu(childWindow, repairReason, *repairReasonList)

                    comments = ScrolledText(childWindow, width=30, height=18)
                    comments.insert("1.0", activeRepairDict["comments"])

                    comments.grid(row=0, column=0, rowspan=3)

                    repairStatus.grid(row=0, column=1)

                    exitButton.grid(row=3, column=1)
                    saveButton.grid(row=3, column=0)
                    changeStatusButton.grid(row=1, column=1)
                    w.grid(row=2, column=1)

        def exitShowData(displayWarning: bool):

            def yesPressed():
                self.keyData = []
                self.accept_scan = False
                self.itnum = ""
                self.welcomeScreen()
                childWindow.destroy()  #

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

        def saveAndExit(textbox: str):
            saveData(textbox)
            exitShowData(False)

        def saveData(textbox: str):
            self.itnumDict["comments"] = textbox[0:len(textbox) - 1:1]
            self.backend.device_dict["Ipads"][self.itnum] = self.itnumDict
            self.backend.save()

        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure((1, 2, 3), weight=1)

        notes = tk.Label(self.root, text="Anmerkungen:", font=("Arial", 15))
        textfield = ScrolledText(self.root)
        textfield.insert("1.0", str(self.itnumDict["comments"]))

        user = tk.Label(self.root, text="Besitzer:", font=("Arial", 15))
        name = tk.Label(self.root, text=str("Name:  " + self.itnumDict["userInfo"]["surname"] + " " + self.itnumDict["userInfo"]["name"]))

        if self.itnumDict["userInfo"]["subclass"] is not None:
            classs = tk.Label(self.root, text=str("Klasse:  " + str(self.itnumDict["userInfo"]["class"]) + "." + str(self.itnumDict["userInfo"]["subclass"])))
        else:
            classs = tk.Label(self.root, text=str("Klasse:  " + str(self.itnumDict["userInfo"]["class"])))

        # besitzer_bearbeiten = tk.Button(self.root, text="Bearbeiten", command=editUserWindow)

        device = tk.Label(self.root, text="Gerät:", font=("Arial", 15))

        statusVar = tk.StringVar(self.root, "")
        setStatus()

        status = tk.Label(self.root, textvariable=statusVar)

        serialNum = tk.Label(self.root, text=str("Seriennummer: " + self.itnumDict["deviceInfo"]["SNr"]))

        if self.itnumDict["status"] == 0:
            history = tk.Button(self.root, text="Reperatur beginnen", command=lambda: repairWindow())
        else:
            history = tk.Button(self.root, text="Reperatur bearbeiten", command=lambda: repairWindow())

        save_button = tk.Button(self.root, text="Save", command=lambda: saveData(textfield.get("1.0", "end")))
        save_exit_button = tk.Button(self.root, text="Save + Exit", command=lambda: saveAndExit(textfield.get("1.0", "end")))
        exit_button = tk.Button(self.root, text="Exit", command=lambda: exitShowData(True))

        textfield.grid(row=1, column=0, rowspan=7, padx="20")
        notes.grid(row=0, column=0, sticky="w")
        user.grid(row=0, column=1, columnspan=3, sticky="w")
        name.grid(row=1, column=1, columnspan=3, sticky="w")
        classs.grid(row=2, column=1, columnspan=3, sticky="w")
        # besitzer_bearbeiten.grid(row=3, column=3, sticky="w")
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

        addITNum = tk.Label(self.root, text='"{0}" not in Database. You will be redirected in 3 Seconds'.format(itnum), font=("Arial", 30))
        addITNum.pack()
        time.sleep(3)
        self.welcomeScreen()

    def getScan(self):     # returns itnum (don't touch) (if touched, horrible things will happen)
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
            return
        else:
            self.itnum = None
            return

    def keylogger(self, event):     # saves every keystroke with timestamp in keyData and waits until enter is pressed. If so calls self.getScan
        if self.accept_scan:
            if event.keysym == "Return":
                self.keyData.append(("\n", time.time()))
                self.getScan()
                if self.itnum is not None:
                    if self.backend.inList(self.itnum) is True:
                        self.itnumDict = self.backend.getIpad(self.itnum)
                        self.showData()
                    else:
                        self.newITNum(self.itnum)
            else:
                self.keyData.append((event.char, time.time()))


if __name__ == "__main__":
    while 1:
        print("Installed Version: {0}".format(version))
        url = "https://api.github.com/repos/Westpol/GeS-Ipad-Verwaltung/releases/latest"
        try:
            response = requests.get(url)
            latestVersion = response.json()["name"]
            print("Latest Version: {0}".format(latestVersion))
            if latestVersion == version:
                print(colors.OKGREEN + "latest Version installed!" + colors.ENDC)
            else:
                print(colors.WARNING + "Version outdated!" + colors.ENDC)
        except:
            print(colors.WARNING + "Can't check Version might be because of bad Internet connection." + colors.ENDC)
        frontend = Frontend()
        frontend.begin()
