"""Scheduled district power cuts, delivery bonuses and a status panel."""

import math

import pygame
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from lighting3d import NightRenderer, NIGHT_SHADER
from renderer3d import VERTEX_SHADER
from screens import Screens
from world import EDUVOS_BUILDING, WATER_X, WORLD_HEIGHT


class Blackouts:
    CLEAR_SECONDS = 25.0
    WARNING_SECONDS = 8.0
    DARK_SECONDS = 35.0

    DISTRICTS = (
        ("CENTRE", (0, 0, 2260, 1600)),
        ("HARBOUR", (2260, 0, WATER_X, WORLD_HEIGHT)),
        ("GARDENS", (0, 1600, 2260, 2440)),
        ("SOUTHBANK", (0, 2440, 2260, WORLD_HEIGHT)),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.elapsed = 0.0
        self.bonus_total = 0

    @property
    def period(self):
        return self.CLEAR_SECONDS + self.DARK_SECONDS

    @property
    def cycle(self):
        return int((self.elapsed + 1e-8) // self.period)

    @property
    def phase(self):
        return (self.elapsed + 1e-8) % self.period

    @property
    def district(self):
        index = self.cycle % len(self.DISTRICTS)
        return self.DISTRICTS[index]

    @property
    def active(self):
        return self.phase >= self.CLEAR_SECONDS

    @property
    def warning(self):
        return (
            not self.active
            and self.phase
            >= self.CLEAR_SECONDS - self.WARNING_SECONDS
        )

    @property
    def stage(self):
        if self.active:
            return "BLACKOUT"

        return "WARNING" if self.warning else "POWER ON"

    @property
    def remaining(self):
        end = (
            self.period
            if self.active
            else self.CLEAR_SECONDS
        )

        return max(
            1,
            math.ceil(end - self.phase - 1e-7),
        )

    @property
    def bounds(self):
        if self.active:
            return self.district[1]

        return (0, 0, 0, 0)

    def is_dark(self, x, y):
        left, top, right, bottom = self.bounds

        return (
            left <= x < right
            and top <= y < bottom
        )

    def update(self, dt):
        previous = self.stage
        self.elapsed += max(0.0, dt)

        return self.stage != previous

    def interact(self, delivery, car):
        before = delivery.completed_count
        bonus = 0

        if delivery.state == "dropoff":
            x, y, width, height = (
                delivery.contract.destination
            )

            if self.is_dark(
                x + width / 2,
                y + height / 2,
            ):
                bonus = delivery.calculate_reward() // 4

        delivery.interact(car)

        # A bonus is awarded only after a successful delivery.
        if delivery.completed_count > before and bonus > 0:
            delivery.score += bonus
            self.bonus_total += bonus

            delivery.feedback(
                f"Blackout bonus +{bonus}! "
                f"Total {delivery.score} pts."
            )


# Extend the existing shader for district power cuts.
POWER_SHADER = NIGHT_SHADER.replace(
    "uniform vec3 uEye;",
    """uniform vec3 uEye;
uniform vec4 uPowerBounds;
uniform bool uTownPass;
uniform vec3 uEmergencyPosition;""",
).replace(
    "    vec3 colour = vColour.rgb * illumination;",
    """    vec2 ground = vec2(vPosition.x, -vPosition.y);

    bool dark = uTownPass
        && ground.x >= uPowerBounds.x
        && ground.y >= uPowerBounds.y
        && ground.x < uPowerBounds.z
        && ground.y < uPowerBounds.w;

    bool emergency = all(lessThan(
        abs(vPosition - uEmergencyPosition),
        vec3(6.0, 1.0, 2.5)
    ));

    vec3 surface = vColour.rgb;
    float emission = vEmission;

    if (
        dark
        && !emergency
        && vPosition.z > 5.0
        && vEmission >= 0.3
    )
    {
        surface = vec3(0.025, 0.045, 0.065);
        emission = 0.0;
    }

    vec3 colour = surface * illumination;""",
).replace(
    "vColour.rgb * 1.45,\n        vEmission",
    "surface * 1.45,\n        emission",
)


class BlackoutRenderer(NightRenderer):
    def __init__(
        self, width, height,
        lights, blockers, power,
    ):
        super().__init__(
            width, height, lights, blockers
        )

        self.power = power
        self.all_lights = self.lights

        try:
            program = compileProgram(
                compileShader(
                    VERTEX_SHADER,
                    GL.GL_VERTEX_SHADER,
                ),
                compileShader(
                    POWER_SHADER,
                    GL.GL_FRAGMENT_SHADER,
                ),
            )

        except Exception:
            GL.glDeleteProgram(self.program)
            raise

        GL.glDeleteProgram(self.program)
        self.program = program

        names = (
            *self.locations,
            "uPowerBounds",
            "uTownPass",
            "uEmergencyPosition",
        )

        self.locations = {
            name: GL.glGetUniformLocation(
                self.program, name
            )
            for name in names
        }

    def begin(
        self, camera,
        car_pose=None, headlights=True,
    ):
        # Remove streetlights belonging to the affected district.
        self.lights = tuple(
            light
            for light in self.all_lights
            if not self.power.is_dark(
                light[0][0],
                light[0][1],
            )
        )

        super().begin(
            camera, car_pose, headlights
        )

        GL.glUniform4f(
            self.locations["uPowerBounds"],
            *self.power.bounds,
        )

        GL.glUniform1i(
            self.locations["uTownPass"],
            0,
        )

        # Preserve the small emergency lamp at Eduvos.
        x, y, _, length = EDUVOS_BUILDING

        GL.glUniform3f(
            self.locations["uEmergencyPosition"],
            x + 230,
            -(y + length + 1.5),
            78.5,
        )

    def draw_town(self, mesh):
        GL.glUniform1i(
            self.locations["uTownPass"],
            1,
        )

        try:
            self.draw(mesh)

        finally:
            # Vehicles, particles and markers retain their lights.
            GL.glUniform1i(
                self.locations["uTownPass"],
                0,
            )


class PowerBanner(Screens):
    def __init__(self, width, height, power):
        self.power = power
        self.headlights = True

        super().__init__(width, height)

    def draw_power(
        self, delivery, car, audio,
        records, fuel, headlights,
    ):
        self.headlights = headlights

        key = (
            self.power.cycle,
            self.power.stage,
            self.power.remaining,
            self.power.bonus_total,
            headlights,
        )

        super().draw(
            key, delivery, car,
            audio, records, fuel,
        )

    def compose(
        self, mode, delivery,
        car, audio, records, fuel,
    ):
        self.surface.fill((0, 0, 0, 0))

        power = self.power
        name = power.district[0]
        colour = (58, 214, 200)

        if power.active:
            colour = (255, 190, 91)

            title = (
                f"BLACKOUT: {name} | "
                f"{power.remaining}s | BONUS +25%"
            )

        elif power.warning:
            colour = (255, 107, 102)

            title = (
                f"WARNING: {name} loses power "
                f"in {power.remaining}s"
            )

        else:
            title = (
                f"POWER ON | Next blackout: "
                f"{name} in {power.remaining}s"
            )

        pygame.draw.rect(
            self.surface,
            (12, 22, 36, 235),
            (16, 14, 760, 62),
            border_radius=8,
        )

        pygame.draw.rect(
            self.surface,
            colour,
            (16, 14, 4, 62),
        )

        self.text(
            title,
            (32, 22),
            "body",
            colour,
        )

        lamps = "ON" if self.headlights else "OFF"

        self.text(
            f"Headlights: {lamps} (L) | "
            f"Blackout bonus earned: "
            f"{power.bonus_total} pts",
            (32, 49),
            "small",
            (190, 207, 220),
        )