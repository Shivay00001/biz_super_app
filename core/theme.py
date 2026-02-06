import tkinter as tk
from tkinter import ttk

class Theme:
    @staticmethod
    def apply_theme(root):
        style = ttk.Style(root)
        style.theme_use('clam')  # Base theme
        
        # Colors
        PRIMARY = "#0078D7"    # Corporate Blue
        SECONDARY = "#F0F0F0"  # Light Grey
        TEXT = "#333333"
        WHITE = "#FFFFFF"
        ACCENT = "#005a9e"
        
        # Configure Defaults
        style.configure(".", 
                        background=WHITE, 
                        foreground=TEXT, 
                        font=("Segoe UI", 10))
        
        # Frames
        style.configure("TFrame", background=WHITE)
        style.configure("TLabelframe", background=WHITE, borderwidth=1)
        style.configure("TLabelframe.Label", background=WHITE, foreground=PRIMARY, font=("Segoe UI", 11, "bold"))
        
        # Labels
        style.configure("TLabel", background=WHITE, foreground=TEXT)
        style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground=PRIMARY)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 14), foreground="#666666")
        
        # Buttons
        style.configure("TButton", 
                        background=PRIMARY, 
                        foreground=WHITE, 
                        borderwidth=0, 
                        font=("Segoe UI", 10, "bold"),
                        padding=(15, 8))
        style.map("TButton", 
                  background=[('active', ACCENT), ('pressed', ACCENT)],
                  relief=[('pressed', 'flat')])
        
        # Danger Button (Red)
        style.configure("Danger.TButton", background="#e74c3c")
        style.map("Danger.TButton", background=[('active', "#c0392b")])
        
        # Treeview
        style.configure("Treeview", 
                        background=WHITE, 
                        fieldbackground=WHITE, 
                        foreground=TEXT, 
                        rowheight=30,
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        background=SECONDARY, 
                        foreground=TEXT, 
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Treeview", background=[('selected', PRIMARY)], foreground=[('selected', WHITE)])
        
        # Notebook (Tabs)
        style.configure("TNotebook", background=SECONDARY, borderwidth=0)
        style.configure("TNotebook.Tab", 
                        padding=(20, 10), 
                        font=("Segoe UI", 11),
                        background=SECONDARY,
                        foreground=TEXT)
        style.map("TNotebook.Tab", 
                  background=[('selected', WHITE)], 
                  foreground=[('selected', PRIMARY)])
