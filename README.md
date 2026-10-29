# Midnight Delivery

A single-player, top-down delivery driving game set in a fictional
South African coastal town.

Developed by Reynard Brits using Python, PyGame and PyOpenGL.

## Development status

This is the Question 2 base implementation.

The player can explore the town, drive the delivery car, test collisions
and listen to night-time ambience.

Delivery contracts, traffic, fuel, cargo condition, scoring and shift
progression are planned for the Question 3 implementation.

## Implemented features

- A 2560 × 1920 town viewed through a 1280 × 720 game window.
- Connected streets, pavements and pedestrian crossings.
- Residential, commercial and industrial building colours.
- A delivery depot with a marked loading bay.
- A northern park with trees in raised beds.
- An eastern waterfront.
- Streetlights, roof details, windows and shop awnings.
- A delivery car with mirrors, a roof rack and a strapped parcel.
- Acceleration, braking, reversing and speed-dependent steering.
- Rotated car collision checks against buildings and other obstacles.
- Map boundaries and a blocked water area.
- A following camera that stops scrolling at the map edges.
- Brake lights and reverse lights.
- Generated wind and cricket ambience.
- Sound muting and automatic pausing when the window loses focus.

## Requirements

The development setup uses:

- Windows.
- Python 3.12.10.
- PyGame 2.6.1.
- PyOpenGL 3.1.10.
- Graphics hardware and a driver supporting OpenGL 3.3 Core.
- An audio output device for sound playback.

The window resolution is fixed at 1280 × 720.

The game targets 60 rendered frames per second, with movement calculated
using a fixed 120 Hz update step. Actual performance depends on the
computer.

## Installation

### 1. Obtain the project

Using Git:

```powershell
git clone https://github.com/ReynardBrits/midnight-delivery.git
cd midnight-delivery
```

Alternatively, extract the supplied project ZIP and open a terminal
inside the folder containing `main.py` and `requirements.txt`.

### 2. Create the Python environment

```powershell
py -3.12 -m venv .venv
```

### 3. Install the dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

These commands use the environment's Python directly. Activating the
environment is not required.

## Running the game

Run this command from the project folder:

```powershell
.\.venv\Scripts\python.exe main.py
```

Click the game window if it does not have keyboard focus.

Once the dependencies are installed, the game runs locally without an
internet connection.

## Controls

| Input | Action |
| --- | --- |
| W or Up Arrow | Accelerate forward; brake first if reversing |
| S or Down Arrow | Brake while moving forward, then reverse |
| A or Left Arrow | Steer left |
| D or Right Arrow | Steer right |
| Space | Apply the stronger brake |
| R | Reset the car to its starting position |
| M | Mute or unmute the ambience |
| Escape | Close the game |
| Window close button | Close the game |

Steering becomes effective as the car starts moving.

Movement and ambience pause when another window has keyboard focus.
They resume when the game regains focus.

The window title displays speed in pixels per second and the sound
status.

## Exploring the base game

1. Accelerate and follow the connected streets.
2. Turn at intersections to explore different parts of the town.
3. Find the depot and loading bay in the north-west.
4. Visit the park near the northern road.
5. Drive east to find the waterfront.
6. Test braking, reversing and collisions.
7. Press R whenever you want to return to the starting position.

This stage is a free-driving demonstration of the environment and
movement. There is no delivery objective, score or win condition yet.

## Checks for the marker

| Check | Expected behaviour |
| --- | --- |
| Launch the game | The town and delivery car appear |
| Accelerate and steer | The car moves and turns smoothly |
| Brake and reverse | The car slows before changing direction |
| Brake lights | Rear lights brighten while braking |
| Reverse lights | Small white rear lights appear while reversing |
| Approach an obstacle | The car is prevented from entering it |
| Explore the map | The camera follows and stops at map edges |
| Press R | The car returns to its starting position |
| Press M twice | Sound mutes, then returns |
| Switch windows | Movement and sound pause, then resume on return |
| Press Escape | The program closes |

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Window setup, input, game loop and application cleanup |
| `world.py` | Town layout, scenery and obstacle definitions |
| `car.py` | Car artwork, driving, collision checks and vehicle lights |
| `camera.py` | Camera tracking and world-to-screen coordinates |
| `renderer.py` | OpenGL shaders and rectangle rendering |
| `audio.py` | Generated ambience and playback controls |
| `requirements.txt` | Pinned Python dependencies |
| `.gitignore` | Excludes the local environment and temporary files |

## Visuals, audio and development assistance

The environment and vehicle artwork are constructed programmatically
using coloured OpenGL shapes.

The wind, low background hum and cricket sounds are generated in
`audio.py`. This base version does not load downloaded image packs,
music or sound recordings.

Third-party libraries:

- PyGame: window handling, input, timing and sound playback.
- PyOpenGL: access to OpenGL rendering functions.

ChatGPT assisted with planning, code generation and documentation.

## Troubleshooting

### Python 3.12 cannot be found

Check the installed Python versions:

```powershell
py --list
```

Python 3.12 must be installed before creating the environment with the
installation command above.

### A Python module cannot be found

Install the dependencies again using the project environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then launch the game using the environment's Python executable.

### An OpenGL context error appears

The game requires OpenGL 3.3 Core support from the graphics hardware
and its driver.

### There is no sound

- Click the game window so that it has keyboard focus.
- Check the computer's output volume and selected audio device.
- Check the sound status in the window title.
- If it says `Muted`, press M.
- If it says `Unavailable`, check the terminal for the audio error.

The game can continue running if audio initialisation fails.