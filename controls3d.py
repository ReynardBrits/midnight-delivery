"""Controls screen and screenshots of the rendered game window."""

import ctypes
from datetime import datetime
from pathlib import Path

import pygame
from OpenGL import GL

from interface3d import Screens3D


class GameScreens(Screens3D):
    def compose(
        self, mode, delivery,
        car, audio, records, fuel,
    ):
        if mode != "help":
            super().compose(
                mode, delivery, car,
                audio, records, fuel,
            )

            if mode == "title":
                self.text(
                    "F1: CONTROLS    F12: SAVE SCREENSHOT",
                    (80, 570), "small",
                    (156, 176, 194),
                )

            elif mode == "paused":
                self.text(
                    "F1: CONTROLS    F12: SCREENSHOT",
                    (296, 395), "small",
                    (156, 176, 194),
                )

            return

        self.surface.fill((8, 14, 26, 242))

        self.text(
            "CONTROLS",
            (80, 60), "heading",
            (58, 214, 200),
        )

        self.text(
            "F1 / ESC: return to the previous screen",
            (82, 116), "body",
            (156, 176, 194),
        )

        groups = (
            (
                80,
                "DRIVING AND CAMERA",
                (
                    ("W / UP", "Accelerate"),
                    ("S / DOWN", "Brake, then reverse"),
                    ("A / D", "Steer left / right"),
                    ("SPACE", "Strong brake"),
                    ("Z / C", "Look left / right"),
                    ("WHEEL", "Zoom camera"),
                    ("L", "Toggle headlights"),
                ),
            ),
            (
                656,
                "DELIVERIES AND MENUS",
                (
                    ("E", "Collect / deliver in the bay"),
                    ("F", "Repair at the depot"),
                    ("G", "Refuel at the depot"),
                    ("TAB", "Show / hide map"),
                    ("M", "Mute / unmute sound"),
                    ("P / ENTER", "Pause / resume"),
                    ("R", "Restart the entire night"),
                ),
            ),
        )

        for left, title, rows in groups:
            pygame.draw.rect(
                self.surface,
                (18, 29, 45),
                (left, 160, 544, 408),
                border_radius=10,
            )

            self.text(
                title,
                (left + 24, 183),
                "button",
                (255, 190, 91),
            )

            for index, (key, description) in enumerate(rows):
                y = 238 + index * 43

                self.text(
                    key,
                    (left + 24, y),
                    "small",
                    (58, 214, 200),
                )

                self.text(
                    description,
                    (left + 188, y),
                    "small",
                )

        self.text(
            "F12: SAVE SCREENSHOT TO captures/",
            (82, 605), "body",
        )

        self.text(
            "The night stays paused while this screen is open.",
            (82, 646), "small",
            (156, 176, 194),
        )


def save_capture(width, height, directory=None):
    folder = (
        Path(directory)
        if directory is not None
        else Path(__file__).resolve().parent / "captures"
    )

    try:
        folder.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        path = folder / f"MidnightDelivery_{stamp}.png"

        pixels = (
            ctypes.c_ubyte * (width * height * 4)
        )()

        GL.glReadPixels(
            0, 0, width, height,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            pixels,
        )

        surface = pygame.image.frombytes(
            bytes(pixels),
            (width, height),
            "RGBA",
            True,
        )

        pygame.image.save(surface, str(path))
        print(f"Screenshot saved: {path}")

        return path

    except (OSError, pygame.error) as error:
        print(f"Could not save screenshot: {error}")
        return None