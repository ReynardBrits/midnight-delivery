"""Traffic signals, NPC stopping and red-light penalties."""

import math

import pygame

from blackouts3d import PowerBanner
from renderer3d import Mesh3D, MeshBuilder
from vehicles3d import Traffic3D


TINTS = {
    "RED": (1.0, 0.12, 0.09, 1.0),
    "AMBER": (1.0, 0.67, 0.08, 1.0),
    "GREEN": (0.12, 0.95, 0.38, 1.0),
    "OFF": (0.06, 0.09, 0.12, 1.0),
}


def extents(angle, half_width, half_height):
    radians = math.radians(angle)

    c = abs(math.cos(radians))
    s = abs(math.sin(radians))

    return (
        c * half_width + s * half_height,
        s * half_width + c * half_height,
    )


class TrafficSignals:
    FINE = 20

    # Name, road-left, road-top, cycle offset.
    JUNCTIONS = (
        ("CENTRE WEST", 500, 840, 0.0),
        ("CENTRE EAST", 2100, 840, 14.0),
    )

    def __init__(self, power):
        self.power = power
        self.reset()

    def reset(self):
        self.visited = set()
        self.fines = 0
        self.points_lost = 0
        self.notice = ""
        self.notice_time = 0.0

    def update(self, dt):
        self.notice_time = max(
            0.0, self.notice_time - dt
        )

    def state(self, index, axis):
        _, x, y, offset = self.JUNCTIONS[index]

        if self.power.is_dark(x + 80, y + 80):
            return "OFF"

        phase = (
            self.power.elapsed + offset + 1e-8
        ) % 28.0

        if axis == "NS":
            if phase < 10:
                return "GREEN"

            if phase < 12:
                return "AMBER"

        else:
            if 14 <= phase < 24:
                return "GREEN"

            if 24 <= phase < 26:
                return "AMBER"

        return "RED"

    def heads(self):
        for index, (_, x, y, _) in enumerate(
            self.JUNCTIONS
        ):
            yield (
                index, "NS",
                x + 172, y - 45,
                180,
            )

            yield (
                index, "NS",
                x - 12, y + 205,
                0,
            )

            yield (
                index, "EW",
                x - 45, y - 12,
                90,
            )

            yield (
                index, "EW",
                x + 205, y + 172,
                -90,
            )

    @property
    def obstacles(self):
        return tuple(
            (x - 6, y - 6, 12, 12)
            for _, _, x, y, _ in self.heads()
        )

    @property
    def blockers(self):
        return tuple(
            (*box, 76.0)
            for box in self.obstacles
        )

    def crossings(
        self, old, new,
        half_width, half_height,
    ):
        old_extent = extents(
            old[2], half_width, half_height
        )

        new_extent = extents(
            new[2], half_width, half_height
        )

        for index, (_, x, y, _) in enumerate(
            self.JUNCTIONS
        ):
            lines = (
                ("NS", 1, 1, y - 40, x, x + 160),
                ("NS", 1, -1, y + 200, x, x + 160),
                ("EW", 0, 1, x - 40, y, y + 160),
                ("EW", 0, -1, x + 200, y, y + 160),
            )

            for (
                axis,
                coordinate,
                direction,
                line,
                low,
                high,
            ) in lines:
                movement = (
                    new[coordinate] - old[coordinate]
                ) * direction

                if movement <= 0.000001:
                    continue

                before = (
                    (old[coordinate] - line) * direction
                    + old_extent[coordinate]
                )

                after = (
                    (new[coordinate] - line) * direction
                    + new_extent[coordinate]
                )

                if not before <= 0 < after:
                    continue

                fraction = -before / (after - before)
                other = 1 - coordinate

                across = (
                    old[other]
                    + (new[other] - old[other]) * fraction
                )

                if low <= across < high:
                    yield index, axis

    def check_player(self, car, delivery, audio):
        # Allow another penalty only after leaving the junction.
        for index in tuple(self.visited):
            _, x, y, _ = self.JUNCTIONS[index]

            nearby = (
                x - 120 <= car.x <= x + 280
                and y - 120 <= car.y <= y + 280
            )

            if not nearby:
                self.visited.remove(index)

        entries = self.crossings(
            (
                car.previous_x,
                car.previous_y,
                car.previous_angle,
            ),
            (car.x, car.y, car.angle),
            car.HALF_WIDTH,
            car.HALF_HEIGHT,
        )

        for index, axis in entries:
            if index in self.visited:
                continue

            self.visited.add(index)

            if self.state(index, axis) != "RED":
                continue

            charged = min(
                self.FINE,
                max(0, delivery.score),
            )

            delivery.score -= charged

            self.fines += 1
            self.points_lost += charged

            self.notice = (
                f"RED LIGHT: -{charged} POINTS"
            )

            self.notice_time = 3.0

            delivery.feedback(
                f"Red light: -{charged} pts. "
                "Stop before the line."
            )

            audio.play_effect("warning")

    def status(self, car):
        if self.notice_time > 0:
            return self.notice, (255, 107, 102)

        nearest = min(
            range(len(self.JUNCTIONS)),
            key=lambda i: math.hypot(
                car.x - self.JUNCTIONS[i][1] - 80,
                car.y - self.JUNCTIONS[i][2] - 80,
            ),
        )

        name, x, y, _ = self.JUNCTIONS[nearest]

        dx = car.x - x - 80
        dy = car.y - y - 80

        if math.hypot(dx, dy) > 520:
            return "", (156, 176, 194)

        axis = (
            "EW"
            if abs(dx) > abs(dy)
            else "NS"
        )

        state = self.state(nearest, axis)

        if state == "OFF":
            return (
                f"{name}: SIGNALS OFF | NO LIGHT FINES",
                (156, 176, 194),
            )

        colour = tuple(
            round(c * 255)
            for c in TINTS[state][:3]
        )

        return (
            f"{name}: {state} | RED = 20 POINTS",
            colour,
        )


class SignalTraffic(Traffic3D):
    def __init__(self, signals):
        self.signals = signals
        super().__init__()

    def update(self, dt, car):
        held = []

        for vehicle in self.active_vehicles:
            future = vehicle.route.sample(
                vehicle.distance + vehicle.speed * dt
            )

            entries = self.signals.crossings(
                (
                    vehicle.x,
                    vehicle.y,
                    vehicle.angle,
                ),
                future,
                vehicle.HALF_WIDTH,
                vehicle.HALF_HEIGHT,
            )

            must_stop = any(
                self.signals.state(index, axis)
                in ("RED", "AMBER")
                for index, axis in entries
            )

            if must_stop:
                held.append(
                    (vehicle, vehicle.speed)
                )

                vehicle.speed = 0.0

        try:
            super().update(dt, car)

        finally:
            for vehicle, speed in held:
                vehicle.speed = speed
                vehicle.waiting = True


class SignalModels:
    def __init__(self, signals):
        self.signals = signals
        self.meshes = []

        def upload(builder):
            mesh = Mesh3D(builder)
            self.meshes.append(mesh)
            return mesh

        builder = MeshBuilder()

        metal = (0.30, 0.35, 0.39, 1.0)
        paint = (0.83, 0.87, 0.87, 1.0)

        for _, _, x, y, _ in signals.heads():
            builder.box(
                x - 6, y - 6, 0,
                12, 12, 3,
                metal,
            )

            builder.box(
                x - 2, y - 2, 3,
                4, 4, 29,
                metal,
            )

        # Stop lines for left-hand traffic.
        for _, x, y, _ in signals.JUNCTIONS:
            builder.plane(
                x + 84, y - 40, 0.24,
                72, 4,
                paint,
            )

            builder.plane(
                x + 4, y + 200, 0.24,
                72, 4,
                paint,
            )

            builder.plane(
                x - 40, y + 4, 0.24,
                4, 72,
                paint,
            )

            builder.plane(
                x + 200, y + 84, 0.24,
                4, 72,
                paint,
            )

        self.body = upload(builder)
        self.lamps = {}

        for state in (
            "RED", "AMBER", "GREEN", "OFF"
        ):
            builder = MeshBuilder()

            builder.box(
                -5, -4, 30,
                10, 8, 44,
                (0.025, 0.035, 0.05, 1.0),
            )

            for colour, height in (
                ("RED", 62),
                ("AMBER", 49),
                ("GREEN", 36),
            ):
                lit = state == colour

                builder.box(
                    -3, 4.2, height,
                    6, 0.8, 7,
                    TINTS[colour] if lit else TINTS["OFF"],
                    1.0 if lit else 0.0,
                )

            # A matching cap is visible from the raised camera.
            builder.plane(
                -4, -3, 74.1,
                8, 6,
                TINTS[state],
                0.9 if state != "OFF" else 0,
            )

            self.lamps[state] = upload(builder)

    def draw(self, renderer):
        renderer.draw(self.body)

        for index, axis, x, y, angle in (
            self.signals.heads()
        ):
            renderer.draw(
                self.lamps[
                    self.signals.state(index, axis)
                ],
                x, y, 0, angle,
            )

    def close(self):
        for mesh in reversed(self.meshes):
            mesh.close()

        self.meshes.clear()


class SignalBanner(PowerBanner):
    def __init__(
        self, width, height, power, signals,
    ):
        self.signals = signals

        self.signal_status = (
            "",
            (156, 176, 194),
        )

        super().__init__(
            width, height, power
        )

    def draw_power(
        self, delivery, car, audio,
        records, fuel, headlights,
    ):
        status = self.signals.status(car)

        if status != self.signal_status:
            self.last_state = None
            self.signal_status = status

        super().draw_power(
            delivery,
            car,
            audio,
            records,
            fuel,
            headlights,
        )

    def compose(
        self, mode, delivery,
        car, audio, records, fuel,
    ):
        super().compose(
            mode,
            delivery,
            car,
            audio,
            records,
            fuel,
        )

        title, colour = self.signal_status

        if title:
            pygame.draw.rect(
                self.surface,
                (12, 22, 36, 235),
                (16, 84, 760, 38),
                border_radius=8,
            )

            self.text(
                title,
                (32, 92),
                "small",
                colour,
            )