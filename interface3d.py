"""Delivery paint and navigation for the rotating 3D camera."""

from dataclasses import dataclass
import math

from hud import HUD_HEIGHT
from minimap import Minimap
from renderer3d import Mesh3D, MeshBuilder
from screens import Screens


class GroundPaint:
    def __init__(self):
        self.builder = MeshBuilder()

    def draw_rect(self, x, y, width, height, colour):
        self.builder.plane(
            x, y, 0.30, width, height, colour, 0.8
        )


class DeliveryMarkers:
    def __init__(self):
        self.mesh: Mesh3D | None = None
        self.key = None

    def draw(self, renderer, delivery):
        key = (
            delivery.zone,
            delivery.marker_colour,
            int(delivery.elapsed * 10),
        )

        if key != self.key:
            paint = GroundPaint()
            delivery.draw_marker(paint)
            mesh = Mesh3D(paint.builder)

            if self.mesh is not None:
                self.mesh.close()

            self.mesh = mesh
            self.key = key

        if self.mesh is not None:
            renderer.draw(self.mesh)

    def close(self):
        if self.mesh is not None:
            self.mesh.close()
            self.mesh = None


@dataclass
class MapBounds:
    x: float
    y: float
    width: float
    view_height: float


def screen_point(matrix, x, y, width, height):
    # Match the renderer's reflected game Y coordinate.
    clip_x = matrix[0] * x - matrix[4] * y + matrix[12]
    clip_y = matrix[1] * x - matrix[5] * y + matrix[13]

    return (
        (clip_x + 1) * width / 2,
        (1 - clip_y) * height / 2,
    )


def map_bounds(matrix, width, height):
    # Ground-plane bounds of the area above the dashboard.
    a, b = matrix[0], -matrix[4]
    c, d = matrix[1], -matrix[5]
    determinant = a * d - b * c
    bottom = 1 - 2 * (height - HUD_HEIGHT) / height
    points = []

    for clip_x, clip_y in (
        (-1, 1), (1, 1),
        (1, bottom), (-1, bottom),
    ):
        dx = clip_x - matrix[12]
        dy = clip_y - matrix[13]

        points.append((
            (dx * d - b * dy) / determinant,
            (a * dy - dx * c) / determinant,
        ))

    xs, ys = zip(*points)

    return MapBounds(
        min(xs), min(ys),
        max(xs) - min(xs),
        max(ys) - min(ys),
    )


class Navigation:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.minimap = Minimap(width)

    def draw(
        self, renderer, world, car,
        delivery, camera, show_map,
    ):
        matrix, _ = camera.view_projection()

        if delivery.zone is not None:
            x, y, width, height = delivery.zone

            sx, sy = screen_point(
                matrix,
                x + width / 2,
                y + height / 2,
                self.width,
                self.height,
            )

            view_height = self.height - HUD_HEIGHT
            colour = delivery.marker_colour

            if (
                20 <= sx <= self.width - 20
                and 20 <= sy <= view_height - 20
            ):
                renderer.draw_rect(
                    sx - 5, sy - 5,
                    10, 10, colour, angle=45,
                )

            else:
                cx = self.width / 2
                cy = view_height / 2
                dx, dy = sx - cx, sy - cy

                scale = min(
                    (cx - 36) / abs(dx) if dx else math.inf,
                    (cy - 36) / abs(dy) if dy else math.inf,
                )

                px = cx + dx * scale
                py = cy + dy * scale

                distance = math.hypot(dx, dy)
                ux, uy = dx / distance, dy / distance
                tip = (px + ux * 10, py + uy * 10)

                renderer.draw_rect(
                    px - 15, py - 15,
                    30, 30,
                    (0.035, 0.06, 0.10, 0.95),
                    angle=45,
                )

                for side in (-1, 1):
                    wx = px - ux * 7 - uy * side * 8
                    wy = py - uy * 7 + ux * side * 8

                    length = math.hypot(
                        tip[0] - wx, tip[1] - wy
                    )

                    angle = math.degrees(
                        math.atan2(
                            tip[1] - wy,
                            tip[0] - wx,
                        )
                    )

                    renderer.draw_rect(
                        (wx + tip[0]) / 2 - length / 2,
                        (wy + tip[1]) / 2 - 2,
                        length, 4, colour,
                        angle=angle,
                    )

        if show_map:
            bounds = map_bounds(
                matrix, self.width, self.height
            )

            left = max(0.0, bounds.x)
            top = max(0.0, bounds.y)

            right = min(
                world.width,
                bounds.x + bounds.width,
            )

            bottom = min(
                world.height,
                bounds.y + bounds.view_height,
            )

            clipped = MapBounds(
                left, top,
                max(0.0, right - left),
                max(0.0, bottom - top),
            )

            self.minimap.draw(
                renderer, world, car, delivery, clipped
            )


class Screens3D(Screens):
    def compose(
        self, mode, delivery,
        car, audio, records, fuel,
    ):
        super().compose(
            mode, delivery, car, audio, records, fuel
        )

        if mode == "title":
            self.text(
                "3D CAMERA: Z / C LOOK    WHEEL ZOOM    L HEADLIGHTS",
                (84, 295),
                "small",
                (156, 176, 194),
            )