"""Original fictional Eduvos campus and its open forecourt."""

from world import EDUVOS_BUILDING, lettering


BLUE = (0.08, 0.32, 0.72, 1.0)
WHITE = (0.86, 0.91, 0.94, 1.0)
DARK = (0.045, 0.08, 0.13, 1.0)
GLASS = (0.10, 0.30, 0.40, 1.0)
AMBER = (1.0, 0.72, 0.28, 1.0)


class GroundText:
    def __init__(self, builder):
        self.builder = builder

    def draw_rect(self, x, y, width, height, colour):
        self.builder.plane(
            x, y, 0.24,
            width, height,
            colour, 0.15,
        )


def make_campus_ground(builder):
    # Open forecourt.
    builder.plane(
        1490, 2601, 0.08,
        520, 115,
        (0.17, 0.21, 0.26, 1.0),
    )

    # Three ordinary parking bays.
    for x in (1510, 1580, 1650):
        for edge in (x, x + 60):
            builder.plane(
                edge, 2620, 0.16,
                2, 64,
                WHITE,
            )

        builder.plane(
            x, 2620, 0.16,
            62, 2,
            WHITE,
        )

    # Equipment delivery bay.
    for y in (2620, 2682):
        builder.plane(
            1840, y, 0.18,
            120, 2,
            AMBER,
        )

    for x in (1840, 1958):
        builder.plane(
            x, 2620, 0.18,
            2, 64,
            AMBER,
        )

    text = GroundText(builder)

    lettering(
        text,
        "DELIVERY",
        1852, 2646,
        AMBER,
        scale=2,
    )

    lettering(
        text,
        "SOUTHBANK",
        1510, 2894,
        WHITE,
        scale=3,
    )


def make_campus(builder):
    from buildings3d import faces, window

    x, y, width, length = EDUVOS_BUILDING

    # Each exterior section occupies a separate height range.
    # Dark base: 0–7.
    builder.box(
        x, y, 0,
        width, length, 7,
        DARK,
    )

    # White walls: 7–108.
    builder.box(
        x, y, 7,
        width, length, 101,
        WHITE,
    )

    # Blue trim: 108–114.
    builder.box(
        x, y, 108,
        width, length, 6,
        BLUE,
    )

    # Roof: 114–118.
    builder.box(
        x, y, 114,
        width, length, 4,
        DARK,
    )

    sides = faces(
        builder, x, y, width, length
    )

    for side in sides:
        for z in (38, 74):
            for u in range(
                18, int(side.width) - 36, 52
            ):
                entrance = (
                    side in sides[:2]
                    and u < 310
                    and u + 34 > 150
                )

                if entrance:
                    continue

                window(
                    side, u, z,
                    34, 23,
                    lit=True,
                )

    # Taller entrance tower.
    builder.box(
        x + 150, y + 2, 0,
        160, length - 4, 130,
        BLUE,
    )

    front, back = sides[:2]

    for face in (front, back):
        face.rect(
            187, 8,
            86, 68,
            DARK,
            offset=1.0,
        )

        face.rect(
            191, 10,
            78, 62,
            GLASS,
            0.12,
            1.2,
        )

        for u in (191, 229, 267):
            face.rect(
                u, 10,
                2, 62,
                WHITE,
                offset=1.4,
            )

        face.rect(
            191, 42,
            78, 2,
            WHITE,
            offset=1.4,
        )

        face.sign(
            "EDUVOS",
            88,
            WHITE,
            scale=4,
        )

    # Entrance pillars.
    for px in (x + 174, x + 278):
        builder.box(
            px, y + length - 10, 0,
            8, 9, 78,
            WHITE,
        )

    # Entrance canopy.
    builder.box(
        x + 170, y + length - 20, 78,
        120, 20, 5,
        BLUE,
    )

    # Small entrance lamp.
    front.rect(
        225, 77,
        10, 3,
        AMBER,
        1.0,
        1.5,
    )