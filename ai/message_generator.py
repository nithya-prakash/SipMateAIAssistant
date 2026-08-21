import random
from datetime import datetime
from tracker.hydration_tracker import HydrationTracker
from characters.character import Character

class MessageGenerator:
    # Tracks the last message shown per character id, so the same line doesn't
    # repeat twice in a row for that character.
    _last_message = {}

    @staticmethod
    def generate_message(character: Character, tracker: HydrationTracker) -> str:
        base_message = MessageGenerator._pick_message(character)

        now = datetime.now()
        history = tracker.get_reminder_history()

        # Calculate recent streak
        streak = 0
        for row in reversed(history):
            if row[2]: # accepted
                streak += 1
            else:
                break

        # Synthesize personalized AI text based on the character's personality description
        traits = character.personality.lower()
        greeting = ""
        if "confident" in traits or "focused" in traits or "determined" in traits:
            greeting = "Status update: "
        elif "playful" in traits or "energetic" in traits or "cheerful" in traits:
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

    @staticmethod
    def _pick_message(character: Character) -> str:
        messages = character.messages or ["Time for a water break!"]
        if len(messages) == 1:
            return messages[0]

        last = MessageGenerator._last_message.get(character.id)
        candidates = [m for m in messages if m != last] or messages
        choice = random.choice(candidates)
        MessageGenerator._last_message[character.id] = choice
        return choice
