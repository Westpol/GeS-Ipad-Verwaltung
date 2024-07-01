from ttkwidgets.autocomplete import AutocompleteEntry
from tkinter import *

countries = [
        'Antigua and Barbuda', 'Bahamas','Barbados','Belize', 'Canada',
        'Costa Rica ', 'Cuba', 'Dominica', 'Dominican Republic', 'El Salvador ',
        'Grenada', 'Guatemala ', 'Haiti', 'Honduras ', 'Jamaica', 'Mexico',
        'Nicaragua', 'Saint Kitts and Nevis', 'Panama ', 'Saint Lucia',
        'Saint Vincent and the Grenadines', 'Trinidad and Tobago', 'United States of America'
        ]

ws = Tk()
ws.title('PythonGuides')
ws.geometry('400x300')
ws.config(bg='#f25252')

frame = Frame(ws, bg='#f25252')
frame.pack(expand=True)

Label(
    frame,
    bg='#f25252',
    font = ('Times',21),
    text='Countries in North America '
    ).pack()

entry = AutocompleteEntry(
    frame,
    width=30,
    font=('Times', 18),
    completevalues=countries
    )
entry.pack()

ws.mainloop()