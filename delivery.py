import math
from dataclasses import dataclass


PICKUP_ZONE = (120, 206, 200, 60)
HARBOUR_ZONE = (2292, 768, 116, 64)
MARKET_ZONE = (760, 1320, 120, 64)
PARK_ZONE = (900, 232, 120, 56)


@dataclass(frozen=True)
class Contract:
    name: str
    destination: tuple[int, int, int, int]
    reward: int = 100
    time_limit: float = 90.0
    kind: str = "STANDARD"


SHIFTS = (
    (
        Contract(
            "HARBOUR OFFICE", HARBOUR_ZONE,
            100, 90.0,
        ),
        Contract(
            "NIGHT MARKET", MARKET_ZONE,
            125, 90.0, "FRAGILE",
        ),
        Contract(
            "PARK ENTRANCE", PARK_ZONE,
            150, 40.0, "EXPRESS",
        ),
    ),
    (
        Contract(
            "NIGHT MARKET", MARKET_ZONE,
            175, 50.0, "EXPRESS",
        ),
        Contract(
            "PARK ENTRANCE", PARK_ZONE,
            125, 50.0,
        ),
        Contract(
            "HARBOUR OFFICE", HARBOUR_ZONE,
            150, 95.0, "FRAGILE",
        ),
    ),
    (
        Contract(
            "PARK ENTRANCE", PARK_ZONE,
            175, 60.0, "FRAGILE",
        ),
        Contract(
            "HARBOUR OFFICE", HARBOUR_ZONE,
            200, 50.0, "EXPRESS",
        ),
        Contract(
            "NIGHT MARKET", MARKET_ZONE,
            150, 55.0,
        ),
    ),
)


TEAL = (0.227, 0.839, 0.784, 1.0)
AMBER = (1.000, 0.745, 0.357, 1.0)
WHITE = (0.950, 0.970, 0.930, 1.0)
CORAL = (1.000, 0.420, 0.400, 1.0)
LILAC = (0.730, 0.600, 1.000, 1.0)


class Delivery:
    STOP_SPEED = 10.0
    MAX_TIME_BONUS = 50
    FRAGILE_DAMAGE_MULTIPLIER = 2.0

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = "pickup"
        self.shift_index = 0
        self.contract_index = 0
        self.completed_count = 0
        self.score = 0
        self.time_left = 0.0

        self.cargo_condition = 100.0
        self.previous_car_condition = 100.0

        self.elapsed = 0.0
        self.message = ""
        self.message_time = 0.0

    @property
    def shift_number(self):
        return self.shift_index + 1

    @property
    def contracts(self) -> tuple[Contract, ...]:
        return SHIFTS[self.shift_index]

    @property
    def total_deliveries(self):
        return sum(len(shift) for shift in SHIFTS)

    @property
    def contract(self) -> Contract:
        return self.contracts[self.contract_index]

    @property
    def zone(self) -> tuple[int, int, int, int] | None:
        if self.state in ("pickup", "handover"):
            return PICKUP_ZONE

        if self.state == "dropoff":
            return self.contract.destination

        return None

    @property
    def objective(self):
        total = len(self.contracts)

        progress = (
            f"S{self.shift_number} "
            f"{self.contract_index + 1}/{total}"
        )

        if self.state == "handover":
            return (
                f"SHIFT {self.shift_number}/{len(SHIFTS)} "
                "DONE - DEPOT"
            )

        if self.state == "pickup":
            return (
                f"{progress} DEPOT - "
                f"{self.contract.kind}"
            )

        if self.state == "dropoff":
            return (
                f"{progress} {self.contract.name} "
                f"{self.timer_text}"
            )

        return (
            "NIGHT COMPLETE - "
            f"{self.completed_count}/{self.total_deliveries}"
        )

    @property
    def timer_text(self):
        if self.time_left <= 0.0:
            return "LATE"

        seconds = math.ceil(self.time_left)
        minutes, seconds = divmod(seconds, 60)

        return f"{minutes:02d}:{seconds:02d}"

    @property
    def time_bonus(self):
        fraction = max(
            0.0,
            min(
                self.time_left / self.contract.time_limit,
                1.0,
            ),
        )

        return int(self.MAX_TIME_BONUS * fraction)

    @property
    def cargo_status(self):
        if self.contract.kind == "FRAGILE":
            return (
                "FRAGILE "
                f"{math.ceil(self.cargo_condition)}%"
            )

        if (
            self.contract.kind == "EXPRESS"
            and self.time_left <= 0.0
        ):
            return "EXPRESS LATE"

        return self.contract.kind

    def calculate_reward(self):
        if (
            self.contract.kind == "EXPRESS"
            and self.time_left <= 0.0
        ):
            return self.contract.reward // 2

        reward = self.contract.reward + self.time_bonus

        if self.contract.kind == "FRAGILE":
            reward = math.floor(
                reward * self.cargo_condition / 100.0
            )

        return reward

    @property
    def marker_colour(self):
        if self.state in ("pickup", "handover"):
            return TEAL

        if self.time_left <= 15.0:
            return CORAL

        if self.contract.kind == "FRAGILE":
            return LILAC

        return AMBER

    def update(self, dt, car):
        self.elapsed = (self.elapsed + dt) % 2.0

        self.message_time = max(
            0.0,
            self.message_time - dt,
        )

        # Compare actual vehicle damage.
        # Braking alone therefore cannot damage cargo.
        damage = max(
            0.0,
            self.previous_car_condition - car.condition,
        )

        self.previous_car_condition = car.condition

        if (
            self.state == "dropoff"
            and self.contract.kind == "FRAGILE"
            and damage > 0.0
        ):
            self.cargo_condition = max(
                0.0,
                self.cargo_condition
                - damage * self.FRAGILE_DAMAGE_MULTIPLIER,
            )

            self.feedback(
                "Fragile parcel: "
                f"{math.ceil(self.cargo_condition)}% intact."
            )

        if car.disabled:
            return

        # main.py calls this only while the game has focus.
        if self.state == "dropoff":
            was_on_time = self.time_left > 0.0

            self.time_left = max(
                0.0,
                self.time_left - dt,
            )

            # Remove tiny floating-point remainders.
            if self.time_left < 0.000001:
                self.time_left = 0.0

            if (
                was_on_time
                and self.time_left == 0.0
                and self.contract.kind == "EXPRESS"
            ):
                self.feedback(
                    "Express late: base reward halved."
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
                "Night complete. R starts a new run."
            )
            return

        if car.disabled:
            self.feedback(
                "Vehicle disabled. R restarts night."
            )
            return

        if not self.contains(car):
            self.feedback(
                "Move into the marked bay."
            )
            return

        if abs(car.speed) > self.STOP_SPEED:
            self.feedback(
                "Stop first: hold SPACE."
            )
            return

        if self.state == "handover":
            self.shift_index += 1
            self.contract_index = 0
            self.state = "pickup"

            self.feedback(
                f"Shift {self.shift_number} ready. E: collect parcel."
            )
            return

        if self.state == "pickup":
            self.state = "dropoff"
            self.time_left = self.contract.time_limit
            self.cargo_condition = 100.0

            # Existing vehicle damage must not be applied
            # to a newly collected parcel.
            self.previous_car_condition = car.condition

            if self.contract.kind == "FRAGILE":
                self.feedback(
                    "Fragile loaded. Avoid crashes."
                )

            elif self.contract.kind == "EXPRESS":
                self.feedback(
                    "Express loaded. Late = half pay."
                )

            else:
                self.feedback(
                    "Standard loaded. Timer started."
                )

            return

        reward = self.calculate_reward()

        if self.contract.kind == "FRAGILE":
            receipt = (
                f"+{reward} pts. "
                f"Parcel {math.ceil(self.cargo_condition)}%."
            )

        elif (
            self.contract.kind == "EXPRESS"
            and self.time_left <= 0.0
        ):
            receipt = f"+{reward} pts. Late: half pay."

        else:
            receipt = (
                f"+{reward} pts "
                f"(+{self.time_bonus} time)."
            )

        self.score += reward
        self.completed_count += 1
        self.time_left = 0.0

        if self.contract_index + 1 == len(self.contracts):
            if self.shift_index + 1 == len(SHIFTS):
                self.state = "complete"

                self.feedback(
                    f"Night finished! Total: {self.score} points."
                )

            else:
                self.state = "handover"

                self.feedback(
                    f"Shift {self.shift_number} done! "
                    f"+{reward} pts. Depot next."
                )

        else:
            self.contract_index += 1
            self.state = "pickup"

            self.feedback(
                f"{receipt} Depot next."
            )

    def prompt(self, car):
        if car.disabled and self.state != "complete":
            return "Vehicle disabled. R restarts night."

        if self.message_time > 0.0:
            return self.message

        zone = self.zone

        if zone is None:
            return (
                f"{self.total_deliveries} deliveries done. R to replay."
            )

        if self.contains(car):
            if abs(car.speed) > self.STOP_SPEED:
                return "Stop first: hold SPACE."

            if self.state == "handover":
                return (
                    f"E: START SHIFT {self.shift_number + 1}"
                )

            if self.state == "pickup":
                return f"E: COLLECT {self.contract.kind}"

            return f"E: DELIVER {self.cargo_status}"

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

        if self.state == "handover":
            status = "DEPOT"

        elif self.state == "pickup":
            status = self.contract.kind

        else:
            status = self.cargo_status

        return f"{status} | {bearing} {distance}px"

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