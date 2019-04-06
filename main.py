#!/usr/bin/env python

import tkinter as tk
from tkinter.ttk import Notebook
from pReponse.app import Application

def main():
    root = tk.Tk()  # instantiate root window
    root.title('Py Response')
    app = Application(root)  # instantiate app and pass root window as argument
    root.mainloop()


if __name__ == "__main__":
    main()
