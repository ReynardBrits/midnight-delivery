import math


CAR_BODY = (1.000, 0.710, 0.280, 1.0)
CAR_GLASS = (0.090, 0.160, 0.240, 1.0)
TYRE = (0.025, 0.035, 0.050, 1.0)
HEADLIGHT = (1.000, 0.960, 0.760, 1.0)
TAILLIGHT = (0.940, 0.260, 0.260, 1.0)

CAR_PARTS = (
    (-20, -21, 6, 13, TYRE),
    (14, -21, 6, 13, TYRE),
    (-20, 10, 6, 13, TYRE),
    (14, 10, 6, 13, TYRE),
    (-16, -28, 32, 56, CAR_BODY),
    (-12, -15, 24, 13, CAR_GLASS),
    (-11, 12, 22, 8, CAR_GLASS),
    (-13, -28, 7, 4, HEADLIGHT),
    (6, -28, 7, 4, HEADLIGHT),
    (-13, 24, 7, 4, TAILLIGHT),
    (6, 24, 7, 4, TAILLIGHT),
)


def approach(value, target, change):
    """Move towards a target without going past it."""
    if value < target:
        return min(value + change, target)

    return max(value - change, target)


class Car:
    MAX_SPEED = 300.0
    REVERSE_SPEED = 90.0
    ACCELERATION = 200.0
    BRAKING = 360.0
    STRONG_BRAKING = 520.0
    COASTING = 80.0
    TURN_SPEED = 150.0
    BOUNDARY_MARGIN = 35.0

    def __init__(self, x, y):
        self.start_x = float(x)
        self.start_y = float(y)
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.angle = 0.0
        self.speed = 0.0
        self.sync_render_state()

    def sync_render_state(self):
        self.previous_x = self.x
        self.previous_y = self.y
        self.previous_angle = self.angle

    def update(
        self, dt, throttle, steering, braking,
        world_width, world_height,
    ):
        self.sync_render_state()

        if braking:
            self.speed = approach(
                self.speed, 0.0, self.STRONG_BRAKING * dt
            )

        elif throttle > 0:
            rate = (
                self.BRAKING
                if self.speed < 0
                else self.ACCELERATION
            )

            target = (
                0.0
                if self.speed < 0
                else self.MAX_SPEED
            )

            self.speed = approach(
                self.speed, target, rate * dt
            )

        elif throttle < 0:
            rate = (
                self.BRAKING
                if self.speed > 0
                else self.ACCELERATION
            )

            target = (
                0.0
                if self.speed > 0
                else -self.REVERSE_SPEED
            )

            self.speed = approach(
                self.speed, target, rate * dt
            )

        else:
            self.speed = approach(
                self.speed, 0.0, self.COASTING * dt
            )

        # Steering becomes stronger as the car gains speed.
        steering_strength = min(
            abs(self.speed) / 100.0, 1.0
        )

        travel_direction = (
            -1.0 if self.speed < 0 else 1.0
        )

        self.angle = (
            self.angle
            + steering * self.TURN_SPEED
            * steering_strength * travel_direction * dt
        ) % 360.0

        radians = math.radians(self.angle)

        self.x += math.sin(radians) * self.speed * dt
        self.y -= math.cos(radians) * self.speed * dt

        # Keep the whole car inside the current scene.
        margin = self.BOUNDARY_MARGIN

        clamped_x = max(
            margin,
            min(self.x, world_width - margin),
        )

        clamped_y = max(
            margin,
            min(self.y, world_height - margin),
        )

        if clamped_x != self.x or clamped_y != self.y:
            self.speed = 0.0

        self.x = clamped_x
        self.y = clamped_y

    def draw(self, renderer, alpha):
        # Interpolate between physics updates.
        x = (
            self.previous_x
            + (self.x - self.previous_x) * alpha
        )

        y = (
            self.previous_y
            + (self.y - self.previous_y) * alpha
        )

        angle_change = (
            self.angle - self.previous_angle + 180.0
        ) % 360.0 - 180.0

        angle = (
            self.previous_angle + angle_change * alpha
        )

        radians = math.radians(angle)
        c = math.cos(radians)
        s = math.sin(radians)

        # Rotate every part around the same car centre.
        for left, top, width, height, colour in CAR_PARTS:
            local_x = left + width / 2
            local_y = top + height / 2

            centre_x = x + local_x * c - local_y * s
            centre_y = y + local_x * s + local_y * c

            renderer.draw_rect(
                centre_x - width / 2,
                centre_y - height / 2,
                width,
                height,
                colour,
                angle=angle,
            )