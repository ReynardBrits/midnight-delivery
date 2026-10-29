import pygame

from OpenGL import GL

from car import Car
from renderer import Renderer


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TARGET_FPS = 60

PHYSICS_STEP = 1.0 / 120.0
MAX_UPDATES = 12

BACKGROUND = (0.071, 0.106, 0.200, 1.0)
ROAD = (0.180, 0.220, 0.290, 1.0)
PAVEMENT = (0.300, 0.350, 0.420, 1.0)
ROAD_MARKING = (0.760, 0.780, 0.750, 1.0)

BUILDING = (0.160, 0.220, 0.330, 1.0)
ROOF_EDGE = (0.230, 0.310, 0.430, 1.0)
SHADOW = (0.035, 0.055, 0.100, 1.0)
WINDOW_LIGHT = (1.000, 0.710, 0.280, 1.0)

TEAL = (0.227, 0.839, 0.784, 1.0)

# Each building is: x, y, width, height.
# Drawing and collision checks use the same dimensions.
BUILDINGS = (
    (70, 55, 290, 140),
    (730, 60, 200, 145),
    (990, 60, 210, 145),
    (70, 510, 175, 140),
    (300, 510, 130, 140),
    (740, 510, 430, 140),
)


def draw_building(renderer, x, y, width, height):
    renderer.draw_rect(
        x + 8, y + 8, width, height, SHADOW
    )

    renderer.draw_rect(
        x, y, width, height, BUILDING
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


def draw_scene(renderer):
    # Pavements and roads.
    renderer.draw_rect(
        488, 0, 184, WINDOW_HEIGHT, PAVEMENT
    )

    renderer.draw_rect(
        0, 268, WINDOW_WIDTH, 184, PAVEMENT
    )

    renderer.draw_rect(
        500, 0, 160, WINDOW_HEIGHT, ROAD
    )

    renderer.draw_rect(
        0, 280, WINDOW_WIDTH, 160, ROAD
    )

    # Road markings.
    for y in range(0, WINDOW_HEIGHT, 50):
        if y + 26 <= 280 or y >= 440:
            renderer.draw_rect(
                578, y, 4, 26, ROAD_MARKING
            )

    for x in range(0, WINDOW_WIDTH, 50):
        if x + 26 <= 500 or x >= 660:
            renderer.draw_rect(
                x, 358, 26, 4, ROAD_MARKING
            )

    # Buildings.
    for building in BUILDINGS:
        draw_building(renderer, *building)

    # Depot loading bay.
    renderer.draw_rect(150, 208, 130, 4, TEAL)
    renderer.draw_rect(150, 254, 130, 4, TEAL)
    renderer.draw_rect(150, 208, 4, 50, TEAL)
    renderer.draw_rect(276, 208, 4, 50, TEAL)


def main():
    pygame.display.init()
    renderer = None

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

        pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.OPENGL | pygame.DOUBLEBUF,
        )

        pygame.display.set_caption("Midnight Delivery")

        renderer = Renderer(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )

        car = Car(540, 560)

        version = GL.glGetString(GL.GL_VERSION)

        if version is None:
            raise RuntimeError(
                "Could not read the OpenGL version."
            )

        print("OpenGL version:", version.decode())
        print("W / Up: accelerate")
        print("S / Down: brake, then reverse")
        print("A / D or Left / Right: steer")
        print(
            "Space: strong brake | R: reset | Escape: exit"
        )

        clock = pygame.time.Clock()
        accumulator = 0.0
        caption_timer = 0.0
        running = True

        while running:
            frame_time = min(
                clock.tick(TARGET_FPS) / 1000.0,
                0.1,
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_r:
                        car.reset()
                        accumulator = 0.0

            if not running:
                break

            if pygame.key.get_focused():
                keys = pygame.key.get_pressed()

                forward = (
                    keys[pygame.K_w]
                    or keys[pygame.K_UP]
                )

                backward = (
                    keys[pygame.K_s]
                    or keys[pygame.K_DOWN]
                )

                left = (
                    keys[pygame.K_a]
                    or keys[pygame.K_LEFT]
                )

                right = (
                    keys[pygame.K_d]
                    or keys[pygame.K_RIGHT]
                )

                throttle = int(forward) - int(backward)
                steering = int(right) - int(left)
                braking = bool(keys[pygame.K_SPACE])

                accumulator += frame_time
                updates = 0

                while (
                    accumulator >= PHYSICS_STEP
                    and updates < MAX_UPDATES
                ):
                    car.update(
                        PHYSICS_STEP,
                        throttle,
                        steering,
                        braking,
                        WINDOW_WIDTH,
                        WINDOW_HEIGHT,
                        BUILDINGS,
                    )

                    accumulator -= PHYSICS_STEP
                    updates += 1

                if accumulator >= PHYSICS_STEP:
                    accumulator %= PHYSICS_STEP

            else:
                # Freeze movement while another window
                # has keyboard focus.
                accumulator = 0.0
                car.sync_render_state()

            alpha = max(
                0.0,
                min(accumulator / PHYSICS_STEP, 1.0),
            )

            renderer.begin_frame(BACKGROUND)
            draw_scene(renderer)
            car.draw(renderer, alpha)
            renderer.end_frame()

            pygame.display.flip()

            caption_timer += frame_time

            if caption_timer >= 0.2:
                pygame.display.set_caption(
                    "Midnight Delivery"
                    f" | Speed: {abs(car.speed):.0f} px/s"
                    " | R: reset | Escape: exit"
                )

                caption_timer = 0.0

    finally:
        if renderer is not None:
            renderer.close()

        pygame.quit()


if __name__ == "__main__":
    main()