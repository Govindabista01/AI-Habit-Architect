# AI Habit Architect

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Django-4.2-green.svg" alt="Django">
  <img src="https://img.shields.io/badge/ML-scikit--learn-orange.svg" alt="scikit-learn">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

> An intelligent habit tracking system powered by machine learning that predicts your habit completion probability and provides personalized recommendations to help you build lasting habits.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [ML Pipeline](#ml-pipeline)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

AI Habit Architect is a comprehensive habit tracking platform that combines traditional habit tracking with artificial intelligence. The system analyzes your behavioral patterns and uses machine learning to predict the likelihood of completing habits, providing intelligent recommendations based on your unique patterns.

### Key Objectives

- **Behavior Analysis**: Track and analyze habit completion patterns over time
- **AI Predictions**: Use machine learning to predict daily habit completion probability
- **Personalized Recommendations**: Receive category-specific, data-driven tips
- **Visual Analytics**: Beautiful dashboards with charts and heatmaps
- **Streak Management**: Track current and longest streaks with automatic updates

---

## Features

### 🔐 User Management
- User registration with email and password
- Secure login/logout functionality
- Password validation (minimum length, complexity)
- Session management

### ✅ Habit Management
- Create habits with custom names and descriptions
- 7 category types: Health, Productivity, Learning, Mindfulness, Social, Finance, Other
- Configurable frequency (1-7 times per week)
- Motivation score (1-10 scale)
- Difficulty level (1-10 scale)
- Soft delete (deactivation) of habits
- Edit existing habits

### 📊 Daily Tracking
- One-click habit completion toggle
- Date-based record tracking
- Notes for each completion
- Automatic streak calculation
- "Fresh Start" monthly completion rate logic

### 🤖 AI-Powered Predictions
- Logistic Regression model for completion prediction
- Probability scores (0-100%)
- Confidence levels (High/Medium/Low)
- 9 features used for prediction:
  - Habit frequency per week
  - Current streak length
  - Completed days in last 7
  - Missed days in last 7
  - 30-day completion rate
  - Previous day completion status
  - Motivation score
  - Habit difficulty
  - Weekend indicator

### 💡 Personalized Recommendations
- Category-specific tips based on probability
- Risk level assessment (Low/Medium/High/Critical)
- 5 personalized tips per prediction
- Dynamic recommendations based on:
  - Current streak
  - Recent performance
  - Motivation level
  - Difficulty assessment

### 📈 Analytics Dashboard
- **Overall Statistics**: Total habits, completions, active streaks
- **30-Day Completion Rate**: Aggregate completion percentage
- **7-Day Line Chart**: Daily completion trends
- **Category Breakdown**: Pie chart showing habit distribution
- **30-Day Heatmap**: Visual calendar showing activity
- **Top Performers**: Best performing habits list
- **Struggling Habits**: Habits needing attention

---

## Tech Stack

### Backend
- **Framework**: Django 4.2
- **Language**: Python 3.10+
- **REST API**: Django REST Framework 3.16

### Database
- **Primary**: MySQL 8.0
- **ORM**: Django ORM

### Machine Learning
- **Framework**: scikit-learn 1.8.0
- **Algorithm**: Logistic Regression
- **Preprocessing**: StandardScaler, One-Hot Encoding

### Data Processing
- **Library**: pandas 3.0.0, numpy 2.4.1
- **Serialization**: joblib 1.5.3

### Frontend
- HTML5 templates
- CSS3 with custom styling
- Chart.js for visualizations
- Responsive design

---

## Project Structure

```
AI_Habit_Architect/
├── README.md                     # Project documentation
├── .gitignore                    # Git ignore rules
│
├── backend/                      # Django backend application
│   ├── manage.py                 # Django management script
│   ├── requirements.txt          # Python dependencies
│   │
│   ├── habit_architect_project/  # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py           # Configuration settings
│   │   ├── urls.py               # Root URL configuration
│   │   ├── wsgi.py               # WSGI application
│   │   └── asgi.py               # ASGI application
│   │
│   ├── accounts/                  # User authentication app
│   │   ├── models.py              # Custom user model
│   │   ├── views.py               # Login/Register views
│   │   ├── urls.py                # Account URLs
│   │   └── admin.py               # Admin configuration
│   │
│   ├── habits/                    # Habit management app
│   │   ├── models.py              # Habit, HabitRecord models
│   │   ├── views.py               # Dashboard, CRUD views
│   │   ├── urls.py                # Habit URLs
│   │   ├── serializers.py         # DRF serializers
│   │   ├── api_views.py           # API endpoints
│   │   ├── api_urls.py            # API URLs
│   │   ├── admin.py               # Admin configuration
│   │   └── management/commands/   # Custom Django commands
│   │       ├── generate_dummy_data.py
│   │       └── retrain_ai_model.py
│   │
│   ├── predictions/               # AI predictions app
│   │   ├── models.py              # Prediction, Recommendation models
│   │   ├── views.py               # Prediction views
│   │   ├── urls.py                # Prediction URLs
│   │   ├── utils.py               # Prediction utilities
│   │   ├── admin.py               # Admin configuration
│   │   └── templatetags/           # Custom template tags
│   │
│   ├── analytics/                 # Analytics dashboard app
│   │   ├── models.py              # Analytics models
│   │   ├── views.py               # Dashboard analytics views
│   │   ├── urls.py                # Analytics URLs
│   │   └── admin.py               # Admin configuration
│   │
│   ├── templates/                 # HTML templates
│   │   ├── base.html              # Base template
│   │   ├── home.html              # Home page
│   │   ├── accounts/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── habits/
│   │   │   ├── dashboard.html
│   │   │   ├── create_habit.html
│   │   │   └── habit_detail.html
│   │   ├── analytics/
│   │   │   └── dashboard.html
│   │   └── predictions/
│   │       ├── predict.html
│   │       └── history.html
│   │
│   └── venv/                      # Virtual environment (gitignored)
│
└── ml_models/                      # Machine learning module
    ├── train_model.py             # Model training script
    ├── preprocess_data.py          # Data preprocessing
    ├── prediction.py               # Prediction engine
    │
    ├── data/                       # Training data
    │   └── habit_architect_dataset.csv
    │
    └── trained/                    # Trained model artifacts
        ├── habit_predictor.pkl     # Trained model
        ├── scaler.pkl              # Feature scaler
        └── feature_names.pkl        # Feature names list
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/AI_Habit_Architect.git
cd AI_Habit_Architect
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv backend/venv

# Activate on Windows
backend\venv\Scripts\activate

# Activate on macOS/Linux
source backend/venv/bin/activate
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Set Up MySQL Database

```sql
-- Create database
CREATE DATABASE habit_architect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'habit_user'@'localhost' IDENTIFIED BY 'HabitPass123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON habit_architect_db.* TO 'habit_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;
```

### Step 5: Run Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

---

## Configuration

### Environment Variables (Optional)

Create a `.env` file in the `backend/` directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=habit_architect_db
DB_USER=habit_user
DB_PASSWORD=HabitPass123!
```

### Django Settings

The main configuration is in [`backend/habit_architect_project/settings.py`](backend/habit_architect_project/settings.py:1):

```python
# Key Settings
SECRET_KEY = 'django-insecure-your-secret-key-change-this-in-production'
DEBUG = True  # Set to False in production
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'habit_architect_db',
        'USER': 'habit_user',
        'PASSWORD': 'HabitPass123!',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

## Running the Application

### 1. Start the Development Server

```bash
cd backend
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

### 2. Access the Application

| Page | URL |
|------|-----|
| Home | `/` |
| Login | `/accounts/login/` |
| Register | `/accounts/register/` |
| Dashboard | `/habits/dashboard/` |
| Analytics | `/analytics/dashboard/` |
| Predictions | `/predictions/predict/` |
| Admin | `/admin/` |

### 3. Generate Sample Data (Optional)

```bash
python manage.py generate_dummy_data
```

This creates test users and habits with historical data.

---

## ML Pipeline

### Overview

The machine learning pipeline uses Logistic Regression to predict whether a user will complete a specific habit on a given day.

### Features Used

| Feature | Description | Type |
|---------|-------------|------|
| `habit_frequency_per_week` | How often the habit should be performed | Numerical |
| `streak_length` | Current consecutive days of completion | Numerical |
| `completed_days_last_7` | Completions in the last 7 days | Numerical |
| `missed_days_last_7` | Misses in the last 7 days | Numerical |
| `completion_rate_last_30` | 30-day completion rate (0-1) | Numerical |
| `previous_day_completed` | Whether completed yesterday (0/1) | Numerical |
| `motivation_score` | User's motivation level (1-10) | Numerical |
| `habit_difficulty` | Difficulty level (1-10) | Numerical |
| `is_weekend` | Whether it's a weekend (0/1) | Numerical |
| `habit_category_*` | One-hot encoded categories | Categorical |
| `day_of_week_*` | One-hot encoded day of week | Categorical |

### Training the Model

```bash
cd ml_models
python train_model.py
```

**Output:**
```
============================================================
 AI HABIT ARCHITECT - MODEL TRAINING
============================================================

 Step 1: Preprocessing data...
 Step 2: Training model...
 Step 3: Evaluating model...
 Step 4: Analyzing features...
 Step 5: Saving model...
 Step 6: Final Summary

 Model Quality: GOOD/EXCELLENT
 Training Accuracy: XX.XX%
 Testing Accuracy: XX.XX%
```

### Re-training with Live Data

```bash
cd backend
python manage.py retrain_ai_model
```

This command:
1. Exports all habit records from the database
2. Preprocesses the data
3. Trains a new model
4. Evaluates performance
5. Saves updated model files

### Prediction API

```python
from ml_models.prediction import HabitPredictor

predictor = HabitPredictor()

habit_data = {
    'habit_name': 'Morning Run',
    'habit_category': 'health',
    'habit_frequency_per_week': 7,
    'streak_length': 12,
    'completed_days_last_7': 6,
    'missed_days_last_7': 1,
    'completion_rate_last_30': 0.85,
    'previous_day_completed': 1,
    'motivation_score': 8,
    'habit_difficulty': 6
}

result = predictor.predict(habit_data)
recommendation = predictor.get_recommendation(result, habit_data)

print(f"Probability: {result['probability_percentage']}")
print(f"Confidence: {result['confidence']}")
print(f"Risk Level: {recommendation['risk_level']}")
print(f"Message: {recommendation['message']}")
print("Tips:", recommendation['tips'])
```

---

## API Documentation

### REST Framework Endpoints

The application includes RESTful API endpoints for mobile app integration.

#### Habits API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/habits/` | GET | List all user's habits |
| `/api/habits/` | POST | Create a new habit |
| `/api/habits/{id}/` | GET | Get habit details |
| `/api/habits/{id}/` | PUT | Update a habit |
| `/api/habits/{id}/` | DELETE | Delete a habit |
| `/api/habits/{id}/track/` | POST | Track habit completion |

#### Predictions API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/predictions/predict/` | POST | Get AI prediction for a habit |
| `/api/predictions/history/` | GET | Get prediction history |

### Authentication

All API endpoints require authentication. Include session cookie or use token authentication.

---

## Database Schema

### Users Table (Django Auth)

Standard Django user model with:
- username, email, password
- first_name, last_name
- date_joined, last_login

### Habits Table

```sql
CREATE TABLE habits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT FOREIGN KEY REFERENCES auth_user(id),
    name VARCHAR(200),
    description TEXT,
    category VARCHAR(50),
    frequency_per_week INT,
    motivation_score INT,
    difficulty_level INT,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    total_completions INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Habit Records Table

```sql
CREATE TABLE habit_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    habit_id INT FOREIGN KEY REFERENCES habits(id),
    date DATE,
    completed BOOLEAN,
    notes TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    UNIQUE(habit_id, date)
);
```

### Predictions Table

```sql
CREATE TABLE predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    habit_id INT FOREIGN KEY REFERENCES habits(id),
    prediction_date DATE,
    will_complete BOOLEAN,
    completion_probability FLOAT,
    confidence_level VARCHAR(20),
    created_at DATETIME
);
```

### Recommendations Table

```sql
CREATE TABLE recommendations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prediction_id INT FOREIGN KEY REFERENCES predictions(id),
    message TEXT,
    tips JSON,
    risk_level VARCHAR(20),
    created_at DATETIME
);
```

### Model Metadata Table

```sql
CREATE TABLE model_metadata (
    id INT PRIMARY KEY AUTO_INCREMENT,
    last_trained_at DATETIME,
    record_count_at_training INT,
    accuracy_achieved FLOAT
);
```

---

## Advanced Features

### Streak Calculation Logic

The system uses an intelligent streak algorithm:

```python
def update_streak(habit):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    completed_today = habit.records.filter(date=today, completed=True).exists()
    completed_yesterday = habit.records.filter(date=yesterday, completed=True).exists()
    
    if completed_today:
        if completed_yesterday:
            habit.current_streak += 1
        else:
            habit.current_streak = 1
    elif not completed_yesterday:
        habit.current_streak = 0
```

### Fresh Start Monthly Logic

Completion rate is calculated from the 1st of the current month (not historical creation date) to encourage fresh starts:

```python
def get_completion_rate_30_days(habit):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    actual_start = max(start_of_month, habit.created_at.date())
    
    denominator = (today - actual_start).days + 1
    completed = habit.records.filter(
        date__gte=actual_start, completed=True
    ).count()
    
    return completed / denominator
```

### Confidence Level Calculation

```python
def calculate_confidence(probability):
    if probability >= 0.8 or probability <= 0.2:
        return 'High'
    elif probability >= 0.6 or probability <= 0.4:
        return 'Medium'
    else:
        return 'Low'
```

### Category-Specific Recommendations

The AI generates different tips based on habit category:

| Category | Example Habits | Key Focus Areas |
|----------|---------------|-----------------|
| Health | Exercise, Diet | Physical preparation, Recovery |
| Productivity | Work tasks, Planning | Focus techniques, Time management |
| Learning | Study, Reading | Active recall, Environment |
| Mindfulness | Meditation, Journaling | Mental state, Stress relief |
| Social | Calling, Events | Connection, Accountability |
| Finance | Budgeting, Saving | Awareness, Automation |

---

## Troubleshooting

### Common Issues

#### 1. MySQL Connection Error

```
Error: Access denied for user 'habit_user'@'localhost'
```

**Solution:**
```bash
# Check MySQL user exists
mysql -u root -p
SELECT user FROM mysql.user;

# Recreate user if needed
DROP USER 'habit_user'@'localhost';
CREATE USER 'habit_user'@'localhost' IDENTIFIED BY 'HabitPass123!';
GRANT ALL ON habit_architect_db.* TO 'habit_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 2. Model Files Not Found

```
Error: Model files not found. Run retrain_ai_model.py or train_model.py first.
```

**Solution:**
```bash
cd ml_models
python train_model.py
```

#### 3. Migration Errors

```bash
# Reset migrations (development only!)
cd backend
rm -rf habits/migrations/0*.py
rm -rf predictions/migrations/0*.py
rm -rf analytics/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

#### 4. Static Files Not Loading

```bash
cd backend
python manage.py collectstatic
```

### Performance Tips

1. **Database Indexing**: Add indexes to frequently queried columns
2. **Caching**: Use Django's caching framework for analytics
3. **Lazy Loading**: Load prediction results only when needed
4. **Model Retraining**: Retrain monthly with accumulated data

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Use meaningful commit messages

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- ML powered by [scikit-learn](https://scikit-learn.org/)
- Charts by [Chart.js](https://www.chartjs.org/)
- Inspired by habit tracking best practices from behavioral science

---

## Contact

- **Author**: Govinda
- **Email**: govinda@example.com
- **GitHub**: [Your GitHub Profile](https://github.com/yourusername)

---

<div align="center">
  <p>Made with ❤️ and 🤖 for better habits</p>
  <p>© 2024 AI Habit Architect</p>
</div>
