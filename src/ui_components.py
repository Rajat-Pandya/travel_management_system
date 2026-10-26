"""
UI Components module for Travel Management System.
Contains reusable UI components and helper functions.
"""

import os
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from PIL import ImageTk, Image

# Theme colors
THEMES = {
    "light": {
        "bg": "#f8f9fa",
        "fg": "#212529",
        "card_bg": "#ffffff",
        "header_bg": "#2c3e50",
        "header_fg": "#ffffff",
        "accent": "#3498db",
        "accent_hover": "#2980b9",
        "success": "#27ae60",
        "warning": "#f39c12",
        "danger": "#e74c3c",
        "border": "#dee2e6",
        "hover_bg": "#e9ecef",
        "sidebar_bg": "#ffffff",
        "sidebar_fg": "#495057",
        "sidebar_active": "#e3f2fd",
        "text_secondary": "#6c757d",
        "input_bg": "#ffffff",
        "input_border": "#ced4da"
    },
    "dark": {
        "bg": "#1a1d21",
        "fg": "#e9ecef",
        "card_bg": "#242830",
        "header_bg": "#1e2127",
        "header_fg": "#ffffff",
        "accent": "#64b5f6",
        "accent_hover": "#90caf9",
        "success": "#81c784",
        "warning": "#ffb74d",
        "danger": "#e57373",
        "border": "#343a40",
        "hover_bg": "#2d333b",
        "sidebar_bg": "#242830",
        "sidebar_fg": "#adb5bd",
        "sidebar_active": "#1e3a5f",
        "text_secondary": "#868e96",
        "input_bg": "#2d333b",
        "input_border": "#495057"
    }
}


def setup_fonts():
    """Setup modern fonts."""
    return {
        "title": Font(family="Segoe UI", size=24, weight="bold"),
        "subtitle": Font(family="Segoe UI", size=16, weight="bold"),
        "heading": Font(family="Segoe UI", size=14, weight="bold"),
        "body": Font(family="Segoe UI", size=11),
        "body_bold": Font(family="Segoe UI", size=11, weight="bold"),
        "caption": Font(family="Segoe UI", size=9),
        "button": Font(family="Segoe UI", size=11, weight="bold"),
        "nav": Font(family="Segoe UI", size=11)
    }


def setup_styles(style, theme, fonts):
    """Setup ttk styles for current theme."""
    style.configure("Modern.TFrame", background=theme["bg"])
    style.configure("Card.TFrame", background=theme["card_bg"])
    
    style.configure("Modern.TLabel", 
                   background=theme["bg"], 
                   foreground=theme["fg"],
                   font=fonts["body"])
    
    style.configure("Title.TLabel",
                   background=theme["bg"],
                   foreground=theme["fg"],
                   font=fonts["title"])
    
    style.configure("Card.TLabelframe", 
                   background=theme["card_bg"],
                   foreground=theme["fg"])
    style.configure("Card.TLabelframe.Label",
                   background=theme["card_bg"],
                   foreground=theme["fg"],
                   font=fonts["heading"])
    
    style.configure("Accent.TButton",
                   background=theme["accent"],
                   foreground="white",
                   font=fonts["button"],
                   padding=(20, 10))
    
    style.configure("Treeview",
                   background=theme["card_bg"],
                   foreground=theme["fg"],
                   fieldbackground=theme["card_bg"],
                   rowheight=30)
    style.configure("Treeview.Heading",
                   background=theme["header_bg"],
                   foreground=theme["header_fg"],
                   font=fonts["body_bold"])
    
    style.configure("Horizontal.TProgressbar",
                   background=theme["accent"],
                   troughcolor=theme["border"])


def create_styled_entry(parent, theme, fonts, show=None):
    """Create a styled entry widget."""
    entry = Entry(parent, font=fonts["body"],
                 bg=theme["input_bg"], fg=theme["fg"],
                 insertbackground=theme["fg"],
                 highlightbackground=theme["input_border"],
                 highlightthickness=1, bd=0,
                 relief=FLAT, show=show if show else "")
    entry.config(highlightcolor=theme["accent"])
    return entry


def create_stat_card(parent, icon, label, value, color, theme, fonts):
    """Create a statistic card."""
    card = Frame(parent, bg=theme["card_bg"], padx=20, pady=20,
                highlightbackground=theme["border"], highlightthickness=1)
    
    Label(card, text=icon, font=("Segoe UI", 32),
          bg=theme["card_bg"], fg=color).pack(anchor=W)
    
    Label(card, text=str(value), font=fonts["title"],
          bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
    
    Label(card, text=label, font=fonts["body"],
          bg=theme["card_bg"], fg=theme["text_secondary"]).pack(anchor=W)
    
    return card


def load_image_label(label, image_path, width, height):
    """Load and display an image on a label."""
    try:
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img = img.resize((width, height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo
            return True
    except Exception as e:
        print(f"Error loading image: {e}")
    
    label.config(text="📷", font=("Segoe UI", 48))
    return False


class ScrollableFrame(Frame):
    """A scrollable frame widget."""
    
    def __init__(self, parent, theme, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.canvas = Canvas(self, bg=theme["bg"], highlightthickness=0)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg=theme["bg"])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")


def create_card_frame(parent, theme, title=None):
    """Create a styled card frame."""
    if title:
        card = LabelFrame(parent, text=title, font=("Segoe UI", 12, "bold"),
                         bg=theme["card_bg"], fg=theme["fg"],
                         padx=20, pady=20)
    else:
        card = Frame(parent, bg=theme["card_bg"], padx=20, pady=20,
                    highlightbackground=theme["border"], highlightthickness=1)
    
    return card
