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


def overlaps_building(
    x, y, angle, half_width, half_height, building
):
    """Check a rotated car against a rectangular building."""
    left, top, width, height = building

    dx = x - (left + width / 2)
    dy = y - (top + height / 2)

    radians = math.radians(angle)
    c = math.cos(radians)
    s = math.sin(radians)

    # Test the world axes and the rotated car axes.
    for axis_x, axis_y in (
        (1.0, 0.0),
        (0.0, 1.0),
        (c, s),
        (-s, c),
    ):
        distance = abs(
            dx * axis_x + dy * axis_y
        )

        car_radius = (
            half_width * abs(c * axis_x + s * axis_y)
            + half_height * abs(-s * axis_x + c * axis_y)
        )

        building_radius = (
            width / 2 * abs(axis_x)
            + height / 2 * abs(axis_y)
        )

        if distance >= car_radius + building_radius - 0.000001:
            return False

    return True


class Car:
    MAX_SPEED = 300.0
    REVERSE_SPEED = 90.0
    ACCELERATION = 200.0
    BRAKING = 360.0
    STRONG_BRAKING = 520.0
    COASTING = 80.0
    TURN_SPEED = 150.0

    HALF_WIDTH = 20.0
    HALF_HEIGHT = 28.0

    def __init__(self, x, y):
        self.start_x = float(x)
        self.start_y = float(y)
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.angle = 0.0
        self.speed = 0.0
        self.colliding = False
        self.sync_render_state()

    def sync_render_state(self):
        self.previous_x = self.x
        self.previous_y = self.y
        self.previous_angle = self.angle

    def update(
        self, dt, throttle, steering, braking,
        world_width, world_height, obstacles=(),
    ):
        self.sync_render_state()

        was_colliding = self.colliding
        self.colliding = False

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
                0.0 if self.speed < 0 else self.MAX_SPEED
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
                0.0 if self.speed > 0 else -self.REVERSE_SPEED
            )

            self.speed = approach(
                self.speed, target, rate * dt
            )

        else:
            self.speed = approach(
                self.speed, 0.0, self.COASTING * dt
            )

        steering_strength = min(
            abs(self.speed) / 100.0, 1.0
        )

        travel_direction = (
            -1.0 if self.speed < 0 else 1.0
        )

        next_angle = (
            self.angle
            + steering * self.TURN_SPEED
            * steering_strength * travel_direction * dt
        ) % 360.0

        # Prevent rotation into a building or map boundary.
        if not self.is_blocked(
            self.x,
            self.y,
            next_angle,
            world_width,
            world_height,
            obstacles,
        ):
            self.angle = next_angle
        else:
            self.colliding = True

        radians = math.radians(self.angle)

        move_x = math.sin(radians) * self.speed * dt
        move_y = -math.cos(radians) * self.speed * dt

        old_x = self.x
        old_y = self.y

        # Check each axis separately so the car can
        # move along a wall during a glancing collision.
        if not self.is_blocked(
            self.x + move_x,
            self.y,
            self.angle,
            world_width,
            world_height,
            obstacles,
        ):
            self.x += move_x
        else:
            self.colliding = True

        if not self.is_blocked(
            self.x,
            self.y + move_y,
            self.angle,
            world_width,
            world_height,
            obstacles,
        ):
            self.y += move_y
        else:
            self.colliding = True

        if self.colliding:
            distance_squared = (
                (self.x - old_x) ** 2
                + (self.y - old_y) ** 2
            )

            if distance_squared < 0.000001:
                self.speed = 0.0

            elif not was_colliding:
                # Reduce speed on first contact.
                self.speed *= 0.35

    def is_blocked(
        self, x, y, angle,
        world_width, world_height, obstacles,
    ):
        radians = math.radians(angle)

        extent_x = (
            abs(math.cos(radians)) * self.HALF_WIDTH
            + abs(math.sin(radians)) * self.HALF_HEIGHT
        )

        extent_y = (
            abs(math.sin(radians)) * self.HALF_WIDTH
            + abs(math.cos(radians)) * self.HALF_HEIGHT
        )

        if (
            x - extent_x < 0
            or x + extent_x > world_width
            or y - extent_y < 0
            or y + extent_y > world_height
        ):
            return True

        return any(
            overlaps_building(
                x,
                y,
                angle,
                self.HALF_WIDTH,
                self.HALF_HEIGHT,
                building,
            )
            for building in obstacles
        )

    def draw(self, renderer, alpha):
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