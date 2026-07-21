import random
from datetime import datetime
from tracker.hydration_tracker import HydrationTracker
from characters.character import Character

class MessageGenerator:
    @staticmethod
    def generate_message(character: Character, tracker: HydrationTracker) -> str:
        base_message = random.choice(character.messages)
        
        now = datetime.now()
        history = tracker.get_reminder_history()
        
        # Calculate recent streak
        streak = 0
        for row in reversed(history):
            if row[2]: # accepted
                streak += 1
            else:
                break
                
        # Synthesize personalized AI text based on traits
        greeting = ""
        if "professional" in character.personality_traits:
            greeting = "Status update: "
        elif "playful" in character.personality_traits:
            greeting = "Hey there! "
            
        context = ""
        if streak >= 3:
            context = f"🔥 {streak}x streak! Keep it up!\n"
        elif streak == 0 and len(history) > 0:
            context = "Let's get back on track.\n"
        elif now.hour < 11:
            context = "Morning hydration!\n"
        elif now.hour > 17:
            context = "Evening check-in.\n"
            
        # 60% chance to inject dynamic AI context
        if random.random() > 0.4 and (greeting or context):
            return f"{greeting}{context}{base_message}"
            
        return base_message
