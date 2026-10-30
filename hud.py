import ctypes
import math

import pygame
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader


HUD_HEIGHT = 104

WHITE = (235, 242, 247)
MUTED = (156, 176, 194)
TEAL = (58, 214, 200)
AMBER = (255, 190, 91)
CORAL = (255, 107, 102)
DIVIDER = (57, 75, 94)


VERTEX_SHADER = """
#version 330 core

layout (location = 0) in vec2 aPosition;
layout (location = 1) in vec2 aUV;

out vec2 vUV;

void main()
{
    gl_Position = vec4(aPosition, 0.0, 1.0);
    vUV = aUV;
}
"""


FRAGMENT_SHADER = """
#version 330 core

in vec2 vUV;
out vec4 fragmentColour;

uniform sampler2D uTexture;

void main()
{
    fragmentColour = texture(uTexture, vUV);
}
"""


def compose_dashboard(
    surface, fonts, state, max_speed
):
    """Draw the interface into a reusable PyGame surface."""
    (
        speed,
        direction,
        sound_status,
        objective,
        prompt,
        score,
        condition,
        impact_flash,
        fuel_percent,
        fuel_low,
        fuel_spent,
        fuel_hint,
    ) = state

    width = surface.get_width()
    surface.fill((18, 27, 45, 245))

    pygame.draw.rect(
        surface, TEAL, (0, 0, width, 3)
    )

    pygame.draw.line(
        surface, DIVIDER, (360, 18), (360, 88)
    )

    pygame.draw.line(
        surface, DIVIDER, (650, 18), (650, 88)
    )

    pygame.draw.line(
        surface, DIVIDER, (1016, 18), (1016, 88)
    )

    def text(
        message, position, font="body", colour=WHITE
    ):
        image = fonts[font].render(
            message, True, colour
        )
        surface.blit(image, position)

    text("MIDNIGHT DELIVERY", (24, 15), "title")

    objective_colour = (
        CORAL if direction == "DISABLED" else TEAL
    )

    text(objective, (24, 47), "body", objective_colour)
    text(prompt, (24, 78), "small", MUTED)

    text("SPEED", (384, 12), "small", MUTED)
    text(f"{speed:03d}", (384, 34), "speed")
    text("px/s", (462, 51), "small", MUTED)

    if direction == "DISABLED":
        direction_colour = CORAL
    elif direction in ("BRAKING", "REVERSE"):
        direction_colour = AMBER
    else:
        direction_colour = TEAL

    if impact_flash or condition <= 30:
        condition_colour = CORAL
    elif condition <= 60:
        condition_colour = AMBER
    else:
        condition_colour = TEAL

    text(
        f"CAR: {condition}%",
        (535, 12),
        "small",
        condition_colour,
    )

    text(
        direction,
        (535, 47),
        "body",
        direction_colour,
    )

    pygame.draw.rect(
        surface, DIVIDER, (384, 83, 128, 6)
    )

    fraction = max(
        0.0, min(speed / max_speed, 1.0)
    )

    if fraction > 0.0:
        pygame.draw.rect(
            surface,
            direction_colour,
            (384, 83, round(128 * fraction), 6),
        )

    pygame.draw.rect(
        surface, DIVIDER, (535, 83, 87, 6)
    )

    if condition > 0:
        pygame.draw.rect(
            surface,
            condition_colour,
            (535, 83, round(87 * condition / 100), 6),
        )

    text(
        "E INTERACT   F REPAIR   G FUEL",
        (682, 16),
    )

    text(
        f"SCORE: {score}   FUEL SPENT: {fuel_spent}",
        (682, 46),
    )

    text(
        "TAB MAP   P PAUSE   M SOUND: "
        + sound_status.upper(),
        (682, 76),
        "small",
        MUTED,
    )

    if fuel_low:
        fuel_colour = CORAL
    elif fuel_percent <= 40:
        fuel_colour = AMBER
    else:
        fuel_colour = TEAL

    text(
        f"FUEL: {fuel_percent}%",
        (1040, 16),
        colour=fuel_colour,
    )

    pygame.draw.rect(
        surface, DIVIDER, (1040, 49, 192, 8)
    )

    if fuel_percent > 0:
        pygame.draw.rect(
            surface,
            fuel_colour,
            (1040, 49, round(192 * fuel_percent / 100), 8),
        )

    text(
        fuel_hint,
        (1040, 76),
        "small",
        fuel_colour if fuel_low else MUTED,
    )


class Hud:
    def __init__(self, width, height):
        pygame.font.init()

        self.width = width

        self.surface = pygame.Surface(
            (width, HUD_HEIGHT),
            pygame.SRCALPHA,
        )

        self.fonts = {
            "title": pygame.font.Font(None, 28),
            "body": pygame.font.Font(None, 22),
            "small": pygame.font.Font(None, 18),
            "speed": pygame.font.Font(None, 42),
        }

        self.last_state = None
        self.next_refresh = 0

        self.program = compileProgram(
            compileShader(
                VERTEX_SHADER,
                GL.GL_VERTEX_SHADER,
            ),
            compileShader(
                FRAGMENT_SHADER,
                GL.GL_FRAGMENT_SHADER,
            ),
        )

        top = -1.0 + 2.0 * HUD_HEIGHT / height

        # Position X/Y followed by texture U/V.
        vertices = (
            -1.0, top, 0.0, 0.0,
             1.0, top, 1.0, 0.0,
             1.0, -1.0, 1.0, 1.0,
            -1.0, top, 0.0, 0.0,
             1.0, -1.0, 1.0, 1.0,
            -1.0, -1.0, 0.0, 1.0,
        )

        data = (
            ctypes.c_float * len(vertices)
        )(*vertices)

        stride = 4 * ctypes.sizeof(ctypes.c_float)

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            ctypes.sizeof(data),
            data,
            GL.GL_STATIC_DRAW,
        )

        GL.glVertexAttribPointer(
            0, 2, GL.GL_FLOAT, GL.GL_FALSE,
            stride, ctypes.c_void_p(0),
        )

        GL.glEnableVertexAttribArray(0)

        GL.glVertexAttribPointer(
            1, 2, GL.GL_FLOAT, GL.GL_FALSE,
            stride,
            ctypes.c_void_p(
                2 * ctypes.sizeof(ctypes.c_float)
            ),
        )

        GL.glEnableVertexAttribArray(1)

        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        self.texture = GL.glGenTextures(1)

        GL.glBindTexture(
            GL.GL_TEXTURE_2D,
            self.texture,
        )

        for parameter in (
            GL.GL_TEXTURE_MIN_FILTER,
            GL.GL_TEXTURE_MAG_FILTER,
        ):
            GL.glTexParameteri(
                GL.GL_TEXTURE_2D,
                parameter,
                GL.GL_LINEAR,
            )

        for parameter in (
            GL.GL_TEXTURE_WRAP_S,
            GL.GL_TEXTURE_WRAP_T,
        ):
            GL.glTexParameteri(
                GL.GL_TEXTURE_2D,
                parameter,
                GL.GL_CLAMP_TO_EDGE,
            )

        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA8,
            width,
            HUD_HEIGHT,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            None,
        )

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

        GL.glUseProgram(self.program)

        GL.glUniform1i(
            GL.glGetUniformLocation(
                self.program, "uTexture"
            ),
            0,
        )

        GL.glUseProgram(0)

    def draw(self, car, audio, delivery, fuel):
        if car.disabled:
            direction = "DISABLED"
        elif car.braking:
            direction = "BRAKING"
        elif car.speed < -1.0:
            direction = "REVERSE"
        elif car.speed > 1.0:
            direction = "FORWARD"
        else:
            direction = "STOPPED"

        if car.disabled and delivery.state != "complete":
            objective = "VEHICLE DISABLED"
            prompt = "R: RESTART THE NIGHT"
        else:
            objective = delivery.objective
            prompt = delivery.prompt(car)

        if fuel.empty:
            fuel_hint = "TANK EMPTY"

        elif delivery.at_depot(car):
            _, cost = fuel.refill_quote()

            if abs(car.speed) > delivery.STOP_SPEED:
                fuel_hint = "STOP TO REFUEL"
            elif cost == 0:
                fuel_hint = "TANK FULL"
            elif delivery.score < cost:
                fuel_hint = f"NEED {cost} PTS"
            else:
                fuel_hint = f"G: REFUEL {cost} PTS"

        elif fuel.low:
            fuel_hint = "LOW: RETURN TO DEPOT"

        else:
            fuel_hint = "G: REFUEL AT DEPOT"

        state = (
            round(abs(car.speed)),
            direction,
            audio.status,
            objective,
            prompt,
            delivery.score,
            math.ceil(car.condition),
            car.impact_flash > 0.0,
            fuel.percentage,
            fuel.low,
            fuel.points_spent,
            fuel_hint,
        )

        now = pygame.time.get_ticks()

        GL.glActiveTexture(GL.GL_TEXTURE0)

        GL.glBindTexture(
            GL.GL_TEXTURE_2D,
            self.texture,
        )

        if self.last_state is None or (
            state != self.last_state
            and now >= self.next_refresh
        ):
            compose_dashboard(
                self.surface,
                self.fonts,
                state,
                car.MAX_SPEED,
            )

            pixels = pygame.image.tobytes(
                self.surface, "RGBA", False
            )

            GL.glTexSubImage2D(
                GL.GL_TEXTURE_2D,
                0,
                0,
                0,
                self.width,
                HUD_HEIGHT,
                GL.GL_RGBA,
                GL.GL_UNSIGNED_BYTE,
                pixels,
            )

            self.last_state = state
            self.next_refresh = now + 100

        GL.glUseProgram(self.program)
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

        GL.glBindVertexArray(0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)

    def close(self):
        GL.glDeleteTextures([self.texture])
        GL.glDeleteBuffers(1, [self.vbo])
        GL.glDeleteVertexArrays(1, [self.vao])
        GL.glDeleteProgram(self.program)