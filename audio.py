from array import array
import math
import random

import pygame


SAMPLE_RATE = 22050
LOOP_SECONDS = 8
AMBIENCE_VOLUME = 0.4


def build_ambience():
    """Create a stereo, signed 16-bit wind-and-cricket loop."""
    frame_count = SAMPLE_RATE * LOOP_SECONDS
    rng = random.Random(27)

    noise = [
        rng.uniform(-1.0, 1.0)
        for _ in range(frame_count)
    ]

    samples = array("h")

    # Warm the filter using the end of the same noise loop.
    # This keeps the wind continuous across the loop boundary.
    wind = 0.0

    for value in noise[-2048:]:
        wind += 0.04 * (value - wind)

    for index, value in enumerate(noise):
        t = index / SAMPLE_RATE
        wind += 0.04 * (value - wind)

        gust = (
            0.7
            + 0.3 * math.sin(math.tau * t / 4.0)
        )

        breeze = wind * gust * 0.7

        hum = (
            0.012 * math.sin(math.tau * 80.0 * t)
            + 0.006 * math.sin(math.tau * 120.0 * t)
        )

        chirp = 0.0

        for start in (0.8, 3.2, 5.9):
            elapsed = t - start

            if 0.0 <= elapsed < 0.48:
                pulse = elapsed % 0.16

                if pulse < 0.07:
                    envelope = math.sin(
                        math.pi * pulse / 0.07
                    ) ** 2

                    chirp = envelope * (
                        0.07 * math.sin(
                            math.tau * 3100.0 * t
                        )
                        + 0.03 * math.sin(
                            math.tau * 3600.0 * t
                        )
                    )

                break

        # Place the crickets slightly to the right.
        left = breeze + hum + chirp * 0.55
        right = breeze * 0.9 + hum * 0.8 + chirp

        for sample in (left, right):
            sample = max(-1.0, min(sample, 1.0))
            samples.append(round(sample * 32767))

    return samples.tobytes()


class Audio:
    def __init__(self):
        self.sound = None
        self.channel = None
        self.muted = False
        self.paused = False

        try:
            pygame.mixer.init(
                frequency=SAMPLE_RATE,
                size=-16,
                channels=2,
                buffer=1024,
                allowedchanges=0,
            )

            self.sound = pygame.mixer.Sound(
                buffer=build_ambience()
            )

            self.sound.set_volume(AMBIENCE_VOLUME)

            self.channel = pygame.mixer.Channel(0)

            self.channel.play(
                self.sound,
                loops=-1,
                fade_ms=600,
            )

        except pygame.error as error:
            self.close()
            pygame.mixer.quit()

            print(
                "Audio unavailable; continuing without sound:"
                f" {error}"
            )

    @property
    def status(self):
        if self.channel is None:
            return "Unavailable"

        return "Muted" if self.muted else "On"

    def toggle_mute(self):
        self.muted = not self.muted

        if self.sound is not None:
            volume = (
                0.0
                if self.muted
                else AMBIENCE_VOLUME
            )

            self.sound.set_volume(volume)

    def set_paused(self, paused):
        if self.channel is None or self.paused == paused:
            return

        self.paused = paused

        if paused:
            self.channel.pause()
        else:
            self.channel.unpause()

    def close(self):
        if self.channel is not None:
            self.channel.stop()

        self.channel = None
        self.sound = None