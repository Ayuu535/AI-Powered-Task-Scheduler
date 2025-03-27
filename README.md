# TaskMaster - Task Management Application

A web-based task management application that uses the Earliest Deadline First (EDF) algorithm for optimal task prioritization.

## Features

- User authentication (register, login, profile management)
- Task management (create, complete, delete tasks)
- Task prioritization using EDF algorithm
- Dark mode toggle
- Responsive design

## Local Setup Instructions

1. Download and extract the ZIP file from this project.

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install flask flask-login flask-sqlalchemy flask-wtf email-validator
   ```

4. Run the SQLite version of the application:
   ```
   python sqlite_main.py
   ```

5. Access the application at http://localhost:5000

## Database

The local version uses SQLite for simplicity. The database file will be created as `taskmaster.db` in the project directory when you first run the application.

## Using the Application

1. Register a new account
2. Log in with your credentials
3. Add tasks with deadlines
4. View, complete, and delete tasks as needed
5. Toggle between light and dark mode using the icon in the navbar

## Task Prioritization

Tasks are prioritized using the Earliest Deadline First (EDF) algorithm, which sorts tasks based on their deadlines. Tasks with earlier deadlines appear first in the list.

## Project Structure

- `sqlite_app.py`: Main application file with all routes and SQLite configuration
- `sqlite_main.py`: Entry point for running the application
- `forms.py`: Form definitions using Flask-WTF
- `utils.py`: Utility functions including the EDF algorithm
- `templates/`: HTML templates
- `static/`: CSS and JavaScript files