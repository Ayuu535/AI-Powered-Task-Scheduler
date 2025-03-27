"""
This script modifies the necessary files to run with SQLite instead of PostgreSQL.
Run this script once to convert the project for local development.
"""

import os
import re

def modify_app_py():
    """Modify app.py to use SQLite instead of PostgreSQL"""
    with open('app.py', 'r') as file:
        content = file.read()
    
    # Replace database configuration
    content = content.replace(
        'app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")',
        'app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taskmaster.db"'
    )
    
    with open('app.py', 'w') as file:
        file.write(content)
    
    print("✓ Modified app.py to use SQLite")

def create_env_file():
    """Create a .env file with the necessary environment variables"""
    env_content = """SESSION_SECRET=local_development_secret_key
"""
    
    with open('.env', 'w') as file:
        file.write(env_content)
    
    print("✓ Created .env file with session secret")

def modify_main_py():
    """Modify main.py to load environment variables from .env file"""
    with open('main.py', 'r') as file:
        content = file.read()
    
    if 'dotenv' not in content:
        # Add dotenv import
        new_content = """from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from app import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
"""
        with open('main.py', 'w') as file:
            file.write(new_content)
        
        print("✓ Modified main.py to load .env file")
    else:
        print("✓ main.py already configured for .env")

def create_requirements_txt():
    """Create a requirements.txt file for easy installation"""
    requirements = """flask==2.3.3
flask-login==0.6.2
flask-sqlalchemy==3.1.1
flask-wtf==1.2.1
email-validator==2.1.0
python-dotenv==1.0.0
werkzeug==2.3.7
"""
    
    with open('requirements.txt', 'w') as file:
        file.write(requirements)
    
    print("✓ Created requirements.txt for easy dependency installation")

def create_readme():
    """Create a README.md file with setup instructions"""
    readme = """# TaskMaster - Task Management Application

A web-based task management application that uses the Earliest Deadline First (EDF) algorithm for optimal task prioritization.

## Features

- User authentication (register, login, profile management)
- Task management (create, complete, delete tasks)
- Task prioritization using EDF algorithm
- Dark mode toggle
- Responsive design

## Local Setup Instructions

1. Clone this repository or extract the downloaded ZIP file

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   
   # On Windows:
   venv\\Scripts\\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python main.py
   ```

5. Access the application at http://localhost:5000

## Database

This local version uses SQLite for simplicity. The database file will be created as `taskmaster.db` in the project directory.

## Dark Mode

The application includes a dark mode toggle that remembers your preference using local storage.

## Task Prioritization

Tasks are prioritized using the Earliest Deadline First (EDF) algorithm, which sorts tasks based on their deadlines. Tasks with earlier deadlines appear first in the list.
"""
    
    with open('README.md', 'w') as file:
        file.write(readme)
    
    print("✓ Created README.md with setup instructions")

def main():
    print("Converting TaskMaster to use SQLite for local development...\n")
    
    modify_app_py()
    create_env_file()
    modify_main_py()
    create_requirements_txt()
    create_readme()
    
    print("\nConversion complete! Follow these steps to run the application locally:")
    print("1. Create and activate a virtual environment:")
    print("   python -m venv venv")
    print("   venv\\Scripts\\activate (Windows) or source venv/bin/activate (macOS/Linux)")
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("3. Run the application:")
    print("   python main.py")
    print("4. Access the application at http://localhost:5000")

if __name__ == "__main__":
    main()