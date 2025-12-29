# Daily Habit Tracker 📋✅

A simple, extensible daily habit tracker with a visual dashboard built using **Python + Streamlit + SQLite**.

## 🎯 Features

- **Habit Management**: Create, edit, and delete habits
- **Daily Tracking**: Check off habits each day
- **Persistent Storage**: SQLite database (local, no cloud required)
- **Dashboard Metrics**:
  - Daily completion percentage
  - Weekly and monthly averages
  - Current and longest streaks
  - Consistency trends
- **Visual Analytics**:
  - Line charts for completion trends
  - Bar charts for habit consistency
  - 7-day activity heatmap
  - Calendar view per habit

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Streamlit (Python-based web UI)
- **Backend**: Python
- **Database**: SQLite (local file-based)
- **Visualization**: Plotly

### Data Model

**Tables:**

1. **habits**
   - `id` (Primary Key)
   - `name` (TEXT) - Habit name
   - `description` (TEXT) - Optional description
   - `created_at` (DATE) - Creation date
   - `is_active` (BOOLEAN) - Soft delete flag

2. **habit_logs**
   - `id` (Primary Key)
   - `habit_id` (Foreign Key → habits.id)
   - `log_date` (DATE) - Date of the log
   - `completed` (BOOLEAN) - Whether completed
   - **Unique constraint**: (habit_id, log_date)

### Data Flow

```
User Input (Streamlit UI)
    ↓
Database Layer (database.py)
    ↓
SQLite Database (data/habits.db)
    ↓
Metrics Calculation (metrics.py)
    ↓
Visualization (Plotly Charts)
    ↓
Dashboard Display (Streamlit)
```

## 📁 Folder Structure

```
Daily_Scheduler/
├── app.py              # Main Streamlit application
├── database.py         # Database layer (CRUD operations)
├── metrics.py          # Metrics calculation logic
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
└── data/              # Created automatically
    └── habits.db      # SQLite database
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   streamlit run app.py
   ```

3. **Access the app**:
   - Opens automatically in your browser
   - Usually at: http://localhost:8501

## 📖 Usage Guide

### 1. Create Habits
- Navigate to **🎯 Manage Habits** → **Add New Habit**
- Enter habit name (e.g., "Wake up at 7 AM", "Gym", "Read for 30 min")
- Add optional description
- Click "Add Habit"

### 2. Track Daily Progress
- Go to **✅ Today's Habits**
- Check off habits as you complete them
- Progress updates automatically

### 3. View Dashboard
- **📊 Dashboard** shows:
  - Today's completion %
  - 7-day average
  - Current streaks for all habits
  - Last 7 days activity grid

### 4. Analyze Trends
- **📈 Analytics** provides:
  - Daily completion trend graph
  - Habit-wise consistency comparison
  - Detailed breakdown per habit
  - Calendar view with completion history

## 🧮 How Metrics Are Calculated

### 1. **Daily Completion %**
```
(Habits Completed Today / Total Active Habits) × 100
```

### 2. **Current Streak**
- Counts consecutive days from today backwards where habit was completed
- Breaks if any day is missed

### 3. **Longest Streak**
- Scans all historical logs
- Finds the longest sequence of consecutive completed days

### 4. **Consistency %**
```
(Days Completed / Total Days in Period) × 100
```

### 5. **Weekly/Monthly Average**
- Aggregates all habit completions in the period
- Calculates average completion rate

## 🔮 Future Enhancement Ideas

### High Priority
- [ ] **Reminders**: Daily notifications at custom times
- [ ] **Mobile-Friendly UI**: Responsive design improvements
- [ ] **Export/Import**: CSV/JSON backup and restore
- [ ] **Habit Categories**: Group habits (Health, Work, Personal)

### Medium Priority
- [ ] **Notes per Log**: Add context to why you missed/completed
- [ ] **Goals**: Set weekly/monthly targets
- [ ] **Rewards System**: Badges for streaks
- [ ] **Dark Mode**: Theme toggle
- [ ] **Multi-user Support**: Basic authentication

### Low Priority
- [ ] **Advanced Charts**: Heatmaps, correlation analysis
- [ ] **API Integration**: Sync with fitness trackers
- [ ] **AI Insights**: Pattern recognition and suggestions
- [ ] **Social Features**: Share progress with friends

## 🛠️ Design Decisions

### Why SQLite?
- **Lightweight**: No server required
- **Portable**: Single file database
- **Fast**: Sufficient for personal use
- **Zero Config**: Works out of the box

### Why Streamlit?
- **Rapid Development**: Build UI with pure Python
- **Interactive**: Auto-reloads on changes
- **Rich Components**: Built-in widgets and charts
- **Easy Deployment**: Can deploy to Streamlit Cloud

### Why This Structure?
- **Modular**: Separate concerns (UI, DB, Logic)
- **Testable**: Each module can be tested independently
- **Scalable**: Easy to add new features
- **Readable**: Clear code organization

## 📝 Example Habits

Here are some habit ideas to get started:

**Morning Routine**
- Wake up at 7 AM
- Morning meditation (10 min)
- Breakfast before 8:30 AM

**Health & Fitness**
- Gym / Exercise (30 min)
- 10,000 steps daily
- Drink 8 glasses of water

**Productivity**
- Read for 30 minutes
- Learn something new (coding, language, etc.)
- Journal / Reflection

**Digital Wellness**
- Screen time < 3 hours (social media)
- No phone 1 hour before bed
- Email inbox zero

## 🐛 Troubleshooting

**App won't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

**Database errors:**
- Delete `data/habits.db` and restart (note: this deletes all data)
- Check file permissions in the `data/` folder

**Charts not displaying:**
- Update Plotly: `pip install --upgrade plotly`
- Clear browser cache

## 📄 License

Free to use for personal projects. Modify and extend as needed.

## 🤝 Contributing

This is a personal habit tracker, but feel free to:
- Fork and customize for your needs
- Suggest improvements via issues
- Share your enhancements

---

**Built with ❤️ for better daily habits**
