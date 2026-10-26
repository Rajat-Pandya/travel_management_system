"""
UI module continuation - Views for Destinations, Bookings, Planner, Recommendations, and Profile.
"""

import os
import re
import json
from tkinter import *
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image

# Import functions from main ui module
from ui_components import (
    THEMES, create_styled_entry, create_stat_card, create_card_frame
)
from database import (
    search_destinations, get_destination_categories, get_destination_reviews,
    add_booking, get_user_bookings, get_booking_by_id, update_booking_status,
    add_review, create_trip_plan, get_user_trip_plans, delete_trip_plan,
    get_recommendations, get_popular_destinations, save_user_preferences,
    export_user_data, calculate_package_price, get_all_destinations
)


class TravelAppViews:
    """Mixin class for app views. To be inherited by ModernTravelApp."""
    
    # ==================== DESTINATIONS VIEW ====================
    
    def show_destinations_view(self):
        """Show destinations with search and filters."""
        self.clear_content()
        theme = self.get_theme()
        
        # Header
        header = Frame(self.content_frame, bg=theme["bg"])
        header.pack(fill=X, pady=(0, 20))
        
        Label(header, text="Explore Destinations",
              font=self.fonts["title"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W)
        
        # Search and filter bar
        filter_frame = Frame(self.content_frame, bg=theme["card_bg"], padx=20, pady=15,
                            highlightbackground=theme["border"], highlightthickness=1)
        filter_frame.pack(fill=X, pady=(0, 20))
        
        # Search
        search_frame = Frame(filter_frame, bg=theme["card_bg"])
        search_frame.pack(side=LEFT, fill=Y, padx=(0, 20))
        
        Label(search_frame, text="🔍 Search:", font=self.fonts["body"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(side=LEFT, padx=(0, 10))
        
        self.search_entry = create_styled_entry(search_frame, theme, self.fonts)
        self.search_entry.pack(side=LEFT, width=200)
        self.search_entry.bind('<KeyRelease>', lambda e: self.filter_destinations())
        
        # Category filter
        Label(filter_frame, text="Category:", font=self.fonts["body"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(side=LEFT, padx=(20, 10))
        
        self.category_var = StringVar(value="All")
        categories = ["All"] + get_destination_categories()
        
        category_menu = OptionMenu(filter_frame, self.category_var, *categories,
                                   command=lambda _: self.filter_destinations())
        category_menu.config(font=self.fonts["body"], bg=theme["bg"],
                            fg=theme["fg"], width=12)
        category_menu.pack(side=LEFT)
        
        # Budget filter
        Label(filter_frame, text="Max Budget: ₹", font=self.fonts["body"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(side=LEFT, padx=(20, 5))
        
        self.budget_var = StringVar(value="")
        budget_entry = create_styled_entry(filter_frame, theme, self.fonts)
        budget_entry.config(textvariable=self.budget_var, width=10)
        budget_entry.pack(side=LEFT)
        budget_entry.bind('<KeyRelease>', lambda e: self.filter_destinations())
        
        # Clear filters
        Button(filter_frame, text="Clear Filters",
               font=self.fonts["body"],
               bg=theme["border"], fg=theme["fg"],
               bd=0, padx=15, pady=5, cursor="hand2",
               command=self.clear_filters).pack(side=RIGHT)
        
        # Destinations grid
        self.destinations_canvas = Canvas(self.content_frame, bg=theme["bg"],
                                          highlightthickness=0)
        self.destinations_canvas.pack(fill=BOTH, expand=True)
        
        scrollbar = Scrollbar(self.content_frame, orient=VERTICAL,
                             command=self.destinations_canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.destinations_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.destinations_container = Frame(self.destinations_canvas, bg=theme["bg"])
        self.destinations_canvas.create_window((0, 0), window=self.destinations_container,
                                               anchor=NW, width=self.content_frame.winfo_width() - 40)
        
        self.destinations_container.bind("<Configure>", 
                                         lambda e: self.destinations_canvas.configure(
                                             scrollregion=self.destinations_canvas.bbox("all")))
        
        # Initial display
        self.filter_destinations()
    
    def filter_destinations(self):
        """Filter destinations based on search criteria."""
        search = self.search_entry.get().strip()
        category = self.category_var.get()
        budget_str = self.budget_var.get().strip()
        
        max_budget = None
        if budget_str:
            try:
                max_budget = float(budget_str)
            except ValueError:
                pass
        
        cat_filter = None if category == "All" else category
        
        self.filtered_destinations = search_destinations(
            query=search if search else None,
            category=cat_filter,
            max_price=max_budget
        )
        
        self.display_destinations()
    
    def clear_filters(self):
        """Clear all filters."""
        self.search_entry.delete(0, END)
        self.category_var.set("All")
        self.budget_var.set("")
        self.filter_destinations()
    
    def display_destinations(self):
        """Display filtered destinations in grid."""
        theme = self.get_theme()
        
        # Clear existing
        for widget in self.destinations_container.winfo_children():
            widget.destroy()
        
        if not self.filtered_destinations:
            Label(self.destinations_container, text="No destinations found",
                  font=self.fonts["body"], bg=theme["bg"],
                  fg=theme["text_secondary"]).pack(pady=100)
            return
        
        # Display in grid (3 columns)
        for i, dest in enumerate(self.filtered_destinations):
            row = i // 3
            col = i % 3
            
            card = self.create_destination_card(self.destinations_container, dest)
            card.grid(row=row, column=col, padx=10, pady=10, sticky=NSEW)
        
        # Configure grid weights
        for i in range(3):
            self.destinations_container.columnconfigure(i, weight=1)
    
    def show_destination_detail(self, dest):
        """Show detailed view of a destination."""
        theme = self.get_theme()
        
        detail_window = Toplevel(self.root)
        detail_window.title(f"{dest['name']} - Details")
        detail_window.geometry("800x600")
        detail_window.transient(self.root)
        
        container = Frame(detail_window, bg=theme["bg"], padx=30, pady=30)
        container.pack(fill=BOTH, expand=True)
        
        # Header
        Label(container, text=dest['name'], font=self.fonts["title"],
              bg=theme["bg"], fg=theme["fg"]).pack(anchor=W)
        
        Label(container, text=dest['category'], font=self.fonts["body"],
              bg=theme["bg"], fg=theme["accent"]).pack(anchor=W, pady=5)
        
        # Description
        desc_frame = LabelFrame(container, text="About", font=self.fonts["heading"],
                                bg=theme["card_bg"], fg=theme["fg"], padx=20, pady=20)
        desc_frame.pack(fill=X, pady=20)
        
        Label(desc_frame, text=dest.get('description', 'No description available'),
              font=self.fonts["body"], bg=theme["card_bg"],
              fg=theme["fg"], wraplength=700, justify=LEFT).pack(anchor=W)
        
        # Price
        Label(desc_frame, text=f"Starting from: ₹{dest.get('base_price', 0):,.0f}",
              font=self.fonts["subtitle"], bg=theme["card_bg"],
              fg=theme["accent"]).pack(anchor=W, pady=(20, 0))
        
        # Reviews section
        reviews_frame = LabelFrame(container, text="Reviews", font=self.fonts["heading"],
                                   bg=theme["card_bg"], fg=theme["fg"], padx=20, pady=20)
        reviews_frame.pack(fill=X, pady=20)
        
        reviews = get_destination_reviews(dest['id'])
        
        if reviews:
            for review in reviews[:3]:  # Show top 3
                review_card = Frame(reviews_frame, bg=theme["bg"], padx=15, pady=10,
                                   highlightbackground=theme["border"], highlightthickness=1)
                review_card.pack(fill=X, pady=5)
                
                Label(review_card, text=f"{review.get('username', 'Anonymous')} - {'⭐' * review['rating']}",
                      font=self.fonts["body_bold"], bg=theme["bg"],
                      fg=theme["fg"]).pack(anchor=W)
                
                if review.get('comment'):
                    Label(review_card, text=review['comment'],
                          font=self.fonts["body"], bg=theme["bg"],
                          fg=theme["text_secondary"], wraplength=650).pack(anchor=W, pady=(5, 0))
        else:
            Label(reviews_frame, text="No reviews yet. Be the first to review!",
                  font=self.fonts["body"], bg=theme["card_bg"],
                  fg=theme["text_secondary"]).pack(pady=20)
        
        # Action buttons
        btn_frame = Frame(container, bg=theme["bg"])
        btn_frame.pack(fill=X, pady=20)
        
        Button(btn_frame, text="Book This Trip",
               font=self.fonts["button"],
               bg=theme["accent"], fg="white",
               bd=0, padx=30, pady=12, cursor="hand2",
               command=lambda: [detail_window.destroy(), self.quick_book(dest)]
              ).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Add Review",
               font=self.fonts["body"],
               bg=theme["success"], fg="white",
               bd=0, padx=20, pady=10, cursor="hand2",
               command=lambda: [detail_window.destroy(), self.add_review_dialog(dest)]
              ).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Close",
               font=self.fonts["body"],
               bg=theme["border"], fg=theme["fg"],
               bd=0, padx=20, pady=10, cursor="hand2",
               command=detail_window.destroy
              ).pack(side=RIGHT, padx=5)
    
    def quick_book(self, dest):
        """Quick book dialog."""
        theme = self.get_theme()
        
        book_window = Toplevel(self.root)
        book_window.title(f"Book {dest['name']}")
        book_window.geometry("500x600")
        book_window.transient(self.root)
        book_window.grab_set()
        
        container = Frame(book_window, bg=theme["bg"], padx=30, pady=30)
        container.pack(fill=BOTH, expand=True)
        
        Label(container, text=f"Book {dest['name']}",
              font=self.fonts["title"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W, pady=(0, 20))
        
        # Form fields
        fields_frame = Frame(container, bg=theme["card_bg"], padx=20, pady=20,
                            highlightbackground=theme["border"], highlightthickness=1)
        fields_frame.pack(fill=X, pady=10)
        
        entries = {}
        
        # Name
        Label(fields_frame, text="Full Name:", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        entries['name'] = create_styled_entry(fields_frame, theme, self.fonts)
        entries['name'].pack(fill=X)
        
        # Date
        Label(fields_frame, text="Travel Date (DD/MM/YYYY):", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        entries['date'] = create_styled_entry(fields_frame, theme, self.fonts)
        entries['date'].pack(fill=X)
        
        # People
        Label(fields_frame, text="Number of People:", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        entries['people'] = create_styled_entry(fields_frame, theme, self.fonts)
        entries['people'].insert(0, "1")
        entries['people'].pack(fill=X)
        
        # Package
        Label(fields_frame, text="Package:", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        
        entries['package'] = StringVar(value="Silver")
        package_frame = Frame(fields_frame, bg=theme["card_bg"])
        package_frame.pack(fill=X, pady=5)
        
        for pkg in ["Silver", "Golden", "Diamond"]:
            rb = Radiobutton(package_frame, text=pkg, variable=entries['package'],
                           value=pkg, bg=theme["card_bg"], fg=theme["fg"],
                           font=self.fonts["body"], selectcolor=theme["accent"])
            rb.pack(side=LEFT, padx=10)
        
        # Address
        Label(fields_frame, text="Address:", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        entries['address'] = create_styled_entry(fields_frame, theme, self.fonts)
        entries['address'].pack(fill=X)
        
        # Price preview
        price_frame = Frame(container, bg=theme["bg"])
        price_frame.pack(fill=X, pady=20)
        
        self.price_preview = Label(price_frame, text="Estimated Price: ₹0",
                                   font=self.fonts["heading"],
                                   bg=theme["bg"], fg=theme["accent"])
        self.price_preview.pack(anchor=W)
        
        def update_price(*args):
            try:
                people = int(entries['people'].get() or 1)
                package = entries['package'].get()
                price = calculate_package_price(dest.get('base_price', 0), package, people)
                self.price_preview.config(text=f"Estimated Price: ₹{price:,.0f}")
            except:
                pass
        
        entries['people'].bind('<KeyRelease>', update_price)
        update_price()
        
        # Buttons
        btn_frame = Frame(container, bg=theme["bg"])
        btn_frame.pack(fill=X, pady=20)
        
        Button(btn_frame, text="Confirm Booking",
               font=self.fonts["button"],
               bg=theme["accent"], fg="white",
               bd=0, padx=30, pady=12, cursor="hand2",
               command=lambda: self.process_booking(entries, dest, book_window)
              ).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Cancel",
               font=self.fonts["body"],
               bg=theme["border"], fg=theme["fg"],
               bd=0, padx=20, pady=10, cursor="hand2",
               command=book_window.destroy
              ).pack(side=RIGHT, padx=5)
    
    def process_booking(self, entries, dest, window):
        """Process booking form submission."""
        name = entries['name'].get().strip()
        date = entries['date'].get().strip()
        people_str = entries['people'].get().strip()
        package = entries['package'].get()
        address = entries['address'].get().strip()
        
        # Validation
        if not name or len(name) < 2:
            messagebox.showerror("Error", "Please enter a valid name")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Error", "Please enter a valid date (DD/MM/YYYY)")
            return
        
        try:
            people = int(people_str)
            if people < 1 or people > 100:
                raise ValueError()
        except:
            messagebox.showerror("Error", "Number of people must be between 1 and 100")
            return
        
        if len(address) < 10:
            messagebox.showerror("Error", "Please enter a complete address (min 10 characters)")
            return
        
        # Calculate price
        total_price = calculate_package_price(dest.get('base_price', 0), package, people)
        
        # Create booking
        booking_id = add_booking(
            user_id=self.current_user_id,
            customer_name=name,
            destination_name=dest['name'],
            package_type=package,
            travel_date=date,
            number_of_people=people,
            customer_address=address,
            destination_id=dest.get('id'),
            total_price=total_price
        )
        
        if booking_id:
            messagebox.showinfo("Success", 
                              f"Booking confirmed!\n\nBooking ID: #{booking_id}\nTotal: ₹{total_price:,.0f}")
            window.destroy()
            self.show_bookings_view()
        else:
            messagebox.showerror("Error", "Failed to create booking. Please try again.")
    
    def add_review_dialog(self, dest):
        """Show review dialog."""
        theme = self.get_theme()
        
        review_window = Toplevel(self.root)
        review_window.title(f"Review {dest['name']}")
        review_window.geometry("400x400")
        review_window.transient(self.root)
        
        container = Frame(review_window, bg=theme["bg"], padx=30, pady=30)
        container.pack(fill=BOTH, expand=True)
        
        Label(container, text=f"Rate {dest['name']}",
              font=self.fonts["heading"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W)
        
        # Rating
        rating_frame = Frame(container, bg=theme["bg"])
        rating_frame.pack(fill=X, pady=20)
        
        rating_var = IntVar(value=5)
        
        Label(rating_frame, text="Your Rating:", font=self.fonts["body_bold"],
              bg=theme["bg"], fg=theme["fg"]).pack(side=LEFT, padx=(0, 10))
        
        for i in range(1, 6):
            rb = Radiobutton(rating_frame, text=str(i), variable=rating_var,
                           value=i, bg=theme["bg"], fg=theme["fg"],
                           font=self.fonts["body"], selectcolor=theme["accent"])
            rb.pack(side=LEFT, padx=5)
        
        # Comment
        Label(container, text="Your Review:", font=self.fonts["body_bold"],
              bg=theme["bg"], fg=theme["fg"]).pack(anchor=W, pady=(20, 10))
        
        comment_text = Text(container, font=self.fonts["body"],
                           bg=theme["input_bg"], fg=theme["fg"],
                           height=5, wrap=WORD)
        comment_text.pack(fill=X)
        
        # Submit
        Button(container, text="Submit Review",
               font=self.fonts["button"],
               bg=theme["accent"], fg="white",
               bd=0, padx=30, pady=10, cursor="hand2",
               command=lambda: self.submit_review(dest['id'], rating_var.get(),
                                                  comment_text.get("1.0", END).strip(),
                                                  review_window)
              ).pack(fill=X, pady=30)
    
    def submit_review(self, dest_id, rating, comment, window):
        """Submit review to database."""
        if add_review(self.current_user_id, dest_id, rating, comment):
            messagebox.showinfo("Success", "Thank you for your review!")
            window.destroy()
        else:
            messagebox.showerror("Error", "Failed to submit review")
    
    def validate_date(self, date_str):
        """Validate date format."""
        pattern = r'^\d{2}/\d{2}/\d{4}$'
        if not re.match(pattern, date_str):
            return False
        try:
            day, month, year = map(int, date_str.split('/'))
            return 1 <= day <= 31 and 1 <= month <= 12 and year >= 2020
        except:
            return False
    
    # ==================== BOOKINGS VIEW ====================
    
    def show_bookings_view(self):
        """Show user bookings."""
        self.clear_content()
        theme = self.get_theme()
        
        # Header
        header = Frame(self.content_frame, bg=theme["bg"])
        header.pack(fill=X, pady=(0, 20))
        
        Label(header, text="My Bookings",
              font=self.fonts["title"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W)
        
        # Actions
        actions_frame = Frame(self.content_frame, bg=theme["bg"])
        actions_frame.pack(fill=X, pady=(0, 20))
        
        Button(actions_frame, text="🔄 Refresh",
               font=self.fonts["body"],
               bg=theme["accent"], fg="white",
               bd=0, padx=20, pady=8, cursor="hand2",
               command=self.show_bookings_view).pack(side=LEFT, padx=5)
        
        Button(actions_frame, text="📥 Export",
               font=self.fonts["body"],
               bg=theme["success"], fg="white",
               bd=0, padx=20, pady=8, cursor="hand2",
               command=self.export_bookings).pack(side=LEFT, padx=5)
        
        # Bookings table
        table_frame = Frame(self.content_frame, bg=theme["card_bg"],
                           highlightbackground=theme["border"], highlightthickness=1)
        table_frame.pack(fill=BOTH, expand=True)
        
        # Treeview
        columns = ("id", "destination", "date", "people", "package", "price", "status")
        self.bookings_tree = ttk.Treeview(table_frame, columns=columns,
                                          show="headings", height=15)
        
        # Configure columns
        self.bookings_tree.heading("id", text="ID")
        self.bookings_tree.heading("destination", text="Destination")
        self.bookings_tree.heading("date", text="Travel Date")
        self.bookings_tree.heading("people", text="People")
        self.bookings_tree.heading("package", text="Package")
        self.bookings_tree.heading("price", text="Price")
        self.bookings_tree.heading("status", text="Status")
        
        self.bookings_tree.column("id", width=50, anchor=CENTER)
        self.bookings_tree.column("destination", width=150)
        self.bookings_tree.column("date", width=100, anchor=CENTER)
        self.bookings_tree.column("people", width=70, anchor=CENTER)
        self.bookings_tree.column("package", width=80, anchor=CENTER)
        self.bookings_tree.column("price", width=100, anchor=CENTER)
        self.bookings_tree.column("status", width=100, anchor=CENTER)
        
        # Scrollbar
        scrollbar = Scrollbar(table_frame, orient=VERTICAL,
                             command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        self.bookings_tree.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        
        # Action buttons
        btn_frame = Frame(self.content_frame, bg=theme["bg"])
        btn_frame.pack(fill=X, pady=20)
        
        Button(btn_frame, text="🗑 Cancel Booking",
               font=self.fonts["body"],
               bg=theme["danger"], fg="white",
               bd=0, padx=20, pady=8, cursor="hand2",
               command=self.cancel_selected_booking).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="📄 View Details",
               font=self.fonts["body"],
               bg=theme["border"], fg=theme["fg"],
               bd=0, padx=20, pady=8, cursor="hand2",
               command=self.view_booking_details).pack(side=LEFT, padx=5)
        
        # Load data
        self.load_bookings_data()
    
    def load_bookings_data(self):
        """Load bookings into treeview."""
        # Clear existing
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)
        
        bookings = get_user_bookings(self.current_user_id)
        
        for booking in bookings:
            self.bookings_tree.insert("", END, values=(
                booking['id'],
                booking.get('destination_name', 'N/A'),
                booking['travel_date'],
                booking['number_of_people'],
                booking['package_type'],
                f"₹{booking.get('total_price', 0):,.0f}" if booking.get('total_price') else "N/A",
                booking['status'].capitalize()
            ))
    
    def cancel_selected_booking(self):
        """Cancel selected booking."""
        selected = self.bookings_tree.selection()
        
        if not selected:
            messagebox.showerror("Error", "Please select a booking to cancel")
            return
        
        booking_id = self.bookings_tree.item(selected[0])["values"][0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this booking?"):
            if update_booking_status(booking_id, 'cancelled'):
                messagebox.showinfo("Success", "Booking cancelled")
                self.load_bookings_data()
            else:
                messagebox.showerror("Error", "Failed to cancel booking")
    
    def view_booking_details(self):
        """View details of selected booking."""
        selected = self.bookings_tree.selection()
        
        if not selected:
            messagebox.showerror("Error", "Please select a booking to view")
            return
        
        booking_id = self.bookings_tree.item(selected[0])["values"][0]
        booking = get_booking_by_id(booking_id)
        
        if booking:
            theme = self.get_theme()
            
            detail_window = Toplevel(self.root)
            detail_window.title(f"Booking #{booking_id} Details")
            detail_window.geometry("500x500")
            
            container = Frame(detail_window, bg=theme["bg"], padx=30, pady=30)
            container.pack(fill=BOTH, expand=True)
            
            Label(container, text=f"Booking #{booking_id}",
                  font=self.fonts["title"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W)
            
            details = [
                ("Customer", booking.get('customer_name', 'N/A')),
                ("Destination", booking.get('destination_name', 'N/A')),
                ("Package", booking.get('package_type', 'N/A')),
                ("Travel Date", booking.get('travel_date', 'N/A')),
                ("People", booking.get('number_of_people', 'N/A')),
                ("Total Price", f"₹{booking.get('total_price', 0):,.0f}" if booking.get('total_price') else "N/A"),
                ("Status", booking.get('status', 'N/A').capitalize()),
                ("Booking Date", booking.get('booking_date', 'N/A')),
                ("Address", booking.get('customer_address', 'N/A'))
            ]
            
            for label, value in details:
                frame = Frame(container, bg=theme["bg"])
                frame.pack(fill=X, pady=5)
                
                Label(frame, text=f"{label}:", font=self.fonts["body_bold"],
                      bg=theme["bg"], fg=theme["text_secondary"], width=15).pack(side=LEFT)
                
                Label(frame, text=str(value), font=self.fonts["body"],
                      bg=theme["bg"], fg=theme["fg"], wraplength=300).pack(side=LEFT, padx=10)
            
            Button(container, text="Close",
                   font=self.fonts["body"],
                   bg=theme["border"], fg=theme["fg"],
                   bd=0, padx=20, pady=8, cursor="hand2",
                   command=detail_window.destroy).pack(pady=20)
    
    def export_bookings(self):
        """Export bookings to JSON."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"bookings_{self.current_user}.json"
        )
        
        if file_path:
            data = export_user_data(self.current_user_id)
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                messagebox.showinfo("Success", f"Bookings exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    # ==================== TRIP PLANNER VIEW ====================
    
    def show_planner_view(self):
        """Show trip planner."""
        self.clear_content()
        theme = self.get_theme()
        
        # Header
        header = Frame(self.content_frame, bg=theme["bg"])
        header.pack(fill=X, pady=(0, 20))
        
        Label(header, text="Trip Planner",
              font=self.fonts["title"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W)
        
        Label(header, text="Create and manage your trip itineraries",
              font=self.fonts["body"], bg=theme["bg"], fg=theme["text_secondary"]).pack(anchor=W, pady=5)
        
        # Actions
        actions_frame = Frame(self.content_frame, bg=theme["bg"])
        actions_frame.pack(fill=X, pady=(0, 20))
        
        Button(actions_frame, text="➕ Create New Plan",
               font=self.fonts["button"],
               bg=theme["accent"], fg="white",
               bd=0, padx=25, pady=10, cursor="hand2",
               command=self.create_plan_dialog).pack(side=LEFT, padx=5)
        
        # Plans list
        plans_frame = LabelFrame(self.content_frame, text="Your Trip Plans",
                                 font=self.fonts["heading"],
                                 bg=theme["card_bg"], fg=theme["fg"],
                                 padx=20, pady=20)
        plans_frame.pack(fill=BOTH, expand=True)
        
        # Treeview for plans
        columns = ("id", "name", "destination", "dates", "budget")
        self.plans_tree = ttk.Treeview(plans_frame, columns=columns,
                                       show="headings", height=12)
        
        self.plans_tree.heading("id", text="ID")
        self.plans_tree.heading("name", text="Plan Name")
        self.plans_tree.heading("destination", text="Destination")
        self.plans_tree.heading("dates", text="Dates")
        self.plans_tree.heading("budget", text="Budget")
        
        self.plans_tree.column("id", width=50, anchor=CENTER)
        self.plans_tree.column("name", width=200)
        self.plans_tree.column("destination", width=150)
        self.plans_tree.column("dates", width=150, anchor=CENTER)
        self.plans_tree.column("budget", width=100, anchor=CENTER)
        
        scrollbar = Scrollbar(plans_frame, orient=VERTICAL,
                             command=self.plans_tree.yview)
        self.plans_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        self.plans_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Actions
        btn_frame = Frame(self.content_frame, bg=theme["bg"])
        btn_frame.pack(fill=X, pady=20)
        
        Button(btn_frame, text="🗑 Delete Plan",
               font=self.fonts["body"],
               bg=theme["danger"], fg="white",
               bd=0, padx=20, pady=8, cursor="hand2",
               command=self.delete_selected_plan).pack(side=LEFT, padx=5)
        
        # Load data
        self.load_plans_data()
    
    def load_plans_data(self):
        """Load trip plans into treeview."""
        for item in self.plans_tree.get_children():
            self.plans_tree.delete(item)
        
        plans = get_user_trip_plans(self.current_user_id)
        
        for plan in plans:
            dates = f"{plan.get('start_date', 'N/A')} - {plan.get('end_date', 'N/A')}"
            self.plans_tree.insert("", END, values=(
                plan['id'],
                plan['plan_name'],
                plan.get('destination_name', 'Any'),
                dates,
                f"₹{plan.get('budget', 0):,.0f}" if plan.get('budget') else "Not set"
            ))
    
    def create_plan_dialog(self):
        """Show create plan dialog."""
        theme = self.get_theme()
        
        plan_window = Toplevel(self.root)
        plan_window.title("Create Trip Plan")
        plan_window.geometry("500x550")
        plan_window.transient(self.root)
        plan_window.grab_set()
        
        container = Frame(plan_window, bg=theme["bg"], padx=30, pady=30)
        container.pack(fill=BOTH, expand=True)
        
        Label(container, text="Create Trip Plan",
              font=self.fonts["title"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W, pady=(0, 20))
        
        # Form fields
        fields_frame = Frame(container, bg=theme["card_bg"], padx=20, pady=20,
                            highlightbackground=theme["border"], highlightthickness=1)
        fields_frame.pack(fill=X, pady=10)
        
        entries = {}
        
        # Plan name
        Label(fields_frame, text="Plan Name:", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        entries['name'] = create_styled_entry(fields_frame, theme, self.fonts)
        entries['name'].pack(fill=X)
        
        # Destination
        Label(fields_frame, text="Destination (optional):", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        
        entries['destination'] = StringVar()
        dest_options = ["Any"] + [d['name'] for d in get_all_destinations()]
        dest_menu = OptionMenu(fields_frame, entries['destination'], *dest_options)
        dest_menu.config(font=self.fonts["body"], bg=theme["bg"], fg=theme["fg"], width=20)
        dest_menu.pack(fill=X)
        entries['destination'].set("Any")
        
        # Dates
        Label(fields_frame, text="Start Date (DD/MM/YYYY):", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        entries['start_date'] = create_styled_entry(fields_frame, theme, self.fonts)
        entries['start_date'].pack(fill=X)
        
        Label(fields_frame, text="End Date (DD/MM/YYYY):", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        entries['end_date'] = create_styled_entry(fields_frame, theme, self.fonts)
        entries['end_date'].pack(fill=X)
        
        # Budget
        Label(fields_frame, text="Budget (₹):", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        entries['budget'] = create_styled_entry(fields_frame, theme, self.fonts)
        entries['budget'].pack(fill=X)
        
        # Buttons
        btn_frame = Frame(container, bg=theme["bg"])
        btn_frame.pack(fill=X, pady=20)
        
        Button(btn_frame, text="Create Plan",
               font=self.fonts["button"],
               bg=theme["accent"], fg="white",
               bd=0, padx=30, pady=12, cursor="hand2",
               command=lambda: self.process_plan_creation(entries, plan_window)
              ).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Cancel",
               font=self.fonts["body"],
               bg=theme["border"], fg=theme["fg"],
               bd=0, padx=20, pady=10, cursor="hand2",
               command=plan_window.destroy
              ).pack(side=RIGHT, padx=5)
    
    def process_plan_creation(self, entries, window):
        """Process plan creation."""
        name = entries['name'].get().strip()
        dest_name = entries['destination'].get()
        start_date = entries['start_date'].get().strip()
        end_date = entries['end_date'].get().strip()
        budget_str = entries['budget'].get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a plan name")
            return
        
        # Validate dates
        if start_date and not self.validate_date(start_date):
            messagebox.showerror("Error", "Please enter a valid start date (DD/MM/YYYY)")
            return
        
        if end_date and not self.validate_date(end_date):
            messagebox.showerror("Error", "Please enter a valid end date (DD/MM/YYYY)")
            return
        
        # Get destination ID
        dest_id = None
        if dest_name and dest_name != "Any":
            for dest in self.destinations:
                if dest['name'] == dest_name:
                    dest_id = dest['id']
                    break
        
        # Parse budget
        budget = None
        if budget_str:
            try:
                budget = float(budget_str)
            except:
                messagebox.showerror("Error", "Please enter a valid budget")
                return
        
        plan_id = create_trip_plan(
            user_id=self.current_user_id,
            plan_name=name,
            destination_id=dest_id,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            budget=budget
        )
        
        if plan_id:
            messagebox.showinfo("Success", f"Trip plan '{name}' created successfully!")
            window.destroy()
            self.load_plans_data()
        else:
            messagebox.showerror("Error", "Failed to create trip plan")
    
    def delete_selected_plan(self):
        """Delete selected plan."""
        selected = self.plans_tree.selection()
        
        if not selected:
            messagebox.showerror("Error", "Please select a plan to delete")
            return
        
        plan_id = self.plans_tree.item(selected[0])["values"][0]
        plan_name = self.plans_tree.item(selected[0])["values"][1]
        
        if messagebox.askyesno("Confirm", f"Delete plan '{plan_name}'?"):
            if delete_trip_plan(plan_id):
                messagebox.showinfo("Success", "Plan deleted")
                self.load_plans_data()
            else:
                messagebox.showerror("Error", "Failed to delete plan")
    
    # ==================== RECOMMENDATIONS VIEW ====================
    
    def show_recommendations_view(self):
        """Show travel recommendations."""
        self.clear_content()
        theme = self.get_theme()
        
        # Header
        header = Frame(self.content_frame, bg=theme["bg"])
        header.pack(fill=X, pady=(0, 20))
        
        Label(header, text="Travel Recommendations",
              font=self.fonts["title"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W)
        
        Label(header, text="Personalized suggestions for your next adventure",
              font=self.fonts["body"], bg=theme["bg"], fg=theme["text_secondary"]).pack(anchor=W, pady=5)
        
        # Budget filter
        filter_frame = Frame(self.content_frame, bg=theme["card_bg"], padx=20, pady=15,
                            highlightbackground=theme["border"], highlightthickness=1)
        filter_frame.pack(fill=X, pady=(0, 20))
        
        Label(filter_frame, text="Your Budget:", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(side=LEFT, padx=(0, 10))
        
        self.rec_budget_var = StringVar()
        budget_entry = create_styled_entry(filter_frame, theme, self.fonts)
        budget_entry.config(textvariable=self.rec_budget_var, width=15)
        budget_entry.pack(side=LEFT, padx=(0, 10))
        
        Button(filter_frame, text="Get Recommendations",
               font=self.fonts["body"],
               bg=theme["accent"], fg="white",
               bd=0, padx=20, pady=8, cursor="hand2",
               command=self.load_recommendations).pack(side=LEFT, padx=10)
        
        # Recommendations frame
        self.rec_frame = Frame(self.content_frame, bg=theme["bg"])
        self.rec_frame.pack(fill=BOTH, expand=True)
        
        # Load initial recommendations
        self.load_recommendations()
    
    def load_recommendations(self):
        """Load and display recommendations."""
        theme = self.get_theme()
        
        # Clear existing
        for widget in self.rec_frame.winfo_children():
            widget.destroy()
        
        # Get budget from input
        budget = None
        budget_str = self.rec_budget_var.get().strip()
        if budget_str:
            try:
                budget = float(budget_str)
            except:
                pass
        
        # Get recommendations
        recs = get_recommendations(user_id=self.current_user_id, budget=budget)
        
        if recs:
            # Section title
            Label(self.rec_frame, text="Recommended For You",
                  font=self.fonts["heading"], bg=theme["bg"],
                  fg=theme["fg"]).pack(anchor=W, pady=(0, 20))
            
            # Display recommendations
            for dest in recs:
                card = self.create_destination_card(self.rec_frame, dest, compact=True)
                card.pack(fill=X, pady=10)
        else:
            Label(self.rec_frame, text="No recommendations available",
                  font=self.fonts["body"], bg=theme["bg"],
                  fg=theme["text_secondary"]).pack(pady=100)
    
    # ==================== PROFILE VIEW ====================
    
    def show_profile_view(self):
        """Show user profile."""
        self.clear_content()
        theme = self.get_theme()
        
        # Header
        header = Frame(self.content_frame, bg=theme["bg"])
        header.pack(fill=X, pady=(0, 20))
        
        Label(header, text="My Profile",
              font=self.fonts["title"], bg=theme["bg"], fg=theme["fg"]).pack(anchor=W)
        
        # Profile card
        profile_frame = Frame(self.content_frame, bg=theme["card_bg"], padx=40, pady=40,
                             highlightbackground=theme["border"], highlightthickness=1)
        profile_frame.pack(fill=X, pady=20)
        
        # Get user info
        user = get_user_by_id(self.current_user_id)
        
        if user:
            # Avatar
            avatar = Label(profile_frame, text="👤", font=("Segoe UI", 64),
                          bg=theme["card_bg"], fg=theme["accent"])
            avatar.pack(pady=(0, 20))
            
            # User info
            info_items = [
                ("Username", user.get('username', 'N/A')),
                ("Full Name", user.get('full_name', 'Not set')),
                ("Email", user.get('email', 'Not set')),
                ("Phone", user.get('phone', 'Not set')),
                ("Member Since", user.get('created_at', 'N/A'))
            ]
            
            for label, value in info_items:
                frame = Frame(profile_frame, bg=theme["card_bg"])
                frame.pack(fill=X, pady=8)
                
                Label(frame, text=f"{label}:", font=self.fonts["body_bold"],
                      bg=theme["card_bg"], fg=theme["text_secondary"],
                      width=15).pack(side=LEFT)
                
                Label(frame, text=str(value), font=self.fonts["body"],
                      bg=theme["card_bg"], fg=theme["fg"]).pack(side=LEFT, padx=10)
        
        # Preferences section
        prefs_frame = LabelFrame(self.content_frame, text="Preferences",
                                 font=self.fonts["heading"],
                                 bg=theme["card_bg"], fg=theme["fg"],
                                 padx=30, pady=30)
        prefs_frame.pack(fill=X, pady=20)
        
        Label(prefs_frame, text="Preferred Category:", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        
        self.pref_category = StringVar(value="Any")
        cats = ["Any"] + get_destination_categories()
        pref_menu = OptionMenu(prefs_frame, self.pref_category, *cats)
        pref_menu.config(font=self.fonts["body"], bg=theme["bg"], width=20)
        pref_menu.pack(anchor=W, pady=(0, 20))
        
        Label(prefs_frame, text="Budget Range:", font=self.fonts["body_bold"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(anchor=W, pady=(10, 5))
        
        budget_frame = Frame(prefs_frame, bg=theme["card_bg"])
        budget_frame.pack(fill=X, pady=(0, 20))
        
        Label(budget_frame, text="Max:", font=self.fonts["body"],
              bg=theme["card_bg"], fg=theme["fg"]).pack(side=LEFT)
        
        self.pref_budget = create_styled_entry(budget_frame, theme, self.fonts)
        self.pref_budget.pack(side=LEFT, padx=10)
        
        # Save button
        Button(prefs_frame, text="Save Preferences",
               font=self.fonts["button"],
               bg=theme["accent"], fg="white",
               bd=0, padx=30, pady=10, cursor="hand2",
               command=self.save_preferences
              ).pack(anchor=W, pady=20)
    
    def save_preferences(self):
        """Save user preferences."""
        category = self.pref_category.get()
        budget_str = self.pref_budget.get().strip()
        
        budget = None
        if budget_str:
            try:
                budget = float(budget_str)
            except:
                messagebox.showerror("Error", "Please enter a valid budget")
                return
        
        if save_user_preferences(
            self.current_user_id,
            preferred_category=None if category == "Any" else category,
            budget_range_max=budget
        ):
            messagebox.showinfo("Success", "Preferences saved!")
        else:
            messagebox.showerror("Error", "Failed to save preferences")
