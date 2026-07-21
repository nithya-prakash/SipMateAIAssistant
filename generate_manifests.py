import json
import os

manifests = [
    {"id": "airplane", "renderer": "vector", "behavior": "fly_across", "personality": "professional", "messages": ["Hydration flight incoming 💧\nDrink some water!", "Cruising altitude reached.\nTime for a water break!"], "effects": ["smoke_trail", "propeller"], "duration": 15},
    {"id": "cat", "renderer": "vector", "behavior": "walk_across", "personality": "lazy", "messages": ["Meow 😺\nEven cats need water.", "Purrfect time for a drink!"], "effects": ["tail_swish", "blink"], "duration": 15},
    {"id": "dog", "renderer": "vector", "behavior": "walk_across", "personality": "playful", "messages": ["Woof! Did you drink water today?", "Fetch some water!"], "effects": ["tail_wag"], "duration": 12},
    {"id": "girl", "renderer": "vector", "behavior": "walk_to_center", "personality": "caring", "messages": ["I needed my water break.\nYou need yours too 💙"], "effects": ["sip_water", "wave"], "duration": 10},
    {"id": "rocket", "renderer": "vector", "behavior": "launch_upward", "personality": "energetic", "messages": ["Blast off to hydration! 🚀"], "effects": ["fire_particles"], "duration": 8},
    {"id": "robot", "renderer": "vector", "behavior": "teleport", "personality": "robotic", "messages": ["Beep boop.\nLiquid coolant levels low. Please refill.", "System check:\nHydration required."], "effects": ["glitch"], "duration": 10},
    {"id": "penguin", "renderer": "vector", "behavior": "walk_across", "personality": "cool", "messages": ["Stay cool. Drink water. 🐧"], "effects": ["waddle"], "duration": 15},
    {"id": "panda", "renderer": "vector", "behavior": "appear_center", "personality": "chill", "messages": ["Take a bamboo... I mean water break. 🐼"], "effects": ["chew"], "duration": 12},
    {"id": "butterfly", "renderer": "vector", "behavior": "fly_across", "personality": "gentle", "messages": ["Flutter by for a sip of water. 🦋"], "effects": ["flap_wings"], "duration": 10},
    {"id": "ghost", "renderer": "vector", "behavior": "float", "personality": "spooky", "messages": ["Boo! 👻\nDid I scare you into drinking water?"], "effects": ["fade"], "duration": 10},
    {"id": "cow", "renderer": "vector", "behavior": "walk_across", "personality": "funny", "messages": ["Mooooove to the water bottle! 🐄"], "effects": ["chew"], "duration": 15},
    {"id": "wizard", "renderer": "vector", "behavior": "teleport", "personality": "wise", "messages": ["A wizard is never dehydrated. 🧙‍♂️"], "effects": ["magic_sparkles"], "duration": 12},
    {"id": "alien", "renderer": "vector", "behavior": "float", "personality": "quirky", "messages": ["Greetings Earthling.\nConsume H2O. 👽"], "effects": ["hover"], "duration": 10},
    {"id": "dragon", "renderer": "vector", "behavior": "fly_across", "personality": "fierce", "messages": ["Quench your fire with water! 🐉"], "effects": ["breathe_fire"], "duration": 12},
    {"id": "eiffel_tower", "renderer": "vector", "behavior": "appear_center", "personality": "elegant", "messages": ["Even monuments need maintenance.\nYou need hydration too. 🗼"], "effects": ["sparkle"], "duration": 10}
]

os.makedirs("characters/manifests", exist_ok=True)
for m in manifests:
    with open(f"characters/manifests/{m['id']}.json", "w") as f:
        json.dump(m, f, indent=4)
