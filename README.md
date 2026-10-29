# Midnight Delivery

A top-down delivery driving game developed with Python, PyGame and PyOpenGL.

## Development status

The project is currently building the Question 2 base implementation.

Currently implemented:
- OpenGL 3.3 game window.
- Town intersection with roads, pavements and buildings.
- Delivery depot loading bay.
- Stationary delivery car.
- Escape key and window-close handling.

Planned features include driving, collisions, deliveries, traffic, fuel,
parcel damage, scoring and three progressively harder shifts.

## Requirements

- Windows 10 or 11.
- Python 3.12.
- Graphics hardware and drivers supporting OpenGL 3.3.
- PyGame 2.6.1.
- PyOpenGL 3.1.10.

## Installation

Clone the repository and open its folder:

```powershell
git clone https://github.com/ReynardBrits/midnight-delivery.git
cd midnight-delivery
```

Create a Python environment:

```powershell
py -3.12 -m venv .venv
```

Install the dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Running the game

From the project folder, run:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Current controls

- Escape: close the game.
- Window close button: close the game.

Driving controls will be added during development.

## Project files

- main.py: window setup, game loop and town scene.
- renderer.py: OpenGL shaders and rectangle drawing.
- requirements.txt: required Python libraries.
- .gitignore: excludes the local environment and temporary files.

## Academic project

This repository contains the development history for the Midnight Delivery
game development project.