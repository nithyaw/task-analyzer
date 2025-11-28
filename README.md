Smart Task Analyzer

A mini full-stack application that scores and prioritizes tasks intelligently based on urgency, importance, effort, and dependencies.
This project was built as part of the Software Development Intern technical assessment.

Overview

The Smart Task Analyzer helps users decide which tasks they should work on first.
It uses a custom scoring algorithm and provides a simple, clear user interface with multiple sorting strategies.

The project demonstrates:

Algorithm design

Backend development with Django

Clean and modular code

Handling edge cases

Functional frontend using HTML, CSS, and JavaScript

Project Structure
task-analyzer/
│
├── backend/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── tasks/
│   ├── models.py
│   ├── scoring.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── README.md
├── requirements.txt
└── manage.py

Algorithm Explanation

The scoring algorithm evaluates each task using five main components.

1. Urgency

Based on the number of days until the due date:

Overdue tasks receive a large score increase

Tasks due within 1 day or 3 days get an urgency boost

Tasks due within 7 days get a smaller boost

Tasks with no due date are treated as low urgency

2. Importance

The user provides an importance level from 1 to 10.
Different strategies apply different importance weights:

Smart Balance: moderate weight

High Impact: highest weight

Fastest Wins: lower weight

Deadline Driven: balanced weight

3. Effort

Estimated hours influence the score:

Tasks ≤ 1 hour get a strong bonus

Tasks ≤ 2 hours get a moderate bonus

Tasks ≥ 8 hours receive a small penalty

4. Dependencies

Two aspects are considered:

If a task depends on many others, its score decreases

If a task unblocks many other tasks, its score increases

5. Circular Dependencies

A cycle detection function identifies circular dependencies.
Tasks inside a cycle receive a penalty because they cannot be completed without corrections.

Sorting Strategies

The user can choose from four different strategies:

Smart Balance
A balanced approach between urgency, importance, and effort.

Fastest Wins
Gives preference to quick, low-effort tasks.

High Impact
Prioritizes tasks with high importance scores.

Deadline Driven
Focuses strongly on due dates and urgency.

Unit Tests

Three tests are included:

Overdue tasks have higher priority than future tasks

Missing importance defaults to 5

Fastest Wins strategy favors quick tasks over long tasks

Run tests with:

python manage.py test

Frontend Overview

The frontend is built using plain HTML, CSS, and JavaScript.

Features:

Add tasks individually through a form

Bulk JSON input

Sorting strategy dropdown

Buttons to analyze tasks or get top 3 suggestions

Result cards with priority level, details, and explanation

Setup Instructions
1. Clone the repository
git clone <your_repo_url>
cd task-analyzer

2. Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Mac/Linux

3. Install dependencies
pip install -r requirements.txt

4. Run database migrations
python manage.py makemigrations
python manage.py migrate

5. Start the backend server
python manage.py runserver

6. Start the frontend

Open:

frontend/index.html


Either double-click it or open it using a Live Server extension.

Design Decisions

Used JSONField for dependencies to keep input flexible.

Placed scoring logic in a separate file for clarity and maintainability.

Used DFS for cycle detection, which is simple and efficient for this scale.

API-based design was chosen because the assignment required analysis, not CRUD UI.

Kept the frontend simple and readable instead of over-engineering the interface.

Time Breakdown
Task	Time
Algorithm design	45 minutes
Backend setup and development	45 minutes
Scoring logic and views	45 minutes
Frontend UI	60 minutes
Debugging and testing	30 minutes
README and final review	20 minutes

Total: Approximately 4 hours.

Future Improvements

Visual dependency graph

Eisenhower matrix (Urgent vs Important)

Weekend and holiday-aware urgency

Learning system that adjusts weights over time

Saved tasks and user accounts

Dark mode for the interface