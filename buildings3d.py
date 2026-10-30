"""Original low-poly buildings, assembled once into the town's static mesh."""

from world import lettering


DARK = (0.055, 0.09, 0.13, 1.0)
FRAME = (0.54, 0.59, 0.58, 1.0)
GLASS = (0.10, 0.26, 0.31, 1.0)
WARM = (1.0, 0.69, 0.35, 1.0)
CREAM = (0.86, 0.81, 0.65, 1.0)
TEAL = (0.12, 0.76, 0.70, 1.0)


class Facade:
    """Place details in local coordinates on any of a building's four walls."""

    def __init__(self, builder, origin, along, width):
        self.builder = builder
        self.x, self.y = origin
        self.ux, self.uy = along
        self.nx, self.ny = -self.uy, self.ux
        self.width = width

    def point(self, u, z, offset=0.25):
        return (
            self.x + self.ux * u + self.nx * offset,
            self.y + self.uy * u + self.ny * offset,
            z,
        )

    def rect(self, u, z, width, height, colour, emission=0.0, offset=0.25):
        self.builder.quad(
            (
                self.point(u, z, offset),
                self.point(u, z + height, offset),
                self.point(u + width, z + height, offset),
                self.point(u + width, z, offset),
            ),
            colour,
            emission,
        )

    def slab(self, u, z, width, height, depth, colour, offset=0.3):
        a = self.point(u, z, offset)
        c = self.point(u + width, z, offset + depth)

        self.builder.box(
            min(a[0], c[0]), min(a[1], c[1]), z,
            abs(c[0] - a[0]), abs(c[1] - a[1]), height, colour,
        )

    def draw_rect(self, x, y, width, height, colour):
        # Adapter for the project's original 5-by-7 pixel lettering.
        self.rect(x, -y - height, width, height, colour, 0.85, 1.1)

    def sign(self, label, z, colour=TEAL, scale=2):
        width = (len(label) * 6 - 1) * scale + 12
        left = (self.width - width) / 2
        height = 7 * scale + 8

        self.rect(left, z, width, height, DARK, offset=0.6)
        self.rect(left, z, width, 1.5, colour, 0.7, 0.8)

        lettering(
            self,
            label,
            left + 6,
            -(z + height - 4),
            colour,
            scale,
        )


def faces(builder, x, y, width, length):
    return (
        Facade(builder, (x, y + length), (1, 0), width),  # South
        Facade(builder, (x + width, y), (-1, 0), width),  # North
        Facade(builder, (x + width, y + length), (0, -1), length),
        Facade(builder, (x, y), (0, 1), length),
    )


def window(face, u, z, width=22, height=18, lit=True):
    face.slab(
        u - 1, z - 1,
        width + 2, height + 2,
        0.4, FRAME,
    )

    face.rect(
        u + 1, z + 1,
        width - 2, height - 2,
        WARM if lit else GLASS,
        0.45 if lit else 0.05,
        0.85,
    )

    face.rect(
        u + width / 2 - 0.6,
        z, 1.2, height,
        DARK, offset=1.0,
    )

    face.rect(
        u, z + height * 0.6,
        width, 1.0,
        DARK, offset=1.0,
    )

    face.slab(
        u - 2, z - 2,
        width + 4, 2,
        2, FRAME,
    )


def door(face, u, z=2, width=22, height=35, colour=TEAL):
    face.slab(
        u - 2, z,
        width + 4, height + 2,
        0.6, DARK,
    )

    face.rect(
        u, z,
        width, height,
        colour, offset=1.0,
    )

    face.rect(
        u + 3, z + height * 0.4,
        width - 6, height * 0.49,
        GLASS, 0.08, 1.15,
    )

    face.rect(
        u + width - 5, z + height * 0.4,
        2, 4,
        CREAM, offset=1.3,
    )


def awning(face, u, width, z, colour, depth=13):
    stripes = max(4, int(width / 12))
    stripe_width = width / stripes

    for stripe in range(stripes):
        left = u + stripe * stripe_width
        tint = colour if stripe % 2 == 0 else CREAM

        face.builder.quad(
            (
                face.point(left, z, 0.8),
                face.point(left + stripe_width, z, 0.8),
                face.point(left + stripe_width, z - 4, depth),
                face.point(left, z - 4, depth),
            ),
            tint,
        )

        face.rect(
            left, z - 7,
            stripe_width, 3,
            tint, offset=depth,
        )


def flat_roof(builder, x, y, width, length, height):
    roof = height - 5

    builder.box(
        x - 2, y - 2, roof,
        width + 4, length + 4, 2,
        DARK,
    )

    for edge in (x - 2, x + width):
        builder.box(
            edge, y - 2, roof + 2,
            2, length + 4, 7,
            FRAME,
        )

    for edge in (y - 2, y + length):
        builder.box(
            x, edge, roof + 2,
            width, 2, 7,
            FRAME,
        )

    builder.box(
        x + 14, y + 14, roof + 2,
        28, 24, 7,
        FRAME,
    )

    for line in range(4):
        builder.plane(
            x + 17, y + 17 + line * 5,
            height + 4.1,
            22, 1.2,
            DARK,
        )


def pitched_roof(builder, x, y, width, length, eave, ridge, colour):
    left, right = x - 3, x + width + 3
    north, south = y - 3, y + length + 3
    middle = x + width / 2

    for a, c in ((left, middle), (middle, right)):
        za = eave if a == left else ridge
        zc = eave if c == right else ridge

        builder.quad(
            (
                (a, north, za),
                (c, north, zc),
                (c, south, zc),
                (a, south, za),
            ),
            colour,
        )

        for seam_y in range(int(north) + 12, int(south), 16):
            builder.quad(
                (
                    (a, seam_y, za + 0.15),
                    (c, seam_y, zc + 0.15),
                    (c, seam_y + 0.7, zc + 0.15),
                    (a, seam_y + 0.7, za + 0.15),
                ),
                DARK,
            )

    # Gables close the roof, so there are no hollow triangular ends.
    gable = (0.37, 0.44, 0.46, 1.0)

    builder.triangle(
        (left, south, eave),
        (middle, south, ridge),
        (right, south, eave),
        gable,
    )

    builder.triangle(
        (right, north, eave),
        (middle, north, ridge),
        (left, north, eave),
        gable,
    )


def roller_door(face, u, width, height=36):
    face.slab(
        u - 2, 2,
        width + 4, height + 4,
        0.7, DARK,
    )

    face.rect(
        u, 3,
        width, height,
        (0.36, 0.46, 0.49, 1.0),
        offset=1.1,
    )

    for z in range(7, int(height) + 2, 5):
        face.rect(
            u, z,
            width, 0.8,
            DARK, offset=1.25,
        )

    for edge in (u - 5, u + width + 3):
        for z in range(3, int(height), 6):
            face.rect(
                edge, z,
                2, 3,
                WARM, offset=1.25,
            )


def depot(builder, sides, x, y, width, length, height):
    wall_height = height - 5

    builder.box(
        x, y, 0,
        width, length, wall_height,
        (0.22, 0.39, 0.42, 1.0),
    )

    flat_roof(builder, x, y, width, length, height)

    front = sides[0]

    for u in (16, 112):
        roller_door(front, u, 80)

        front.rect(
            u + 7, 25,
            66, 6,
            GLASS, 0.08, 1.4,
        )

    door(front, width - 42, height=35)

    front.rect(
        0, 46,
        width, 3,
        TEAL, 0.65, 0.6,
    )

    front.sign("MIDNIGHT DEPOT", 52)
    sides[1].sign("MIDNIGHT", 52)

    for side in sides[1:]:
        for u in range(14, int(side.width) - 28, 42):
            window(side, u, 18, 26, 22)

    builder.plane(
        x + 5, y + length + 1, 0.08,
        width - 10, 6,
        DARK,
    )


def shop(builder, sides, x, y, width, length, height, index):
    accents = (
        TEAL,
        (0.90, 0.42, 0.22, 1.0),
        (0.48, 0.55, 0.79, 1.0),
    )

    walls = (
        (0.43, 0.55, 0.56, 1.0),
        (0.57, 0.46, 0.39, 1.0),
        (0.43, 0.46, 0.57, 1.0),
    )

    accent = accents[index % 3]
    wall_height = height - 5

    builder.box(
        x, y, 0,
        width, length, wall_height,
        walls[index % 3],
    )

    flat_roof(builder, x, y, width, length, height)

    label = ("CAFE", "MARKET", "ARCADE", "BAKERY")[index % 4]

    for side in sides:
        side.rect(0, 0, side.width, 7, DARK)
        side.rect(0, 48, side.width, 3, FRAME)

        for u in range(16, int(side.width) - 24, 38):
            window(
                side, u, wall_height - 24,
                20, 14,
                (index + u) % 3 != 0,
            )

    for front in sides[:2]:
        centre = (width - 22) / 2
        display_width = centre - 16

        window(front, 9, 10, display_width, 30)
        window(front, centre + 29, 10, display_width, 30)

        door(
            front, centre,
            height=37,
            colour=accent,
        )

        awning(
            front, 6,
            width - 12,
            50, accent,
        )

        front.sign(label, 54, accent)

    for side in sides[2:]:
        for u in range(14, int(side.width) - 24, 40):
            window(
                side, u, 15,
                24, 22,
                (index + u) % 3 != 0,
            )


def house(builder, sides, x, y, width, length, height, index):
    walls = (
        (0.63, 0.57, 0.43, 1.0),
        (0.39, 0.54, 0.45, 1.0),
        (0.40, 0.51, 0.60, 1.0),
    )

    roofs = (
        (0.50, 0.25, 0.19, 1.0),
        (0.19, 0.36, 0.43, 1.0),
        (0.29, 0.32, 0.38, 1.0),
    )

    eave = height - 22

    builder.box(
        x, y, 0,
        width, length, eave,
        walls[index % 3],
    )

    pitched_roof(
        builder,
        x, y, width, length,
        eave, height + 4,
        roofs[index % 3],
    )

    builder.box(
        x + width * 0.72,
        y + length * 0.65,
        height - 10,
        10, 12, 14,
        (0.44, 0.31, 0.27, 1.0),
    )

    for side in sides:
        side.rect(0, 0, side.width, 5, DARK)
        side.rect(0, eave - 3, side.width, 3, CREAM)

    front_index = 0 if y == 1870 else 1

    for side_index, side in enumerate(sides):
        for u in (14, side.width - 38):
            window(
                side, u, 12,
                22, 15,
                (index + side_index) % 3 != 0,
            )

    front = sides[front_index]
    centre = (width - 20) / 2

    door(
        front, centre,
        width=20,
        height=26,
        colour=(0.28, 0.38, 0.40, 1.0),
    )

    front.slab(
        centre - 5, 30,
        30, 2,
        8, CREAM,
    )

    for side in sides[:2]:
        side.rect(
            width / 2 - 6, eave + 7,
            12, 10,
            DARK, offset=3.2,
        )

        side.rect(
            width / 2 - 4, eave + 9,
            8, 6,
            WARM, 0.4, 3.3,
        )


def warehouse(builder, sides, x, y, width, length, height, index):
    wall_height = height - 10

    wall = (
        (0.30, 0.41, 0.44, 1.0),
        (0.39, 0.37, 0.46, 1.0),
    )[index % 2]

    builder.box(
        x, y, 0,
        width, length, wall_height,
        wall,
    )

    pitched_roof(
        builder,
        x, y, width, length,
        wall_height, height + 4,
        (0.29, 0.36, 0.41, 1.0),
    )

    for side in sides:
        side.rect(0, 0, side.width, 6, DARK)

        for u in range(6, int(side.width), 18):
            side.rect(
                u, 6,
                1.5, wall_height - 6,
                FRAME,
            )

    for front in sides[:2]:
        count = max(1, int(width / 100))
        spacing = width / count

        for bay in range(count):
            door_width = min(64, spacing - 20)

            roller_door(
                front,
                bay * spacing + (spacing - door_width) / 2,
                door_width,
                36,
            )

        front.slab(
            6, 43,
            width - 12, 2,
            9, DARK,
        )

        front.sign(
            "DOCKS" if index % 2 else "CARGO",
            wall_height - 14,
            WARM,
            scale=1,
        )

    for side in sides[2:]:
        for u in range(14, int(side.width) - 24, 36):
            window(
                side, u, wall_height - 18,
                22, 9,
            )


def add_buildings(builder, world):
    """All decorative structures use the existing collision footprints."""

    for index, building in enumerate(world.buildings):
        x, y, width, length = building

        _, depth, _ = world.building_style(
            building, index
        )

        height = depth * 2.2

        builder.quad(
            (
                (x, y, 0.18),
                (x + width, y, 0.18),
                (
                    x + width + height * 0.5,
                    y + length + height * 0.4,
                    0.18,
                ),
                (
                    x + height * 0.5,
                    y + length + height * 0.4,
                    0.18,
                ),
            ),
            (0.015, 0.025, 0.045, 0.30),
            1.0,
        )

        sides = faces(
            builder, x, y, width, length
        )

        arguments = (
            builder, sides,
            x, y, width, length,
            height,
        )

        if index == 0:
            depot(*arguments)

        elif x >= 2260:
            warehouse(*arguments, index)

        elif y >= 1600:
            house(*arguments, index)

        else:
            shop(*arguments, index)