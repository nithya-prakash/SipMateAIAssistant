# SipMate
**AI-Powered Animated Wellness Companion**

SipMate is not just another boring notification app. It's a magical desktop companion built for macOS that reminds you to hydrate through delightful, non-intrusive animated characters that float across your screen. 

Powered by local AI and strict macOS overlay policies, SipMate ensures you stay hydrated without ever breaking your flow.

---

##  Features

- **8 SipMate Originals**: Dog, Ghost, Aeroplane, Cat, Penguin, Frog, Rocket, and Sloth - each a real illustrated Lottie animation with its own personality, sound effect, and entrance behavior.
- **Soft, Disney-style Motion**: Characters cross the full screen on arced, bouncy paths (not flat linear slides) and land with a squash-and-stretch bounce; any character without illustrated artwork yet falls back gracefully to hand-drawn vector art or a soft gradient emoji badge instead of breaking.
- **A Sound for Every Character**: Each reminder plays its own short sound effect - a bark, a meow, a launch whoosh - toggleable from Settings.
- **Character Collection & Selection Modes**: Browse, favorite, preview, and pick a character from a dedicated collection window; choose Random, Single Character, Daily Rotation, Favorites, or SipMate Originals-only from Settings.
- **Unobtrusive Overlay**: Characters float natively over full-screen applications (like VS Code, Chrome, or Spotify) without stealing your keyboard focus or cluttering your Dock.
- **AI Adaptive Scheduling**: SipMate learns your habits. A local Logistic Regression model analyzes when you accept or skip water breaks and dynamically adjusts the schedule to your optimal hydration times.
- **Dynamic Messaging**: Characters have personalities! Messages adapt based on your current hydration streak and the time of day, and never repeat the same line twice in a row.
- **Rich Insights Dashboard**: Track your consistency, best hydration hours, and missed times.

##  Demo

![SipMate animated demo](docs/media/demo.gif)

*Dog, rocket, and cat reminders back to back - real illustrated animations, personality-driven messages, and the drink response.*

---

##  Architecture

SipMate is completely background-driven, utilizing `PySide6` for its UI layer and raw `macOS AppKit` APIs to manipulate the window server.

```mermaid
graph TD
    A[macOS Menu Bar] -->|Controls| B(Background Application)
    B --> C{AI Adaptive Scheduler}
    C -->|Trigger| D[Overlay Window]
    D --> E[Character Rendering Pipeline]
    E --> F[Lottie / Vector / Emoji Fallback, per JSON Manifest]
    D --> G[SQLite Hydration Tracker]
    G --> C
```

### Tech Stack
- **Python 3.10+**
- **PySide6** (Qt for Python)
- **PyObjC** (macOS Native Window bindings)
- **scikit-learn** (Local ML modeling)
- **SQLite3** (Persistence)

---

##  Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:nithya-prakash/SipmateAssistant.git
   cd SipmateAssistant
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run SipMate:
   ```bash
   python main.py
   ```

   SipMate runs quietly in the menu bar - a successful launch looks like this:

   ![Terminal demo of installing and launching SipMate](docs/media/terminal_demo.png)

---

##  AI Features

SipMate puts privacy first. It does not send your data to the cloud.
- **Insights Engine**: Parses your local SQLite history to calculate consistency metrics.
- **scikit-learn Scheduler**: Uses binary classification on your hydration logs (accepted vs skipped) based on the hour of the day to predict the highest probability of you drinking water.
- **Procedural Personalities**: The Message Generator synthesizes text using templates driven by your active streak (e.g., "🔥 3x streak!").

---

##  Character Engine

SipMate's characters are completely data-driven - the `CharacterRegistry` loads every manifest in `characters/manifests/`, and `RendererFactory` picks how each one gets drawn. Adding a new character takes only a JSON file, no code changes:

```json
{
  "id": "rocket",
  "name": "Rocket",
  "emoji": "🚀",
  "category": "sipmate_original",
  "personality": "Energetic, motivational",
  "renderer": "lottie",
  "asset": "rocket.json",
  "movement_style": "launch_upward",
  "animation_type": "launch",
  "messages": [
    "3… 2… 1… HYDRATE!",
    "Prepare for hydration launch!",
    "Fuel your body for liftoff!",
    "Mission objective: drink water!"
  ],
  "sound": "rocket.mp3"
}
```

- **`renderer`** is `"lottie"` for a real illustrated animation (`asset` points to a file in `assets/characters/`), or `"static_image"` to use a PNG with graceful fallback to hand-drawn vector art or an emoji badge if no asset exists yet.
- **`movement_style`** drives how the character crosses the screen (`walk_across`, `fly_across`, `float`, `launch_upward`, ...) - entrance and exit share one random side-to-side crossing, not a peek-in-and-retreat.
- **`animation_type`** drives its idle motion once it lands (`bounce`, `float`, `pulse`, `hop`, `sway`, ...), reused across characters rather than hand-authored per character.
- **`sound`** points to a short effect in `sounds/effects/`, played through `AudioPlayer` on every reminder.

---

##  Future Roadmap

- Additional character packs (Seasonal: Santa, Pumpkin), with real illustrated art sourced for each before they ship.
- Multi-monitor explicit targeting (choosing which display the character appears on).
- Apple HealthKit synchronization.

*Stay hydrated! 💧*
