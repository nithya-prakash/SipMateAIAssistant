from tracker.hydration_tracker import HydrationTracker
from collections import Counter

class InsightsEngine:
    def __init__(self, tracker: HydrationTracker):
        self.tracker = tracker
        
    def generate_insights(self) -> dict:
        history = self.tracker.get_reminder_history()
        
        if not history:
            return {
                "best_time": "Need more data",
                "worst_time": "Need more data",
                "consistency": "0%"
            }
            
        # Group by hour
        hour_stats = {}
        for row in history:
            hr, _, accepted = row
            if hr not in hour_stats:
                hour_stats[hr] = {"shown": 0, "accepted": 0}
            hour_stats[hr]["shown"] += 1
            if accepted:
                hour_stats[hr]["accepted"] += 1
                
        # Filter for min 3 shown
        reliable_hours = {hr: stats for hr, stats in hour_stats.items() if stats["shown"] >= 3}
        
        best_time = "Need more data"
        worst_time = "None yet"
        
        if reliable_hours:
            # Sort by success rate = accepted / shown
            rates = [(hr, stats["accepted"] / stats["shown"]) for hr, stats in reliable_hours.items()]
            rates.sort(key=lambda x: x[1])
            
            best_hour = rates[-1][0]
            worst_hour = rates[0][0]
            
            best_time = f"{best_hour % 12 or 12}:00 {'AM' if best_hour < 12 else 'PM'}"
            worst_time = f"{worst_hour % 12 or 12}:00 {'AM' if worst_hour < 12 else 'PM'}"
            
        accepted_total = sum(1 for row in history if row[2])
        consistency = int((accepted_total / len(history)) * 100)
        
        return {
            "best_time": best_time,
            "worst_time": worst_time,
            "consistency": f"{consistency}%"
        }
