# Incentive Management System

A Django-based web application for calculating and managing employee incentives based on performance metrics, targets, and various bonus structures.

## Features

- Employee performance tracking
- Incentive calculation based on configurable slabs
- Target management and achievement tracking
- Load growth bonus calculations
- Excel data import/export functionality
- Admin dashboard for managing incentive rules
- User authentication and role-based access

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package installer)
- Git

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd incentive-project
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### PostgreSQL Setup
1. Install PostgreSQL if not already installed
2. Create a database named `erp_db`
3. Create a user with appropriate permissions

```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE erp_db;
CREATE USER postgres WITH PASSWORD 'root';
GRANT ALL PRIVILEGES ON DATABASE erp_db TO postgres;
```

### 5. Environment Configuration

The project uses environment variables for configuration. Update the `.env` file with your settings:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://username:password@localhost:5432/erp_db
```

**Note:** For production, set `DEBUG=False` and use a strong, unique secret key.

### 6. Database Migration

```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Collect Static Files (For Production)

```bash
python manage.py collectstatic
```

## Running the Application

### Development Server

```bash
cd src
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

### Production Deployment

For production deployment, consider using:
- Gunicorn as WSGI server
- Nginx as reverse proxy
- PostgreSQL as database
- Environment-specific settings

## Project Structure

```
src/
├── config/          # Django project configuration
├── users/           # User management app
├── employees/       # Employee and performance models
├── dashboard/       # Dashboard views and templates
├── commons/         # Shared utilities and services
└── manage.py        # Django management script
```

## Key Applications

- **users**: Custom user model and authentication
- **employees**: Employee data, performance records, incentive rules
- **dashboard**: Web interface for data management and reporting
- **commons**: Shared utilities for calculations and services

## Usage

1. **Admin Access**: Visit `/admin/` to access Django admin panel
2. **Dashboard**: Main application interface for managing incentives
3. **Excel Import**: Upload employee data via Excel files
4. **Reports**: Generate incentive reports and calculations

## Development

### Running Tests

```bash
cd src
python manage.py test
```

### Database Reset (Development Only)

```bash
cd src
python manage.py flush
python manage.py migrate
```

### Creating New Migrations

```bash
cd src
python manage.py makemigrations app_name
python manage.py migrate
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Verify PostgreSQL is running and credentials are correct
2. **Migration Issues**: Try `python manage.py migrate --fake-initial` for initial setup
3. **Static Files**: Run `python manage.py collectstatic` if CSS/JS not loading
4. **Permission Errors**: Ensure proper database user permissions

### Environment Variables

Make sure all required environment variables are set:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DATABASE_URL`: PostgreSQL connection string

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Add your license information here]
