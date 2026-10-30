import math


class Fuel:
    """Track fuel separately from vehicle condition and delivery progress."""

    CAPACITY = 100.0
    LOW_LEVEL = 15.0

    IDLE_RATE = 0.08
    DRIVING_RATE = 0.18

    REFILL_AMOUNT = 40.0
    POINTS_PER_UNIT = 1.5

    def __init__(self):
        self.reset()

    def reset(self):
        self.amount = self.CAPACITY
        self.points_spent = 0

    @property
    def empty(self) -> bool:
        return self.amount <= 0.0

    @property
    def low(self) -> bool:
        return self.amount <= self.LOW_LEVEL

    @property
    def percentage(self) -> int:
        return math.ceil(
            100.0 * self.amount / self.CAPACITY
        )

    def update(
        self,
        dt: float,
        speed: float,
        max_speed: float,
    ):
        """Consume fuel during active simulation, including while idling."""
        if dt <= 0.0 or self.empty:
            return

        if max_speed <= 0.0:
            raise ValueError("Maximum speed must be positive.")

        speed_fraction = min(
            abs(speed) / max_speed,
            1.0,
        )

        rate = (
            self.IDLE_RATE
            + self.DRIVING_RATE * speed_fraction
        )

        self.amount = max(
            0.0,
            self.amount - rate * dt,
        )

        if self.amount < 0.000001:
            self.amount = 0.0

    def refill_quote(self) -> tuple[float, int]:
        """Quote up to 40 units, charging only for the available space."""
        missing = max(
            0.0,
            self.CAPACITY - self.amount,
        )

        if missing < 0.000001:
            return 0.0, 0

        amount = min(self.REFILL_AMOUNT, missing)

        # Remove tiny floating-point errors before rounding up.
        cost = math.ceil(
            round(amount * self.POINTS_PER_UNIT, 6)
        )

        return amount, cost

    def refuel(self, available_points: int) -> int:
        """Add fuel and return the cost for the caller to deduct from score."""
        amount, cost = self.refill_quote()

        if cost == 0 or available_points < cost:
            return 0

        self.amount = min(
            self.CAPACITY,
            self.amount + amount,
        )

        self.points_spent += cost
        return cost