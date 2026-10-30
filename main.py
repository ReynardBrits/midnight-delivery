import pygame

from OpenGL import GL

from audio import Audio
from camera import Camera, CameraRenderer
from car import Car
from delivery import Delivery
from hud import Hud, HUD_HEIGHT
from renderer import Renderer
from screens import Screens
from traffic import Traffic
from world import World, BACKGROUND


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TARGET_FPS = 60

PHYSICS_STEP = 1.0 / 120.0
MAX_UPDATES = 12


def main():
    pygame.display.init()

    renderer = None
    hud = None
    screens = None
    audio = None

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

        hud = Hud(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )

        screens = Screens(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )

        audio = Audio()

        world = World()
        car = Car(*world.spawn)
        delivery = Delivery()
        traffic = Traffic()

        camera = Camera(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            world.width,
            world.height,
            bottom_margin=HUD_HEIGHT,
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
            "Enter: start/resume/replay | P: pause"
            " | Space: strong brake | E: interact"
            " | F: depot repair | M: mute"
            " | R: restart night | Escape: exit"
        )

        clock = pygame.time.Clock()
        accumulator = 0.0
        caption_timer = 0.0
        running = True
        mode = "title"

        def restart_night():
            car.reset()
            delivery.reset()
            traffic.reset()
            audio.reset_state()

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

                    elif event.key == pygame.K_m:
                        audio.toggle_mute()

                    elif event.key == pygame.K_e:
                        if (
                            mode == "playing"
                            and pygame.key.get_focused()
                        ):
                            delivery.interact(car)

                    elif event.key == pygame.K_f:
                        if (
                            mode == "playing"
                            and pygame.key.get_focused()
                        ):
                            delivery.repair(car)

                    elif event.key == pygame.K_r:
                        restart_night()
                        accumulator = 0.0
                        mode = "playing"

                    elif event.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER,
                    ):
                        if pygame.key.get_focused():
                            if mode == "paused":
                                mode = "playing"

                            elif mode in (
                                "title",
                                "complete",
                                "game_over",
                            ):
                                restart_night()
                                accumulator = 0.0
                                mode = "playing"

                    elif event.key == pygame.K_p:
                        if pygame.key.get_focused():
                            if mode == "playing":
                                mode = "paused"

                            elif mode == "paused":
                                mode = "playing"

            if not running:
                break

            focused = pygame.key.get_focused()

            if mode in ("playing", "paused"):
                if delivery.state == "complete":
                    mode = "complete"

                elif car.disabled:
                    mode = "game_over"

                elif mode == "playing" and not focused:
                    mode = "paused"

            traffic.set_shift(delivery.shift_number)

            if mode == "playing" and focused:
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
                    traffic.update(PHYSICS_STEP, car)

                    car.update(
                        PHYSICS_STEP,
                        throttle,
                        steering,
                        braking,
                        world.width,
                        world.height,
                        world.obstacles + traffic.obstacles,
                    )

                    delivery.update(
                        PHYSICS_STEP,
                        car,
                    )

                    accumulator -= PHYSICS_STEP
                    updates += 1

                    if car.disabled:
                        mode = "game_over"
                        break

                if accumulator >= PHYSICS_STEP:
                    accumulator %= PHYSICS_STEP

            if mode != "playing":
                accumulator = 0.0
                car.sync_render_state()
                traffic.sync_render_state()

            audio.update(
                car,
                delivery,
                mode,
                focused,
            )

            alpha = max(
                0.0,
                min(accumulator / PHYSICS_STEP, 1.0),
            )

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
            delivery.draw_marker(world_renderer)
            traffic.draw(world_renderer, alpha)

            car.draw(world_renderer, alpha)

            if mode == "playing":
                delivery.draw_guidance(
                    renderer,
                    camera,
                    HUD_HEIGHT,
                )

                # Draw the shape batch before the textured HUD.
                renderer.flush()
                hud.draw(car, audio, delivery)

            else:
                renderer.flush()

                screens.draw(
                    mode,
                    delivery,
                    car,
                    audio,
                )

            renderer.end_frame()
            pygame.display.flip()

            caption_timer += frame_time

            if caption_timer >= 0.2:
                if mode == "playing":
                    caption = (
                        "Midnight Delivery"
                        f" | Speed: {abs(car.speed):.0f} px/s"
                        f" | Sound: {audio.status} (M)"
                        f" | Traffic: {traffic.active_count}"
                        " | F: depot repair"
                        " | P: pause | R: restart night | Escape: exit"
                    )

                else:
                    label = (
                        mode.replace("_", " ").title()
                    )

                    caption = (
                        f"Midnight Delivery | {label}"
                        " | Enter: continue | Escape: exit"
                    )

                pygame.display.set_caption(caption)
                caption_timer = 0.0

    finally:
        if screens is not None:
            screens.close()

        if hud is not None:
            hud.close()

        if audio is not None:
            audio.close()

        if renderer is not None:
            renderer.close()

        pygame.quit()


if __name__ == "__main__":
    main()