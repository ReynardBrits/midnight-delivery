import math


class Camera:
    def __init__(
        self, width, height, world_width, world_height
    ):
        self.width = width
        self.height = height
        self.world_width = world_width
        self.world_height = world_height

        self.x = 0.0
        self.y = 0.0

    def follow(self, target_x, target_y):
        max_x = max(
            0.0,
            self.world_width - self.width,
        )

        max_y = max(
            0.0,
            self.world_height - self.height,
        )

        self.x = max(
            0.0,
            min(target_x - self.width / 2, max_x),
        )

        self.y = max(
            0.0,
            min(target_y - self.height / 2, max_y),
        )


class CameraRenderer:
    """Convert world positions into screen positions."""

    def __init__(self, renderer, camera):
        self.renderer = renderer
        self.camera = camera

    def draw_rect(
        self, x, y, width, height, colour, angle=0.0
    ):
        screen_x = x - self.camera.x
        screen_y = y - self.camera.y

        centre_x = screen_x + width / 2
        centre_y = screen_y + height / 2

        radius = math.hypot(width, height) / 2

        if (
            centre_x + radius < 0
            or centre_x - radius > self.camera.width
            or centre_y + radius < 0
            or centre_y - radius > self.camera.height
        ):
            return

        self.renderer.draw_rect(
            screen_x,
            screen_y,
            width,
            height,
            colour,
            angle=angle,
        )

    def draw_quad(self, points, colour):
        screen_points = tuple(
            (
                x - self.camera.x,
                y - self.camera.y,
            )
            for x, y in points
        )

        xs = [point[0] for point in screen_points]
        ys = [point[1] for point in screen_points]

        if (
            max(xs) < 0
            or min(xs) > self.camera.width
            or max(ys) < 0
            or min(ys) > self.camera.height
        ):
            return

        self.renderer.draw_quad(
            screen_points,
            colour,
        )