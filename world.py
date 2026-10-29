WORLD_WIDTH = 2560
WORLD_HEIGHT = 1920
ROAD_WIDTH = 160

VERTICAL_ROADS = (500, 1300, 2100)
HORIZONTAL_ROADS = (280, 840, 1400)

WATER_X = 2440
SPAWN = (540, 560)


def colour(hex_value, alpha=1.0):
    """Convert an RGB hex colour into OpenGL colour values."""
    rgb = tuple(
        int(hex_value[i:i + 2], 16) / 255.0
        for i in (0, 2, 4)
    )
    return rgb + (alpha,)


BACKGROUND = colour("121B2D")
ROAD = colour("293345")
PAVEMENT = colour("4B596D")
MARKING = colour("B4C0C4")

SHADOW = colour("0A1020", 0.8)
ROOF_EDGE = colour("1A263A")
ROOF_LINE = colour("52627A", 0.45)

RESIDENTIAL = colour("354764")
COMMERCIAL = colour("29525F")
INDUSTRIAL = colour("49435A")

GLASS = colour("142C42")
WINDOW_LIGHT = colour("FFC36B")

TEAL = colour("3AD6C8")
TEAL_DARK = colour("287F85")
METAL = colour("6C7D91")

WATER = colour("0B273E")
WAVE = colour("28556D")
QUAY = colour("394A60")

PARK = colour("183C36")
PARK_PATH = colour("59665B")

TREE_BED = colour("263C3B")
TREE_DARK = colour("163B32")
TREE = colour("245B48")
TREE_LIGHT = colour("38725A")

LAMP_GLOW = colour("FFD793", 0.045)


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


TREES = (
    (765, 100),
    (855, 100),
    (1050, 100),
    (1140, 100),
    (765, 195),
    (855, 195),
    (1050, 195),
    (1140, 195),
)


LAMPS = tuple(
    point
    for x in VERTICAL_ROADS
    for y in HORIZONTAL_ROADS
    for point in (
        (x - 22, y - 22),
        (x + 182, y + 182),
    )
)


class World:
    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT
        self.spawn = SPAWN
        self.buildings = BUILDINGS

        water = (
            WATER_X,
            0,
            WORLD_WIDTH - WATER_X,
            WORLD_HEIGHT,
        )

        tree_beds = tuple(
            (x - 24, y - 24, 48, 48)
            for x, y in TREES
        )

        lamp_bases = tuple(
            (x - 6, y - 6, 12, 12)
            for x, y in LAMPS
        )

        self.obstacles = (
            self.buildings
            + (water,)
            + tree_beds
            + lamp_bases
        )

    def draw_waterfront(self, renderer):
        r = renderer.draw_rect

        r(
            WATER_X,
            0,
            WORLD_WIDTH - WATER_X,
            WORLD_HEIGHT,
            WATER,
        )

        r(
            WATER_X - 40,
            0,
            40,
            WORLD_HEIGHT,
            QUAY,
        )

        for y in range(20, WORLD_HEIGHT, 80):
            r(WATER_X - 38, y, 36, 2, ROOF_EDGE)
            r(WATER_X + 18, y + 16, 46, 2, WAVE)
            r(WATER_X + 46, y + 44, 58, 2, WAVE)

    def draw_roads(self, renderer):
        r = renderer.draw_rect

        for x in VERTICAL_ROADS:
            r(
                x - 12,
                0,
                ROAD_WIDTH + 24,
                WORLD_HEIGHT,
                PAVEMENT,
            )

        for y in HORIZONTAL_ROADS:
            r(
                0,
                y - 12,
                WATER_X,
                ROAD_WIDTH + 24,
                PAVEMENT,
            )

        for x in VERTICAL_ROADS:
            r(x, 0, ROAD_WIDTH, WORLD_HEIGHT, ROAD)

        for y in HORIZONTAL_ROADS:
            r(0, y, WATER_X, ROAD_WIDTH, ROAD)

        # Leave clear space around junctions and crossings.
        for x in VERTICAL_ROADS:
            for y in range(0, WORLD_HEIGHT, 50):
                near_junction = any(
                    y < road_y + ROAD_WIDTH + 38
                    and y + 26 > road_y - 38
                    for road_y in HORIZONTAL_ROADS
                )

                if not near_junction:
                    r(x + 78, y, 4, 26, MARKING)

        for y in HORIZONTAL_ROADS:
            for x in range(0, WATER_X - 25, 50):
                near_junction = any(
                    x < road_x + ROAD_WIDTH + 38
                    and x + 26 > road_x - 38
                    for road_x in VERTICAL_ROADS
                )

                if not near_junction:
                    r(x, y + 78, 26, 4, MARKING)

        # Four zebra crossings around each junction.
        for x in VERTICAL_ROADS:
            for y in HORIZONTAL_ROADS:
                for offset in range(12, 145, 20):
                    r(
                        x + offset,
                        y - 32,
                        12,
                        20,
                        MARKING,
                    )

                    r(
                        x + offset,
                        y + 172,
                        12,
                        20,
                        MARKING,
                    )

                    r(
                        x - 32,
                        y + offset,
                        20,
                        12,
                        MARKING,
                    )

                    r(
                        x + 172,
                        y + offset,
                        20,
                        12,
                        MARKING,
                    )

    def draw_building(self, renderer, building, index):
        r = renderer.draw_rect
        x, y, width, height = building
        is_depot = index == 0

        if is_depot or 660 <= x < 1460:
            roof = COMMERCIAL
        elif x < 660:
            roof = RESIDENTIAL
        else:
            roof = INDUSTRIAL

        r(x + 9, y + 10, width, height, SHADOW)
        r(x, y, width, height, ROOF_EDGE)
        r(x + 6, y + 6, width - 12, height - 12, roof)

        # Roof seams and a raised central ridge.
        for seam_y in range(
            y + 30,
            y + height - 18,
            32,
        ):
            r(x + 9, seam_y, width - 18, 2, ROOF_LINE)

        r(
            x + width / 2 - 2,
            y + 8,
            4,
            height - 16,
            ROOF_EDGE,
        )

        # Skylights with a small reflected highlight.
        for light_x in range(
            x + 18,
            x + width - 40,
            56,
        ):
            r(light_x, y + 20, 28, 18, ROOF_EDGE)
            r(light_x + 3, y + 23, 22, 12, GLASS)
            r(light_x + 4, y + 24, 18, 2, METAL)

        # Ventilation unit.
        r(
            x + width - 38,
            y + height - 52,
            22,
            22,
            ROOF_EDGE,
        )

        r(
            x + width - 36,
            y + height - 50,
            18,
            16,
            METAL,
        )

        for vent_y in range(
            y + height - 47,
            y + height - 35,
            4,
        ):
            r(
                x + width - 33,
                vent_y,
                12,
                2,
                ROOF_EDGE,
            )

        # Warm windows along the front edge.
        for window_x in range(
            x + 18,
            x + width - 28,
            40,
        ):
            r(
                window_x,
                y + height - 14,
                20,
                6,
                WINDOW_LIGHT,
            )

        if roof == COMMERCIAL:
            for awning_x in range(
                x + 8,
                x + width - 8,
                20,
            ):
                stripe_index = (
                    (awning_x - x - 8) // 20
                )

                stripe = (
                    TEAL
                    if stripe_index % 2 == 0
                    else TEAL_DARK
                )

                stripe_width = min(
                    20,
                    x + width - 8 - awning_x,
                )

                r(
                    awning_x,
                    y + height - 6,
                    stripe_width,
                    10,
                    stripe,
                )

        if is_depot:
            # A distinctive loading door and teal roof sign.
            r(
                x + 116,
                y + height - 18,
                68,
                18,
                GLASS,
            )

            r(
                x + 110,
                y + 48,
                80,
                24,
                ROOF_EDGE,
            )

            r(
                x + 116,
                y + 54,
                68,
                12,
                TEAL,
            )

    def draw_park(self, renderer):
        r = renderer.draw_rect

        r(720, 60, 480, 170, PARK)
        r(945, 60, 30, 170, PARK_PATH)
        r(720, 130, 480, 30, PARK_PATH)

        for x, y in TREES:
            # Raised beds make the collision area visible.
            r(x - 24, y - 24, 48, 48, TREE_BED)
            r(x - 12, y - 13, 38, 38, SHADOW)

            r(x - 20, y - 12, 40, 24, TREE_DARK)
            r(x - 12, y - 20, 24, 40, TREE_DARK)

            r(x - 16, y - 11, 32, 22, TREE)
            r(x - 10, y - 17, 20, 34, TREE)

            r(x - 11, y - 12, 14, 12, TREE_LIGHT)

    def draw_lamps(self, renderer):
        r = renderer.draw_rect

        for x, y in LAMPS:
            # Translucent shapes suggest pools of light.
            r(x - 36, y - 20, 72, 40, LAMP_GLOW)
            r(x - 24, y - 32, 48, 64, LAMP_GLOW)
            r(x - 18, y - 18, 36, 36, LAMP_GLOW)

            r(x - 3, y - 2, 14, 14, SHADOW)
            r(x - 6, y - 6, 12, 12, ROOF_EDGE)
            r(x - 4, y - 4, 8, 8, METAL)
            r(x - 3, y - 3, 6, 6, WINDOW_LIGHT)

    def draw(self, renderer):
        self.draw_waterfront(renderer)
        self.draw_roads(renderer)
        self.draw_park(renderer)

        for index, building in enumerate(self.buildings):
            self.draw_building(
                renderer,
                building,
                index,
            )

        # Depot loading bay.
        r = renderer.draw_rect

        r(120, 206, 200, 4, TEAL)
        r(120, 262, 200, 4, TEAL)
        r(120, 206, 4, 60, TEAL)
        r(316, 206, 4, 60, TEAL)

        for x in range(140, 300, 40):
            r(x, 251, 20, 3, TEAL_DARK)

        self.draw_lamps(renderer)