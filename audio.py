from array import array
from dataclasses import dataclass
import math
import random

import pygame


SAMPLE_RATE = 22050
LOOP_SECONDS = 8

AMBIENCE_VOLUME = 0.4
ENGINE_VOLUME = 0.18
EFFECT_VOLUME = 0.28


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


def build_engine(frequency):
    """An exactly one-second, seamless engine loop."""
    samples = array("h")

    for index in range(SAMPLE_RATE):
        t = index / SAMPLE_RATE
        phase = math.tau * frequency * t

        pulse = (
            0.85
            + 0.15 * math.sin(math.tau * 5 * t)
        )

        value = pulse * (
            0.18 * math.sin(phase)
            + 0.09 * math.sin(phase * 2)
            + 0.04 * math.sin(phase * 3)
        )

        sample = round(value * 32767)
        samples.extend((sample, sample))

    return samples.tobytes()


def build_tones(notes):
    """Short musical cues with soft attacks and releases."""
    samples = array("h")

    for frequency, duration in notes:
        count = round(duration * SAMPLE_RATE)

        for index in range(count):
            t = index / SAMPLE_RATE
            attack = min(1.0, t / 0.008)

            release = min(
                1.0,
                (count - 1 - index)
                / (SAMPLE_RATE * 0.035),
            )

            envelope = (
                attack
                * release
                * math.exp(-2 * t / duration)
            )

            value = envelope * (
                0.55 * math.sin(
                    math.tau * frequency * t
                )
                + 0.18 * math.sin(
                    math.tau * frequency * 2 * t
                )
            )

            sample = round(value * 32767)
            samples.extend((sample, sample))

    return samples.tobytes()


def build_crash():
    """A short, low thud with filtered noise."""
    samples = array("h")
    rng = random.Random(43)

    noise = 0.0
    count = round(SAMPLE_RATE * 0.18)

    for index in range(count):
        t = index / SAMPLE_RATE

        noise += 0.2 * (
            rng.uniform(-1.0, 1.0) - noise
        )

        attack = min(1.0, t / 0.004)

        release = min(
            1.0,
            (count - 1 - index)
            / (SAMPLE_RATE * 0.02),
        )

        value = (
            attack
            * release
            * math.exp(-20 * t)
            * (
                0.65 * math.sin(math.tau * 70 * t)
                + 0.35 * noise
            )
        )

        sample = round(value * 32767)
        samples.extend((sample, sample))

    return samples.tobytes()


@dataclass(frozen=True)
class AudioState:
    mode: str
    delivery_state: str
    completed: int
    condition: float
    time_left: float
    kind: str


class Audio:
    def __init__(self):
        self.sound = None
        self.channel = None

        self.muted = False
        self.paused = False

        self.engines = []
        self.engine_channels = []
        self.effects = {}
        self.fx_channels = []
        self.sound_volumes = []

        self.fx_paused = False
        self.next_fx = 0
        self.previous: AudioState | None = None

        try:
            pygame.mixer.init(
                frequency=SAMPLE_RATE,
                size=-16,
                channels=2,
                buffer=1024,
                allowedchanges=0,
            )

            pygame.mixer.set_num_channels(8)

            self.sound = self.make_sound(
                build_ambience(),
                AMBIENCE_VOLUME,
            )

            self.channel = pygame.mixer.Channel(0)

            self.channel.play(
                self.sound,
                loops=-1,
                fade_ms=600,
            )

            # Four engine bands are blended using channel volumes.
            for index, frequency in enumerate(
                (65, 95, 140, 190),
                start=1,
            ):
                sound = self.make_sound(
                    build_engine(frequency),
                    ENGINE_VOLUME,
                )

                channel = pygame.mixer.Channel(index)

                self.engines.append(sound)
                self.engine_channels.append(channel)

                channel.play(
                    sound,
                    loops=-1,
                    fade_ms=300,
                )

                channel.set_volume(0.0)

            clips = {
                "pickup": build_tones((
                    (523.25, 0.09),
                    (659.25, 0.14),
                )),

                "delivery": build_tones((
                    (523.25, 0.08),
                    (659.25, 0.08),
                    (783.99, 0.16),
                )),

                "warning": build_tones((
                    (880.0, 0.1),
                    (0.0, 0.06),
                    (880.0, 0.1),
                )),

                "crash": build_crash(),

                "complete": build_tones((
                    (523.25, 0.12),
                    (659.25, 0.12),
                    (783.99, 0.12),
                    (1046.5, 0.28),
                )),

                "failure": (
                    build_crash()
                    + build_tones((
                        (220.0, 0.12),
                        (165.0, 0.16),
                        (110.0, 0.24),
                    ))
                ),
            }

            self.effects = {
                name: self.make_sound(
                    data, EFFECT_VOLUME
                )
                for name, data in clips.items()
            }

            self.fx_channels = [
                pygame.mixer.Channel(index)
                for index in (5, 6, 7)
            ]

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

    def make_sound(self, data, volume):
        sound = pygame.mixer.Sound(buffer=data)
        sound.set_volume(volume)

        self.sound_volumes.append(
            (sound, volume)
        )

        return sound

    def toggle_mute(self):
        self.muted = not self.muted

        for sound, volume in self.sound_volumes:
            sound.set_volume(
                0.0 if self.muted else volume
            )

    def set_paused(self, paused):
        if (
            self.channel is None
            or self.paused == paused
        ):
            return

        self.paused = paused

        for channel in (
            [self.channel] + self.engine_channels
        ):
            if paused:
                channel.pause()
            else:
                channel.unpause()

    def reset_state(self):
        self.previous = None
        self.next_fx = 0

        for channel in self.fx_channels:
            channel.stop()

    def play_effect(self, name):
        sound = self.effects.get(name)

        if sound is None or not self.fx_channels:
            return

        channel = self.fx_channels[self.next_fx]

        self.next_fx = (
            self.next_fx + 1
        ) % len(self.fx_channels)

        channel.play(sound)

        if self.fx_paused:
            channel.pause()

    def update(
        self, car, delivery, mode, focused=True
    ):
        current = AudioState(
            mode,
            delivery.state,
            delivery.completed_count,
            car.condition,
            delivery.time_left,
            delivery.contract.kind,
        )

        previous = self.previous
        self.previous = current

        if self.channel is None:
            return

        self.set_paused(
            mode != "playing" or not focused
        )

        pause_effects = (
            not focused or mode == "paused"
        )

        if pause_effects != self.fx_paused:
            self.fx_paused = pause_effects

            for channel in self.fx_channels:
                if pause_effects:
                    channel.pause()
                else:
                    channel.unpause()

        fraction = min(
            abs(car.speed) / car.MAX_SPEED,
            1.0,
        )

        band = fraction * (
            len(self.engine_channels) - 1
        )

        gain = 0.35 + 0.65 * fraction

        if car.braking:
            gain *= 0.55

        for index, channel in enumerate(
            self.engine_channels
        ):
            weight = max(
                0.0,
                1.0 - abs(index - band),
            )

            channel.set_volume(gain * weight)

        if previous is None or mode == "title":
            return

        if (
            mode == "complete"
            and previous.mode != "complete"
        ):
            self.play_effect("complete")
            return

        if (
            mode == "game_over"
            and previous.mode != "game_over"
        ):
            self.play_effect("failure")
            return

        if mode != "playing":
            return

        if current.completed > previous.completed:
            self.play_effect("delivery")

        elif (
            current.delivery_state == "dropoff"
            and previous.delivery_state != "dropoff"
        ):
            self.play_effect("pickup")

        if current.condition < previous.condition:
            self.play_effect("crash")

        if (
            current.kind == "EXPRESS"
            and current.delivery_state == "dropoff"
            and previous.time_left > 0.0
            and current.time_left <= 0.0
        ):
            self.play_effect("warning")

    def close(self):
        if self.channel is not None:
            self.channel.stop()

        for channel in (
            self.engine_channels + self.fx_channels
        ):
            channel.stop()

        self.channel = None
        self.sound = None

        self.engines.clear()
        self.engine_channels.clear()
        self.effects.clear()
        self.fx_channels.clear()
        self.sound_volumes.clear()