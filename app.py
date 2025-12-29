"""
Main Streamlit application for Daily Habit Tracker
With multi-user authentication and leaderboard
"""

import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import HabitDatabase
from metrics import MetricsCalculator
from auth import (
    login_page, logout, is_authenticated, get_current_user, 
    is_admin, get_all_usernames, get_user_display_name
)

# Check authentication FIRST (before any other st commands)
if not is_authenticated():
    login_page()
    st.stop()

# Get current user
current_user = get_current_user()
user_id = current_user["username"]

# Page configuration (after auth check)
st.set_page_config(
    page_title="Daily Habit Tracker",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def get_database():
    return HabitDatabase()

db = get_database()
metrics = MetricsCalculator()

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .streak-badge {
        background-color: #ff6b6b;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .completion-badge {
        background-color: #51cf66;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    
    /* Excel-like Grid Styles */
    .grid-container {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        overflow: hidden;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .grid-header {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        border-bottom: 2px solid #dee2e6;
        padding: 12px 8px;
        text-align: center;
        font-weight: 600;
        font-size: 0.85rem;
        color: #495057;
    }
    .grid-header-habit {
        background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%);
        border-bottom: 2px solid #90caf9;
        padding: 12px 16px;
        text-align: left;
        font-weight: 700;
        font-size: 1rem;
        color: #1565c0;
    }
    .habit-row {
        background-color: #ffffff;
        border-bottom: 1px solid #e9ecef;
        padding: 10px 16px;
        font-weight: 500;
        font-size: 0.9rem;
        color: #2c3e50;
        display: flex;
        align-items: center;
    }
    .habit-row:nth-child(even) {
        background-color: #f8f9fa;
    }
    .habit-row:hover {
        background-color: #e3f2fd;
    }
    .day-cell {
        text-align: center;
        padding: 8px;
        border-left: 1px solid #e9ecef;
    }
    .week-header {
        background: linear-gradient(180deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 12px 8px;
        text-align: center;
        font-weight: 600;
        font-size: 0.8rem;
        color: #e65100;
        border-bottom: 2px solid #ffcc80;
    }
    .today-highlight {
        background: linear-gradient(180deg, #c8e6c9 0%, #a5d6a7 100%) !important;
        border-bottom: 2px solid #66bb6a;
    }
    .week-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 0.95rem;
        color: white;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Row number styling */
    .row-number {
        color: #6c757d;
        font-size: 0.8rem;
        font-weight: 400;
        width: 30px;
        text-align: center;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        display: flex;
        justify-content: center;
    }
    
    /* Leaderboard styling */
    .leaderboard-item {
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 8px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #dee2e6;
    }
    .leaderboard-item.completed {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
    }
    .leaderboard-item.current-user {
        background: linear-gradient(135deg, #cce5ff 0%, #b8daff 100%);
        border-left: 4px solid #007bff;
    }
    .user-badge {
        font-weight: 600;
        font-size: 0.95rem;
    }
    .streak-badge {
        font-size: 0.8rem;
        color: #e65100;
    }
    </style>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
# User info and logout
st.sidebar.markdown(f"### 👋 Hello, {current_user['display_name']}!")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    logout()

st.sidebar.divider()

# Navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["📅 Weekly View", "📊 Dashboard", "✅ Quick Check", "🎯 Manage Habits", "📈 Analytics"]
)

st.sidebar.divider()

# ===== FRIENDS LEADERBOARD =====
st.sidebar.markdown("### 🏆 Friends Leaderboard")
st.sidebar.caption("Today's Status")

# Get all users and their stats
all_usernames = get_all_usernames()
leaderboard_data = []

for username in all_usernames:
    stats = db.get_user_stats(username)
    display_name = get_user_display_name(username)
    leaderboard_data.append({
        "username": username,
        "display_name": display_name,
        "completed_today": stats["completed_today"],
        "streak": stats["current_streak"],
        "completion_rate": stats["completion_rate"],
        "total_habits": stats["total_habits"]
    })

# Sort by streak (descending), then by completion rate
leaderboard_data.sort(key=lambda x: (x["streak"], x["completion_rate"]), reverse=True)

# Display leaderboard
for idx, user_data in enumerate(leaderboard_data):
    is_current = user_data["username"] == user_id
    is_done = user_data["completed_today"]
    
    # Status emoji
    status = "✅" if is_done else "⬜"
    
    # Streak display
    streak_text = f"🔥 {user_data['streak']}d" if user_data["streak"] > 0 else ""
    
    # Rank emoji for top 3
    rank_emoji = ""
    if idx == 0 and user_data["streak"] > 0:
        rank_emoji = "🥇 "
    elif idx == 1 and user_data["streak"] > 0:
        rank_emoji = "🥈 "
    elif idx == 2 and user_data["streak"] > 0:
        rank_emoji = "🥉 "
    
    # Style based on status
    if is_current:
        style = "background: linear-gradient(135deg, #cce5ff 0%, #b8daff 100%); border-left: 4px solid #007bff;"
    elif is_done:
        style = "background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-left: 4px solid #28a745;"
    else:
        style = "background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-left: 4px solid #dee2e6;"
    
    st.sidebar.markdown(f"""
        <div style="padding: 8px 12px; margin: 4px 0; border-radius: 8px; {style}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600; font-size: 0.9rem;">{rank_emoji}{status} {user_data['display_name']}</span>
                <span style="font-size: 0.8rem; color: #e65100;">{streak_text}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

if not leaderboard_data:
    st.sidebar.info("No friends yet! Ask them to sign up.")

st.sidebar.divider()
st.sidebar.caption("💡 Daily Habit Tracker")
st.sidebar.caption("Track together, grow together!")

# ===== WEEKLY VIEW PAGE (GRID STYLE) =====
if page == "📅 Weekly View":
    st.markdown('<p class="main-header">📅 My Habits</p>', unsafe_allow_html=True)
    
    # Get current week
    today = date.today()
    
    # Week selector
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        if 'week_offset' not in st.session_state:
            st.session_state.week_offset = 0
        
        # Week starts on Monday
        week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=st.session_state.week_offset)
        week_end = week_start + timedelta(days=6)
        
        st.markdown(f'<div class="week-indicator">📆 Week {week_start.isocalendar()[1]} | {week_start.strftime("%b %d")} - {week_end.strftime("%b %d, %Y")}</div>', 
                   unsafe_allow_html=True)
    
    with col2:
        if st.button("◀ Prev", use_container_width=True):
            st.session_state.week_offset -= 1
            st.rerun()
    
    with col3:
        if st.button("Next ▶", use_container_width=True):
            st.session_state.week_offset += 1
            st.rerun()
    
    st.markdown("")
    
    # Get all active habits for current user
    habits = db.get_all_habits(active_only=True, user_id=user_id)
    
    if not habits:
        st.info("📝 No habits yet! Go to '🎯 Manage Habits' to create your first habit.")
    else:
        # Create the grid with days of the week
        days_of_week = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            days_of_week.append(day)
        
        # Build header row: Row# | My Habits | Sa | Su | Mo | Tu | We | Th | Fr | Week
        header_cols = st.columns([0.5, 3] + [1] * 7 + [1.2])
        
        # Row number header
        with header_cols[0]:
            st.markdown('<div class="grid-header">#</div>', unsafe_allow_html=True)
        
        # Habit column header
        with header_cols[1]:
            st.markdown('<div class="grid-header-habit">My Habits</div>', unsafe_allow_html=True)
        
        # Day headers
        for idx, day in enumerate(days_of_week):
            with header_cols[idx + 2]:
                day_name = day.strftime("%a")
                day_num = day.day
                is_today = day == today
                
                if is_today:
                    st.markdown(f'<div class="grid-header today-highlight">{day_name}<br><b>{day_num}</b></div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="grid-header">{day_name}<br>{day_num}</div>', 
                               unsafe_allow_html=True)
        
        # Week header
        with header_cols[9]:
            st.markdown(f'<div class="week-header">Week {week_start.isocalendar()[1]}</div>', 
                       unsafe_allow_html=True)
        
        # Create rows for each habit
        for row_num, habit in enumerate(habits, start=1):
            habit_cols = st.columns([0.5, 3] + [1] * 7 + [1.2])
            
            # Row number
            with habit_cols[0]:
                st.markdown(f'<div class="row-number" style="padding-top: 8px;">{row_num}</div>', 
                           unsafe_allow_html=True)
            
            # Habit name column
            with habit_cols[1]:
                st.markdown(f'<div class="habit-row">{habit["name"]}</div>', 
                           unsafe_allow_html=True)
            
            # Checkbox columns for each day
            week_completed = 0
            for idx, day in enumerate(days_of_week):
                with habit_cols[idx + 2]:
                    # Get the log for this habit and day
                    logs = db.get_logs_for_date(day, user_id=user_id)
                    habit_log = next((log for log in logs if log['habit_id'] == habit['id']), None)
                    
                    is_checked = habit_log['completed'] if habit_log else False
                    if is_checked:
                        week_completed += 1
                    
                    # Create unique key for checkbox
                    checkbox_key = f"habit_{habit['id']}_day_{day.strftime('%Y%m%d')}"
                    
                    # Checkbox with proper label
                    new_value = st.checkbox(
                        f"Mark {habit['name']} for {day.strftime('%b %d')}",
                        value=bool(is_checked),
                        key=checkbox_key,
                        label_visibility="collapsed"
                    )
                    
                    # Update database if value changed
                    if new_value != is_checked:
                        db.log_habit(habit['id'], day, new_value)
                        st.rerun()
            
            # Week completion count
            with habit_cols[9]:
                pct = int((week_completed / 7) * 100)
                color = "#4caf50" if pct >= 70 else "#ff9800" if pct >= 40 else "#f44336"
                st.markdown(f'<div style="text-align:center; padding-top:6px; font-weight:600; color:{color}">{week_completed}/7</div>', 
                           unsafe_allow_html=True)
        
        st.markdown("")
        
        # Weekly summary
        st.subheader("📊 Week Summary")
        
        week_logs = db.get_all_logs(week_start, week_end, user_id=user_id)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_possible = len(habits) * 7
            total_completed = sum(1 for log in week_logs if log['completed'])
            completion_pct = (total_completed / total_possible * 100) if total_possible > 0 else 0
            st.metric("Week Completion", f"{completion_pct:.0f}%", f"{total_completed}/{total_possible}")
        
        with col2:
            # Best day
            best_count = 0
            best_day = None
            for day in days_of_week:
                day_logs = [log for log in week_logs if log['log_date'] == day]
                completed = sum(1 for log in day_logs if log['completed'])
                if completed > best_count:
                    best_count = completed
                    best_day = day
            
            if best_day:
                st.metric("Best Day", best_day.strftime("%A"), f"{best_count} habits")
            else:
                st.metric("Best Day", "N/A")
        
        with col3:
            # Most consistent habit
            habit_consistency = {}
            for habit in habits:
                habit_week_logs = [log for log in week_logs if log['habit_id'] == habit['id']]
                completed = sum(1 for log in habit_week_logs if log['completed'])
                habit_consistency[habit['name']] = completed
            
            if habit_consistency:
                best_habit = max(habit_consistency, key=habit_consistency.get)
                best_count = habit_consistency[best_habit]
                st.metric("Most Consistent", best_habit, f"{best_count}/7 days")

# ===== DASHBOARD PAGE =====
elif page == "📊 Dashboard":
    st.markdown('<p class="main-header">📊 Habit Tracker Dashboard</p>', unsafe_allow_html=True)
    
    # Today's overview
    today = date.today()
    today_logs = db.get_logs_for_date(today, user_id=user_id)
    
    if not today_logs:
        st.info("📝 No habits created yet. Go to 'Manage Habits' to add your first habit!")
    else:
        # Today's metrics
        daily_completion = metrics.calculate_daily_completion(today_logs)
        completed_today = sum(1 for log in today_logs if log['completed'])
        total_today = len(today_logs)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Today's Completion", f"{daily_completion:.0f}%", 
                     f"{completed_today}/{total_today} habits")
        
        with col2:
            # Weekly completion
            week_start = today - timedelta(days=6)
            week_logs = db.get_all_logs(week_start, today, user_id=user_id)
            if week_logs:
                week_completion = metrics.calculate_daily_completion(week_logs)
                st.metric("7-Day Average", f"{week_completion:.0f}%")
            else:
                st.metric("7-Day Average", "N/A")
        
        with col3:
            # Active habits
            active_habits = db.get_all_habits(active_only=True, user_id=user_id)
            st.metric("Active Habits", len(active_habits))
        
        with col4:
            # Current month
            month_logs = db.get_all_logs(
                today.replace(day=1),
                today,
                user_id=user_id
            )
            if month_logs:
                month_completion = metrics.calculate_daily_completion(month_logs)
                st.metric("This Month", f"{month_completion:.0f}%")
            else:
                st.metric("This Month", "N/A")
        
        st.divider()
        
        # Habit-wise streaks
        st.subheader("🔥 Current Streaks")
        
        habits = db.get_all_habits(active_only=True, user_id=user_id)
        streak_data = []
        
        for habit in habits:
            habit_logs = db.get_habit_logs(habit['id'])
            streak_info = metrics.calculate_streak(habit_logs, today)
            
            streak_data.append({
                "Habit": habit['name'],
                "Current Streak": streak_info['current_streak'],
                "Longest Streak": streak_info['longest_streak']
            })
        
        if streak_data:
            df_streaks = pd.DataFrame(streak_data)
            st.dataframe(df_streaks, width='stretch', hide_index=True)
        
        st.divider()
        
        # Last 7 days heatmap
        st.subheader("📅 Last 7 Days Activity")
        
        heatmap_data = []
        for i in range(6, -1, -1):
            check_date = today - timedelta(days=i)
            day_logs = db.get_logs_for_date(check_date, user_id=user_id)
            
            for log in day_logs:
                heatmap_data.append({
                    "Date": check_date.strftime("%a, %b %d"),
                    "Habit": log['name'],
                    "Status": "✅" if log['completed'] else "⬜"
                })
        
        if heatmap_data:
            df_heatmap = pd.DataFrame(heatmap_data)
            pivot_table = df_heatmap.pivot(index="Habit", columns="Date", values="Status")
            st.dataframe(pivot_table, width='stretch')

# ===== QUICK CHECK PAGE =====
elif page == "✅ Quick Check":
    st.markdown('<p class="main-header">✅ Quick Check</p>', unsafe_allow_html=True)
    
    today = date.today()
    st.write(f"**Date:** {today.strftime('%A, %B %d, %Y')}")
    
    today_logs = db.get_logs_for_date(today, user_id=user_id)
    
    if not today_logs:
        st.info("📝 No habits created yet. Go to 'Manage Habits' to add your first habit!")
    else:
        st.write("✨ Quick check-in for today:")
        st.divider()
        
        # Create a more compact grid layout
        for log in today_logs:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{log['name']}**")
                if log['description']:
                    st.caption(log['description'])
            
            with col2:
                checked = st.checkbox(
                    "✓",
                    value=bool(log['completed']),
                    key=f"quick_habit_{log['habit_id']}",
                    label_visibility="visible"
                )
                
                # Update database
                if checked != bool(log['completed']):
                    db.log_habit(log['habit_id'], today, checked)
                    st.rerun()
        
        st.divider()
        
        # Show completion summary
        completed = sum(1 for log in today_logs if log['completed'])
        total = len(today_logs)
        completion_pct = (completed / total * 100) if total > 0 else 0
        
        st.progress(completion_pct / 100)
        st.write(f"**Progress:** {completed}/{total} habits completed ({completion_pct:.0f}%)")

# ===== MANAGE HABITS PAGE =====
elif page == "🎯 Manage Habits":
    st.markdown('<p class="main-header">🎯 Manage Habits</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Add New Habit", "📝 Edit/Delete Habits"])
    
    with tab1:
        st.subheader("Create a New Habit")
        
        with st.form("add_habit_form"):
            habit_name = st.text_input("Habit Name*", placeholder="e.g., Wake up at 7 AM")
            habit_desc = st.text_area("Description (optional)", 
                                      placeholder="Additional details or goals...")
            
            submitted = st.form_submit_button("Add Habit")
            
            if submitted:
                if habit_name.strip():
                    db.add_habit(habit_name.strip(), habit_desc.strip(), user_id=user_id)
                    st.success(f"✅ Habit '{habit_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a habit name.")
    
    with tab2:
        st.subheader("Your Habits")
        
        habits = db.get_all_habits(active_only=True, user_id=user_id)
        
        if not habits:
            st.info("No habits yet. Add your first habit in the 'Add New Habit' tab!")
        else:
            for habit in habits:
                with st.expander(f"**{habit['name']}**"):
                    st.write(f"**Description:** {habit['description'] or 'N/A'}")
                    st.write(f"**Created:** {habit['created_at']}")
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{habit['id']}"):
                            st.session_state[f'editing_{habit["id"]}'] = True
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{habit['id']}"):
                            db.delete_habit(habit['id'])
                            st.success(f"Deleted '{habit['name']}'")
                            st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f'editing_{habit["id"]}', False):
                        with st.form(f"edit_form_{habit['id']}"):
                            new_name = st.text_input("Name", value=habit['name'])
                            new_desc = st.text_area("Description", value=habit['description'] or "")
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("Save"):
                                    db.update_habit(habit['id'], new_name, new_desc)
                                    st.session_state[f'editing_{habit["id"]}'] = False
                                    st.success("Updated!")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("Cancel"):
                                    st.session_state[f'editing_{habit["id"]}'] = False
                                    st.rerun()

# ===== ANALYTICS PAGE =====
elif page == "📈 Analytics":
    st.markdown('<p class="main-header">📈 Analytics & Insights</p>', unsafe_allow_html=True)
    
    habits = db.get_all_habits(active_only=True, user_id=user_id)
    
    if not habits:
        st.info("📝 No habits to analyze yet. Add some habits and start tracking!")
    else:
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            days_back = st.selectbox("Time Period", [7, 14, 30, 60, 90], index=2)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back - 1)
        
        st.divider()
        
        # Overall completion trend
        st.subheader("📊 Daily Completion Trend")
        
        trend_data = []
        current = start_date
        
        while current <= end_date:
            day_logs = db.get_logs_for_date(current, user_id=user_id)
            completion = metrics.calculate_daily_completion(day_logs)
            
            trend_data.append({
                "Date": current,
                "Completion %": completion
            })
            current += timedelta(days=1)
        
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            fig = px.line(df_trend, x="Date", y="Completion %", 
                         title=f"Daily Completion Rate (Last {days_back} Days)",
                         markers=True)
            fig.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig, width='stretch')
        
        st.divider()
        
        # Habit-wise consistency
        st.subheader("🎯 Habit Consistency")
        
        consistency_data = []
        for habit in habits:
            habit_logs = db.get_habit_logs(habit['id'], start_date, end_date)
            
            # Count completed days
            completed_days = sum(1 for log in habit_logs if log['completed'])
            consistency_pct = (completed_days / days_back) * 100
            
            consistency_data.append({
                "Habit": habit['name'],
                "Consistency %": consistency_pct,
                "Days Completed": completed_days
            })
        
        if consistency_data:
            df_consistency = pd.DataFrame(consistency_data)
            fig = px.bar(df_consistency, x="Habit", y="Consistency %",
                        title=f"Habit Consistency (Last {days_back} Days)",
                        text="Days Completed")
            fig.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig, width='stretch')
        
        st.divider()
        
        # Detailed habit breakdown
        st.subheader("📋 Detailed Breakdown")
        
        selected_habit = st.selectbox(
            "Select a habit to analyze",
            options=[h['name'] for h in habits]
        )
        
        if selected_habit:
            habit = next(h for h in habits if h['name'] == selected_habit)
            habit_logs = db.get_habit_logs(habit['id'], start_date, end_date)
            
            # Streak info
            streak_info = metrics.calculate_streak(habit_logs, end_date)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Streak", f"{streak_info['current_streak']} days")
            with col2:
                st.metric("Longest Streak", f"{streak_info['longest_streak']} days")
            with col3:
                completed = sum(1 for log in habit_logs if log['completed'])
                st.metric("Completion Rate", f"{(completed/days_back*100):.0f}%")
            
            # Calendar view
            calendar_data = []
            current = start_date
            
            while current <= end_date:
                log = next((l for l in habit_logs if l['log_date'] == current), None)
                status = "✅ Done" if log and log['completed'] else "⬜ Missed"
                
                calendar_data.append({
                    "Date": current.strftime("%Y-%m-%d"),
                    "Day": current.strftime("%a"),
                    "Status": status
                })
                current += timedelta(days=1)
            
            df_calendar = pd.DataFrame(calendar_data)
            st.dataframe(df_calendar, width='stretch', hide_index=True)
