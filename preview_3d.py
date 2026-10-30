import math

import pygame
from OpenGL import GL

from car import Car
from renderer3d import Camera3D, Mesh3D, MeshBuilder
from lighting3d import NightRenderer
from world import (
    BOLLARDS, CONTAINERS, HORIZONTAL_ROADS, LAMPS,
    ROAD_WIDTH, TREES, VERTICAL_ROADS, WATER_X, World, lettering,
)


WIDTH, HEIGHT = 1280, 720
STEP = 1.0 / 120.0

AMBER = (0.96, 0.57, 0.14, 1.0)
TEAL = (0.12, 0.76, 0.70, 1.0)
GLASS = (0.055, 0.13, 0.20, 1.0)
RUBBER = (0.035, 0.045, 0.06, 1.0)
METAL = (0.42, 0.50, 0.58, 1.0)
WARM = (1.0, 0.69, 0.31, 1.0)


def make_lights():
    lights = [
        (
            (float(x), float(y), 86.0),
            (1.0, 0.62, 0.24),
            300.0,
            3.6,
        )
        for x, y in LAMPS
    ]

    # Teal light along the front of the depot.
    lights.extend(
        (
            (x, 202.0, 42.0),
            (0.10, 0.95, 0.78),
            150.0,
            2.8,
        )
        for x in (140.0, 230.0, 320.0)
    )

    return lights


def make_blockers(world):
    blockers = []

    for index, building in enumerate(world.buildings):
        x, y, width, length = building

        _, depth, _ = world.building_style(
            building, index
        )

        blockers.append(
            (x, y, width, length, depth * 2.2 + 4)
        )

    blockers.extend(
        (x, y, width, length, 42.0)
        for x, y, width, length in CONTAINERS
    )

    for x, y in TREES:
        blockers.append(
            (x - 24, y - 24, 48, 48, 3.0)
        )

        blockers.append(
            (x - 3, y - 3, 6, 6, 31.0)
        )

    blockers.extend(
        (x - 2, y - 2, 4, 4, 88.0)
        for x, y in LAMPS
    )

    blockers.extend(
        (x - 6, y - 6, 12, 12, 14.0)
        for x, y in BOLLARDS
    )

    return blockers


class DrivingCamera(Camera3D):
    """Follow the car's heading with temporary Q/E look-around."""

    REAR_ANGLE = 0.0
    LOOK_AHEAD = 80.0

    def __init__(self, width, height, x, y, angle=0.0):
        super().__init__(width, height, x, y)
        self.reset_follow(x, y, angle)

    def reset_follow(self, x, y, angle):
        radians = math.radians(angle)

        self.x = x + math.sin(radians) * self.LOOK_AHEAD
        self.y = y - math.cos(radians) * self.LOOK_AHEAD

        self.yaw = (self.REAR_ANGLE - angle) % 360.0
        self.look_offset = 0.0

    def follow_car(self, x, y, angle, dt, orbit=0):
        if orbit:
            self.look_offset = max(
                -75.0,
                min(75.0, self.look_offset + orbit * 90.0 * dt),
            )
        else:
            self.look_offset *= math.exp(-3.0 * dt)

        target = self.REAR_ANGLE - angle + self.look_offset

        difference = (
            target - self.yaw + 180.0
        ) % 360.0 - 180.0

        weight = 1.0 - math.exp(-4.0 * dt)
        self.yaw = (self.yaw + difference * weight) % 360.0

        radians = math.radians(angle)

        self.follow(
            x + math.sin(radians) * self.LOOK_AHEAD,
            y - math.cos(radians) * self.LOOK_AHEAD,
            dt,
        )


class SignFace:
    def __init__(self, builder, wall_y, top):
        self.builder = builder
        self.wall_y = wall_y
        self.top = top

    def draw_rect(self, x, y, width, height, colour):
        z = self.top - y

        self.builder.quad(
            (
                (x, self.wall_y, z),
                (x, self.wall_y, z - height),
                (x + width, self.wall_y, z - height),
                (x + width, self.wall_y, z),
            ),
            colour,
            0.8,
        )


def make_town(world):
    b = MeshBuilder()

    b.plane(
        -1500, -1500, -1,
        world.width + 3000, world.height + 3000,
        (0.045, 0.08, 0.10, 1.0),
    )

    b.plane(
        0, 0, 0, world.width, world.height,
        (0.10, 0.19, 0.17, 1.0),
    )

    b.plane(
        WATER_X, 0, 0.03,
        world.width - WATER_X, world.height,
        (0.025, 0.12, 0.20, 1.0),
    )

    road = (0.16, 0.20, 0.27, 1.0)
    pavement = (0.32, 0.38, 0.44, 1.0)
    paint = (0.76, 0.79, 0.75, 1.0)

    for x in VERTICAL_ROADS:
        b.plane(
            x, 0, 0.04,
            ROAD_WIDTH, world.height, road,
        )

        start = 0

        for y in (*HORIZONTAL_ROADS, world.height):
            if y > start:
                for edge in (x - 16, x + ROAD_WIDTH):
                    b.box(
                        edge, start, 0,
                        16, y - start, 2.0, pavement,
                    )

            start = y + ROAD_WIDTH

        for y in range(0, world.height, 50):
            if not any(
                h - 35 <= y <= h + ROAD_WIDTH + 35
                for h in HORIZONTAL_ROADS
            ):
                b.plane(
                    x + ROAD_WIDTH / 2 - 2,
                    y, 0.1, 4, 24, paint,
                )

    for y in HORIZONTAL_ROADS:
        b.plane(
            0, y, 0.05,
            WATER_X - 40, ROAD_WIDTH, road,
        )

        start = 0

        for x in (*VERTICAL_ROADS, WATER_X - 40):
            if x > start:
                for edge in (y - 16, y + ROAD_WIDTH):
                    b.box(
                        start, edge, 0,
                        x - start, 16, 2.0, pavement,
                    )

            start = x + ROAD_WIDTH

        for x in range(0, WATER_X - 40, 50):
            if not any(
                v - 35 <= x <= v + ROAD_WIDTH + 35
                for v in VERTICAL_ROADS
            ):
                b.plane(
                    x, y + ROAD_WIDTH / 2 - 2,
                    0.12, 24, 4, paint,
                )

    for x in VERTICAL_ROADS:
        for y in HORIZONTAL_ROADS:
            for offset in range(
                14, ROAD_WIDTH - 12, 24
            ):
                b.plane(
                    x - 30, y + offset,
                    0.15, 20, 12, paint,
                )

                b.plane(
                    x + ROAD_WIDTH + 10, y + offset,
                    0.15, 20, 12, paint,
                )

                b.plane(
                    x + offset, y - 30,
                    0.15, 12, 20, paint,
                )

                b.plane(
                    x + offset, y + ROAD_WIDTH + 10,
                    0.15, 12, 20, paint,
                )

    for index, building in enumerate(world.buildings):
        x, y, width, length = building

        roof, depth, _ = world.building_style(
            building, index
        )

        height = depth * 2.2

        wall = (
            (0.29, 0.40, 0.46, 1.0)
            if x < 2260
            else (0.36, 0.37, 0.44, 1.0)
        )

        b.quad(
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

        b.box(
            x, y, 0,
            width, length, height, wall,
        )

        b.box(
            x - 2, y - 2, height,
            width + 4, length + 4, 4, roof,
        )

        b.box(
            x + 14, y + 14, height + 4,
            28, 24, 10, METAL,
        )

        for wx in range(
            int(x + 18), int(x + width - 18), 38
        ):
            b.box(
                wx, y + length + 0.1,
                height * 0.48,
                18, 0.5, 12, WARM, 0.7,
            )

        for wy in range(
            int(y + 18), int(y + length - 18), 42
        ):
            b.box(
                x + width + 0.1, wy,
                height * 0.48,
                0.5, 18, 12, WARM, 0.7,
            )

        label = (
            "DEPOT"
            if index == 0
            else "CAFE"
            if index % 3 == 0
            else "MARKET"
        )

        if y < 1600 and x < 2260:
            sign_width = len(label) * 12 + 14
            left = x + (width - sign_width) / 2

            b.box(
                left, y + length + 0.7,
                height - 27,
                sign_width, 1, 22,
                (0.025, 0.08, 0.12, 1.0),
            )

            lettering(
                SignFace(
                    b,
                    y + length + 1.8,
                    height - 10,
                ),
                label,
                left + 8,
                0,
                TEAL,
                scale=2,
            )

    for x, y, width, length in CONTAINERS:
        b.box(
            x, y, 0,
            width, length, 42,
            (0.53, 0.37, 0.23, 1.0),
        )

    for x, y in TREES:
        b.box(
            x - 24, y - 24, 0,
            48, 48, 3,
            (0.17, 0.23, 0.22, 1.0),
        )

        b.box(
            x - 3, y - 3, 3,
            6, 6, 28,
            (0.28, 0.19, 0.11, 1.0),
        )

        b.cone(
            x, y, 22, 25, 35,
            (0.15, 0.38, 0.27, 1.0),
        )

        b.cone(
            x, y, 40, 19, 30,
            (0.20, 0.46, 0.32, 1.0),
        )

    for x, y in LAMPS:
        b.box(
            x - 6, y - 6, 0,
            12, 12, 4, METAL,
        )

        b.box(
            x - 1.5, y - 1.5, 4,
            3, 3, 84, METAL,
        )

        b.box(
            x - 3, y - 3, 88,
            6, 6, 3, RUBBER,
        )

        b.box(
            x - 2, y - 2, 84,
            4, 4, 4, WARM, 1.0,
        )

    for x, y in BOLLARDS:
        b.box(
            x - 6, y - 6, 0,
            12, 12, 14, METAL,
        )

    x, y, width, length = 120, 206, 200, 60

    for edge in (y, y + length - 3):
        b.plane(
            x, edge, 0.22,
            width, 3, TEAL, 0.5,
        )

    for edge in (x, x + width - 3):
        b.plane(
            edge, y, 0.22,
            3, length, TEAL, 0.5,
        )

    return b


def make_car(headlights=True):
    b = MeshBuilder()

    b.plane(
        -24, -29, 0.2, 48, 62,
        (0.01, 0.015, 0.025, 0.40),
        1.0,
    )

    for x in (-20, 14):
        for y in (-16, 17):
            b.wheel(x, y, 8, 8, 6, RUBBER)

            hub_x = x - 0.1 if x < 0 else x + 5.8
            b.wheel(hub_x, y, 8, 4, 0.3, METAL)

    b.loft(
        -16, -27, 9, 32, 54, 10,
        1, 1, AMBER,
    )

    b.box(-16, -27, 9, 32, 2, 4, RUBBER)
    b.box(-16, 25, 9, 32, 2, 4, RUBBER)

    b.loft(
        -14, -10, 19, 28, 29, 14,
        3, 6, AMBER,
    )

    b.quad(
        (
            (-12, -9.7, 20), (12, -9.7, 20),
            (10, -5.0, 31), (-10, -5.0, 31),
        ),
        GLASS,
    )

    b.quad(
        (
            (12, 18.7, 20), (-12, 18.7, 20),
            (-10, 14.0, 31), (10, 14.0, 31),
        ),
        GLASS,
    )

    for sign in (-1, 1):
        points = (
            (sign * 13.94, -8, 20),
            (sign * 13.94, 16, 20),
            (sign * 11.58, 11, 31),
            (sign * 11.58, -3, 31),
        )

        b.quad(
            points if sign > 0 else points[::-1],
            GLASS,
        )

        b.box(
            sign * 14 - 1, 7, 20,
            2, 7, 2, METAL,
        )

        b.box(
            sign * 18 - 2, -6, 20,
            4, 5, 3, AMBER,
        )

    b.box(-2, -25, 19.05, 4, 14, 0.3, TEAL)
    b.box(-11, -4, 33, 22, 18, 1.5, RUBBER)

    for x in (-11, 9):
        b.box(x, -4, 34.5, 2, 18, 1.5, METAL)

    b.box(
        -8, -2, 35, 16, 14, 10,
        (0.72, 0.47, 0.25, 1.0),
    )

    b.box(
        -1, -2, 45, 2, 14, 0.3,
        (0.96, 0.82, 0.57, 1.0),
    )

    b.box(-8, 3, 45.1, 16, 3, 0.3, TEAL)

    for x in (-12, 7):
        b.box(
            x, -27.3, 13, 5, 0.6, 3,
            (
                (1.0, 0.91, 0.67, 1.0)
                if headlights
                else (0.15, 0.18, 0.22, 1.0)
            ),
            1.0 if headlights else 0.0,
        )

        b.box(
            x, 26.7, 13, 5, 0.6, 3,
            (0.95, 0.12, 0.07, 1.0),
            0.8,
        )

    return b


def main():
    pygame.display.init()

    renderer = None
    town_mesh = None
    car_mesh = None
    car_unlit_mesh = None

    try:
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_MAJOR_VERSION, 3
        )

        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_MINOR_VERSION, 3
        )

        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK,
            pygame.GL_CONTEXT_PROFILE_CORE,
        )

        pygame.display.gl_set_attribute(
            pygame.GL_DEPTH_SIZE, 24
        )

        pygame.display.gl_set_attribute(
            pygame.GL_MULTISAMPLEBUFFERS, 1
        )

        pygame.display.gl_set_attribute(
            pygame.GL_MULTISAMPLESAMPLES, 4
        )

        try:
            pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.OPENGL | pygame.DOUBLEBUF,
            )

        except pygame.error:
            pygame.display.gl_set_attribute(
                pygame.GL_MULTISAMPLEBUFFERS, 0
            )

            pygame.display.gl_set_attribute(
                pygame.GL_MULTISAMPLESAMPLES, 0
            )

            pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.OPENGL | pygame.DOUBLEBUF,
            )

        GL.glEnable(GL.GL_MULTISAMPLE)

        world = World()
        car = Car(*world.spawn)

        camera = DrivingCamera(
            WIDTH, HEIGHT,
            car.x, car.y, car.angle,
        )

        renderer = NightRenderer(
            WIDTH,
            HEIGHT,
            make_lights(),
            make_blockers(world),
        )

        town_mesh = Mesh3D(make_town(world))
        car_mesh = Mesh3D(make_car())
        car_unlit_mesh = Mesh3D(make_car(False))

        print(
            "3D preview: WASD / arrows drive; Space brakes."
        )

        print(
            "Camera turns automatically. "
            "Q / E look around; release to recenter."
        )

        print(
            "Mouse wheel zooms; L switches headlights; "
            "P pauses; R resets; Escape exits."
        )

        print(
            "This preview tests the graphics and driving. "
            "Run main.py for the campaign."
        )

        clock = pygame.time.Clock()
        accumulator = 0.0
        running = True
        paused = False
        headlights = True

        while running:
            dt = min(
                clock.tick(60) / 1000.0,
                0.1,
            )

            focused = pygame.key.get_focused()

            if not focused:
                paused = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif (
                        focused
                        and event.key == pygame.K_p
                    ):
                        paused = not paused

                    elif (
                        focused
                        and event.key == pygame.K_l
                    ):
                        headlights = not headlights

                    elif (
                        focused
                        and event.key == pygame.K_r
                    ):
                        car.reset()

                        camera.reset_follow(
                            car.x, car.y, car.angle
                        )

                        accumulator = 0.0

                elif (
                    event.type == pygame.MOUSEWHEEL
                    and focused
                ):
                    camera.zoom(event.y)

            if not running:
                break

            orbit = 0

            if focused and not paused:
                keys = pygame.key.get_pressed()

                throttle = int(
                    keys[pygame.K_w]
                    or keys[pygame.K_UP]
                ) - int(
                    keys[pygame.K_s]
                    or keys[pygame.K_DOWN]
                )

                steering = int(
                    keys[pygame.K_d]
                    or keys[pygame.K_RIGHT]
                ) - int(
                    keys[pygame.K_a]
                    or keys[pygame.K_LEFT]
                )

                orbit = (
                    int(keys[pygame.K_e])
                    - int(keys[pygame.K_q])
                )

                accumulator += dt

                while accumulator >= STEP:
                    car.update(
                        STEP,
                        throttle,
                        steering,
                        bool(keys[pygame.K_SPACE]),
                        world.width,
                        world.height,
                        world.obstacles,
                    )

                    accumulator -= STEP

            else:
                accumulator = 0.0
                car.sync_render_state()

            alpha = accumulator / STEP

            x = (
                car.previous_x
                + (car.x - car.previous_x) * alpha
            )

            y = (
                car.previous_y
                + (car.y - car.previous_y) * alpha
            )

            turn = (
                car.angle - car.previous_angle + 180
            ) % 360 - 180

            angle = car.previous_angle + turn * alpha

            if not paused:
                camera.follow_car(
                    x, y, angle, dt, orbit
                )

            renderer.begin(
                camera,
                (x, y, 0.3, angle),
                headlights,
            )

            renderer.draw(town_mesh)

            renderer.draw(
                car_mesh if headlights else car_unlit_mesh,
                x, y, 0.3, angle,
            )

            pygame.display.flip()

            status = (
                "PAUSED - P resumes"
                if paused
                else "DRIVING"
            )

            pygame.display.set_caption(
                f"Midnight Delivery | 3D PREVIEW | {status}"
                f" | {abs(car.speed):.0f} px/s"
                f" | Car {math.ceil(car.condition)}%"
                " | AUTO CAMERA | Q/E look | Wheel zoom"
                f" | Headlights: {'ON' if headlights else 'OFF'} (L)"
                " | P pause | R reset | ESC exit"
            )

    finally:
        for mesh in (
            car_unlit_mesh,
            car_mesh,
            town_mesh,
        ):
            if mesh is not None:
                mesh.close()

        if renderer is not None:
            renderer.close()

        pygame.quit()


if __name__ == "__main__":
    main()