#!/usr/bin/env python

import tkinter as tk
from tkinter import ttk
import discovery


class Application:
    def __init__(self, root_window):
        self.root = root_window
        nb = Notebook(self.root)
        # self.create_widgets()

class Notebook:
    def __init__(self, root_window):
        self.root_window = root_window
        notebook = ttk.Notebook(root_window)
        notebook.pack()

        # Make 1st tab
        f1 = tk.Frame(notebook)
        # Add the tab
        notebook.add(f1, text="Discovery")
        discovery_tab = discovery.Discovery(f1)

        # Make 2nd tab
        f2 = tk.Frame(notebook)
        # Add 2nd tab
        notebook.add(f2, text="Enumeration")

        # Make 3nd tab
        f3 = tk.Frame(notebook)
        # Add 2nd tab
        notebook.add(f3, text="Analysis")

        # select the default notebook (Discovery)
        notebook.select(f1)

        # allow the user to toggle notebooks
        notebook.enable_traversal()

