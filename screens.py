import ctypes
import math

import pygame
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from hud import VERTEX_SHADER, FRAGMENT_SHADER


WHITE = (235, 242, 247)
MUTED = (156, 176, 194)
TEAL = (58, 214, 200)
AMBER = (255, 190, 91)
CORAL = (255, 107, 102)
LILAC = (186, 153, 255)

INK = (10, 24, 36)
PANEL = (18, 28, 45, 255)
OUTLINE = (57, 75, 94)


class Screens:
    """Render full-screen menus over the frozen town scene."""

    def __init__(self, width, height):
        pygame.font.init()

        self.width = width
        self.height = height

        self.surface = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        )

        self.fonts = {
            "hero": pygame.font.Font(None, 84),
            "heading": pygame.font.Font(None, 48),
            "score": pygame.font.Font(None, 76),
            "button": pygame.font.Font(None, 30),
            "body": pygame.font.Font(None, 26),
            "small": pygame.font.Font(None, 22),
        }

        self.last_state = None

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

        vertices = (
            -1.0, 1.0, 0.0, 0.0,
             1.0, 1.0, 1.0, 0.0,
             1.0, -1.0, 1.0, 1.0,
            -1.0, 1.0, 0.0, 0.0,
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
            height,
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

    def text(
        self,
        message,
        position,
        font="body",
        colour=WHITE,
        centred=False,
    ):
        image = self.fonts[font].render(
            message, True, colour
        )

        target = (
            image.get_rect(center=position)
            if centred
            else position
        )

        self.surface.blit(image, target)

    def button(self, label, rect, colour=TEAL):
        pygame.draw.rect(
            self.surface,
            colour,
            rect,
            border_radius=8,
        )

        x, y, width, height = rect

        self.text(
            label,
            (x + width / 2, y + height / 2),
            "button",
            INK,
            centred=True,
        )

    def parcel_art(self):
        pygame.draw.polygon(
            self.surface,
            (121, 87, 60),
            (
                (940, 130),
                (1040, 180),
                (1040, 290),
                (940, 240),
            ),
        )

        pygame.draw.polygon(
            self.surface,
            (170, 124, 77),
            (
                (1040, 180),
                (1140, 130),
                (1140, 240),
                (1040, 290),
            ),
        )

        pygame.draw.polygon(
            self.surface,
            AMBER,
            (
                (940, 130),
                (1040, 85),
                (1140, 130),
                (1040, 180),
            ),
        )

        pygame.draw.polygon(
            self.surface,
            (248, 223, 166),
            (
                (978, 113),
                (1001, 103),
                (1101, 150),
                (1078, 161),
            ),
        )

        pygame.draw.polygon(
            self.surface,
            (220, 192, 137),
            (
                (1078, 161),
                (1101, 150),
                (1101, 260),
                (1078, 271),
            ),
        )

        pygame.draw.lines(
            self.surface,
            TEAL,
            False,
            (
                (860, 230),
                (900, 230),
                (900, 280),
                (940, 280),
            ),
            4,
        )

        pygame.draw.circle(
            self.surface, TEAL, (860, 230), 7
        )

    def compose(self, mode, delivery, car, audio):
        self.surface.fill((8, 14, 26, 235))

        if mode == "title":
            self.text(
                "AFTER HOURS COURIER",
                (80, 65),
                "small",
                TEAL,
            )

            self.text(
                "MIDNIGHT", (80, 112), "hero"
            )

            self.text(
                "DELIVERY", (80, 182), "hero", AMBER
            )

            self.text(
                "Nine deliveries. Three shifts. One long night.",
                (84, 265),
            )

            self.parcel_art()

            cards = (
                (
                    80,
                    "STANDARD",
                    "Base pay + time bonus",
                    TEAL,
                ),
                (
                    464,
                    "FRAGILE",
                    "Crashes reduce parcel value",
                    LILAC,
                ),
                (
                    848,
                    "EXPRESS",
                    "Late delivery = half base pay",
                    AMBER,
                ),
            )

            for x, title, description, colour in cards:
                pygame.draw.rect(
                    self.surface,
                    PANEL,
                    (x, 330, 352, 112),
                    border_radius=8,
                )

                pygame.draw.rect(
                    self.surface,
                    colour,
                    (x, 330, 352, 4),
                )

                self.text(
                    title,
                    (x + 20, 351),
                    "button",
                    colour,
                )

                self.text(
                    description,
                    (x + 20, 397),
                    "small",
                    MUTED,
                )

            self.text(
                "WASD / ARROWS: DRIVE    SPACE: BRAKE",
                (80, 480),
            )

            self.text(
                "E: COLLECT / DELIVER    P: PAUSE"
                "    M: SOUND    ESC: EXIT",
                (80, 516),
                "small",
                MUTED,
            )

            self.button(
                "ENTER  START NIGHT",
                (80, 588, 400, 64),
            )

            self.text(
                f"SOUND: {audio.status.upper()}  (M)",
                (530, 610),
                "small",
                MUTED,
            )

            self.text(
                "Your score rewards speed and careful driving.",
                (80, 674),
                "small",
                MUTED,
            )

            return

        pygame.draw.rect(
            self.surface,
            PANEL,
            (256, 130, 768, 460),
            border_radius=12,
        )

        pygame.draw.rect(
            self.surface,
            OUTLINE,
            (256, 130, 768, 460),
            2,
            border_radius=12,
        )

        if mode == "paused":
            self.text(
                "NIGHT PAUSED",
                (296, 175),
                "heading",
                TEAL,
            )

            self.text(
                f"SHIFT {delivery.shift_number} / 3",
                (296, 250),
                "button",
            )

            self.text(
                f"SCORE: {delivery.score}",
                (704, 250),
                "button",
                AMBER,
            )

            self.text(
                delivery.objective,
                (296, 315),
            )

            self.text(
                "VEHICLE CONDITION: "
                f"{math.ceil(car.condition)}%",
                (296, 360),
                "small",
                MUTED,
            )

            self.button(
                "ENTER / P  RESUME",
                (296, 430, 688, 58),
            )

            self.text(
                "R: RESTART NIGHT    ESC: EXIT",
                (296, 522),
                "small",
                MUTED,
            )

            self.text(
                f"SOUND: {audio.status.upper()}  (M)",
                (296, 555),
                "small",
                MUTED,
            )

            return

        won = mode == "complete"
        colour = TEAL if won else CORAL

        title = (
            "NIGHT COMPLETE"
            if won
            else "VEHICLE DISABLED"
        )

        reason = (
            "Three shifts completed."
            if won
            else "Your vehicle could not continue."
        )

        self.text(
            title,
            (296, 175),
            "heading",
            colour,
        )

        self.text(
            reason, (296, 237), colour=MUTED
        )

        self.text(
            "FINAL SCORE",
            (296, 288),
            "small",
            MUTED,
        )

        self.text(
            str(delivery.score),
            (296, 313),
            "score",
            AMBER,
        )

        self.text(
            "CONTRACTS",
            (720, 288),
            "small",
            MUTED,
        )

        self.text(
            f"{delivery.completed_count}/"
            f"{delivery.total_deliveries}",
            (720, 323),
            "heading",
        )

        self.text(
            "VEHICLE CONDITION: "
            f"{math.ceil(car.condition)}%",
            (296, 397),
            "small",
            MUTED,
        )

        self.button(
            "ENTER  PLAY AGAIN",
            (296, 446, 688, 58),
            colour,
        )

        self.text(
            "R: RESTART NIGHT    ESC: EXIT",
            (296, 536),
            "small",
            MUTED,
        )

    def draw(self, mode, delivery, car, audio):
        state = (
            mode,
            delivery.score,
            delivery.completed_count,
            delivery.shift_number,
            delivery.objective,
            math.ceil(car.condition),
            audio.status,
        )

        GL.glActiveTexture(GL.GL_TEXTURE0)

        GL.glBindTexture(
            GL.GL_TEXTURE_2D,
            self.texture,
        )

        if state != self.last_state:
            self.compose(mode, delivery, car, audio)

            pixels = pygame.image.tobytes(
                self.surface, "RGBA", False
            )

            GL.glTexSubImage2D(
                GL.GL_TEXTURE_2D,
                0,
                0,
                0,
                self.width,
                self.height,
                GL.GL_RGBA,
                GL.GL_UNSIGNED_BYTE,
                pixels,
            )

            self.last_state = state

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