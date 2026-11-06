"""3D delivery campaign with blackouts and traffic signals."""

from pathlib import Path

import pygame
from OpenGL import GL

from audio import Audio
from blackouts3d import Blackouts, BlackoutRenderer
from car import Car
from controls3d import GameScreens, save_capture
from delivery import Delivery
from effects3d import Effects
from fuel import Fuel
from hud import Hud
from interface3d import DeliveryMarkers, Navigation
from preferences3d import Preferences
from preview_3d import (
    WIDTH, HEIGHT, STEP, DrivingCamera,
    create_window, make_lights, make_blockers,
)
from records import Records
from renderer import Renderer
from renderer3d import Mesh3D
from scenery3d import make_town
from signals3d import (
    TrafficSignals,
    SignalTraffic,
    SignalModels,
    SignalBanner,
)
from vehicles3d import (
    VehicleModels,
    cargo_key,
    interpolated_pose,
)
from visibility3d import CarVisibility
from world import World


def refuel(car, delivery, fuel, audio):
    if delivery.state == "complete":
        return

    if car.disabled or fuel.empty:
        delivery.feedback(
            "Cannot continue. R restarts night."
        )

    elif not delivery.at_depot(car):
        delivery.feedback("Refuel at the depot.")

    elif abs(car.speed) > delivery.STOP_SPEED:
        delivery.feedback(
            "Stop before refuelling."
        )

    else:
        _, cost = fuel.refill_quote()

        if cost == 0:
            delivery.feedback(
                "Tank already full."
            )

        elif delivery.score < cost:
            delivery.feedback(
                f"Need {cost} points for fuel."
            )

        else:
            paid = fuel.refuel(delivery.score)
            delivery.score -= paid

            delivery.feedback(
                f"Fuel {fuel.percentage}%. "
                f"-{paid} pts."
            )

            audio.play_effect("pickup")


def main():
    pygame.display.init()

    resources = []
    preferences = audio = camera = None
    headlights = show_map = True

    try:
        stencil = create_window()
        GL.glEnable(GL.GL_MULTISAMPLE)

        def keep(value):
            resources.append(value)
            return value

        world = World()
        car = Car(*world.spawn)
        delivery = Delivery()
        power = Blackouts()

        signals = TrafficSignals(power)
        world.obstacles += signals.obstacles

        fuel = Fuel()
        traffic = SignalTraffic(signals)
        preferences = Preferences()

        records = Records(
            Path(__file__).resolve().parent
            / "save_data"
            / "records_3d.json"
        )

        camera = DrivingCamera(
            WIDTH,
            HEIGHT,
            car.x,
            car.y,
            car.angle,
        )

        static_blockers = (
            tuple(make_blockers(world))
            + signals.blockers
        )

        scene = keep(
            BlackoutRenderer(
                WIDTH,
                HEIGHT,
                make_lights(),
                static_blockers,
                power,
            )
        )

        town = keep(
            Mesh3D(make_town(world))
        )

        models = keep(VehicleModels())

        signal_models = keep(
            SignalModels(signals)
        )

        effects = keep(
            Effects(car, delivery)
        )

        visibility = keep(
            CarVisibility(stencil)
        )

        markers = keep(DeliveryMarkers())
        overlay = keep(Renderer(WIDTH, HEIGHT))
        hud = keep(Hud(WIDTH, HEIGHT))

        screens = keep(
            GameScreens(WIDTH, HEIGHT)
        )

        banner = keep(
            SignalBanner(
                WIDTH,
                HEIGHT,
                power,
                signals,
            )
        )

        audio = keep(Audio())

        navigation = Navigation(
            WIDTH, HEIGHT
        )

        mode = "title"
        help_open = False
        help_return = "title"
        running = True

        show_map = preferences.show_map
        headlights = preferences.headlights
        camera.span = preferences.zoom

        if preferences.muted:
            audio.toggle_mute()

        accumulator = 0.0
        clock = pygame.time.Clock()

        audio.update(
            car,
            delivery,
            mode,
            focused=False,
        )

        def restart():
            nonlocal mode, accumulator, help_open

            help_open = False

            car.reset()
            delivery.reset()
            power.reset()
            signals.reset()
            fuel.reset()
            traffic.reset()

            effects.reset(car, delivery)
            audio.reset_state()
            records.reset_night()

            camera.reset_follow(
                car.x,
                car.y,
                car.angle,
            )

            hud.last_state = None
            accumulator = 0.0
            mode = "playing"

        def close_help(resume=False):
            nonlocal mode, help_open

            help_open = False

            mode = (
                "playing"
                if resume
                and help_return in ("playing", "paused")
                else help_return
            )

        def settle():
            nonlocal mode

            if mode not in ("playing", "paused"):
                return

            if delivery.state == "complete":
                records.record_completed(
                    delivery.score
                )

                car.speed = 0.0
                mode = "complete"

            elif car.disabled or fuel.empty:
                car.speed = 0.0
                mode = "game_over"

        print(
            "ENTER starts | WASD/arrows drive | Space brake"
        )

        print(
            "E deliver | F repair | G refuel | TAB map"
        )

        print(
            "Z/C look | Wheel zoom | L lights | M mute"
            " | F1 help | F12 screenshot"
            " | P pause | R restart | ESC exit"
        )

        while running:
            dt = min(
                clock.tick(60) / 1000.0,
                0.1,
            )

            focused = pygame.key.get_focused()

            if mode == "playing" and not focused:
                mode = "paused"

            capture_requested = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    key = event.key

                    if key == pygame.K_ESCAPE:
                        if help_open:
                            if focused:
                                close_help()
                        else:
                            running = False

                    elif focused:
                        if key == pygame.K_F12:
                            capture_requested = True

                        elif (
                            key == pygame.K_F1
                            and mode in (
                                "title",
                                "playing",
                                "paused",
                            )
                        ):
                            if help_open:
                                close_help()

                            else:
                                help_return = mode

                                if mode == "playing":
                                    mode = "paused"

                                help_open = True

                        elif key == pygame.K_m:
                            audio.toggle_mute()

                        elif key == pygame.K_l:
                            headlights = not headlights

                        elif help_open:
                            if key in (
                                pygame.K_p,
                                pygame.K_RETURN,
                                pygame.K_KP_ENTER,
                            ):
                                close_help(resume=True)

                        elif key == pygame.K_r:
                            restart()

                        elif key in (
                            pygame.K_RETURN,
                            pygame.K_KP_ENTER,
                        ):
                            if mode == "paused":
                                mode = "playing"

                            elif mode in (
                                "title",
                                "complete",
                                "game_over",
                            ):
                                restart()

                        elif (
                            key == pygame.K_p
                            and mode in (
                                "playing",
                                "paused",
                            )
                        ):
                            mode = (
                                "paused"
                                if mode == "playing"
                                else "playing"
                            )

                        elif mode == "playing":
                            if key == pygame.K_e:
                                power.interact(
                                    delivery, car
                                )

                            elif key == pygame.K_f:
                                delivery.repair(car)

                            elif key == pygame.K_g:
                                refuel(
                                    car,
                                    delivery,
                                    fuel,
                                    audio,
                                )

                            elif key == pygame.K_TAB:
                                show_map = not show_map

                        settle()

                elif (
                    event.type == pygame.MOUSEWHEEL
                    and focused
                ):
                    camera.zoom(event.y)

            if not running:
                break

            traffic.set_shift(
                delivery.shift_number,
                car,
            )

            orbit = 0

            if mode == "playing" and focused:
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
                    int(keys[pygame.K_c])
                    - int(keys[pygame.K_z])
                )

                accumulator += dt

                while (
                    accumulator >= STEP
                    and mode == "playing"
                ):
                    if power.update(STEP):
                        audio.play_effect("warning")

                    signals.update(STEP)
                    traffic.update(STEP, car)

                    car.update(
                        STEP,
                        throttle,
                        steering,
                        bool(keys[pygame.K_SPACE]),
                        world.width,
                        world.height,
                        world.obstacles
                        + traffic.obstacles,
                    )

                    delivery.update(STEP, car)

                    signals.check_player(
                        car,
                        delivery,
                        audio,
                    )

                    was_low = fuel.low

                    fuel.update(
                        STEP,
                        car.speed,
                        car.MAX_SPEED,
                    )

                    if fuel.low and not was_low:
                        delivery.feedback(
                            "Fuel low. G refuels at depot."
                        )

                        audio.play_effect("warning")

                    accumulator -= STEP
                    settle()

            if mode != "playing":
                accumulator = 0.0

                car.sync_render_state()
                traffic.sync_render_state()

            effects.observe(car, delivery)

            if (
                mode in (
                    "playing",
                    "complete",
                    "game_over",
                )
                and focused
            ):
                effects.update(dt)

            audio.update(
                car,
                delivery,
                "paused" if help_open else mode,
                focused,
            )

            alpha = accumulator / STEP

            pose = interpolated_pose(
                car, alpha
            )

            x, y, z, angle = pose

            if mode == "playing":
                camera.follow_car(
                    x,
                    y,
                    angle,
                    dt,
                    orbit,
                )

            traffic_poses = [
                interpolated_pose(vehicle, alpha)
                for vehicle in traffic.active_vehicles
            ]

            scene.blockers = static_blockers + tuple(
                (
                    *vehicle.bounds_at(
                        vehicle_pose[0],
                        vehicle_pose[1],
                        vehicle_pose[3],
                    ),
                    34.0,
                )
                for vehicle, vehicle_pose in zip(
                    traffic.active_vehicles,
                    traffic_poses,
                )
            )

            scene.begin(
                camera,
                pose,
                headlights,
            )

            scene.draw_town(town)
            signal_models.draw(scene)

            GL.glDepthMask(GL.GL_FALSE)

            try:
                markers.draw(scene, delivery)

            finally:
                GL.glDepthMask(GL.GL_TRUE)

            models.draw_traffic(
                scene,
                traffic,
                traffic_poses,
            )

            visibility.draw(
                camera,
                models.silhouettes[
                    cargo_key(delivery)
                ],
                scene.program,
                *pose,
            )

            models.draw_player(
                scene,
                car,
                delivery,
                pose,
                headlights,
            )

            effects.draw(
                scene,
                camera,
                delivery,
            )

            GL.glDisable(GL.GL_DEPTH_TEST)

            if mode == "playing" and not help_open:
                navigation.draw(
                    overlay,
                    world,
                    car,
                    delivery,
                    camera,
                    show_map,
                )

                overlay.flush()

                hud.draw(
                    car,
                    audio,
                    delivery,
                    fuel,
                )

                banner.draw_power(
                    delivery,
                    car,
                    audio,
                    records,
                    fuel,
                    headlights,
                )

            else:
                screens.draw(
                    "help" if help_open else mode,
                    delivery,
                    car,
                    audio,
                    records,
                    fuel,
                )

            if capture_requested:
                save_capture(WIDTH, HEIGHT)

            pygame.display.flip()

            pygame.display.set_caption(
                f"Midnight Delivery 3D | {mode.upper()}"
                " | F1 help | F12 screenshot"
                f" | Traffic {traffic.active_count}"
                " | E interact | Z/C look | L lights"
                " | P pause | R restart"
            )

    finally:
        if (
            preferences is not None
            and audio is not None
            and camera is not None
        ):
            preferences.save(
                audio.muted,
                headlights,
                show_map,
                camera.span,
            )

        for resource in reversed(resources):
            resource.close()

        pygame.quit()


if __name__ == "__main__":
    main()