"""Static low-poly streets, gardens and waterfront scenery."""

import math

from buildings3d import add_buildings, faces
from renderer3d import MeshBuilder
from world import (
    BOLLARDS, CONTAINERS, HORIZONTAL_ROADS, HOUSES,
    LAMPS, ROAD_WIDTH, TREES, VERTICAL_ROADS, WATER_X,
)


TEAL = (0.12, 0.76, 0.70, 1.0)
METAL = (0.42, 0.50, 0.58, 1.0)
DARK = (0.055, 0.09, 0.13, 1.0)
PAINT = (0.76, 0.79, 0.75, 1.0)
WARM = (1.0, 0.69, 0.31, 1.0)


def arrow(builder, x, y, dx, dy):
    """A flat arrow, with a shaft and triangular head."""

    right_x, right_y = -dy, dx

    def point(along, across):
        return (
            x + dx * along + right_x * across,
            y + dy * along + right_y * across,
            0.16,
        )

    builder.quad(
        (
            point(-13, -2),
            point(2, -2),
            point(2, 2),
            point(-13, 2),
        ),
        PAINT,
    )

    builder.triangle(
        point(0, -7),
        point(13, 0),
        point(0, 7),
        PAINT,
    )


def manhole(builder, x, y):
    for segment in range(12):
        a = math.tau * segment / 12
        c = math.tau * (segment + 1) / 12

        builder.triangle(
            (x, y, 0.17),
            (
                x + math.cos(a) * 7,
                y + math.sin(a) * 7,
                0.17,
            ),
            (
                x + math.cos(c) * 7,
                y + math.sin(c) * 7,
                0.17,
            ),
            DARK,
        )

    for offset in (-3, 0, 3):
        builder.plane(
            x - 4, y + offset, 0.19,
            8, 0.6, METAL,
        )


def make_roads(builder, world):
    road = (0.16, 0.20, 0.27, 1.0)
    pavement = (0.32, 0.38, 0.44, 1.0)

    for x in VERTICAL_ROADS:
        builder.plane(
            x, 0, 0.04,
            ROAD_WIDTH, world.height, road,
        )

        start = 0

        for y in (*HORIZONTAL_ROADS, world.height):
            if y > start:
                for edge in (x - 16, x + ROAD_WIDTH):
                    builder.box(
                        edge, start, 0,
                        16, y - start, 2, pavement,
                    )

            start = y + ROAD_WIDTH

        for y in range(0, world.height, 50):
            if not any(
                h - 35 <= y <= h + ROAD_WIDTH + 35
                for h in HORIZONTAL_ROADS
            ):
                builder.plane(
                    x + ROAD_WIDTH / 2 - 2,
                    y, 0.1, 4, 24, PAINT,
                )

    for y in HORIZONTAL_ROADS:
        builder.plane(
            0, y, 0.05,
            WATER_X - 40, ROAD_WIDTH, road,
        )

        start = 0

        for x in (*VERTICAL_ROADS, WATER_X - 40):
            if x > start:
                for edge in (y - 16, y + ROAD_WIDTH):
                    builder.box(
                        start, edge, 0,
                        x - start, 16, 2, pavement,
                    )

            start = x + ROAD_WIDTH

        for x in range(0, WATER_X - 40, 50):
            if not any(
                v - 35 <= x <= v + ROAD_WIDTH + 35
                for v in VERTICAL_ROADS
            ):
                builder.plane(
                    x, y + ROAD_WIDTH / 2 - 2,
                    0.12, 24, 4, PAINT,
                )

    for x in VERTICAL_ROADS:
        for y in HORIZONTAL_ROADS:
            for offset in range(14, ROAD_WIDTH - 12, 24):
                builder.plane(
                    x - 30, y + offset,
                    0.15, 20, 12, PAINT,
                )

                builder.plane(
                    x + ROAD_WIDTH + 10, y + offset,
                    0.15, 20, 12, PAINT,
                )

                builder.plane(
                    x + offset, y - 30,
                    0.15, 12, 20, PAINT,
                )

                builder.plane(
                    x + offset, y + ROAD_WIDTH + 10,
                    0.15, 12, 20, PAINT,
                )

    # Tile joints only appear where a raised pavement exists.
    for x in VERTICAL_ROADS:
        for y in range(16, world.height, 32):
            if not any(
                h <= y <= h + ROAD_WIDTH
                for h in HORIZONTAL_ROADS
            ):
                for edge in (x - 16, x + ROAD_WIDTH):
                    builder.plane(
                        edge, y, 2.03,
                        16, 0.7, DARK,
                    )

    for y in HORIZONTAL_ROADS:
        for x in range(16, WATER_X - 40, 32):
            if not any(
                v <= x <= v + ROAD_WIDTH
                for v in VERTICAL_ROADS
            ):
                for edge in (y - 16, y + ROAD_WIDTH):
                    builder.plane(
                        x, edge, 2.03,
                        0.7, 16, DARK,
                    )

    # South African left-hand lane directions.
    for x in VERTICAL_ROADS:
        for north, south in zip(
            HORIZONTAL_ROADS,
            HORIZONTAL_ROADS[1:],
        ):
            middle = (north + ROAD_WIDTH + south) / 2

            arrow(builder, x + 40, middle, 0, -1)
            arrow(builder, x + 120, middle, 0, 1)
            manhole(builder, x + 24, middle + 64)

    for y in HORIZONTAL_ROADS:
        for west, east in zip(
            VERTICAL_ROADS,
            VERTICAL_ROADS[1:],
        ):
            middle = (west + ROAD_WIDTH + east) / 2

            arrow(builder, middle, y + 40, 1, 0)
            arrow(builder, middle, y + 120, -1, 0)


def make_gardens(builder, world):
    builder.plane(
        0, 1600, 0.01,
        2260, world.height - 1600,
        (0.08, 0.17, 0.14, 1.0),
    )

    builder.plane(
        2260, 0, 0.01,
        WATER_X - 2260, world.height,
        (0.14, 0.16, 0.20, 1.0),
    )

    grass = (0.08, 0.23, 0.17, 1.0)
    path = (0.38, 0.40, 0.33, 1.0)

    builder.plane(
        720, 60, 0.02,
        480, 170, grass,
    )

    builder.plane(
        945, 60, 0.035,
        30, 170, path,
    )

    builder.plane(
        720, 130, 0.035,
        480, 30, path,
    )

    for y in range(70, 230, 20):
        builder.plane(
            945, y, 0.045,
            30, 0.7, DARK,
        )

    for x in range(730, 1200, 24):
        builder.plane(
            x, 130, 0.045,
            0.7, 30, DARK,
        )

    for x, y, width, length in HOUSES:
        builder.plane(
            x - 10, y - 10, 0.02,
            184, 174, grass,
        )

        if y == 1870:
            start = y + length

            end = min(
                h for h in HORIZONTAL_ROADS
                if h >= start
            )

        else:
            start = max(
                h + ROAD_WIDTH
                for h in HORIZONTAL_ROADS
                if h + ROAD_WIDTH <= y
            )

            end = y

        builder.plane(
            x + width / 2 - 8,
            start, 0.035,
            16, end - start, path,
        )


def make_containers(builder):
    colours = (
        (0.55, 0.26, 0.18, 1.0),
        (0.16, 0.40, 0.42, 1.0),
        (0.27, 0.36, 0.48, 1.0),
        (0.60, 0.47, 0.18, 1.0),
    )

    for index, (x, y, width, length) in enumerate(CONTAINERS):
        colour = colours[index % len(colours)]

        rib = tuple(
            value * 0.72
            for value in colour[:3]
        ) + (1.0,)

        builder.box(
            x, y, 0,
            width, length, 42, colour,
        )

        sides = faces(
            builder, x, y, width, length
        )

        for side in sides:
            side.rect(
                0, 2,
                side.width, 2, DARK,
            )

            side.rect(
                0, 38,
                side.width, 2, rib,
            )

            for u in range(8, int(side.width) - 4, 12):
                side.slab(
                    u, 4,
                    1.5, 34,
                    0.7, rib,
                )

        # Double doors and locking bars on the short ends.
        for side in sides[2:]:
            side.rect(
                3, 3,
                side.width - 6, 35,
                colour, offset=1.2,
            )

            side.rect(
                side.width / 2 - 0.6,
                3, 1.2, 35,
                DARK, offset=1.4,
            )

            for u in (
                side.width * 0.25,
                side.width * 0.75,
            ):
                side.slab(
                    u, 6,
                    1.3, 28,
                    0.7, METAL,
                    offset=1.4,
                )

                side.rect(
                    u - 2, 14,
                    5, 2,
                    DARK, offset=2.3,
                )

            for edge in (1, side.width - 4):
                for z in (7, 28):
                    side.slab(
                        edge, z,
                        3, 4,
                        0.7, METAL,
                        offset=1.4,
                    )

        for offset in range(10, int(width) - 4, 14):
            builder.box(
                x + offset, y + 3, 42,
                1.5, length - 6, 0.5,
                rib,
            )


def make_trees(builder):
    for index, (x, y) in enumerate(TREES):
        builder.box(
            x - 24, y - 24, 0,
            48, 48, 3,
            (0.17, 0.23, 0.22, 1.0),
        )

        builder.plane(
            x - 21, y - 21, 3.02,
            42, 42,
            (0.16, 0.12, 0.09, 1.0),
        )

        builder.box(
            x - 3, y - 3, 3,
            6, 6, 28,
            (0.28, 0.19, 0.11, 1.0),
        )

        builder.cone(
            x, y, 22, 25, 35,
            (0.15, 0.38, 0.27, 1.0),
        )

        builder.cone(
            x, y, 40, 19, 30,
            (0.20, 0.46, 0.32, 1.0),
        )

        # Flowers remain inside the existing solid tree beds.
        flower = (
            WARM
            if index % 2
            else (0.73, 0.38, 0.51, 1.0)
        )

        for dx, dy in (
            (-17, -17),
            (17, -17),
            (-17, 17),
            (17, 17),
        ):
            builder.cone(
                x + dx, y + dy,
                3, 4, 5,
                (0.16, 0.33, 0.19, 1.0),
            )

            builder.plane(
                x + dx - 1.5,
                y + dy - 1.5,
                8.1, 3, 3,
                flower, 0.1,
            )


def make_waterfront(builder, world):
    builder.plane(
        WATER_X, 0, 0.03,
        world.width - WATER_X, world.height,
        (0.025, 0.12, 0.20, 1.0),
    )

    builder.plane(
        WATER_X - 40, 0, 0.06,
        40, world.height,
        (0.25, 0.32, 0.37, 1.0),
    )

    builder.box(
        WATER_X - 2, 0, -14,
        6, world.height, 17,
        METAL,
    )

    for y in range(20, world.height, 64):
        builder.plane(
            WATER_X - 39, y, 0.08,
            37, 0.8, DARK,
        )

    # Rails sit beyond the existing impassable water boundary.
    for y in range(0, world.height, 80):
        builder.box(
            WATER_X + 2, y, 3,
            3, 3, 24,
            METAL,
        )

    for z in (14, 25):
        builder.box(
            WATER_X + 2, 0, z,
            3, world.height, 2,
            METAL,
        )

    wave = (0.10, 0.29, 0.37, 1.0)

    for row, y in enumerate(
        range(0, world.height - 40, 72)
    ):
        builder.plane(
            WATER_X + 18 + row % 3 * 8,
            y + 12, 0.10,
            38, 1.5, wave, 0.05,
        )

        builder.plane(
            WATER_X + 90 + row % 2 * 9,
            y + 39, 0.10,
            62, 1.2, wave, 0.05,
        )


def make_lamps(builder):
    for x, y in LAMPS:
        builder.box(
            x - 6, y - 6, 0,
            12, 12, 4, METAL,
        )

        builder.box(
            x - 1.5, y - 1.5, 4,
            3, 3, 84, METAL,
        )

        builder.box(
            x - 3, y - 3, 88,
            6, 6, 3, DARK,
        )

        builder.box(
            x - 2, y - 2, 84,
            4, 4, 4, WARM, 1.0,
        )

    for x, y in BOLLARDS:
        builder.box(
            x - 6, y - 6, 0,
            12, 12, 14, METAL,
        )

        builder.box(
            x - 6.1, y - 6.1, 9,
            12.2, 12.2, 3,
            WARM,
        )


def make_town(world):
    builder = MeshBuilder()

    builder.plane(
        -1500, -1500, -1,
        world.width + 3000,
        world.height + 3000,
        (0.045, 0.08, 0.10, 1.0),
    )

    builder.plane(
        0, 0, 0,
        world.width, world.height,
        (0.10, 0.19, 0.17, 1.0),
    )

    make_gardens(builder, world)
    make_roads(builder, world)
    make_waterfront(builder, world)
    add_buildings(builder, world)
    make_containers(builder)
    make_trees(builder)
    make_lamps(builder)

    # Keep the depot bay aligned with the gameplay coordinates.
    x, y, width, length = 120, 206, 200, 60

    for edge in (y, y + length - 3):
        builder.plane(
            x, edge, 0.22,
            width, 3, TEAL, 0.5,
        )

    for edge in (x, x + width - 3):
        builder.plane(
            edge, y, 0.22,
            3, length, TEAL, 0.5,
        )

    return builder