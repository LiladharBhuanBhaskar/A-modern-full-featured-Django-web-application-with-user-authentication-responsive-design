# MyProject - Django Web Application

A modern, full-featured Django web application with user authentication, responsive design, and a beautiful UI.

## Features

- ✅ **User Authentication**: Secure signup, login, and logout with password hashing
- ✅ **Contact Form**: Store contact messages in the database
- ✅ **Responsive Design**: Mobile-first design using Bootstrap 5
- ✅ **Modern UI**: Beautiful, gradient-based design with smooth animations
- ✅ **Protected Routes**: Dashboard accessible only after login
- ✅ **Form Validation**: Client and server-side validation with error messages
- ✅ **CSRF Protection**: Built-in Django CSRF protection

## Project Structure

```
.
├── manage.py
├── requirements.txt
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── main/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── forms.py
    ├── views.py
    ├── urls.py
    └── templates/
        └── main/
            ├── base.html
            ├── home.html
            ├── about.html
            ├── contact.html
            ├── dashboard.html
            ├── login.html
            └── signup.html
```

## Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Open your browser and navigate to `http://127.0.0.1:8000/`

## Pages

- **Home** (`/`): Modern hero section with CTA buttons
- **About** (`/about/`): Project information and mission section
- **Contact** (`/contact/`): Contact form that stores messages in the database
- **Dashboard** (`/dashboard/`): Protected page accessible only after login
- **Sign Up** (`/signup/`): User registration with email and password
- **Login** (`/login/`): User authentication
- **Logout** (`/logout/`): User logout

## Admin Panel

Access the Django admin panel at `http://127.0.0.1:8000/admin/` to:
- View and manage contact messages
- Manage users
- Access other admin features

## Security Features

- Password hashing using Django's built-in authentication
- CSRF protection on all forms
- Session-based authentication
- Secure password validation
- Email uniqueness validation

## Technologies Used

- **Backend**: Django 4.2+
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Icons**: Bootstrap Icons
- **Database**: SQLite (default, can be changed in settings.py)

## Customization

### Changing the Secret Key

Before deploying to production, change the `SECRET_KEY` in `myproject/settings.py`:

```python
SECRET_KEY = 'your-secret-key-here'
```

### Database Configuration

To use a different database (PostgreSQL, MySQL, etc.), update the `DATABASES` setting in `myproject/settings.py`.

## License

This project is open source and available for educational purposes.
