import math


CAR_BODY = (1.000, 0.710, 0.280, 1.0)
CAR_EDGE = (0.650, 0.350, 0.130, 1.0)
CAR_HIGHLIGHT = (1.000, 0.820, 0.440, 1.0)

CAR_GLASS = (0.080, 0.160, 0.240, 1.0)
GLASS_REFLECTION = (0.280, 0.450, 0.530, 1.0)

TYRE = (0.025, 0.035, 0.050, 1.0)
METAL = (0.390, 0.470, 0.550, 1.0)
TEAL = (0.227, 0.839, 0.784, 1.0)

PARCEL = (0.690, 0.470, 0.280, 1.0)
PARCEL_TOP = (0.840, 0.650, 0.410, 1.0)
PARCEL_TAPE = (0.960, 0.850, 0.610, 1.0)
PARCEL_SIDE = (0.520, 0.320, 0.170, 1.0)
PARCEL_SCAR = (0.300, 0.180, 0.130, 1.0)

CARGO_WARNING = (1.000, 0.420, 0.400, 1.0)

CARGO_COLOURS = {
    "STANDARD": TEAL,
    "EXPRESS": (1.000, 0.745, 0.357, 1.0),
    "FRAGILE": (0.730, 0.600, 1.000, 1.0),
}

HEADLIGHT = (1.000, 0.960, 0.760, 1.0)
TAILLIGHT = (0.550, 0.080, 0.100, 1.0)
BRAKE_LIGHT = (1.000, 0.230, 0.180, 1.0)
REVERSE_LIGHT = (0.900, 0.950, 1.000, 1.0)

CAR_SHADOW = (0.020, 0.030, 0.050, 0.45)


# Coordinates are relative to the car centre.
# The front of the car points towards negative Y.
CAR_PARTS = (
    # Tyres.
    (-20, -20, 6, 12, TYRE),
    (14, -20, 6, 12, TYRE),
    (-20, 10, 6, 12, TYRE),
    (14, 10, 6, 12, TYRE),

    # Stepped body silhouette and bumpers.
    (-16, -24, 32, 48, CAR_EDGE),
    (-13, -28, 26, 56, CAR_EDGE),
    (-15, -23, 30, 46, CAR_BODY),
    (-12, -26, 24, 52, CAR_BODY),
    (-11, -28, 22, 2, METAL),
    (-11, 26, 22, 2, METAL),

    # Bonnet and courier stripe.
    (-11, -23, 22, 8, CAR_HIGHLIGHT),
    (-2, -24, 4, 9, TEAL),

    # Windows and reflections.
    (-12, -14, 24, 10, CAR_GLASS),
    (-10, -13, 19, 2, GLASS_REFLECTION),
    (-14, -1, 4, 14, CAR_GLASS),
    (10, -1, 4, 14, CAR_GLASS),
    (-10, 16, 20, 7, CAR_GLASS),
    (-8, 17, 16, 2, GLASS_REFLECTION),

    # Wing mirrors and door handles.
    (-20, -5, 4, 6, CAR_EDGE),
    (16, -5, 4, 6, CAR_EDGE),
    (-19, -5, 2, 3, CAR_HIGHLIGHT),
    (17, -5, 2, 3, CAR_HIGHLIGHT),
    (-15, 8, 2, 4, METAL),
    (13, 8, 2, 4, METAL),

    # Empty roof rack. Cargo is drawn separately when loaded.
    (-10, -2, 20, 18, TYRE),
    (-10, -2, 3, 18, METAL),
    (7, -2, 3, 18, METAL),
    (-7, 2, 14, 2, METAL),
    (-7, 10, 14, 2, METAL),

    # Headlights and rear number plate.
    (-12, -26, 6, 4, HEADLIGHT),
    (6, -26, 6, 4, HEADLIGHT),
    (-4, 24, 8, 2, HEADLIGHT),
)


def approach(value, target, change):
    """Move towards a target without going past it."""
    if value < target:
        return min(value + change, target)

    return max(value - change, target)


def overlaps_building(
    x, y, angle, half_width, half_height, building
):
    """Check a rotated car against a rectangular obstacle."""
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

    MIN_IMPACT_SPEED = 75.0
    DAMAGE_SCALE = 0.1
    MAX_IMPACT_DAMAGE = 30.0
    DAMAGE_COOLDOWN = 0.6

    def __init__(self, x, y):
        self.start_x = float(x)
        self.start_y = float(y)
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.angle = 0.0
        self.speed = 0.0

        self.condition = 100.0
        self.impact_speed = 0.0
        self.impact_cooldown = 0.0
        self.impact_flash = 0.0

        self.colliding = False
        self.braking = False

        self.sync_render_state()

    @property
    def disabled(self):
        return self.condition <= 0.0

    def sync_render_state(self):
        self.previous_x = self.x
        self.previous_y = self.y
        self.previous_angle = self.angle

    def update(
        self, dt, throttle, steering, braking,
        world_width, world_height, obstacles=(),
    ):
        self.sync_render_state()

        self.impact_speed = 0.0

        self.impact_cooldown = max(
            0.0,
            self.impact_cooldown - dt,
        )

        self.impact_flash = max(
            0.0,
            self.impact_flash - dt,
        )

        if self.disabled:
            self.speed = 0.0
            self.braking = True
            self.colliding = False
            return

        # Opposite throttle also applies the service brake.
        self.braking = bool(
            braking
            or (throttle < 0 and self.speed > 0)
            or (throttle > 0 and self.speed < 0)
        )

        was_colliding = self.colliding
        self.colliding = False

        if braking:
            self.speed = approach(
                self.speed,
                0.0,
                self.STRONG_BRAKING * dt,
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
                self.speed,
                target,
                rate * dt,
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
                self.speed,
                target,
                rate * dt,
            )

        else:
            self.speed = approach(
                self.speed,
                0.0,
                self.COASTING * dt,
            )

        steering_strength = min(
            abs(self.speed) / 100.0,
            1.0,
        )

        travel_direction = (
            -1.0 if self.speed < 0 else 1.0
        )

        next_angle = (
            self.angle
            + steering * self.TURN_SPEED
            * steering_strength * travel_direction * dt
        ) % 360.0

        # Prevent rotation into an obstacle or map boundary.
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
        impact = 0.0

        # Separate axis checks allow glancing movement
        # along walls.
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

            impact = max(
                impact,
                abs(math.sin(radians) * self.speed),
            )

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

            impact = max(
                impact,
                abs(math.cos(radians) * self.speed),
            )

        # Only blocked movement causes damage. A rejected
        # steering angle alone is not treated as a crash.
        if (
            impact > self.MIN_IMPACT_SPEED
            and self.impact_cooldown <= 0.0
        ):
            damage = min(
                self.MAX_IMPACT_DAMAGE,
                (impact - self.MIN_IMPACT_SPEED)
                * self.DAMAGE_SCALE,
            )

            self.condition = max(
                0.0,
                self.condition - damage,
            )

            self.impact_speed = impact
            self.impact_cooldown = self.DAMAGE_COOLDOWN
            self.impact_flash = 0.35

        if self.colliding:
            distance_squared = (
                (self.x - old_x) ** 2
                + (self.y - old_y) ** 2
            )

            if distance_squared < 0.000001:
                self.speed = 0.0

            elif not was_colliding:
                self.speed *= 0.35

        if self.disabled:
            self.speed = 0.0

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

    def draw(
        self, renderer, alpha,
        cargo_kind=None, cargo_condition=100.0,
    ):
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
            self.previous_angle
            + angle_change * alpha
        )

        radians = math.radians(angle)
        c = math.cos(radians)
        s = math.sin(radians)

        def draw_part(left, top, width, height, colour):
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

        def draw_quad(points, colour):
            renderer.draw_quad(tuple(
                (
                    x + px * c - py * s,
                    y + px * s + py * c,
                )
                for px, py in points
            ), colour)

        # Offset the shadow in world space.
        renderer.draw_rect(
            x - 16 + 5,
            y - 26 + 7,
            32,
            52,
            CAR_SHADOW,
            angle=angle,
        )

        for part in CAR_PARTS:
            draw_part(*part)

        if cargo_kind in CARGO_COLOURS:
            self.draw_cargo(
                draw_part,
                draw_quad,
                cargo_kind,
                cargo_condition,
            )

        rear_colour = (
            BRAKE_LIGHT
            if self.braking
            else TAILLIGHT
        )

        draw_part(-13, 23, 6, 3, rear_colour)
        draw_part(7, 23, 6, 3, rear_colour)

        if self.braking:
            draw_part(-5, 21, 10, 2, BRAKE_LIGHT)

        if self.speed < -1.0:
            draw_part(-6, 24, 2, 2, REVERSE_LIGHT)
            draw_part(4, 24, 2, 2, REVERSE_LIGHT)

    def draw_cargo(self, part, quad, kind, condition):
        label = CARGO_COLOURS[kind]

        damaged = (
            kind == "FRAGILE"
            and condition < 70.0
        )

        badly_damaged = (
            kind == "FRAGILE"
            and condition <= 35.0
        )

        top = (
            tuple(
                value * 0.78
                for value in PARCEL_TOP[:3]
            ) + (1.0,)
            if badly_damaged
            else PARCEL_TOP
        )

        # Raised parcel faces, fitted inside the roof rack.
        part(-5, 2, 14, 12, CAR_SHADOW)

        quad((
            (-7, 8),
            (5, 8),
            (8, 12),
            (-4, 12),
        ), PARCEL)

        quad((
            (5, -1),
            (8, 3),
            (8, 12),
            (5, 8),
        ), PARCEL_SIDE)

        part(-7, -1, 12, 9, top)
        part(-7, -1, 12, 1, PARCEL_TAPE)
        part(-1, -1, 2, 9, PARCEL_TAPE)
        part(-7, 4, 12, 2, PARCEL_TAPE)

        # Contract label and matching securing strap.
        part(-6, 0, 5, 6, label)
        part(-8, 12, 16, 2, label)

        if kind == "EXPRESS":
            # Small arrow printed on the label.
            part(-5, 2, 4, 1, TYRE)
            part(-3, 1, 1, 1, TYRE)
            part(-3, 3, 1, 1, TYRE)

        elif kind == "FRAGILE":
            # Glass symbol: bowl, stem and base.
            part(-5, 1, 3, 2, TYRE)
            part(-4, 3, 1, 1, TYRE)
            part(-5, 4, 3, 1, TYRE)

        else:
            # Shipping-label lines.
            part(-5, 1, 3, 1, TYRE)
            part(-5, 3, 2, 1, TYRE)

        if damaged:
            part(2, 0, 2, 2, PARCEL_SCAR)
            part(1, 2, 2, 2, PARCEL_SCAR)
            part(2, 4, 2, 3, PARCEL_SCAR)
            part(4, 0, 2, 3, CARGO_WARNING)

        if badly_damaged:
            part(-6, 6, 3, 2, PARCEL_SCAR)
            part(-3, 7, 3, 1, PARCEL_SCAR)
            part(3, 9, 2, 2, CARGO_WARNING)