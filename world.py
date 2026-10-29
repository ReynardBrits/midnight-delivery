WORLD_WIDTH = 2560
WORLD_HEIGHT = 1920

ROAD_WIDTH = 160
VERTICAL_ROADS = (500, 1300, 2100)
HORIZONTAL_ROADS = (280, 840, 1400)

WATER_X = 2440
SPAWN = (540, 560)

BACKGROUND = (0.071, 0.106, 0.200, 1.0)
ROAD = (0.180, 0.220, 0.290, 1.0)
PAVEMENT = (0.300, 0.350, 0.420, 1.0)
ROAD_MARKING = (0.760, 0.780, 0.750, 1.0)

RESIDENTIAL = (0.160, 0.220, 0.330, 1.0)
COMMERCIAL = (0.150, 0.280, 0.330, 1.0)
INDUSTRIAL = (0.260, 0.220, 0.300, 1.0)

ROOF_EDGE = (0.230, 0.310, 0.430, 1.0)
SHADOW = (0.035, 0.055, 0.100, 1.0)
WINDOW_LIGHT = (1.000, 0.710, 0.280, 1.0)
TEAL = (0.227, 0.839, 0.784, 1.0)

WATER = (0.045, 0.155, 0.245, 1.0)
QUAY = (0.230, 0.300, 0.370, 1.0)
PARK = (0.095, 0.205, 0.180, 1.0)
PARK_PATH = (0.270, 0.330, 0.300, 1.0)

BUILDINGS = (
    (80, 70, 300, 130),
    (1510, 70, 210, 150),
    (1810, 70, 200, 150),
    (2300, 50, 100, 170),
    (70, 510, 160, 220),
    (310, 510, 120, 220),
    (710, 510, 220, 240),
    (1030, 510, 210, 240),
    (1510, 510, 210, 240),
    (1810, 510, 210, 240),
    (2300, 500, 100, 250),
    (70, 1070, 160, 230),
    (310, 1070, 120, 230),
    (710, 1070, 220, 230),
    (1030, 1070, 210, 230),
    (1510, 1070, 210, 230),
    (1810, 1070, 210, 230),
    (2300, 1060, 100, 260),
    (80, 1640, 300, 180),
    (710, 1640, 220, 180),
    (1030, 1640, 210, 180),
    (1510, 1620, 210, 230),
    (1810, 1620, 210, 230),
    (2300, 1620, 100, 230),
)


class World:
    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT
        self.spawn = SPAWN
        self.buildings = BUILDINGS

        # The water also blocks the car.
        water_boundary = (
            WATER_X,
            0,
            WORLD_WIDTH - WATER_X,
            WORLD_HEIGHT,
        )

        self.obstacles = (
            self.buildings + (water_boundary,)
        )

    def draw_building(self, renderer, building):
        x, y, width, height = building

        if x < 660:
            colour = RESIDENTIAL
        elif x < 1460:
            colour = COMMERCIAL
        else:
            colour = INDUSTRIAL

        renderer.draw_rect(
            x + 8, y + 8, width, height, SHADOW
        )

        renderer.draw_rect(
            x, y, width, height, colour
        )

        renderer.draw_rect(
            x, y, width, 8, ROOF_EDGE
        )

        for window_x in range(
            int(x + 20), int(x + width - 15), 40
        ):
            renderer.draw_rect(
                window_x,
                y + height - 14,
                18,
                6,
                WINDOW_LIGHT,
            )

    def draw(self, renderer):
        # Waterfront.
        renderer.draw_rect(
            WATER_X,
            0,
            WORLD_WIDTH - WATER_X,
            WORLD_HEIGHT,
            WATER,
        )

        renderer.draw_rect(
            WATER_X - 40,
            0,
            40,
            WORLD_HEIGHT,
            QUAY,
        )

        # Draw pavements first.
        for x in VERTICAL_ROADS:
            renderer.draw_rect(
                x - 12,
                0,
                ROAD_WIDTH + 24,
                WORLD_HEIGHT,
                PAVEMENT,
            )

        for y in HORIZONTAL_ROADS:
            renderer.draw_rect(
                0,
                y - 12,
                WATER_X,
                ROAD_WIDTH + 24,
                PAVEMENT,
            )

        # Draw connected road surfaces.
        for x in VERTICAL_ROADS:
            renderer.draw_rect(
                x,
                0,
                ROAD_WIDTH,
                WORLD_HEIGHT,
                ROAD,
            )

        for y in HORIZONTAL_ROADS:
            renderer.draw_rect(
                0,
                y,
                WATER_X,
                ROAD_WIDTH,
                ROAD,
            )

        # Vertical centre markings.
        for road_x in VERTICAL_ROADS:
            for y in range(0, WORLD_HEIGHT, 50):
                in_junction = any(
                    y < road_y + ROAD_WIDTH
                    and y + 26 > road_y
                    for road_y in HORIZONTAL_ROADS
                )

                if not in_junction:
                    renderer.draw_rect(
                        road_x + 78,
                        y,
                        4,
                        26,
                        ROAD_MARKING,
                    )

        # Horizontal centre markings.
        for road_y in HORIZONTAL_ROADS:
            for x in range(0, WATER_X - 25, 50):
                in_junction = any(
                    x < road_x + ROAD_WIDTH
                    and x + 26 > road_x
                    for road_x in VERTICAL_ROADS
                )

                if not in_junction:
                    renderer.draw_rect(
                        x,
                        road_y + 78,
                        26,
                        4,
                        ROAD_MARKING,
                    )

        # Northern park and its paths.
        renderer.draw_rect(
            720, 60, 480, 170, PARK
        )
        renderer.draw_rect(
            945, 60, 30, 170, PARK_PATH
        )
        renderer.draw_rect(
            720, 130, 480, 30, PARK_PATH
        )

        # Town buildings.
        for building in self.buildings:
            self.draw_building(renderer, building)

        # Loading bay outside the depot.
        renderer.draw_rect(120, 206, 200, 4, TEAL)
        renderer.draw_rect(120, 262, 200, 4, TEAL)
        renderer.draw_rect(120, 206, 4, 60, TEAL)
        renderer.draw_rect(316, 206, 4, 60, TEAL)