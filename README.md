# Midnight Delivery

A single-player courier driving game set in a fictional South African
coastal town. Complete nine deliveries across three shifts while managing
deadlines, traffic, vehicle damage, fragile cargo and fuel.

Developed by Reynard Brits using Python, PyGame and PyOpenGL.

## Submission versions

- `main` contains the Question 3 game implementation.
- The separate Question 2 base implementation is preserved at
  [q2-base-v1](https://github.com/ReynardBrits/midnight-delivery/tree/q2-base-v1).
- The instructions below describe the Question 3 version.

## Features

- A 3360 x 2560 town with Centre, Harbour and Gardens districts.
- A top-down view with raised building faces, roof details and shadows.
- Nine distinct destinations and standard, express and fragile contracts.
- Smooth acceleration, braking, reversing and speed-dependent steering.
- Rotated vehicle collisions, vehicle damage and paid depot repairs.
- Two, four and six active traffic vehicles across the three shifts.
- A following camera, destination arrow and toggleable minimap.
- Visible roof parcels that match the loaded contract and fragile damage.
- Fuel consumption, low-fuel warnings and paid depot refuelling.
- A dashboard, title screen, pause screen and win/failure results.
- Generated ambience, engine sounds and gameplay sound effects.
- Saved best completed-night score and completed-night count.

## Requirements

The Windows development setup uses:

- Python 3.12.10, 64-bit.
- PyGame 2.6.1.
- PyOpenGL 3.1.10.
- Graphics hardware and a driver supporting OpenGL 3.3 Core.
- A keyboard and a display that can accommodate the 1280 x 720 window.
- An audio output device for sound playback.

The window size is fixed at 1280 x 720. Rendering targets 60 frames per
second and physics uses a fixed 120 Hz update step with interpolation.
Actual performance depends on the computer.

## Installation

### 1. Obtain the project

Using Git:

```powershell
git clone https://github.com/ReynardBrits/midnight-delivery.git
cd midnight-delivery
```

Alternatively, extract the supplied source ZIP and open a terminal in the
folder containing `main.py` and `requirements.txt`.

### 2. Create the environment

```powershell
py -3.12 -m venv .venv
```

### 3. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

These commands use the environment's Python directly; activation is not
required. Internet access is needed to download dependencies. Once they
are installed, the game runs locally without an internet connection.

## Run the game

From the project folder:

```powershell
.\.venv\Scripts\python.exe main.py
```

Click the game window if necessary, then press Enter to start.

## Controls

| Input | Action |
| --- | --- |
| Enter | Start, resume or play again |
| W / Up Arrow | Accelerate forward; brake first if reversing |
| S / Down Arrow | Brake while moving forward, then reverse |
| A / Left Arrow | Steer left |
| D / Right Arrow | Steer right |
| Space | Apply the stronger brake |
| E | Collect, deliver or advance to the next shift at the marked bay |
| F | Buy vehicle repairs while stopped in the depot bay |
| G | Buy fuel while stopped in the depot bay |
| Tab | Show or hide the minimap during play |
| P | Pause or resume |
| M | Mute or unmute all game audio |
| R | Restart the entire night from shift 1 |
| Escape / window close | Exit |

Steering becomes effective as the car moves. Stop inside a marked bay
before interacting; hold Space to brake fully.

Switching to another window pauses the game automatically. Return to the
game and press Enter or P to resume. Movement, traffic, delivery timers
and fuel consumption remain frozen while paused.

## How to play

1. Drive to the depot bay in the north-west of the town.
2. Stop inside the bay and press E to collect the next parcel.
3. Follow the destination marker, arrow and minimap to its delivery bay.
4. Stop inside the destination bay and press E to deliver.
5. Return to the depot for each new parcel.
6. After the third delivery of shifts 1 and 2, return to the depot and
   press E to start the next shift. Press E again to collect its parcel.
7. Complete all nine deliveries to finish the night and save your result.

The contract order is fixed. Shift 1 visits Centre, shift 2 visits Harbour
and shift 3 visits Gardens. Active central traffic increases with each
shift. Use the depot for repairs and fuel before taking a longer route.

## Contracts and scoring

A delivery timer starts when its parcel is collected. The time bonus is
up to 50 points, proportional to the fraction of time remaining and
rounded down.

| Contract | Payout rule |
| --- | --- |
| Standard | Base reward plus time bonus |
| Express | Base reward plus time bonus if on time; half the base reward, rounded down, if late |
| Fragile | Base reward plus time bonus, multiplied by remaining cargo condition and rounded down |

Actual vehicle damage reduces fragile cargo condition by twice the
vehicle condition lost. Braking alone does not damage the parcel.
Repairing the car does not restore cargo condition.

An expired timer removes the time bonus but does not prevent delivery.
A fully damaged fragile parcel can still be delivered for zero points.

The final score is total delivery payouts minus repair and fuel charges.
Each contract awards its payout once.

## Vehicle condition and fuel

- Each new night starts with 100% vehicle condition and 100 fuel units.
- These resources carry across shifts; changing shifts does not refill
  or repair the car.
- F repairs up to 25 condition at the depot. The cost is one score point
  per condition restored, rounded up.
- G buys up to 40 fuel units at the depot. The cost is 1.5 score points per
  unit added, rounded up; 40 units cost 60 points.
- A purchase requires enough earned score points. The dashboard shows
  the fuel quote while stopped in the depot bay.
- Fuel drains while driving and idling during active play. The low-fuel
  threshold is 15 units.
- Zero vehicle condition or zero fuel ends the night. Enter or R starts
  a fresh night from shift 1.

## Saved records

Completing all nine deliveries updates the best completed-night score
and completed-night count in `save_data/records.json` beside the source
files. The title and results screens display these records.

Failed, restarted and unfinished nights do not update the record.
In-progress nights are not saved. Restarting or closing the game loses
the current run, while previously saved completed-night records remain.

The `save_data` folder is excluded from Git. If writing fails, the game
keeps the result for the current session and displays a notice.

## Marker checks

| Check | Expected behaviour |
| --- | --- |
| Launch and press Enter | The night starts with full condition and fuel |
| Drive, brake and reverse | Movement is smooth and changes direction after braking |
| Collect and deliver | A parcel appears, the timer starts and delivery awards points |
| Hit an obstacle at speed | Vehicle condition decreases; loaded fragile cargo can also lose condition |
| Use F at the depot | Condition increases and score pays for the repair |
| Use G at the depot | Fuel increases, score decreases and fuel spending increases |
| Press Tab | The minimap hides or reappears |
| Pause or switch windows | Movement, traffic, timers and fuel freeze |
| Press M twice | Audio mutes and returns |
| Finish three deliveries | Returning to the depot allows the next shift to start |
| Finish nine deliveries | The completion screen appears and the record is saved |
| Relaunch after completion | The saved best score and finished count remain |
| Run out of condition or fuel | The appropriate failure screen appears |
| Press R | The entire night resets; saved records remain |

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Window, input, scene transitions, game loop and fuel integration |
| `world.py` | District layout, scenery, lettering and static obstacles |
| `car.py` | Driving, collision checks, damage, lights and cargo artwork |
| `camera.py` | Camera tracking and world-to-screen coordinates |
| `renderer.py` | OpenGL shaders and batched shape rendering |
| `delivery.py` | Contracts, progression, timers, rewards, repairs and navigation |
| `fuel.py` | Fuel consumption and refill calculations |
| `traffic.py` | Traffic routes, movement and obstacle bounds |
| `minimap.py` | Town overview, player, depot and destination markers |
| `hud.py` | Driving dashboard and contextual information |
| `screens.py` | Title, pause, completion and failure screens |
| `records.py` | Loading and saving completed-night records |
| `audio.py` | Generated ambience, engine sounds and effects |
| `requirements.txt` | Pinned Python dependencies |

## Artwork, audio and assistance

Game scenery, vehicles, parcels and minimap graphics are constructed by
the project's code. Wind, crickets, engine sounds and gameplay effects
are generated in `audio.py`. No downloaded image packs, music or sound
recordings are required. Interface text uses PyGame's bundled default
font; world signs use code-defined pixel lettering.

Third-party libraries are PyGame and PyOpenGL. ChatGPT assisted with
planning, code generation, troubleshooting and documentation.

## Troubleshooting

- **Python 3.12 is not found:** run `py --list` and check that Python 3.12
  is installed before creating the environment.
- **A module is missing:** install `requirements.txt` using the project's
  environment Python, then launch using that same executable.
- **OpenGL context error:** check graphics-driver and OpenGL 3.3 Core
  support.
- **No sound:** check the computer's output device, volume and the game's
  sound status. Press M if muted. If unavailable, check the terminal for
  the audio error; the game can continue without sound.
- **The car does not respond:** click the game window and press Enter or
  P if paused. After failure, press Enter or R to start again.
- **A record cannot be saved:** extract the project into a writable
  folder and check the notice on the results screen.