# 🏗️ Architecture Deep Dive

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit UI Layer                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Dashboard │ │  Today   │ │  Manage  │ │Analytics │  │
│  │   Page   │ │  Habits  │ │  Habits  │ │   Page   │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
└───────┼────────────┼────────────┼────────────┼─────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼────────┐              ┌────────▼─────────┐
│  database.py   │              │   metrics.py     │
│                │              │                  │
│ - add_habit()  │              │ - calculate_     │
│ - get_habits() │              │   streak()       │
│ - log_habit()  │              │ - calculate_     │
│ - update_*()   │              │   completion()   │
│ - delete_*()   │              │ - get_trends()   │
└───────┬────────┘              └──────────────────┘
        │
┌───────▼────────┐
│  SQLite DB     │
│  habits.db     │
│                │
│ Tables:        │
│ - habits       │
│ - habit_logs   │
└────────────────┘
```

## Component Responsibilities

### 1. **app.py** (Presentation Layer)
**Role:** User interface and interaction handling

**Responsibilities:**
- Render UI pages using Streamlit
- Handle user input (forms, checkboxes)
- Display metrics and charts
- Manage navigation between pages
- Format data for visualization

**Key Functions:**
- Page routing (Dashboard, Today, Manage, Analytics)
- Form submission handlers
- Chart generation with Plotly
- Session state management

---

### 2. **database.py** (Data Layer)
**Role:** All database operations and data persistence

**Responsibilities:**
- SQLite connection management
- CRUD operations for habits
- Logging habit completions
- Query optimization
- Data integrity enforcement

**Key Classes:**
```python
HabitDatabase:
    __init__(db_path)          # Initialize DB connection
    
    # Habit operations
    add_habit(name, desc)      # Create new habit
    get_all_habits(active)     # Retrieve habits list
    get_habit(id)              # Get single habit
    update_habit(id, ...)      # Modify habit
    delete_habit(id)           # Soft delete
    
    # Logging operations
    log_habit(id, date, done)  # Record completion
    get_logs_for_date(date)    # Daily logs
    get_habit_logs(id, range)  # Habit history
    get_all_logs(range)        # All logs
```

**Database Schema:**
```sql
-- Habits table
CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATE NOT NULL,
    is_active BOOLEAN DEFAULT 1
);

-- Logs table
CREATE TABLE habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    completed BOOLEAN DEFAULT 0,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE(habit_id, log_date)  -- One log per habit per day
);
```

---

### 3. **metrics.py** (Business Logic Layer)
**Role:** Calculate insights and analytics

**Responsibilities:**
- Streak calculations
- Completion percentage computations
- Trend analysis
- Statistical aggregations

**Key Functions:**
```python
MetricsCalculator:
    calculate_daily_completion(logs)
        → Returns: float (0-100%)
        → Logic: (completed / total) * 100
    
    calculate_streak(logs, date)
        → Returns: {current_streak, longest_streak}
        → Logic: 
            - Count backward from today
            - Break on first missed day
            - Scan all history for longest
    
    calculate_consistency(logs, days)
        → Returns: float (0-100%)
        → Logic: (completed_days / period_days) * 100
    
    calculate_weekly_stats(logs, start, end)
        → Returns: {week: completion%}
        → Logic: Group by week, aggregate
    
    calculate_monthly_summary(logs, month, year)
        → Returns: {stats dictionary}
```

---

## Data Flow Diagrams

### 1. Adding a New Habit
```
User fills form
    ↓
Streamlit validates input
    ↓
app.py calls db.add_habit(name, description)
    ↓
database.py executes INSERT INTO habits
    ↓
SQLite stores record
    ↓
Returns new habit ID
    ↓
app.py refreshes UI (st.rerun())
```

### 2. Daily Habit Tracking
```
User navigates to "Today's Habits"
    ↓
app.py calls db.get_logs_for_date(today)
    ↓
database.py executes JOIN query
    ↓
Returns list of habits with completion status
    ↓
app.py renders checkboxes
    ↓
User checks/unchecks habit
    ↓
app.py calls db.log_habit(id, date, checked)
    ↓
database.py UPSERT into habit_logs
    ↓
SQLite updates record
    ↓
UI auto-updates progress bar
```

### 3. Dashboard Metrics Generation
```
User views Dashboard
    ↓
app.py requests multiple data sets:
    - db.get_logs_for_date(today)
    - db.get_all_logs(last_7_days)
    - db.get_all_habits()
    ↓
For each habit:
    app.py → db.get_habit_logs(id)
    ↓
    metrics.calculate_streak(logs)
    ↓
    Returns streak data
    ↓
app.py aggregates results
    ↓
Renders metrics cards and tables
```

### 4. Analytics Chart Rendering
```
User selects time period (30 days)
    ↓
app.py calculates date range
    ↓
Loops through each day:
    db.get_logs_for_date(date)
    ↓
    metrics.calculate_daily_completion(logs)
    ↓
    Stores in trend_data[]
    ↓
app.py creates DataFrame
    ↓
Plotly generates line chart
    ↓
st.plotly_chart() displays
```

---

## Key Design Patterns

### 1. **Repository Pattern**
`database.py` acts as a repository, abstracting all SQL from the UI layer.

**Benefits:**
- Easy to switch databases (SQLite → PostgreSQL)
- Testable: can mock database methods
- Clean separation of concerns

### 2. **Single Responsibility Principle**
Each module has one job:
- `app.py` → UI only
- `database.py` → Data only
- `metrics.py` → Calculations only

### 3. **Caching Strategy**
```python
@st.cache_resource
def get_database():
    return HabitDatabase()
```
Database connection is cached across reruns.

### 4. **UPSERT Pattern**
```sql
INSERT INTO habit_logs (habit_id, log_date, completed)
VALUES (?, ?, ?)
ON CONFLICT(habit_id, log_date) 
DO UPDATE SET completed = ?
```
Prevents duplicate entries, allows toggling.

---

## Performance Considerations

### Database Queries
- **Indexed columns**: `habit_id`, `log_date`
- **Batch reads**: Fetch date ranges, not individual days
- **Join efficiency**: LEFT JOIN for including unchecked habits

### Streamlit Optimizations
- **@st.cache_resource**: Cache DB connection
- **Selective reruns**: Only refresh when data changes
- **Lazy loading**: Load analytics data only when viewing that page

### Scalability
Current design handles:
- **~50 habits** comfortably
- **5+ years** of daily logs
- **~20,000 records** without performance issues

For more:
- Add database indexes
- Implement pagination
- Use connection pooling

---

## Security Considerations

### Current State
- **Local only**: No network exposure
- **File-based**: Database stored on local machine
- **No authentication**: Single-user application

### For Multi-User Version
1. Add password hashing (bcrypt)
2. Implement session management
3. Row-level security (user_id filtering)
4. HTTPS for remote access
5. Input sanitization (already using parameterized queries)

---

## Testing Strategy

### Unit Tests (Future)
```python
# test_database.py
def test_add_habit():
    db = HabitDatabase(":memory:")
    habit_id = db.add_habit("Test", "Description")
    assert habit_id > 0

# test_metrics.py
def test_streak_calculation():
    logs = [
        {'log_date': date(2025, 12, 20), 'completed': True},
        {'log_date': date(2025, 12, 19), 'completed': True},
    ]
    result = MetricsCalculator.calculate_streak(logs)
    assert result['current_streak'] == 2
```

### Integration Tests
- Full workflow: Add habit → Log → View dashboard
- Data persistence across sessions
- UI interaction testing with Selenium

---

## Deployment Options

### Option 1: Local Desktop App
**Current state** - Run on personal machine
```bash
streamlit run app.py
```

### Option 2: Streamlit Cloud (Free)
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy with one click
4. Get public URL

**Limitations:**
- Single user (no auth)
- Data resets on redeploy

### Option 3: Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### Option 4: Self-Hosted Server
- Deploy on VPS (DigitalOcean, AWS)
- Use Nginx as reverse proxy
- Enable HTTPS with Let's Encrypt
- Add authentication layer

---

## File Structure (Detailed)

```
Daily_Scheduler/
│
├── app.py                    # Main Streamlit application (450 lines)
│   ├── Page: Dashboard       # Overview metrics and streaks
│   ├── Page: Today's Habits  # Daily checklist
│   ├── Page: Manage Habits   # Add/Edit/Delete
│   └── Page: Analytics       # Charts and trends
│
├── database.py               # SQLite operations (250 lines)
│   ├── Class: HabitDatabase
│   ├── Methods: Habit CRUD
│   └── Methods: Logging operations
│
├── metrics.py                # Analytics calculations (200 lines)
│   ├── Class: MetricsCalculator
│   ├── Streak calculations
│   ├── Completion rates
│   └── Trend analysis
│
├── requirements.txt          # Python dependencies
│   ├── streamlit
│   ├── pandas
│   └── plotly
│
├── README.md                 # Full documentation
├── QUICKSTART.md             # 5-minute setup guide
├── enhancements.py           # Future feature examples
│
└── data/                     # Created at runtime
    └── habits.db             # SQLite database file
```

---

## Extension Points

### Where to Add New Features

**1. New Habit Properties**
- Modify: `database.py` → `habits` table schema
- Update: `app.py` → Add form fields
- Example: Add `category`, `priority`, `target_frequency`

**2. New Metrics**
- Add to: `metrics.py` → New calculation method
- Display in: `app.py` → Dashboard or Analytics page
- Example: `calculate_momentum()`, `predict_next_week()`

**3. New Visualizations**
- Use: Plotly in `app.py`
- Data source: `database.py` queries
- Example: Heatmap, correlation matrix, Gantt chart

**4. Export/Import**
- Add methods to: `database.py`
- UI in: `app.py` → Manage Habits page
- Formats: CSV, JSON, Excel

**5. Notifications**
- Create: `notifications.py` module
- Integrate: `schedule` library
- Call from: Background process or `app.py`

---

## Code Quality Metrics

**Current State:**
- **Lines of Code**: ~900
- **Functions**: 35+
- **Classes**: 2 main classes
- **Comments**: Docstrings on all functions
- **Type Hints**: Used in function signatures

**Maintainability:**
- Modular design ✅
- Clear naming conventions ✅
- Separation of concerns ✅
- No code duplication ✅

---

**Built for extensibility. Start simple, grow as needed.** 🚀
