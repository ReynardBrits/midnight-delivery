import math

from delivery import PICKUP_ZONE
from world import (
    CONTAINERS,
    HORIZONTAL_ROADS,
    ROAD_WIDTH,
    VERTICAL_ROADS,
    WATER_X,
    lettering,
)


PANEL = (0.035, 0.060, 0.100, 0.96)
OUTLINE = (0.220, 0.400, 0.470, 0.9)
GROUND = (0.075, 0.110, 0.170, 1.0)
GARDENS = (0.100, 0.220, 0.180, 1.0)
HARBOUR = (0.170, 0.160, 0.240, 1.0)
WATER = (0.035, 0.170, 0.260, 1.0)
ROAD = (0.370, 0.440, 0.520, 1.0)
CONTAINER = (0.490, 0.440, 0.330, 1.0)
VIEW = (0.650, 0.780, 0.850, 0.6)

WHITE = (0.920, 0.960, 1.000, 1.0)
MUTED = (0.520, 0.650, 0.730, 1.0)
TEAL = (0.227, 0.839, 0.784, 1.0)
AMBER = (1.000, 0.745, 0.357, 1.0)


class Minimap:
    """Draw a north-up overview using the town's actual layout."""

    WIDTH = 264
    HEIGHT = 252

    def __init__(self, screen_width):
        # Leave the outer edge clear for the guidance arrow.
        self.left = screen_width - self.WIDTH - 64
        self.top = 64

    def draw(self, renderer, world, car, delivery, camera):
        r = renderer.draw_rect
        left, top = self.left, self.top

        r(
            left + 4, top + 5,
            self.WIDTH, self.HEIGHT,
            (0, 0, 0, 0.3),
        )

        r(
            left, top,
            self.WIDTH, self.HEIGHT,
            PANEL,
        )

        def outline(x, y, width, height, tint):
            r(x, y, width, 1, tint)
            r(x, y + height - 1, width, 1, tint)
            r(x, y, 1, height, tint)
            r(x + width - 1, y, 1, height, tint)

        outline(
            left, top,
            self.WIDTH, self.HEIGHT,
            OUTLINE,
        )

        lettering(
            renderer,
            "TOWN MAP",
            left + 12, top + 10,
            WHITE,
        )

        lettering(
            renderer,
            "TAB",
            left + 235, top + 15,
            MUTED,
            scale=1,
        )

        box_width = 240
        box_height = 184

        scale = min(
            box_width / world.width,
            box_height / world.height,
        )

        map_width = world.width * scale
        map_height = world.height * scale

        map_x = (
            left + 12
            + (box_width - map_width) / 2
        )

        map_y = (
            top + 34
            + (box_height - map_height) / 2
        )

        def point(x, y):
            return (
                map_x + x * scale,
                map_y + y * scale,
            )

        def block(x, y, width, height, tint):
            px, py = point(x, y)

            r(
                px, py,
                width * scale,
                height * scale,
                tint,
            )

        block(
            0, 0,
            world.width, world.height,
            GROUND,
        )

        block(
            0, 1600,
            2260, world.height - 1600,
            GARDENS,
        )

        block(
            2260, 0,
            WATER_X - 2260, world.height,
            HARBOUR,
        )

        block(
            WATER_X, 0,
            world.width - WATER_X, world.height,
            WATER,
        )

        for x in VERTICAL_ROADS:
            block(
                x, 0,
                ROAD_WIDTH, world.height,
                ROAD,
            )

        for y in HORIZONTAL_ROADS:
            block(
                0, y,
                WATER_X - 40, ROAD_WIDTH,
                ROAD,
            )

        for index, building in enumerate(world.buildings):
            roof, _, _ = world.building_style(
                building, index
            )

            x, y, width, height = building
            block(x, y, width, height, roof)

        for x, y, width, height in CONTAINERS:
            block(
                x, y,
                width, height,
                CONTAINER,
            )

        # Outline the area currently shown by the camera.
        view_x, view_y = point(
            camera.x, camera.y
        )

        outline(
            view_x,
            view_y,
            camera.width * scale,
            camera.view_height * scale,
            VIEW,
        )

        depot_x, depot_y, depot_w, depot_h = PICKUP_ZONE

        dx, dy = point(
            depot_x + depot_w / 2,
            depot_y + depot_h / 2,
        )

        r(dx - 4, dy - 4, 8, 8, PANEL)
        r(dx - 3, dy - 3, 6, 6, TEAL)

        zone = delivery.zone

        goal_colour = (
            delivery.marker_colour
            if zone is not None
            else MUTED
        )

        if zone is not None:
            x, y, width, height = zone

            gx, gy = point(
                x + width / 2,
                y + height / 2,
            )

            pulse = (
                0.65
                + 0.3 * math.sin(
                    math.tau * delivery.elapsed
                )
            )

            outline(
                gx - 6, gy - 6,
                12, 12,
                goal_colour[:3] + (pulse,),
            )

            r(
                gx - 3, gy - 3,
                6, 6,
                goal_colour,
            )

        # Magnify the car symbol so its heading stays visible.
        cx, cy = point(car.x, car.y)

        r(
            cx - 4, cy - 5,
            8, 10,
            PANEL,
            angle=car.angle,
        )

        r(
            cx - 3, cy - 4,
            6, 8,
            WHITE,
            angle=car.angle,
        )

        angle = math.radians(car.angle)

        nose_x = cx + math.sin(angle) * 3
        nose_y = cy - math.cos(angle) * 3

        r(
            nose_x - 2, nose_y - 1,
            4, 2,
            AMBER,
            angle=car.angle,
        )

        for offset, label, tint in (
            (12, "YOU", WHITE),
            (80, "DEPOT", TEAL),
            (172, "GOAL", goal_colour),
        ):
            r(
                left + offset, top + 231,
                4, 4,
                tint,
            )

            lettering(
                renderer,
                label,
                left + offset + 9,
                top + 230,
                tint,
                scale=1,
            )