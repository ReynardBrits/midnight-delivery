# Midnight Delivery

**Developer:** Reynard Brits  
**Project:** ITGDA Section A  
**Built with:** Python, PyGame and PyOpenGL

Midnight Delivery is a single-player courier driving game set in a fictional South African coastal town. The player makes deliveries at night while dealing with traffic, blackouts, fuel and vehicle damage.

This README covers Question 2, which is the base implementation, and Question 3, which is the completed game.

## Finding the correct version

| Question | Version | What to run |
| --- | --- | --- |
| Question 2 | Git tag `q2-base-v1` | `main.py` inside the Q2 folder |
| Question 3 | The `main` branch | `main.py` inside the completed game folder |

Question 2 is kept separately so it only includes the base environment, movement and sound.

The `main_2d.py` file in the completed project is a later 2D version. It is not the preserved Question 2 submission.

## Requirements

To run either version from source, you need:

- Python 3.12, preferably the development version, Python 3.12.10.
- PyGame 2.6.1.
- PyOpenGL 3.1.10.
- A graphics driver supporting OpenGL 3.3 Core.
- A keyboard and a display that can show a 1280 × 720 window.
- Speakers or headphones to hear the sound.

The Python packages are listed in `requirements.txt`. Internet access is needed to install them, but the games run offline afterwards.

## Getting both source versions

If Git is installed, run these commands from the folder where you want to keep the projects:

```powershell
git clone --branch q2-base-v1 --single-branch https://github.com/ReynardBrits/midnight-delivery.git MidnightDelivery-Q2

git clone --branch main --single-branch https://github.com/ReynardBrits/midnight-delivery.git MidnightDelivery-Q3
```

This creates separate folders for the base and completed games.

You can also open the repository on GitHub, select the required tag or branch, and choose **Code → Download ZIP**. Extract the ZIP before running the program.

## Installing and running from source

Open PowerShell inside the version's folder, where `main.py` and `requirements.txt` are located.

Run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Follow these steps separately in the Q2 and Q3 folders. If that folder already has a working virtual environment, you only need the final command.

---

## Question 2 - Base implementation

### What I implemented

For Question 2, I created the town, courier car, movement, collisions and background ambience. This version uses a top-down view and allows the player to drive around freely.

The map is 2560 × 1920 pixels. It includes connected roads, buildings, a depot, a park and a waterfront. The different areas help the player recognise where they are. Buildings and other solid obstacles stop the car from driving through them.

The car accelerates gradually, brakes and reverses. The camera follows it around the map. Movement uses fixed updates at 120 Hz, with interpolation between updates to make the drawing smoother. The target frame rate is 60 FPS.

The environment and car are drawn using shapes made in code. The background sound is also generated in code and played through PyGame.

Delivery jobs, scoring, traffic, fuel and the 3D improvements are part of Question 3.

### Question 2 controls

| Key | Action |
| --- | --- |
| W or Up | Accelerate |
| S or Down | Brake, then reverse |
| A / D or Left / Right | Steer |
| Space | Strong brake |
| R | Reset the car to its starting position |
| M | Mute or unmute the ambience |
| Escape | Exit |

### What to try

1. Run `main.py` in the Q2 folder.
2. Drive along the roads and turn at a junction.
3. Visit the depot, park and waterfront.
4. Try braking, reversing and gently driving into a building.
5. Press R to reset the car and M to test mute.

This stage is free driving, so there are no delivery objectives or win screen. Switching away from the window pauses movement and ambience. Returning to the window restores them.

The title bar displays speed in pixels per second in this version.

---

## Question 3 - Completed game

### What I added

For Question 3, I expanded the base idea into a 3D delivery game. It has a larger town, a camera that follows behind the car, nine delivery jobs, traffic, scoring, fuel and vehicle condition.

The town is 3360 × 3200 game units and includes the Centre, Harbour, Gardens and Southbank areas. The Eduvos campus is a recognisable landmark and one of the delivery destinations.

Other additions include headlights, street lighting, fog, a map, delivery markers, engine sounds, event effects, menus and saved records.

### Question 3 controls

| Key | Action |
| --- | --- |
| Enter | Start, resume or replay |
| W or Up | Accelerate |
| S or Down | Brake, then reverse |
| A / D or Left / Right | Steer |
| Space | Strong brake |
| E | Collect a parcel, deliver it or advance a completed shift |
| F | Repair at the depot using points |
| G | Refuel at the depot using points |
| Tab | Show or hide the map |
| Mouse wheel | Adjust camera zoom |
| Z / C | Temporarily look left or right |
| L | Toggle headlights |
| M | Mute or unmute sound |
| P | Pause or resume |
| F1 | Open or close the controls screen |
| F12 | Save a screenshot |
| R | Restart the entire night |
| Escape | Close help, or exit |

Opening help pauses the game. Switching to another window also pauses it. Return and press P or Enter to resume.

### How to play

1. Press Enter to start.
2. Stop inside the marked depot bay and press E to collect a parcel.
3. Follow the navigation marker and map to the destination.
4. Stop inside the delivery bay and press E to hand over the parcel.
5. Return to the depot for the next job.
6. After the third delivery in shift 1 or 2, press E at the depot to advance, then E again to load the next parcel.

The centre of the car must be inside the bay and the car must be nearly stopped before collecting or delivering.

| Shift | Delivery area | Traffic cars |
| --- | --- | --- |
| 1 | Centre | 2 |
| 2 | Harbour | 4 |
| 3 | Gardens and Southbank | 6 |

Complete all nine deliveries to finish the night. If fuel or vehicle condition reaches zero first, the run ends. Fuel, condition and score carry forward between shifts.

### Scoring and parcel types

Standard deliveries earn base points and a time bonus of up to 50 points. The more time remaining, the larger the bonus.

Express deliveries earn half their base reward if they are late. Fragile parcels lose condition during collisions, which reduces their reward. Repairing the car does not repair the parcel.

Late or fully damaged parcels can still be delivered so the player can continue the night.

### Blackouts and traffic lights

Power cuts rotate through the four districts. Each cycle has 25 seconds with power on, followed by 35 seconds with one district dark. A warning appears eight seconds before the cut.

The affected streetlights, windows and signs become dark. Headlights and delivery markers remain available. A successful delivery to a destination currently affected by the blackout earns a 25% bonus, rounded down.

Two central junctions have traffic lights. Crossing a red stop line costs up to 20 points, without taking the score below zero. Traffic cars stop for red and amber signals. During a Centre blackout, the signals switch off and red-light penalties stop.

### Fuel and repairs

Fuel is used while driving and idling during active play.

At the depot:

- F repairs up to 25 vehicle condition, costing one point per condition restored.
- G adds up to 40 fuel units, costing 1.5 points per unit, rounded up.

The player needs enough points to pay for the quoted service. Careful driving saves repair costs and protects fragile parcels.

### Graphics and sound

The completed game uses low-poly models made from shapes in code. The buildings, vehicles and props follow the same style.

The camera turns smoothly with the car. A silhouette helps show the car when a building blocks it. Speed is displayed in km/h using an arcade scale, with a maximum forward speed of 90 km/h.

The audio includes night ambience, blended engine tones and effects for deliveries, collisions and warnings. Separate mixer channels allow these sounds to play together.

### Saved data

The source version creates these files when needed:

- `save_data/records_3d.json` stores the best completed-night score and completed-night count.
- `save_data/settings_3d.json` stores preferences such as sound, headlights, map visibility and zoom.
- `captures/` stores screenshots taken with F12.

Unfinished nights are not saved. Pressing R starts the whole night again.

### Changes from the earlier design

I changed the original overhead 2D presentation to a 3D town with a lower follow camera because it gives the buildings and vehicle more detail.

The larger map adds different districts and the campus landmark. Blackouts and traffic signals also make the night setting affect gameplay.

I kept one playable vehicle and one town so the project remained manageable. Multiplayer and saving unfinished runs were left out of the final scope.

---

## Main source files

| File or group | Purpose |
| --- | --- |
| `main.py` | Starts the version in its folder |
| `world.py`, `car.py`, `camera.py`, `renderer.py` | Base town, movement, camera and drawing |
| `audio.py` | Generated ambience, engine sounds and effects |
| `game_3d.py` | Runs the completed 3D game |
| `delivery.py`, `fuel.py` | Delivery progression, rewards, repairs and fuel |
| `traffic.py`, `signals3d.py`, `blackouts3d.py` | Traffic, signals, penalties and power cuts |
| `renderer3d.py`, `lighting3d.py` | 3D rendering and lighting |
| `buildings3d.py`, `campus3d.py`, `scenery3d.py`, `vehicles3d.py` | Town and vehicle models |
| `hud.py`, `minimap.py`, `screens.py`, `interface3d.py`, `controls3d.py` | Dashboard, navigation, menus and help |
| `records.py`, `preferences3d.py` | Saved records and settings |
| `effects3d.py`, `visibility3d.py` | Visual effects and the obscured-car silhouette |

The Q2 folder contains only the files needed for the base implementation.

## Playing the completed Windows build

The completed game is also available without installing Python:

[Download Midnight Delivery for Windows](https://github.com/ReynardBrits/midnight-delivery/releases/download/v1.0.0-Windows/MidnightDelivery-Windows.zip)

1. Download the ZIP.
2. Extract the whole folder.
3. Open the extracted folder and run `MidnightDelivery.exe`.
4. Keep the `_internal` folder with the executable.

This download is Question 3. Question 2 must be run from its separate base source version.

## Checks for the marker

For Q2, check the environment, movement, collisions, camera and ambience.

For Q3, complete a delivery, test the different parcel types, observe a blackout and try a red-light penalty after earning points. Also check repair, refuelling, pause, help and restart.

Completing all nine jobs checks the final result screen. Closing and reopening the game checks saved preferences and the completed-night record.

Both versions target 60 FPS, but performance depends on the computer and graphics driver.

## Assets and acknowledgements

The town layout, models, signs, vehicles, parcels and sounds were developed for this project using code. No external game asset packs are needed. The interface uses PyGame's bundled default font.


## References

- Python documentation: https://docs.python.org/3.12/
- PyGame display: https://www.pygame.org/docs/ref/display.html
- PyGame events: https://www.pygame.org/docs/ref/event.html
- PyGame timing: https://www.pygame.org/docs/ref/time.html
- PyGame sound: https://www.pygame.org/docs/ref/mixer.html
- PyOpenGL: https://pyopengl.sourceforge.net/