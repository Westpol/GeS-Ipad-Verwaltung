import time
from tkinter import *

timme = time.time()


def ping():
    print("PING AFTER" + str(int(time.time()-timme)) + "s")
    top.after(1000, ping)


top = Tk()
Lb = Listbox(top)
Lb.insert(1, 'Python')
Lb.insert(2, 'Java')
Lb.insert(3, 'C++')
Lb.insert(4, 'Any other')
Lb.pack()
Lb.bind("<1>", ping())
top.after(1000, ping)
top.mainloop()
