import math


PICKUP_ZONE = (120, 206, 200, 60)
DROPOFF_ZONE = (2292, 768, 116, 64)

TEAL = (0.227, 0.839, 0.784, 1.0)
AMBER = (1.000, 0.745, 0.357, 1.0)
WHITE = (0.950, 0.970, 0.930, 1.0)


class Delivery:
    STOP_SPEED = 10.0
    REWARD = 100

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = "pickup"
        self.score = 0
        self.elapsed = 0.0
        self.message = ""
        self.message_time = 0.0

    @property
    def zone(self) -> tuple[int, int, int, int] | None:
        if self.state == "pickup":
            return PICKUP_ZONE

        if self.state == "dropoff":
            return DROPOFF_ZONE

        return None

    @property
    def objective(self):
        if self.state == "pickup":
            return "COLLECT AT DEPOT"

        if self.state == "dropoff":
            return "DELIVER TO HARBOUR OFFICE"

        return "DELIVERY COMPLETE"

    @property
    def marker_colour(self):
        return TEAL if self.state == "pickup" else AMBER

    def update(self, dt):
        self.elapsed = (self.elapsed + dt) % 2.0

        self.message_time = max(
            0.0,
            self.message_time - dt,
        )

    def contains(self, car):
        zone = self.zone

        if zone is None:
            return False

        x, y, width, height = zone

        return (
            x <= car.x <= x + width
            and y <= car.y <= y + height
        )

    def feedback(self, message):
        self.message = message
        self.message_time = 2.0

    def interact(self, car):
        if self.state == "complete":
            self.feedback(
                "Job complete. R starts a new run."
            )

        elif not self.contains(car):
            self.feedback(
                "Move into the marked bay."
            )

        elif abs(car.speed) > self.STOP_SPEED:
            self.feedback(
                "Stop first: hold SPACE."
            )

        elif self.state == "pickup":
            self.state = "dropoff"

            self.feedback(
                "Parcel collected. Follow the waypoint."
            )

        else:
            self.state = "complete"
            self.score += self.REWARD

            self.feedback(
                "Delivered! +100 points. R to replay."
            )

    def prompt(self, car):
        if self.message_time > 0.0:
            return self.message

        zone = self.zone

        if zone is None:
            return "Job complete. Press R to replay."

        if self.contains(car):
            if abs(car.speed) > self.STOP_SPEED:
                return "Stop first: hold SPACE."

            return (
                "E: COLLECT PARCEL"
                if self.state == "pickup"
                else "E: DELIVER PARCEL"
            )

        x, y, width, height = zone

        dx = x + width / 2 - car.x
        dy = y + height / 2 - car.y

        vertical = (
            "N" if dy < -20
            else "S" if dy > 20
            else ""
        )

        horizontal = (
            "W" if dx < -20
            else "E" if dx > 20
            else ""
        )

        bearing = vertical + horizontal or "NEARBY"
        distance = round(math.hypot(dx, dy))

        return f"TARGET: {bearing} - {distance} px"

    def draw_marker(self, renderer):
        zone = self.zone

        if zone is None:
            return

        x, y, width, height = zone
        r = renderer.draw_rect

        colour = self.marker_colour

        pulse = (
            0.65
            + 0.25 * math.sin(math.tau * self.elapsed)
        )

        outline = colour[:3] + (pulse,)

        r(
            x, y, width, height,
            colour[:3] + (0.14,),
        )

        r(x, y, width, 4, outline)
        r(x, y + height - 4, width, 4, outline)
        r(x, y, 4, height, outline)
        r(x + width - 4, y, 4, height, outline)

        # Parcel symbol in the active bay.
        cx = x + width / 2
        cy = y + height / 2

        r(cx - 10, cy - 9, 20, 18, colour)
        r(cx - 1, cy - 9, 2, 18, WHITE)
        r(cx - 10, cy - 1, 20, 2, WHITE)

    def draw_guidance(
        self, renderer, camera, hud_height
    ):
        zone = self.zone

        if zone is None:
            return

        x, y, width, height = zone

        target_x = x + width / 2 - camera.x
        target_y = y + height / 2 - camera.y

        view_height = camera.height - hud_height

        if (
            0 <= target_x <= camera.width
            and 0 <= target_y <= view_height
        ):
            return

        centre_x = camera.width / 2
        centre_y = view_height / 2

        dx = target_x - centre_x
        dy = target_y - centre_y

        half_width = centre_x - 32
        half_height = centre_y - 32

        scale_x = (
            half_width / abs(dx)
            if dx else math.inf
        )

        scale_y = (
            half_height / abs(dy)
            if dy else math.inf
        )

        scale = min(scale_x, scale_y)

        px = centre_x + dx * scale
        py = centre_y + dy * scale

        length = math.hypot(dx, dy)

        ux = dx / length
        uy = dy / length

        tip = (
            px + ux * 10,
            py + uy * 10,
        )

        renderer.draw_rect(
            px - 16,
            py - 16,
            32,
            32,
            (0.035, 0.060, 0.100, 0.95),
            angle=45,
        )

        for side in (-1, 1):
            wing_x = (
                px - ux * 7 - uy * side * 8
            )

            wing_y = (
                py - uy * 7 + ux * side * 8
            )

            line_dx = tip[0] - wing_x
            line_dy = tip[1] - wing_y

            line_length = math.hypot(
                line_dx, line_dy
            )

            angle = math.degrees(
                math.atan2(line_dy, line_dx)
            )

            renderer.draw_rect(
                (wing_x + tip[0]) / 2 - line_length / 2,
                (wing_y + tip[1]) / 2 - 2,
                line_length,
                4,
                self.marker_colour,
                angle=angle,
            )