import pygame

from OpenGL import GL

from renderer import Renderer


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TARGET_FPS = 60

BACKGROUND = (0.071, 0.106, 0.200, 1.0)
ROAD = (0.180, 0.220, 0.290, 1.0)
PAVEMENT = (0.300, 0.350, 0.420, 1.0)
ROAD_MARKING = (0.760, 0.780, 0.750, 1.0)

BUILDING = (0.160, 0.220, 0.330, 1.0)
ROOF_EDGE = (0.230, 0.310, 0.430, 1.0)
SHADOW = (0.035, 0.055, 0.100, 1.0)
WINDOW_LIGHT = (1.000, 0.710, 0.280, 1.0)

TEAL = (0.227, 0.839, 0.784, 1.0)
CAR_BODY = (1.000, 0.710, 0.280, 1.0)
CAR_GLASS = (0.090, 0.160, 0.240, 1.0)
TYRE = (0.025, 0.035, 0.050, 1.0)
HEADLIGHT = (1.000, 0.960, 0.760, 1.0)
TAILLIGHT = (0.940, 0.260, 0.260, 1.0)


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


def draw_car(renderer, x, y):
    # x and y represent the centre of the car.
    renderer.draw_rect(
        x - 20, y - 21, 6, 13, TYRE
    )
    renderer.draw_rect(
        x + 14, y - 21, 6, 13, TYRE
    )
    renderer.draw_rect(
        x - 20, y + 10, 6, 13, TYRE
    )
    renderer.draw_rect(
        x + 14, y + 10, 6, 13, TYRE
    )

    renderer.draw_rect(
        x - 16, y - 28, 32, 56, CAR_BODY
    )

    renderer.draw_rect(
        x - 12, y - 15, 24, 13, CAR_GLASS
    )
    renderer.draw_rect(
        x - 11, y + 12, 22, 8, CAR_GLASS
    )

    renderer.draw_rect(
        x - 13, y - 28, 7, 4, HEADLIGHT
    )
    renderer.draw_rect(
        x + 6, y - 28, 7, 4, HEADLIGHT
    )

    renderer.draw_rect(
        x - 13, y + 24, 7, 4, TAILLIGHT
    )
    renderer.draw_rect(
        x + 6, y + 24, 7, 4, TAILLIGHT
    )


def draw_scene(renderer):
    # Pavements beneath the roads.
    renderer.draw_rect(
        488, 0, 184, WINDOW_HEIGHT, PAVEMENT
    )
    renderer.draw_rect(
        0, 268, WINDOW_WIDTH, 184, PAVEMENT
    )

    # A vertical road and a horizontal road.
    renderer.draw_rect(
        500, 0, 160, WINDOW_HEIGHT, ROAD
    )
    renderer.draw_rect(
        0, 280, WINDOW_WIDTH, 160, ROAD
    )

    # Leave the intersection free of centre markings.
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

    # Buildings around the intersection.
    draw_building(renderer, 70, 55, 290, 140)
    draw_building(renderer, 730, 60, 200, 145)
    draw_building(renderer, 990, 60, 210, 145)
    draw_building(renderer, 70, 510, 175, 140)
    draw_building(renderer, 300, 510, 130, 140)
    draw_building(renderer, 740, 510, 430, 140)

    # Teal outline for the depot's loading bay.
    renderer.draw_rect(150, 208, 130, 4, TEAL)
    renderer.draw_rect(150, 254, 130, 4, TEAL)
    renderer.draw_rect(150, 208, 4, 50, TEAL)
    renderer.draw_rect(276, 208, 4, 50, TEAL)

    # Player car in the left lane, facing upwards.
    draw_car(renderer, 540, 560)


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

        version = GL.glGetString(GL.GL_VERSION)
        if version is None:
            raise RuntimeError(
                "Could not read the OpenGL version."
            )

        print("OpenGL version:", version.decode())
        print("Press Escape or close the window to exit.")

        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            if not running:
                break

            renderer.begin_frame(BACKGROUND)
            draw_scene(renderer)
            renderer.end_frame()

            pygame.display.flip()
            clock.tick(TARGET_FPS)

    finally:
        if renderer is not None:
            renderer.close()

        pygame.quit()


if __name__ == "__main__":
    main()