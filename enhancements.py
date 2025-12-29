"""
Future Enhancement Examples
Code snippets for extending the habit tracker
"""

# ===== ENHANCEMENT 1: Email Reminders =====
# Add to requirements.txt: schedule>=1.1.0

"""
import schedule
import time
from datetime import datetime

def send_daily_reminder():
    # Get incomplete habits for today
    today_logs = db.get_logs_for_date(date.today())
    incomplete = [log for log in today_logs if not log['completed']]
    
    if incomplete:
        print(f"Reminder: You have {len(incomplete)} habits to complete today!")
        # Add email/SMS logic here

# Schedule reminder at 8 PM daily
schedule.every().day.at("20:00").do(send_daily_reminder)

# Run in background
while True:
    schedule.run_pending()
    time.sleep(60)
"""


# ===== ENHANCEMENT 2: Data Export =====

"""
import csv
from datetime import timedelta

def export_to_csv(filename="habit_export.csv"):
    # Get all logs for last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    logs = db.get_all_logs(start_date, end_date)
    
    # Write to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['habit_name', 'log_date', 'completed'])
        writer.writeheader()
        writer.writerows(logs)
    
    return filename

# In Streamlit app:
if st.button("Export Last 30 Days"):
    file = export_to_csv()
    with open(file, 'rb') as f:
        st.download_button("Download CSV", f, file_name=file)
"""


# ===== ENHANCEMENT 3: Habit Categories =====

"""
# Add to database.py - modify habits table:
cursor.execute('''
    ALTER TABLE habits ADD COLUMN category TEXT DEFAULT 'General'
''')

# Categories
CATEGORIES = ['Health', 'Work', 'Personal', 'Learning', 'Fitness']

# In UI - add category selector:
category = st.selectbox("Category", CATEGORIES)

# Filter by category in dashboard:
category_filter = st.multiselect("Filter by category", CATEGORIES)
filtered_habits = [h for h in habits if h['category'] in category_filter]
"""


# ===== ENHANCEMENT 4: Goals & Targets =====

"""
# Add goals table:
CREATE TABLE IF NOT EXISTS habit_goals (
    id INTEGER PRIMARY KEY,
    habit_id INTEGER,
    goal_type TEXT,  -- 'weekly', 'monthly'
    target_days INTEGER,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (habit_id) REFERENCES habits(id)
)

# Example: "Exercise 5 times per week"
def set_goal(habit_id, goal_type, target_days):
    db.execute('''
        INSERT INTO habit_goals (habit_id, goal_type, target_days, start_date)
        VALUES (?, ?, ?, ?)
    ''', (habit_id, goal_type, target_days, date.today()))

# Check goal progress
def check_goal_progress(habit_id):
    # Get current week's completion
    week_logs = get_habit_logs_for_week(habit_id)
    completed = sum(1 for log in week_logs if log['completed'])
    
    goal = get_goal(habit_id)
    return {
        'completed': completed,
        'target': goal['target_days'],
        'percentage': (completed / goal['target_days']) * 100
    }
"""


# ===== ENHANCEMENT 5: Advanced Charts =====

"""
import plotly.figure_factory as ff
import numpy as np

# Correlation heatmap: which habits are done together?
def create_habit_correlation():
    # Get last 30 days of data
    habits = db.get_all_habits()
    correlation_matrix = []
    
    for h1 in habits:
        row = []
        for h2 in habits:
            # Calculate how often both habits are completed on same day
            correlation = calculate_correlation(h1['id'], h2['id'])
            row.append(correlation)
        correlation_matrix.append(row)
    
    # Create heatmap
    fig = ff.create_annotated_heatmap(
        z=correlation_matrix,
        x=[h['name'] for h in habits],
        y=[h['name'] for h in habits],
        colorscale='Viridis'
    )
    
    return fig

# In Streamlit:
st.plotly_chart(create_habit_correlation())
"""


# ===== ENHANCEMENT 6: Habit Notes =====

"""
# Add notes to habit_logs table:
ALTER TABLE habit_logs ADD COLUMN note TEXT;

# In daily tracking UI:
note = st.text_area("Add a note (optional)", key=f"note_{habit_id}")
db.log_habit(habit_id, today, checked, note=note)

# Display notes in analytics:
for log in habit_logs:
    if log['note']:
        st.info(f"{log['log_date']}: {log['note']}")
"""


# ===== ENHANCEMENT 7: Streaks & Badges =====

"""
def get_badge(streak_count):
    if streak_count >= 100:
        return "🏆 Century Club"
    elif streak_count >= 30:
        return "🔥 Fire Streak"
    elif streak_count >= 7:
        return "⭐ Week Warrior"
    elif streak_count >= 3:
        return "💪 Getting Started"
    else:
        return "🌱 Beginner"

# Display badges in dashboard:
for habit in habits:
    streak = metrics.calculate_streak(habit_logs)
    badge = get_badge(streak['current_streak'])
    st.write(f"{habit['name']}: {badge}")
"""


# ===== ENHANCEMENT 8: Dark Mode =====

"""
# Add to app.py:
def set_theme():
    theme = st.sidebar.radio("Theme", ["Light", "Dark"])
    
    if theme == "Dark":
        st.markdown('''
            <style>
            .stApp {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            </style>
        ''', unsafe_allow_html=True)

set_theme()
"""


# ===== ENHANCEMENT 9: Multi-User Support =====

"""
# Add users table:
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    created_at DATE
)

# Add user_id to habits and habit_logs:
ALTER TABLE habits ADD COLUMN user_id INTEGER;

# Simple authentication:
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = db.get_user(username)
        if user and user['password_hash'] == hash_password(password):
            st.session_state['user_id'] = user['id']
            return True
    return False
"""


# ===== ENHANCEMENT 10: Mobile-Friendly PWA =====

"""
# Create manifest.json:
{
    "name": "Daily Habit Tracker",
    "short_name": "Habits",
    "description": "Track your daily habits",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#1f77b4",
    "icons": [
        {
            "src": "icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        }
    ]
}

# Add to app.py:
st.markdown('''
    <link rel="manifest" href="/manifest.json">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
''', unsafe_allow_html=True)
"""


# ===== ENHANCEMENT 11: AI Insights =====

"""
# Use simple pattern recognition
def generate_insights(habit_logs):
    insights = []
    
    # Find best day of week
    day_performance = {}
    for log in habit_logs:
        day = log['log_date'].strftime('%A')
        if day not in day_performance:
            day_performance[day] = {'completed': 0, 'total': 0}
        
        day_performance[day]['total'] += 1
        if log['completed']:
            day_performance[day]['completed'] += 1
    
    # Find best day
    best_day = max(day_performance.items(), 
                   key=lambda x: x[1]['completed'] / x[1]['total'])
    
    insights.append(f"You're most consistent on {best_day[0]}!")
    
    # Find declining habits
    recent = habit_logs[:7]
    older = habit_logs[7:14]
    
    recent_rate = sum(1 for l in recent if l['completed']) / len(recent)
    older_rate = sum(1 for l in older if l['completed']) / len(older)
    
    if recent_rate < older_rate - 0.2:
        insights.append("⚠️ This habit is declining. Need a boost?")
    
    return insights
"""


# ===== ENHANCEMENT 12: Integration with Google Calendar =====

"""
# Add to requirements.txt: google-api-python-client, google-auth

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def sync_to_google_calendar(habit, completed):
    # Authenticate
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('calendar', 'v3', credentials=creds)
    
    # Create event
    event = {
        'summary': f'✅ {habit["name"]}' if completed else f'❌ {habit["name"]}',
        'start': {'date': str(date.today())},
        'end': {'date': str(date.today())},
        'colorId': '10' if completed else '11'
    }
    
    service.events().insert(calendarId='primary', body=event).execute()
"""

print("Enhancement examples loaded. Copy and integrate as needed!")
