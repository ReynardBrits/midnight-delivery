WORLD_WIDTH = 3360
WORLD_HEIGHT = 2560
ROAD_WIDTH = 160

VERTICAL_ROADS = (500, 1300, 2100, 2780)
HORIZONTAL_ROADS = (280, 840, 1400, 2040)
WATER_X = 3160
SPAWN = (540, 560)


def colour(hex_value, alpha=1.0):
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


# The first building remains the depot.
SHOPS = (
    (80, 70, 300, 130),
    (1510, 70, 210, 150),
    (1810, 70, 200, 150),
    (70, 510, 160, 220),
    (310, 510, 120, 220),
    (710, 510, 220, 240),
    (1030, 510, 210, 240),
    (1510, 510, 210, 240),
    (1810, 510, 210, 240),
    (70, 1070, 160, 230),
    (310, 1070, 120, 230),
    (710, 1070, 220, 230),
    (1030, 1070, 210, 230),
    (1510, 1070, 210, 230),
    (1810, 1070, 210, 230),
)

HOUSES = tuple(
    (x, y, 120, 128)
    for y in (1650, 1870, 2290)
    for x in (
        80, 285,
        710, 915, 1120,
        1510, 1715, 1920,
    )
)

WAREHOUSES = (
    (2330, 70, 380, 150),
    (3000, 70, 112, 150),
    (2330, 510, 380, 190),
    (3000, 510, 112, 200),
    (2330, 1070, 380, 190),
    (3000, 1070, 112, 200),
    (2330, 1640, 380, 150),
    (3000, 1640, 112, 230),
    (2330, 2290, 380, 160),
    (3000, 2290, 112, 170),
)

BUILDINGS = SHOPS + HOUSES + WAREHOUSES

CONTAINERS = (
    (2490, 720, 190, 56),
    (2340, 1280, 150, 64),
    (2530, 1280, 150, 64),
    (2340, 1850, 150, 64),
    (2530, 1850, 150, 64),
    (2340, 1940, 150, 64),
    (2530, 1940, 150, 64),
    (2980, 750, 150, 64),
    (2980, 1300, 150, 64),
    (2980, 1920, 150, 64),
)

PARK_TREES = (
    (765, 100),
    (855, 100),
    (1050, 100),
    (1140, 100),
    (765, 195),
    (855, 195),
    (1050, 195),
    (1140, 195),
)

TREES = PARK_TREES + tuple(
    (x + 150, y + 24)
    for x, y, _, _ in HOUSES
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

BOLLARDS = tuple(
    (WATER_X - 20, y)
    for y in (200, 600, 1180, 1740, 2380)
)


# Original pixel lettering for rooftop and district signs.
LETTERS = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 14),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (31, 4, 4, 4, 4, 4, 31),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "W": (17, 17, 17, 21, 21, 21, 10),
    "Y": (17, 17, 10, 4, 4, 4, 4),
}


def lettering(renderer, text, x, y, tint, scale=2):
    for index, character in enumerate(text):
        rows = LETTERS.get(character, (0,) * 7)

        for row, bits in enumerate(rows):
            for column in range(5):
                if bits & (1 << (4 - column)):
                    renderer.draw_rect(
                        x + (index * 6 + column) * scale,
                        y + row * scale,
                        scale,
                        scale,
                        tint,
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

        bollards = tuple(
            (x - 8, y - 8, 16, 16)
            for x, y in BOLLARDS
        )

        self.obstacles = (
            BUILDINGS
            + CONTAINERS
            + (water,)
            + tree_beds
            + lamp_bases
            + bollards
        )

    def draw_ground(self, renderer):
        r = renderer.draw_rect

        r(
            0, 1600,
            2260, WORLD_HEIGHT - 1600,
            colour("20342F"),
        )

        r(
            2260, 0,
            WATER_X - 2260, WORLD_HEIGHT,
            colour("303348"),
        )

        for x, y, _, _ in HOUSES:
            r(x - 16, y - 16, 192, 200, PARK)
            r(x + 42, y + 128, 36, 64, PARK_PATH)

            for offset in (0, 16, 32):
                r(
                    x + 8 + offset, y + 153,
                    9, 7,
                    colour("96637E"),
                )

        r(720, 60, 480, 170, PARK)
        r(945, 60, 30, 170, PARK_PATH)
        r(720, 130, 480, 30, PARK_PATH)

    def draw_waterfront(self, renderer):
        r = renderer.draw_rect

        r(
            WATER_X, 0,
            WORLD_WIDTH - WATER_X, WORLD_HEIGHT,
            WATER,
        )

        r(
            WATER_X - 40, 0,
            40, WORLD_HEIGHT,
            QUAY,
        )

        r(
            WATER_X - 4, 0,
            4, WORLD_HEIGHT,
            METAL,
        )

        for y in range(20, WORLD_HEIGHT, 80):
            r(WATER_X - 38, y, 36, 2, ROOF_EDGE)
            r(WATER_X + 18, y + 16, 46, 2, WAVE)
            r(WATER_X + 86, y + 44, 72, 2, WAVE)

        for x, y in BOLLARDS:
            r(x - 5, y - 4, 18, 18, SHADOW)
            r(x - 8, y - 8, 16, 16, ROOF_EDGE)
            r(x - 6, y - 6, 12, 6, WINDOW_LIGHT)

    def draw_roads(self, renderer):
        r = renderer.draw_rect

        for x in VERTICAL_ROADS:
            r(
                x - 12, 0,
                ROAD_WIDTH + 24, WORLD_HEIGHT,
                PAVEMENT,
            )

        for y in HORIZONTAL_ROADS:
            r(
                0, y - 12,
                WATER_X - 40, ROAD_WIDTH + 24,
                PAVEMENT,
            )

        for x in VERTICAL_ROADS:
            r(x, 0, ROAD_WIDTH, WORLD_HEIGHT, ROAD)

        for y in HORIZONTAL_ROADS:
            r(0, y, WATER_X - 40, ROAD_WIDTH, ROAD)

        for x in VERTICAL_ROADS:
            for y in range(0, WORLD_HEIGHT, 50):
                near_junction = any(
                    y < ry + ROAD_WIDTH + 38
                    and y + 26 > ry - 38
                    for ry in HORIZONTAL_ROADS
                )

                if not near_junction:
                    r(x + 78, y, 4, 26, MARKING)

        for y in HORIZONTAL_ROADS:
            for x in range(0, WATER_X - 65, 50):
                near_junction = any(
                    x < rx + ROAD_WIDTH + 38
                    and x + 26 > rx - 38
                    for rx in VERTICAL_ROADS
                )

                if not near_junction:
                    r(x, y + 78, 26, 4, MARKING)

        for x in VERTICAL_ROADS:
            for y in HORIZONTAL_ROADS:
                for offset in range(12, 145, 20):
                    r(
                        x + offset, y - 32,
                        12, 20, MARKING,
                    )

                    r(
                        x + offset, y + 172,
                        12, 20, MARKING,
                    )

                    r(
                        x - 32, y + offset,
                        20, 12, MARKING,
                    )

                    r(
                        x + 172, y + offset,
                        20, 12, MARKING,
                    )

    def building_style(self, building, index):
        x, y, _, height = building

        if index == 0:
            roof, depth = COMMERCIAL, 36

        elif x >= 2260:
            roof = INDUSTRIAL
            depth = 32 + (index % 3) * 6

        elif y >= 1600:
            roof, depth = RESIDENTIAL, 26

        else:
            roof = COMMERCIAL
            depth = 48 + (index % 2) * 8

        depth = min(depth, int(height * 0.4))

        return roof, depth, round(depth * 0.4)

    def draw_building_shadow(
        self, renderer, building, index
    ):
        x, y, width, height = building

        _, depth, _ = self.building_style(
            building, index
        )

        sx = depth * 0.7
        sy = depth * 0.4
        shade = colour("070D1A", 0.42)

        renderer.draw_rect(
            x + 2, y + 3,
            width, height,
            shade,
        )

        renderer.draw_quad((
            (x + width, y),
            (x + width + sx, y + sy),
            (x + width + sx, y + height + sy),
            (x + width, y + height),
        ), shade)

        renderer.draw_quad((
            (x, y + height),
            (x + width, y + height),
            (x + width + sx, y + height + sy),
            (x + sx, y + height + sy),
        ), shade)

    def draw_building(
        self, renderer, building, index
    ):
        r = renderer.draw_rect
        q = renderer.draw_quad

        x, y, width, height = building

        roof, depth, dx = self.building_style(
            building, index
        )

        if roof == RESIDENTIAL:
            self.draw_house(renderer, building, index)
            return

        rw = width - dx
        rh = height - depth

        def shade(value, factor):
            return tuple(
                min(1.0, c * factor)
                for c in value[:3]
            ) + (value[3],)

        # Solid faces fit inside the collision rectangle.
        q((
            (x, y + rh),
            (x + rw, y + rh),
            (x + width, y + height),
            (x + dx, y + height),
        ), shade(roof, 0.78))

        q((
            (x + rw, y),
            (x + width, y + depth),
            (x + width, y + height),
            (x + rw, y + rh),
        ), shade(roof, 0.52))

        def facade(
            left, top, face_width, face_height,
            face_colour,
        ):
            shift_top = dx * top / depth

            shift_bottom = (
                dx * (top + face_height) / depth
            )

            q((
                (
                    x + left + shift_top,
                    y + rh + top,
                ),
                (
                    x + left + face_width + shift_top,
                    y + rh + top,
                ),
                (
                    x + left + face_width + shift_bottom,
                    y + rh + top + face_height,
                ),
                (
                    x + left + shift_bottom,
                    y + rh + top + face_height,
                ),
            ), face_colour)

        facade(0, depth - 3, rw, 3, ROOF_EDGE)

        rows = (
            (8, 29) if depth >= 50 else (8,)
        )

        for row_index, row in enumerate(rows):
            for column, left in enumerate(
                range(16, rw - 25, 40)
            ):
                if index == 0 and 96 < left < 190:
                    continue

                light = (
                    WINDOW_LIGHT
                    if (index + column + row_index) % 4
                    else GLASS
                )

                facade(
                    left - 2, row - 2,
                    24, 12,
                    ROOF_EDGE,
                )

                facade(
                    left, row,
                    20, 8,
                    light,
                )

        # Roof plane, parapet and highlights.
        r(x, y, rw, rh, ROOF_EDGE)

        r(
            x + 4, y + 4,
            rw - 8, rh - 8,
            shade(roof, 1.12),
        )

        r(
            x + 4, y + 4,
            rw - 8, 3,
            shade(roof, 1.45),
        )

        r(
            x + 4, y + 4,
            3, rh - 8,
            shade(roof, 1.3),
        )

        r(
            x + 4, y + rh - 7,
            rw - 8, 3,
            shade(roof, 0.7),
        )

        r(
            x + rw - 7, y + 4,
            3, rh - 8,
            shade(roof, 0.65),
        )

        for seam_y in range(
            y + 26, y + rh - 15, 30
        ):
            r(
                x + 9, seam_y,
                rw - 18, 2,
                ROOF_LINE,
            )

        r(
            x + rw / 2 - 2, y + 8,
            4, rh - 16,
            ROOF_EDGE,
        )

        r(
            x + rw / 2 - 2, y + 8,
            1, rh - 16,
            shade(roof, 1.35),
        )

        for light_x in range(
            x + 15, x + rw - 30, 56
        ):
            r(
                light_x + 3, y + 20,
                26, 17, SHADOW,
            )

            r(
                light_x, y + 17,
                26, 17, ROOF_EDGE,
            )

            r(
                light_x + 3, y + 20,
                20, 10, GLASS,
            )

            r(
                light_x + 4, y + 20,
                17, 2, METAL,
            )

        # Raised rooftop ventilation unit.
        vx = x + rw - 35
        vy = y + rh - 34

        r(vx + 4, vy + 5, 22, 18, SHADOW)
        r(vx, vy + 3, 22, 18, ROOF_EDGE)
        r(vx, vy, 22, 16, METAL)

        r(
            vx + 2, vy + 2,
            18, 2,
            shade(METAL, 1.3),
        )

        for offset in (6, 9, 12):
            r(
                vx + 4, vy + offset,
                14, 1, ROOF_EDGE,
            )

        if roof == COMMERCIAL:
            for left in range(8, rw - 8, 20):
                stripe = (
                    TEAL
                    if ((left - 8) // 20) % 2 == 0
                    else TEAL_DARK
                )

                facade(
                    left,
                    depth - 10,
                    min(20, rw - 8 - left),
                    8,
                    stripe,
                )

        if index == 0:
            # Loading door aligned with the depot bay.
            door_left = 116 - dx

            facade(
                door_left, depth - 24,
                68, 24, GLASS,
            )

            for offset in range(8, 64, 8):
                facade(
                    door_left + offset,
                    depth - 23,
                    1, 22,
                    METAL,
                )

            r(
                x + rw / 2 - 43, y + 43,
                86, 26, SHADOW,
            )

            r(
                x + rw / 2 - 43, y + 38,
                86, 26, ROOF_EDGE,
            )

            r(
                x + rw / 2 - 37, y + 44,
                74, 14, TEAL_DARK,
            )

            lettering(
                renderer,
                "DEPOT",
                x + rw / 2 - 29,
                y + 44,
                TEAL,
            )

        elif roof == COMMERCIAL:
            text = (
                "CAFE", "ARCADE", "MARKET"
            )[index % 3]

            sign_width = len(text) * 12 + 12
            left = x + (rw - sign_width) / 2

            r(
                left + 3, y + 43,
                sign_width, 26, SHADOW,
            )

            r(
                left, y + 39,
                sign_width, 26, ROOF_EDGE,
            )

            lettering(
                renderer,
                text,
                left + 7,
                y + 45,
                TEAL,
            )

    def draw_house(
        self, renderer, building, index
    ):
        r = renderer.draw_rect
        q = renderer.draw_quad

        x, y, width, height = building

        _, depth, dx = self.building_style(
            building, index
        )

        rw = width - dx
        rh = height - depth

        roof = (
            colour("58657B"),
            colour("735356"),
            colour("476775"),
        )[index % 3]

        q((
            (x, y + rh),
            (x + rw, y + rh),
            (x + width, y + height),
            (x + dx, y + height),
        ), RESIDENTIAL)

        q((
            (x + rw, y),
            (x + width, y + depth),
            (x + width, y + height),
            (x + rw, y + rh),
        ), ROOF_EDGE)

        def front(left, top, w, h, tint):
            a = dx * top / depth
            b = dx * (top + h) / depth

            q((
                (x + left + a, y + rh + top),
                (x + left + w + a, y + rh + top),
                (x + left + w + b, y + rh + top + h),
                (x + left + b, y + rh + top + h),
            ), tint)

        for left in (12, 78):
            front(left - 2, 5, 24, 14, ROOF_EDGE)
            front(left, 7, 20, 10, WINDOW_LIGHT)
            front(left + 9, 7, 2, 10, RESIDENTIAL)

        front(47, 5, 18, 21, GLASS)
        front(61, 16, 2, 2, WINDOW_LIGHT)

        r(x, y, rw, rh, ROOF_EDGE)

        q((
            (x + 3, y + 7),
            (x + rw / 2, y + 2),
            (x + rw / 2, y + rh - 7),
            (x + 3, y + rh - 2),
        ), roof)

        darker = tuple(
            c * 0.65 for c in roof[:3]
        ) + (1.0,)

        q((
            (x + rw / 2, y + 2),
            (x + rw - 3, y + 7),
            (x + rw - 3, y + rh - 2),
            (x + rw / 2, y + rh - 7),
        ), darker)

        for offset in range(20, rh - 10, 18):
            r(
                x + 5, y + offset,
                rw - 10, 2, ROOF_LINE,
            )

        r(
            x + rw / 2 - 1, y + 4,
            3, rh - 12, METAL,
        )

        r(x + rw - 30, y + 27, 18, 22, SHADOW)
        r(x + rw - 33, y + 23, 16, 21, ROOF_EDGE)
        r(x + rw - 34, y + 21, 18, 5, METAL)

    def draw_containers(self, renderer):
        r = renderer.draw_rect
        q = renderer.draw_quad

        palette = (
            colour("8F5B56"),
            colour("396F70"),
            colour("736746"),
        )

        for index, (x, y, w, h) in enumerate(CONTAINERS):
            tint = palette[index % len(palette)]

            dark = tuple(
                c * 0.6 for c in tint[:3]
            ) + (1.0,)

            r(x + 8, y + 10, w, h, SHADOW)

            q((
                (x, y + h - 14),
                (x + w - 6, y + h - 14),
                (x + w, y + h),
                (x + 6, y + h),
            ), dark)

            q((
                (x + w - 6, y),
                (x + w, y + 14),
                (x + w, y + h),
                (x + w - 6, y + h - 14),
            ), ROOF_EDGE)

            r(x, y, w - 6, h - 14, tint)
            r(x + 3, y + 3, w - 12, 2, METAL)

            for offset in range(12, w - 10, 14):
                r(
                    x + offset, y + 6,
                    2, h - 24, dark,
                )

            r(
                x + w - 29, y + 12,
                16, 10, MARKING,
            )

    def draw_trees(self, renderer):
        r = renderer.draw_rect

        for x, y in TREES:
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
            r(x - 36, y - 20, 72, 40, LAMP_GLOW)
            r(x - 24, y - 32, 48, 64, LAMP_GLOW)
            r(x - 18, y - 18, 36, 36, LAMP_GLOW)

            r(x - 3, y - 2, 14, 14, SHADOW)
            r(x - 6, y - 6, 12, 12, ROOF_EDGE)
            r(x - 4, y - 4, 8, 8, METAL)
            r(x - 3, y - 3, 6, 6, WINDOW_LIGHT)

    def draw(self, renderer):
        self.draw_ground(renderer)
        self.draw_waterfront(renderer)
        self.draw_roads(renderer)

        for index, building in enumerate(self.buildings):
            self.draw_building_shadow(
                renderer, building, index
            )

        for index, building in enumerate(self.buildings):
            self.draw_building(
                renderer, building, index
            )

        self.draw_containers(renderer)
        self.draw_trees(renderer)

        # Depot loading bay.
        r = renderer.draw_rect

        r(120, 206, 200, 4, TEAL)
        r(120, 262, 200, 4, TEAL)
        r(120, 206, 4, 60, TEAL)
        r(316, 206, 4, 60, TEAL)

        for x in range(140, 300, 40):
            r(x, 251, 20, 3, TEAL_DARK)

        # Ground-painted names do not create obstacles.
        lettering(
            renderer,
            "TOWN CENTRE",
            1530, 242,
            TEAL,
        )

        lettering(
            renderer,
            "HARBOUR",
            2480, 470,
            WINDOW_LIGHT,
        )

        lettering(
            renderer,
            "GARDENS",
            1520, 2235,
            WINDOW_LIGHT,
        )

        self.draw_lamps(renderer)