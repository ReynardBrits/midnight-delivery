import pygame

from OpenGL import GL

from camera import Camera, CameraRenderer
from car import Car
from renderer import Renderer
from world import World, BACKGROUND


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TARGET_FPS = 60

PHYSICS_STEP = 1.0 / 120.0
MAX_UPDATES = 12


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

        world = World()
        car = Car(*world.spawn)

        camera = Camera(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            world.width,
            world.height,
        )

        world_renderer = CameraRenderer(
            renderer,
            camera,
        )

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
                        world.width,
                        world.height,
                        world.obstacles,
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

            # Use the same interpolated position for
            # the camera and the displayed car.
            target_x = (
                car.previous_x
                + (car.x - car.previous_x) * alpha
            )

            target_y = (
                car.previous_y
                + (car.y - car.previous_y) * alpha
            )

            camera.follow(target_x, target_y)

            renderer.begin_frame(BACKGROUND)
            world.draw(world_renderer)
            car.draw(world_renderer, alpha)
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