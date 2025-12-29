"""
Metrics calculation for habit tracker
Calculates streaks, completion rates, and trends
"""

from datetime import date, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict


class MetricsCalculator:
    """Calculate various metrics for habit tracking"""
    
    @staticmethod
    def calculate_daily_completion(logs: List[Dict]) -> float:
        """Calculate completion percentage for a day"""
        if not logs:
            return 0.0
        
        completed = sum(1 for log in logs if log['completed'])
        return (completed / len(logs)) * 100
    
    @staticmethod
    def calculate_streak(habit_logs: List[Dict], current_date: date = None) -> Dict:
        """
        Calculate current streak for a habit
        Returns: {current_streak: int, longest_streak: int}
        """
        if not habit_logs:
            return {"current_streak": 0, "longest_streak": 0}
        
        if current_date is None:
            current_date = date.today()
        
        # Sort logs by date
        sorted_logs = sorted(
            [log for log in habit_logs if log['completed']], 
            key=lambda x: x['log_date'],
            reverse=True
        )
        
        if not sorted_logs:
            return {"current_streak": 0, "longest_streak": 0}
        
        # Calculate current streak
        current_streak = 0
        check_date = current_date
        
        for log in sorted_logs:
            log_date = log['log_date']
            if isinstance(log_date, str):
                log_date = date.fromisoformat(log_date)
            
            if log_date == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            elif log_date < check_date:
                break
        
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 0
        prev_date = None
        
        for log in reversed(sorted_logs):
            log_date = log['log_date']
            if isinstance(log_date, str):
                log_date = date.fromisoformat(log_date)
            
            if prev_date is None or (log_date - prev_date).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
            
            prev_date = log_date
        
        return {
            "current_streak": current_streak,
            "longest_streak": max(longest_streak, current_streak)
        }
    
    @staticmethod
    def calculate_consistency(habit_logs: List[Dict], days: int = 30) -> float:
        """
        Calculate consistency percentage over last N days
        """
        if not habit_logs:
            return 0.0
        
        completed_count = sum(1 for log in habit_logs if log['completed'])
        return (completed_count / days) * 100 if days > 0 else 0.0
    
    @staticmethod
    def calculate_weekly_stats(all_logs: List[Dict], start_date: date, 
                               end_date: date) -> Dict:
        """Calculate weekly completion statistics"""
        # Group logs by week
        weekly_data = defaultdict(lambda: {"total": 0, "completed": 0})
        
        current_date = start_date
        while current_date <= end_date:
            week_start = current_date - timedelta(days=current_date.weekday())
            week_key = week_start.isoformat()
            
            day_logs = [log for log in all_logs if log['log_date'] == current_date]
            
            if day_logs:
                weekly_data[week_key]["total"] += len(day_logs)
                weekly_data[week_key]["completed"] += sum(1 for log in day_logs if log['completed'])
            
            current_date += timedelta(days=1)
        
        # Calculate percentages
        weekly_percentages = {}
        for week, data in weekly_data.items():
            if data["total"] > 0:
                weekly_percentages[week] = (data["completed"] / data["total"]) * 100
            else:
                weekly_percentages[week] = 0.0
        
        return weekly_percentages
    
    @staticmethod
    def get_habit_completion_trend(habit_logs: List[Dict], days: int = 30) -> List[Dict]:
        """Get daily completion trend for a habit"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        # Create date range
        trend_data = []
        current = start_date
        
        while current <= end_date:
            log = next(
                (l for l in habit_logs if l['log_date'] == current),
                None
            )
            
            trend_data.append({
                "date": current,
                "completed": log['completed'] if log else False
            })
            
            current += timedelta(days=1)
        
        return trend_data
    
    @staticmethod
    def calculate_monthly_summary(all_logs: List[Dict], month: int, year: int) -> Dict:
        """Calculate summary statistics for a specific month"""
        # Filter logs for the specified month
        month_logs = [
            log for log in all_logs 
            if (isinstance(log['log_date'], date) and 
                log['log_date'].month == month and 
                log['log_date'].year == year) or
               (isinstance(log['log_date'], str) and 
                date.fromisoformat(log['log_date']).month == month and
                date.fromisoformat(log['log_date']).year == year)
        ]
        
        if not month_logs:
            return {
                "total_habits": 0,
                "total_completions": 0,
                "completion_rate": 0.0,
                "days_tracked": 0
            }
        
        # Group by date
        dates = set()
        total_completions = 0
        total_possible = len(month_logs)
        
        for log in month_logs:
            log_date = log['log_date']
            if isinstance(log_date, str):
                log_date = date.fromisoformat(log_date)
            dates.add(log_date)
            
            if log['completed']:
                total_completions += 1
        
        return {
            "total_habits": len(set(log['habit_id'] for log in month_logs)),
            "total_completions": total_completions,
            "completion_rate": (total_completions / total_possible * 100) if total_possible > 0 else 0.0,
            "days_tracked": len(dates)
        }
