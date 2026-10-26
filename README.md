# Travel Management System

<p align="center">
  <img src="assets/images/silicon.png" alt="Travel Management System Logo" width="120">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Tkinter-GUI-green" alt="Tkinter">
  <img src="https://img.shields.io/badge/SQLite-Database-orange?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
  <img src="https://github.com/Rajat-Pandya/travel_management_system/actions/workflows/ci.yml/badge.svg" alt="CI">
</p>

## Overview

A professional desktop application for managing travel bookings with a modern, polished UI. Built with Python, Tkinter, and SQLite, this application demonstrates clean code architecture, modern UI/UX design principles, and comprehensive database management.

<!--
<p align="center">
  <img src="screenshots/demo-home.png" alt="Home Screen" width="600">
</p>
-->

## Features

### Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| **User Authentication** | Secure login/signup with password hashing | ✅ Complete |
| **Destination Management** | Browse destinations with images and descriptions | ✅ Complete |
| **Search & Filtering** | Real-time search, category, and budget filters | ✅ Complete |
| **Booking System** | Book trips with package selection and price calculation | ✅ Complete |
| **Trip Planner** | Create and manage trip itineraries | ✅ Complete |
| **Reviews & Ratings** | Rate destinations and leave reviews | ✅ Complete |
| **Recommendations** | Personalized travel recommendations | ✅ Complete |
| **Export Functionality** | Export bookings to JSON | ✅ Complete |
| **Dark/Light Mode** | Modern theme switching | ✅ Complete |

### Additional Features

- 📊 **Dashboard Statistics** - Track bookings, plans, and spending
- 🔍 **Advanced Search** - Search by name, category, or budget
- 📅 **Date Validation** - Smart date format validation
- 💰 **Price Calculation** - Automatic price calculation based on package tier
- 📱 **Responsive UI** - Modern card-based design with smooth transitions
- 🔒 **Security** - Password hashing with salt for secure storage

<!--
## Screenshots

### Login Screen
Modern split-screen design with branding

### Dashboard
<p align="center">
  <img src="screenshots/dashboard-light.png" alt="Dashboard - Light Mode" width="45%">
  <img src="screenshots/dashboard-dark.png" alt="Dashboard - Dark Mode" width="45%">
</p>

### Destinations
Browse destinations with filtering capabilities

### Booking Form
Intuitive booking with real-time price preview
-->

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** (developed on 3.13) | Core language |
| **Tkinter** | GUI framework |
| **Pillow** | Image processing |
| **SQLite** | Database |
| **ttk** | Themed widgets |

## Installation

### Prerequisites

- Python 3.10 or higher (developed on 3.13)
- pip package manager

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/travel-management-system.git
cd travel-management-system
```

2. **Create virtual environment (optional but recommended)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python src/main.py
```

## Project Structure

```
travel_management_system/
├── assets/
│   ├── icons/              # Application icons
│   └── images/             # Destination images
│       ├── Goa/
│       ├── Mumbai/
│       └── Sikkim/
├── database/               # Local SQLite database directory
├── src/
│   ├── main.py            # Entry point
│   ├── database.py        # Database layer with context manager
│   ├── ui.py              # Main UI class
│   ├── ui_components.py   # Reusable UI components
│   └── ui_views.py        # View implementations
├── tests/                 # Automated unit and regression test suite
├── screenshots/           # Application screenshots
├── .github/
│   └── workflows/ci.yml   # GitHub Actions CI workflow
├── .gitignore
├── LICENSE
├── pytest.ini
├── README.md
├── requirements.txt       # Core runtime dependencies
└── requirements-dev.txt   # Development dependencies
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE,
    full_name TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1
);
```

### Destinations Table
```sql
CREATE TABLE destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    category TEXT,
    base_price REAL,
    rating REAL DEFAULT 0.0,
    image_path TEXT,
    tags TEXT,
    is_active INTEGER DEFAULT 1
);
```

### Bookings Table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    destination_id INTEGER,
    customer_name TEXT NOT NULL,
    package_type TEXT,
    travel_date TEXT,
    number_of_people INTEGER DEFAULT 1,
    total_price REAL,
    status TEXT DEFAULT 'pending',
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage Guide

### Getting Started

1. **Launch the application**
   ```bash
   python src/main.py
   ```

2. **Create an account**
   - Click "Sign Up" on the login screen
   - Fill in your details (username, full name, email, phone, password)
   - Click "Create Account"

3. **Sign in**
   - Use your registered credentials from sign up to log in

### Booking a Trip

1. Navigate to **Destinations** from the sidebar
2. Use filters to find your preferred destination
3. Click "Book Now" or "View Details"
4. Fill in:
   - Full Name
   - Travel Date (DD/MM/YYYY)
   - Number of People
   - Package Type (Silver/Golden/Diamond)
   - Address
5. View real-time price calculation
6. Click "Confirm Booking"

### Managing Bookings

1. Go to **My Bookings** from the sidebar
2. View all your bookings in the table
3. Click on a booking and "View Details" to see full information
4. Use "Cancel Booking" to cancel a reservation
5. Export your bookings using "Export" button

### Trip Planner

1. Navigate to **Trip Planner**
2. Click "Create New Plan"
3. Enter:
   - Plan name
   - Destination (optional)
   - Start and end dates
   - Budget
4. Save your plan

### Recommendations

1. Go to **Recommendations**
2. Set your budget limit
3. Click "Get Recommendations"
4. Browse personalized destination suggestions

### Switching Themes

- Click the **🌓** (sun/moon) icon in the sidebar to toggle between Light and Dark modes

## Package Pricing

| Package | Multiplier | Description |
|---------|------------|-------------|
| **Silver** | 1.0x | Basic package with standard amenities |
| **Golden** | 1.5x | Premium package with enhanced experiences |
| **Diamond** | 2.0x | Luxury package with exclusive services |

**Price Formula**: `Base Price × Package Multiplier × Number of People`

## Code Architecture

### Design Patterns
- **MVC Pattern**: Separation of Model (database), View (UI), and Controller (logic)
- **Singleton**: Database manager as singleton
- **Mixin**: Views separated into mixin classes

### Key Components

1. **database.py**: Centralized database operations
   - Parameterized queries (SQL injection prevention)
   - Password hashing with salt
   - Context managers for database connection handling

2. **ui.py**: Main application class
   - Theme management
   - Navigation handling
   - State management

3. **ui_views.py**: View implementations
   - Destinations view
   - Bookings view
   - Trip planner view
   - Profile view

4. **ui_components.py**: Reusable components
   - Themed entry widgets
   - Stat cards
   - Scrollable frames

## Security Features

- ✅ Password hashing with PBKDF2
- ✅ Salt generation for each password
- ✅ Parameterized SQL queries
- ✅ Input validation
- ✅ Session management

## Performance

- Lazy loading of images
- Efficient database queries
- Minimal memory footprint
- Smooth UI transitions

## Testing

Automated testing is implemented using `pytest`. The test suite runs against isolated temporary SQLite databases without modifying local database files or requiring a display environment:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run the test suite
pytest
```

### Code Quality & Linting

```bash
# Code formatting check
black --check src/

# Linting
flake8 src/
```

## Roadmap / Known Limitations

- **Date Storage Format (GAP-010)**: Travel dates are currently stored as `DD/MM/YYYY` text strings rather than ISO 8601 (`YYYY-MM-DD`), preventing native database-level chronological sorting and comparison.
- **Tag Search Query (GAP-009)**: Destination tag search uses SQL `IN` against comma-separated string records, which does not match partial or multi-tag combinations.
- **Main Thread Execution (GAP-008)**: Database queries and Pillow image scaling execute synchronously on the Tkinter GUI thread without background worker threads.
- **Structured Logging**: Diagnostic output relies on console `print()` calls rather than Python's standard `logging` module.
- **Accessibility**: Lacks screen reader accessibility labels, tab key focus indicators, and high-contrast theme shortcuts.
- **Admin Features**: No dedicated administrator GUI dashboard or RBAC; administrative queries reside only in the database layer.
- **Local-Only Database**: Data is stored in a local SQLite file without cloud synchronization or multi-user network support.

## Credits

<!-- TODO: image and icon sources -->

## Future Enhancements

- [ ] Payment gateway integration
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Mobile responsive design
- [ ] Cloud database sync
- [ ] AI-powered recommendations
- [ ] Social sharing features

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Icons and images sourced from open-source collections
- Inspired by modern travel booking platforms
- Built as a portfolio project demonstrating Python GUI development

## Contact

Your Name - [@Rajat-Pandya](https://github.com/Rajat-Pandya) - rajatkpandya3451@gmail.com

Project Link: [https://github.com/yourusername/travel-management-system](https://github.com/yourusername/travel-management-system)

---

<p align="center">
  ⭐ Star this repo if you found it helpful!
</p>
