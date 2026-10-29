import math

from car import overlaps_building


TYRE = (0.025, 0.035, 0.050, 1.0)
GLASS = (0.080, 0.160, 0.240, 1.0)
REFLECTION = (0.280, 0.450, 0.530, 1.0)
METAL = (0.390, 0.470, 0.550, 1.0)

HEADLIGHT = (1.000, 0.960, 0.760, 1.0)
TAILLIGHT = (0.550, 0.080, 0.100, 1.0)
BRAKE_LIGHT = (1.000, 0.230, 0.180, 1.0)
SHADOW = (0.020, 0.030, 0.050, 0.45)

COLOURS = (
    (0.300, 0.570, 0.840, 1.0),
    (0.640, 0.450, 0.780, 1.0),
    (0.260, 0.650, 0.540, 1.0),
    (0.820, 0.750, 0.540, 1.0),
    (0.720, 0.390, 0.460, 1.0),
    (0.540, 0.650, 0.740, 1.0),
)


def rectangles_overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b

    return (
        ax < bx + bw
        and ax + aw > bx
        and ay < by + bh
        and ay + ah > by
    )


class Route:
    """A closed road route with rounded corners."""

    def __init__(
        self, left, top, right, bottom, reverse=False
    ):
        radius = 56.0
        points = [(left + radius, top)]

        corners = (
            (right - radius, top + radius, -90),
            (right - radius, bottom - radius, 0),
            (left + radius, bottom - radius, 90),
            (left + radius, top + radius, 180),
        )

        for cx, cy, start in corners:
            for step in range(17):
                angle = math.radians(
                    start + step * 90 / 16
                )

                points.append((
                    cx + math.cos(angle) * radius,
                    cy + math.sin(angle) * radius,
                ))

        if reverse:
            points.reverse()

        self.segments = []
        self.length = 0.0

        for index, (x, y) in enumerate(points):
            next_x, next_y = points[
                (index + 1) % len(points)
            ]

            dx = next_x - x
            dy = next_y - y
            length = math.hypot(dx, dy)

            if length < 0.000001:
                continue

            heading = (
                math.degrees(math.atan2(dx, -dy)) % 360
            )

            self.segments.append((
                x, y, dx, dy, length, heading
            ))

            self.length += length

    def sample(self, distance):
        remaining = distance % self.length

        for x, y, dx, dy, length, heading in self.segments:
            if remaining <= length:
                fraction = remaining / length

                return (
                    x + dx * fraction,
                    y + dy * fraction,
                    heading,
                )

            remaining -= length

        x, y, _, _, _, heading = self.segments[0]
        return x, y, heading


class TrafficCar:
    HALF_WIDTH = 18.0
    HALF_HEIGHT = 28.0

    def __init__(self, route, phase, speed, colour):
        self.route = route
        self.phase = phase
        self.speed = speed

        edge = tuple(
            value * 0.58 for value in colour[:3]
        ) + (1.0,)

        highlight = tuple(
            min(1.0, value * 1.15)
            for value in colour[:3]
        ) + (1.0,)

        self.parts = (
            # Tyres.
            (-17, -19, 5, 12, TYRE),
            (12, -19, 5, 12, TYRE),
            (-17, 9, 5, 12, TYRE),
            (12, 9, 5, 12, TYRE),

            # Body and bonnet.
            (-14, -26, 28, 52, edge),
            (-13, -24, 26, 48, colour),
            (-11, -22, 22, 8, highlight),

            # Windows and roof.
            (-11, -13, 22, 10, GLASS),
            (-9, -12, 17, 2, REFLECTION),
            (-10, 0, 20, 14, highlight),
            (-11, 16, 22, 7, GLASS),
            (-9, 17, 17, 2, REFLECTION),

            # Mirrors and bumpers.
            (-18, -4, 4, 6, edge),
            (14, -4, 4, 6, edge),
            (-10, -28, 20, 2, METAL),
            (-10, 26, 20, 2, METAL),

            # Lights and number plate.
            (-11, -25, 6, 3, HEADLIGHT),
            (5, -25, 6, 3, HEADLIGHT),
            (-4, 24, 8, 2, HEADLIGHT),
        )

        self.reset()

    def reset(self):
        self.distance = self.phase * self.route.length

        self.x, self.y, self.angle = self.route.sample(
            self.distance
        )

        self.waiting = False
        self.sync_render_state()

    def sync_render_state(self):
        self.previous_x = self.x
        self.previous_y = self.y
        self.previous_angle = self.angle

    def bounds_at(self, x, y, angle, padding=0.0):
        radians = math.radians(angle)
        c = abs(math.cos(radians))
        s = abs(math.sin(radians))

        extent_x = (
            c * self.HALF_WIDTH
            + s * self.HALF_HEIGHT
        )

        extent_y = (
            s * self.HALF_WIDTH
            + c * self.HALF_HEIGHT
        )

        return (
            x - extent_x - padding,
            y - extent_y - padding,
            2 * (extent_x + padding),
            2 * (extent_y + padding),
        )

    @property
    def bounds(self):
        return self.bounds_at(
            self.x, self.y, self.angle
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

        change = (
            self.angle - self.previous_angle + 180
        ) % 360 - 180

        angle = self.previous_angle + change * alpha

        radians = math.radians(angle)
        c = math.cos(radians)
        s = math.sin(radians)

        def part(left, top, width, height, colour):
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

        renderer.draw_rect(
            x - 14 + 5,
            y - 26 + 7,
            28,
            52,
            SHADOW,
            angle=angle,
        )

        for item in self.parts:
            part(*item)

        rear = (
            BRAKE_LIGHT if self.waiting else TAILLIGHT
        )

        part(-12, 23, 5, 3, rear)
        part(7, 23, 5, 3, rear)


class Traffic:
    def __init__(self):
        # Opposite routes follow the left-hand traffic lanes.
        routes = (
            Route(540, 320, 2220, 1520),
            Route(
                620, 400, 2140, 1440,
                reverse=True,
            ),
        )

        self.vehicles = []

        for index, colour in enumerate(COLOURS):
            lane = index % 2
            slot = index // 2

            phase = (
                (0.12 if lane == 0 else 0.57)
                + slot / 3
            ) % 1

            self.vehicles.append(
                TrafficCar(
                    routes[lane],
                    phase,
                    110.0 if lane == 0 else 115.0,
                    colour,
                )
            )

        self.reset()

    def reset(self):
        self.active_count = 2

        for vehicle in self.vehicles:
            vehicle.reset()

    def set_shift(self, shift_number):
        self.active_count = max(
            2, min(6, shift_number * 2)
        )

    @property
    def active_vehicles(self):
        return self.vehicles[:self.active_count]

    @property
    def obstacles(self):
        return tuple(
            vehicle.bounds
            for vehicle in self.active_vehicles
        )

    def sync_render_state(self):
        for vehicle in self.vehicles:
            vehicle.sync_render_state()

    def update(self, dt, car):
        active = self.active_vehicles

        for vehicle in active:
            vehicle.sync_render_state()

            next_distance = (
                vehicle.distance + vehicle.speed * dt
            )

            pose = vehicle.route.sample(next_distance)

            ahead = vehicle.route.sample(
                next_distance + 36.0
            )

            def blocked(bounds):
                if overlaps_building(
                    car.x,
                    car.y,
                    car.angle,
                    car.HALF_WIDTH,
                    car.HALF_HEIGHT,
                    bounds,
                ):
                    return True

                return any(
                    other is not vehicle
                    and rectangles_overlap(
                        bounds, other.bounds
                    )
                    for other in active
                )

            vehicle.waiting = (
                blocked(vehicle.bounds_at(*pose))
                or blocked(
                    vehicle.bounds_at(
                        *ahead, padding=8.0
                    )
                )
            )

            if vehicle.waiting:
                continue

            vehicle.distance = (
                next_distance % vehicle.route.length
            )

            vehicle.x, vehicle.y, vehicle.angle = pose

    def draw(self, renderer, alpha):
        for vehicle in self.active_vehicles:
            vehicle.draw(renderer, alpha)