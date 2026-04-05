# Expense Tracker

A comprehensive Django-based expense tracking application with budget management, category organization, and detailed analytics.

## Features

### Core Functionality

- **User Authentication**: Secure registration and login system
- **Expense Management**: Add, edit, delete, and categorize expenses
- **Budget Planning**: Set monthly budgets with category-wise allocation
- **Category Management**: Create custom expense categories
- **Dashboard Analytics**: Visual charts and statistics for expenses and budgets
- **Export Options**: Export data to Excel and PDF formats

### Technical Features

- **Responsive Design**: Bootstrap-based UI that works on all devices
- **Real-time Search**: AJAX-powered search functionality
- **Data Visualization**: Interactive charts using Chart.js
- **Database Flexibility**: Supports both MySQL and SQLite databases
- **PDF Reports**: Generate professional PDF reports using ReportLab

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL (optional - SQLite will be used as fallback)

### Setup Instructions

1. **Clone the repository**

    ```bash
    git clone https://github.com/yourusername/expense-tracker.git
    cd expense-tracker
    ```

2. **Create virtual environment**

    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On Linux/Mac
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Database Setup**
    - For MySQL: Create a database and update `.env` file
    - For SQLite: No additional setup required (automatic fallback)

5. **Environment Configuration**
   Create a `.env` file in the root directory:

    ```env
    # For MySQL (optional)
    DB_NAME=your_database_name
    DB_USER=your_mysql_username
    DB_USER_PASSWORD=your_mysql_password
    DB_HOST=localhost

    # Leave empty for SQLite fallback
    ```

6. **Run migrations**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

7. **Create superuser (optional)**

    ```bash
    python manage.py createsuperuser
    ```

8. **Run the development server**

    ```bash
    python manage.py runserver
    ```

9. **Access the application**
   Open your browser and go to: `http://127.0.0.1:8000`

## Usage

### Getting Started

1. **Register**: Create a new account or login with existing credentials
2. **Add Categories**: Create expense categories (e.g., Food, Transport, Entertainment)
3. **Set Budget**: Define monthly budgets for different categories
4. **Track Expenses**: Add daily expenses with proper categorization
5. **View Analytics**: Check dashboard for spending patterns and budget adherence

### Key Features Guide

#### Expense Management

- Navigate to "Expenses" section
- Click "Add Expense" to record new transactions
- Use search functionality to find specific expenses
- Export data to Excel or PDF

#### Budget Planning

- Go to "Budget" section
- Set monthly budget amounts per category
- View budget vs actual spending charts
- Generate budget reports

#### Category Management

- Access "Categories" to create custom expense categories
- Organize expenses by type for better tracking

## Project Structure

```
ExpenseTracker/
├── ExpenseTracker/          # Main Django project
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── authentication/         # User authentication app
├── budget/                 # Budget management app
├── expense/                # Expense tracking app
├── overview/               # Dashboard and analytics app
├── usercategory/           # Category management app
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## API Endpoints

### Authentication

- `POST /authentication/register/` - User registration
- `POST /authentication/login/` - User login
- `POST /authentication/logout/` - User logout

### Expenses

- `GET /` - Expense dashboard
- `POST /add-expenses/` - Add new expense
- `POST /search-expenses/` - Search expenses (AJAX)
- `GET /export_excel/` - Export expenses to Excel
- `GET /export_pdf/` - Export expenses to PDF

### Budget

- `GET /budget/` - Budget dashboard
- `POST /budget/add-budget/` - Add budget
- `GET /budget/stats/` - Budget statistics
- `GET /budget/export_pdf/` - Export budget to PDF

### Categories

- `GET /usercategory/` - Category management
- `POST /usercategory/add-category/` - Add category

## Database Schema

### Models Overview

- **User**: Django's built-in user model
- **Expense**: Amount, description, category, date, owner
- **Budget**: Monthly budget with category allocations
- **BudgetAmount**: Category-wise budget breakdown
- **Category**: User-defined expense categories

## Deployment

### Production Setup

1. Set `DEBUG = False` in settings.py
2. Configure production database
3. Set up static files serving
4. Configure email settings for user activation
5. Use a production WSGI server (gunicorn)

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
DB_NAME=production_db
DB_USER=production_user
DB_USER_PASSWORD=secure_password
DB_HOST=production_host
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

**Database Connection Error**

- Ensure MySQL is running (if using MySQL)
- Check `.env` file configuration
- Falls back to SQLite automatically

**PDF Export Issues**

- Ensure ReportLab is installed: `pip install reportlab`
- Check file permissions for PDF generation

**Static Files Not Loading**

- Run `python manage.py collectstatic` for production
- Ensure DEBUG=True for development

**Email Not Working**

- Configure EMAIL\_\* settings in `.env`
- Use a service like Gmail or SendGrid

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Django web framework
- Frontend styling with Bootstrap
- Charts powered by Chart.js
- PDF generation using ReportLab
- Icons from various free icon libraries

## Support

For support, email support@expensetracker.com or create an issue in the GitHub repository.

---

**Happy expense tracking!** 📊💰
