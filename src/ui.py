"""
Modern UI module for Travel Management System.
Features professional design, dark/light mode, and comprehensive functionality.
"""

import os
import re
import json
import datetime
from tkinter import *
from tkinter import messagebox, filedialog, ttk
from tkinter.font import Font
from PIL import ImageTk, Image

# Import database module
from database import (
    init_database, add_user, authenticate_user, get_user_by_id, update_user,
    get_all_destinations, get_destination_by_id, search_destinations, get_destination_categories,
    add_booking, get_user_bookings, get_booking_by_id, delete_booking, update_booking_status,
    add_review, get_destination_reviews, get_user_reviews,
    create_trip_plan, get_user_trip_plans, update_trip_plan, delete_trip_plan,
    get_recommendations, get_popular_destinations, save_user_preferences,
    export_user_data, calculate_package_price
)
from ui_components import (
    THEMES, setup_fonts, setup_styles, create_styled_entry,
    create_stat_card, load_image_label, ScrollableFrame, create_card_frame
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")


from ui_views import TravelAppViews

class ModernTravelApp(TravelAppViews):
    """Modern Travel Management System Application.""
    Inherits from TravelAppViews for all view methods."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Travel Management System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Try to set icon
        try:
            icon_path = os.path.join(ICONS_DIR, "silicon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # State
        self.current_user = None
        self.current_user_id = None
        self.current_theme = "light"
        self.destinations = []
        self.filtered_destinations = []
        self.selected_destination = None
        self.bookings = []
        self.current_view = "home"
        
        # Initialize
        self.fonts = setup_fonts()
        self.setup_styles()
        self.load_destinations()
        self.create_login_screen()
    
    def get_theme(self):
        """Get current theme colors."""
        return THEMES[self.current_theme]
    
    def setup_styles(self):
        """Setup ttk styles for current theme."""
        from ui_components import setup_styles as setup_component_styles
        theme = self.get_theme()
        style = ttk.Style()
        setup_component_styles(style, theme, self.fonts)
    
    def clear_window(self):
        """Clear all widgets from window."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def load_destinations(self):
        """Load destinations from database."""
        self.destinations = get_all_destinations()
        self.filtered_destinations = self.destinations
    
    # ==================== LOGIN SCREEN ====================
    
    def create_login_screen(self):
        """Create modern login screen."""
        self.clear_window()
        theme = self.get_theme()
        
        # Main container
        main_container = Frame(self.root, bg=theme["bg"])
        main_container.pack(fill=BOTH, expand=True)
        
        # Left panel (branding)
        left_panel = Frame(main_container, bg=theme["header_bg"], width=400)
        left_panel.pack(side=LEFT, fill=Y)
        left_panel.pack_propagate(False)
        
        # Logo/Brand
        brand_frame = Frame(left_panel, bg=theme["header_bg"])
        brand_frame.place(relx=0.5, rely=0.4, anchor=CENTER)
        
        Label(brand_frame, text="✈", font=("Segoe UI", 72), 
              bg=theme["header_bg"], fg=theme["accent"]).pack()
        
        Label(brand_frame, text="Travel Management", 
              font=self.fonts["subtitle"], bg=theme["header_bg"], 
              fg="white").pack(pady=(20, 5))
        
        Label(brand_frame, text="System", 
              font=self.fonts["subtitle"], bg=theme["header_bg"], 
              fg=theme["accent"]).pack()
        
        Label(brand_frame, text="Discover your next adventure", 
              font=self.fonts["body"], bg=theme["header_bg"], 
              fg=theme["text_secondary"]).pack(pady=20)
        
        # Right panel (login form)
        right_panel = Frame(main_container, bg=theme["bg"])
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Center the form
        form_container = Frame(right_panel, bg=theme["bg"])
        form_container.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Login card
        login_card = Frame(form_container, bg=theme["card_bg"],
                          highlightbackground=theme["border"],
                          highlightthickness=1, padx=40, pady=40)
        login_card.pack()
        
        Label(login_card, text="Welcome Back", font=self.fonts["title"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(pady=(0, 10))
        
        Label(login_card, text="Sign in to continue", font=self.fonts["body"],
              bg=theme["card_bg"], fg=theme["text_secondary"]).pack(pady=(0, 30))
        
        # Username
        Label(login_card, text="Username", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(0, 5))
        
        self.username_entry = create_styled_entry(login_card, theme, self.fonts)
        self.username_entry.pack(fill=X, pady=(0, 15))
        self.username_entry.focus()
        
        # Password
        Label(login_card, text="Password", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(0, 5))
        
        self.password_entry = create_styled_entry(login_card, theme, self.fonts, show="•")
        self.password_entry.pack(fill=X, pady=(0, 25))
        
        # Login button
        login_btn = Button(login_card, text="Sign In", 
                          font=self.fonts["button"],
                          bg=theme["accent"], fg="white",
                          activebackground=theme["accent_hover"],
                          activeforeground="white",
                          bd=0, padx=40, pady=12, cursor="hand2",
                          command=self.login)
        login_btn.pack(fill=X, pady=(0, 15))
        
        # Sign up link
        signup_frame = Frame(login_card, bg=theme["card_bg"])
        signup_frame.pack()
        
        Label(signup_frame, text="Don't have an account? ",
              font=self.fonts["body"], bg=theme["card_bg"],
              fg=theme["text_secondary"]).pack(side=LEFT)
        
        signup_link = Label(signup_frame, text="Sign Up",
                           font=self.fonts["body_bold"], bg=theme["card_bg"],
                           fg=theme["accent"], cursor="hand2")
        signup_link.pack(side=LEFT)
        signup_link.bind("<Button-1>", lambda e: self.show_signup())
        
        # Theme toggle
        theme_btn = Button(main_container, text="🌓",
                          font=("Segoe UI", 14),
                          bg=theme["bg"], fg=theme["fg"],
                          bd=0, cursor="hand2",
                          command=self.toggle_theme)
        theme_btn.place(relx=0.98, rely=0.02, anchor=NE)
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.setup_styles()
        self.create_login_screen()
    
    def login(self):
        """Handle user login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not self.validate_login_input(username, password):
            return
        
        user = authenticate_user(username, password)
        
        if user:
            self.current_user = user['username']
            self.current_user_id = user['id']
            self.create_main_app()
        else:
            messagebox.showerror("Login Failed", 
                               "Invalid username or password. Please try again.")
    
    def validate_login_input(self, username, password):
        """Validate login input."""
        if not username:
            messagebox.showerror("Validation Error", "Please enter your username")
            return False
        
        if not password:
            messagebox.showerror("Validation Error", "Please enter your password")
            return False
        
        if len(username) < 3:
            messagebox.showerror("Validation Error", 
                               "Username must be at least 3 characters")
            return False
        
        return True
    
    # ==================== SIGNUP SCREEN ====================
    
    def show_signup(self):
        """Show signup dialog."""
        theme = self.get_theme()
        
        signup_window = Toplevel(self.root)
        signup_window.title("Create Account")
        signup_window.geometry("500x600")
        signup_window.transient(self.root)
        signup_window.grab_set()
        
        # Center window
        signup_window.update_idletasks()
        x = (signup_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (signup_window.winfo_screenheight() // 2) - (600 // 2)
        signup_window.geometry(f"+{x}+{y}")
        
        # Container
        container = Frame(signup_window, bg=theme["bg"], padx=40, pady=30)
        container.pack(fill=BOTH, expand=True)
        
        # Header
        Label(container, text="Create Account", font=self.fonts["title"],
              bg=theme["bg"], fg=theme["fg"]).pack(pady=(0, 10))
        
        Label(container, text="Join us and start exploring",
              font=self.fonts["body"], bg=theme["bg"],
              fg=theme["text_secondary"]).pack(pady=(0, 30))
        
        # Form fields
        fields = [
            ("Username", "username", False),
            ("Full Name", "full_name", False),
            ("Email", "email", False),
            ("Phone", "phone", False),
            ("Password", "password", True),
            ("Confirm Password", "confirm_password", True)
        ]
        
        entries = {}
        
        for label, key, is_password in fields:
            Label(container, text=label, font=self.fonts["body_bold"],
                  bg=theme["bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
            
            entry = create_styled_entry(container, theme, self.fonts, show="•" if is_password else None)
            entry.pack(fill=X, pady=(0, 5))
            entries[key] = entry
        
        # Create button
        Button(container, text="Create Account",
               font=self.fonts["button"],
               bg=theme["accent"], fg="white",
               activebackground=theme["accent_hover"],
               bd=0, padx=30, pady=12, cursor="hand2",
               command=lambda: self.create_account(entries, signup_window)
              ).pack(fill=X, pady=30)
        
        # Cancel
        Button(container, text="Cancel",
               font=self.fonts["body"],
               bg=theme["border"], fg=theme["fg"],
               bd=0, padx=20, pady=8, cursor="hand2",
               command=signup_window.destroy
              ).pack()
    
    def create_account(self, entries, window):
        """Create new account."""
        username = entries['username'].get().strip()
        full_name = entries['full_name'].get().strip()
        email = entries['email'].get().strip()
        phone = entries['phone'].get().strip()
        password = entries['password'].get()
        confirm_password = entries['confirm_password'].get()
        
        # Validation
        if not username or len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters")
            return
        
        if not full_name:
            messagebox.showerror("Error", "Please enter your full name")
            return
        
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if add_user(username, password, email, full_name, phone):
            messagebox.showinfo("Success", "Account created successfully! Please sign in.")
            window.destroy()
        else:
            messagebox.showerror("Error", "Username already exists or could not create account")
    
    # ==================== MAIN APP INTERFACE ====================
    
    def create_main_app(self):
        """Create main application interface with sidebar."""
        self.clear_window()
        theme = self.get_theme()
        
        # Main container
        self.main_container = Frame(self.root, bg=theme["bg"])
        self.main_container.pack(fill=BOTH, expand=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Content area
        self.content_frame = Frame(self.main_container, bg=theme["bg"])
        self.content_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=20, pady=20)
        
        # Show home view by default
        self.show_home_view()
    
    def create_sidebar(self):
        """Create navigation sidebar."""
        theme = self.get_theme()
        
        sidebar = Frame(self.main_container, bg=theme["sidebar_bg"], width=220)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)
        
        # Logo section
        logo_frame = Frame(sidebar, bg=theme["sidebar_bg"], height=80)
        logo_frame.pack(fill=X, padx=20, pady=20)
        logo_frame.pack_propagate(False)
        
        Label(logo_frame, text="✈ Travel", font=self.fonts["heading"],
              bg=theme["sidebar_bg"], fg=theme["accent"]).place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Navigation buttons
        nav_items = [
            ("🏠", "Home", self.show_home_view),
            ("🌍", "Destinations", self.show_destinations_view),
            ("📋", "My Bookings", self.show_bookings_view),
            ("🗓", "Trip Planner", self.show_planner_view),
            ("⭐", "Recommendations", self.show_recommendations_view),
            ("👤", "Profile", self.show_profile_view)
        ]
        
        self.nav_buttons = {}
        
        for icon, label, command in nav_items:
            btn_frame = Frame(sidebar, bg=theme["sidebar_bg"], height=45, cursor="hand2")
            btn_frame.pack(fill=X, padx=10, pady=2)
            btn_frame.pack_propagate(False)
            
            # Icon and label
            icon_label = Label(btn_frame, text=icon, font=("Segoe UI", 14),
                             bg=theme["sidebar_bg"], fg=theme["sidebar_fg"])
            icon_label.pack(side=LEFT, padx=(15, 10))
            
            text_label = Label(btn_frame, text=label, font=self.fonts["nav"],
                             bg=theme["sidebar_bg"], fg=theme["sidebar_fg"])
            text_label.pack(side=LEFT)
            
            # Click events
            btn_frame.bind("<Button-1>", lambda e, c=command, b=btn_frame: self.nav_click(c, b))
            icon_label.bind("<Button-1>", lambda e, c=command, b=btn_frame: self.nav_click(c, b))
            text_label.bind("<Button-1>", lambda e, c=command, b=btn_frame: self.nav_click(c, b))
            
            # Hover effects
            btn_frame.bind("<Enter>", lambda e, f=btn_frame: self.on_nav_hover(f))
            btn_frame.bind("<Leave>", lambda e, f=btn_frame: self.on_nav_leave(f))
            
            self.nav_buttons[label] = btn_frame
        
        # Bottom section
        bottom_frame = Frame(sidebar, bg=theme["sidebar_bg"])
        bottom_frame.pack(side=BOTTOM, fill=X, padx=20, pady=20)
        
        # Theme toggle
        theme_text = "🌙 Dark Mode" if self.current_theme == "light" else "☀ Light Mode"
        theme_btn = Button(bottom_frame, text=theme_text,
                          font=self.fonts["caption"],
                          bg=theme["bg"], fg=theme["fg"],
                          bd=0, padx=10, pady=5, cursor="hand2",
                          command=self.toggle_theme_main)
        theme_btn.pack(fill=X, pady=(0, 10))
        
        # User info
        user_frame = Frame(bottom_frame, bg=theme["sidebar_bg"])
        user_frame.pack(fill=X, pady=(10, 10))
        
        Label(user_frame, text=f"👤 {self.current_user}", 
              font=self.fonts["body_bold"],
              bg=theme["sidebar_bg"], fg=theme["sidebar_fg"]).pack(anchor=W)
        
        # Logout
        Button(bottom_frame, text="Logout",
               font=self.fonts["body"],
               bg=theme["danger"], fg="white",
               bd=0, padx=20, pady=8, cursor="hand2",
               command=self.logout).pack(fill=X)
    
    def nav_click(self, command, btn_frame):
        """Handle navigation click."""
        self.highlight_nav_button(btn_frame)
        command()
    
    def on_nav_hover(self, frame):
        """Handle nav hover."""
        theme = self.get_theme()
        frame.config(bg=theme["hover_bg"])
        for child in frame.winfo_children():
            child.config(bg=theme["hover_bg"])
    
    def on_nav_leave(self, frame):
        """Handle nav leave."""
        theme = self.get_theme()
        # Only reset if not active
        if frame != getattr(self, 'active_nav', None):
            frame.config(bg=theme["sidebar_bg"])
            for child in frame.winfo_children():
                child.config(bg=theme["sidebar_bg"])
    
    def highlight_nav_button(self, active_frame):
        """Highlight active nav button."""
        theme = self.get_theme()
        self.active_nav = active_frame
        
        for label, frame in self.nav_buttons.items():
            if frame == active_frame:
                frame.config(bg=theme["sidebar_active"])
                for child in frame.winfo_children():
                    child.config(bg=theme["sidebar_active"], fg=theme["accent"])
            else:
                frame.config(bg=theme["sidebar_bg"])
                for child in frame.winfo_children():
                    child.config(bg=theme["sidebar_bg"], fg=theme["sidebar_fg"])
    
    def toggle_theme_main(self):
        """Toggle theme in main app."""
        self.toggle_theme()
        self.create_main_app()
    
    def clear_content(self):
        """Clear content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Logout user."""
        self.current_user = None
        self.current_user_id = None
        self.create_login_screen()
    
    # ==================== HOME VIEW ====================
    
    def show_home_view(self):
        """Show home dashboard."""
        self.clear_content()
        theme = self.get_theme()
        
        # Welcome header
        header = Frame(self.content_frame, bg=theme["bg"])
        header.pack(fill=X, pady=(0, 20))
        
        Label(header, text=f"Welcome back, {self.current_user}!",
              font=self.fonts["title"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W)
        
        Label(header, text="Here's what's happening with your travel plans",
              font=self.fonts["body"], bg=theme["bg"], fg=theme["text_secondary"]).pack(anchor=W, pady=(5, 0))
        
        # Stats cards
        stats_frame = Frame(self.content_frame, bg=theme["bg"])
        stats_frame.pack(fill=X, pady=20)
        
        # Get stats
        bookings = get_user_bookings(self.current_user_id)
        plans = get_user_trip_plans(self.current_user_id)
        
        stats = [
            ("📅", "Active Bookings", len([b for b in bookings if b['status'] == 'confirmed']), theme["accent"]),
            ("🗓", "Trip Plans", len(plans), theme["success"]),
            ("✅", "Completed Trips", len([b for b in bookings if b['status'] == 'completed']), theme["warning"]),
            ("💰", "Total Spent", f"₹{sum(b.get('total_price', 0) or 0 for b in bookings):,.0f}", theme["danger"])
        ]
        
        for icon, label, value, color in stats:
            card = create_stat_card(stats_frame, icon, label, value, color, theme, self.fonts)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        
        # Quick actions
        actions_frame = LabelFrame(self.content_frame, text="Quick Actions",
                                   font=self.fonts["heading"],
                                   bg=theme["card_bg"], fg=theme["fg"],
                                   padx=20, pady=20)
        actions_frame.pack(fill=X, pady=20)
        
        actions = [
            ("🔍 Explore Destinations", self.show_destinations_view),
            ("📖 View My Bookings", self.show_bookings_view),
            ("✨ Get Recommendations", self.show_recommendations_view),
            ("📝 Plan a New Trip", self.show_planner_view)
        ]
        
        for text, command in actions:
            btn = Button(actions_frame, text=text,
                        font=self.fonts["body"],
                        bg=theme["bg"], fg=theme["fg"],
                        activebackground=theme["hover_bg"],
                        bd=0, padx=20, pady=10, cursor="hand2",
                        command=command)
            btn.pack(side=LEFT, padx=10)
        
        # Popular destinations section
        popular_frame = LabelFrame(self.content_frame, text="Popular Destinations",
                                   font=self.fonts["heading"],
                                   bg=theme["card_bg"], fg=theme["fg"],
                                   padx=20, pady=20)
        popular_frame.pack(fill=BOTH, expand=True, pady=20)
        
        popular = get_popular_destinations(3)
        
        if popular:
            for dest in popular:
                card = self.create_destination_card(popular_frame, dest, compact=True)
                card.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        else:
            Label(popular_frame, text="No destinations available",
                  font=self.fonts["body"], bg=theme["card_bg"],
                  fg=theme["text_secondary"]).pack(pady=50)
    
    def create_destination_card(self, parent, dest, compact=False):
        """Create a destination card."""
        theme = self.get_theme()
        
        if compact:
            card = Frame(parent, bg=theme["card_bg"], padx=15, pady=15,
                        highlightbackground=theme["border"], highlightthickness=1)
            width, height = 200, 150
        else:
            card = Frame(parent, bg=theme["card_bg"], padx=20, pady=20,
                        highlightbackground=theme["border"], highlightthickness=1)
            width, height = 300, 200
        
        # Image
        img_label = Label(card, bg=theme["card_bg"])
        img_label.pack(fill=X)
        
        try:
            if dest.get('image_path'):
                img_path = os.path.join(IMAGES_DIR, dest['image_path'])
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img = img.resize((width, height), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    img_label.config(image=photo)
                    img_label.image = photo
                else:
                    img_label.config(text="📷", font=("Segoe UI", 48))
            else:
                img_label.config(text="📷", font=("Segoe UI", 48))
        except:
            img_label.config(text="📷", font=("Segoe UI", 48))
        
        # Info
        Label(card, text=dest['name'], font=self.fonts["heading"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        
        Label(card, text=dest['category'], font=self.fonts["caption"],
              bg=theme["card_bg"], fg=theme["accent"]).pack(anchor=W)
        
        if not compact:
            desc = dest.get('description', '')[:100] + '...' if len(dest.get('description', '')) > 100 else dest.get('description', '')
            Label(card, text=desc, font=self.fonts["body"],
                  bg=theme["card_bg"], fg=theme["text_secondary"],
                  wraplength=280, justify=LEFT).pack(anchor=W, pady=5)
        
        # Price and rating
        price_frame = Frame(card, bg=theme["card_bg"])
        price_frame.pack(fill=X, pady=10)
        
        Label(price_frame, text=f"₹{dest.get('base_price', 0):,.0f}",
              font=self.fonts["body_bold"], bg=theme["card_bg"],
              fg=theme["accent"]).pack(side=LEFT)
        
        rating = dest.get('rating', 0) or 0
        stars = "⭐" * int(rating) + "☆" * (5 - int(rating))
        Label(price_frame, text=f"{stars} ({rating:.1f})",
              font=self.fonts["caption"], bg=theme["card_bg"],
              fg=theme["text_secondary"]).pack(side=RIGHT)
        
        # Buttons
        if not compact:
            btn_frame = Frame(card, bg=theme["card_bg"])
            btn_frame.pack(fill=X, pady=(10, 0))
            
            Button(btn_frame, text="View Details",
                   font=self.fonts["body"],
                   bg=theme["accent"], fg="white",
                   bd=0, padx=20, pady=8, cursor="hand2",
                   command=lambda d=dest: self.show_destination_detail(d)
                  ).pack(side=LEFT, expand=True, fill=X, padx=(0, 5))
            
            Button(btn_frame, text="Book Now",
                   font=self.fonts["body"],
                   bg=theme["success"], fg="white",
                   bd=0, padx=20, pady=8, cursor="hand2",
                   command=lambda d=dest: self.quick_book(d)
                  ).pack(side=RIGHT, expand=True, fill=X, padx=(5, 0))
        
        return card
