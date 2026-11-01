# Midnight Delivery

A single-player courier game set in a fictional South African coastal town.
Complete nine deliveries across three shifts while managing deadlines,
traffic, vehicle condition, fragile parcels and fuel.

Developed by Reynard Brits using Python, PyGame and PyOpenGL, with AI assistance.

## Requirements

- Python 3.12, 64-bit; development version: 3.12.10.
- PyGame 2.6.1 and PyOpenGL 3.1.10, pinned in `requirements.txt`.
- A graphics driver supporting OpenGL 3.3 Core.
- A keyboard and a display supporting a 1280 x 720 window.
- Audio output for sound; the game continues if audio is unavailable.
- Speed is displayed in km/h using an arcade scale: maximum forward speed is 90 km/h and maximum reverse speed is 27 km/h.

The game targets 60 FPS and uses fixed 120 Hz physics. Performance depends
on the computer. A compatible display format is selected if multisampling
or a stencil buffer is unavailable.

## Install and run on Windows

Open PowerShell in the project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

If the environment already exists, run only the final command.
The game works offline after its dependencies have been installed.

## Controls

| Key | Action |
| --- | --- |
| Enter | Start, resume or replay |
| W / Up | Accelerate |
| S / Down | Brake, then reverse |
| A / D or Left / Right | Steer |
| Space | Strong brake |
| E | Load, deliver or advance the shift at the active bay |
| F | Repair at the depot using score points |
| G | Refuel at the depot using score points |
| Tab | Toggle the north-up map |
| Z / C | Look left / right; release to recenter |
| Mouse wheel | Zoom |
| L | Toggle headlights |
| M | Mute / unmute |
| P | Pause / resume |
| F1 | Open / close controls help |
| F12 | Save a screenshot in `captures/` |
| R | Restart the entire night |
| Escape | Close help, or exit the game |

Opening help during play pauses the night. F1 or Escape returns to the
previous screen. P or Enter can resume from help. Switching away from the
game pauses play; return and press P or Enter to resume.

## How to play

1. Press Enter and drive to the teal depot bay.
2. Stop inside the active bay and press E to load a parcel.
3. Follow the map, arrow and floating beacon to the destination.
4. Stop inside the destination bay and press E to deliver.
5. Return to the depot for the next parcel. After the first two shifts,
   press E at the depot to start the next shift, then E again to load.
6. Finish all nine deliveries to complete the night and save your score.

Standard deliveries pay base points plus a time bonus. Express deliveries
lose their time bonus and pay half base points when late. Damage reduces
fragile parcel value; repairs restore the car, not the parcel. Late and
fully damaged parcels can still be delivered, allowing progression.

Traffic grows from two to four to six cars. Fast impacts damage the car.
Fuel is consumed while driving and idling during active play. At the depot,
F repairs up to 25 condition for one point per condition restored. G adds
up to 40 fuel units for 1.5 points per unit, rounded up. Both reduce score.
Vehicle condition reaching zero or an empty fuel tank ends the night.

## Saves and screenshots

- `save_data/records_3d.json`: best completed-night score and completed count.
- `save_data/settings_3d.json`: mute, headlights, map visibility and zoom;
  saved when exiting normally.
- `captures/`: PNG screenshots saved by F12, including the visible interface.

Unfinished nights are not saved. R starts a fresh night. Invalid save files
fall back to defaults, and write failures are reported without ending play.

## Versions

- `main.py`: launcher for the 3D game.
- `game_3d.py`: 3D campaign implementation.
- `preview_3d.py`: separate graphics and driving preview.
- `main_2d.py`: retained 2D campaign.
- Git tag `q2-base-v1`: preserved Question 2 base implementation.

## Assets and credits

Buildings, vehicles, signs, parcels, markers and particles are generated
from code. Night ambience, engine loops and effects are procedurally
synthesised. The interface uses PyGame's bundled default font. No external
game asset packs are required. AI-assisted concept art guided the visual
direction; the running game renders procedural geometry rather than that
concept image. Development and documentation used AI assistance.

## Quick checks

- Start a night, collect a parcel and complete a delivery.
- Try braking, reversing, traffic avoidance, repairs and refuelling.
- Check pause, focus loss, F1 help, F12 screenshots and R restart.
- Exit and reopen to check saved preferences.
- Complete all nine deliveries to check the result screen and saved record.