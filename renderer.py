from array import array
import ctypes
import math

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader


VERTEX_SHADER = """
#version 330 core

layout (location = 0) in vec2 aPosition;
layout (location = 1) in vec4 aColour;

uniform vec2 uResolution;
out vec4 vColour;

void main()
{
    vec2 screenPosition = vec2(
        aPosition.x / uResolution.x * 2.0 - 1.0,
        1.0 - aPosition.y / uResolution.y * 2.0
    );

    gl_Position = vec4(screenPosition, 0.0, 1.0);
    vColour = aColour;
}
"""


FRAGMENT_SHADER = """
#version 330 core

in vec4 vColour;
out vec4 fragmentColour;

void main()
{
    fragmentColour = vColour;
}
"""


class Renderer:
    """Collect coloured shapes and draw them as one ordered batch."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.vertices = array("f")

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

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            144,
            None,
            GL.GL_STREAM_DRAW,
        )

        stride = 6 * ctypes.sizeof(ctypes.c_float)

        GL.glVertexAttribPointer(
            0, 2, GL.GL_FLOAT, GL.GL_FALSE,
            stride, ctypes.c_void_p(0),
        )

        GL.glEnableVertexAttribArray(0)

        GL.glVertexAttribPointer(
            1, 4, GL.GL_FLOAT, GL.GL_FALSE,
            stride,
            ctypes.c_void_p(
                2 * ctypes.sizeof(ctypes.c_float)
            ),
        )

        GL.glEnableVertexAttribArray(1)

        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        self.resolution_location = GL.glGetUniformLocation(
            self.program,
            "uResolution",
        )

        GL.glEnable(GL.GL_BLEND)

        GL.glBlendFunc(
            GL.GL_SRC_ALPHA,
            GL.GL_ONE_MINUS_SRC_ALPHA,
        )

        GL.glViewport(0, 0, width, height)

    def begin_frame(self, colour):
        self.vertices = array("f")
        GL.glClearColor(*colour)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def draw_quad(self, points, colour):
        """Add a convex four-corner shape in perimeter order."""
        p0, p1, p2, p3 = points

        self.vertices.extend((
            *p0, *colour,
            *p1, *colour,
            *p2, *colour,
            *p0, *colour,
            *p2, *colour,
            *p3, *colour,
        ))

    def draw_rect(
        self, x, y, width, height, colour, angle=0.0
    ):
        if angle == 0.0:
            points = (
                (x, y),
                (x + width, y),
                (x + width, y + height),
                (x, y + height),
            )

        else:
            radians = math.radians(angle)
            c = math.cos(radians)
            s = math.sin(radians)

            cx = x + width / 2
            cy = y + height / 2
            hw = width / 2
            hh = height / 2

            points = tuple(
                (
                    cx + px * c - py * s,
                    cy + px * s + py * c,
                )
                for px, py in (
                    (-hw, -hh),
                    (hw, -hh),
                    (hw, hh),
                    (-hw, hh),
                )
            )

        self.draw_quad(points, colour)

    def flush(self):
        """Draw queued shapes before drawing textured UI."""
        if not self.vertices:
            return

        pixels = self.vertices.tobytes()
        count = len(self.vertices) // 6

        GL.glUseProgram(self.program)
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            len(pixels),
            pixels,
            GL.GL_STREAM_DRAW,
        )

        GL.glUniform2f(
            self.resolution_location,
            self.width,
            self.height,
        )

        GL.glDrawArrays(
            GL.GL_TRIANGLES,
            0,
            count,
        )

        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

        self.vertices = array("f")

    def end_frame(self):
        self.flush()
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def close(self):
        GL.glDeleteBuffers(1, [self.vbo])
        GL.glDeleteVertexArrays(1, [self.vao])
        GL.glDeleteProgram(self.program)