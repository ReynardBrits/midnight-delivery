import ctypes
import math

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader


VERTEX_SHADER = """
#version 330 core

layout (location = 0) in vec2 aPosition;

uniform vec2 uResolution;
uniform vec2 uCentre;
uniform vec2 uSize;
uniform float uAngle;

void main()
{
    vec2 localPosition = aPosition * uSize;

    float c = cos(uAngle);
    float s = sin(uAngle);

    mat2 rotation = mat2(c, s, -s, c);

    vec2 pixelPosition =
        uCentre + rotation * localPosition;

    vec2 screenPosition = vec2(
        pixelPosition.x / uResolution.x * 2.0 - 1.0,
        1.0 - pixelPosition.y / uResolution.y * 2.0
    );

    gl_Position = vec4(screenPosition, 0.0, 1.0);
}
"""


FRAGMENT_SHADER = """
#version 330 core

out vec4 fragmentColour;

uniform vec4 uColour;

void main()
{
    fragmentColour = uColour;
}
"""


class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.program = compileProgram(
            compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER),
            compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER),
        )

        # Two triangles form one rectangle.
        vertices = (
            -0.5, -0.5,
             0.5, -0.5,
             0.5,  0.5,
            -0.5, -0.5,
             0.5,  0.5,
            -0.5,  0.5,
        )

        vertex_data = (
            ctypes.c_float * len(vertices)
        )(*vertices)

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            ctypes.sizeof(vertex_data),
            vertex_data,
            GL.GL_STATIC_DRAW,
        )

        GL.glVertexAttribPointer(
            0,
            2,
            GL.GL_FLOAT,
            GL.GL_FALSE,
            2 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0),
        )

        GL.glEnableVertexAttribArray(0)
        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        self.resolution_location = GL.glGetUniformLocation(
            self.program, "uResolution"
        )
        self.centre_location = GL.glGetUniformLocation(
            self.program, "uCentre"
        )
        self.size_location = GL.glGetUniformLocation(
            self.program, "uSize"
        )
        self.angle_location = GL.glGetUniformLocation(
            self.program, "uAngle"
        )
        self.colour_location = GL.glGetUniformLocation(
            self.program, "uColour"
        )

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(
            GL.GL_SRC_ALPHA,
            GL.GL_ONE_MINUS_SRC_ALPHA,
        )

        GL.glViewport(0, 0, width, height)

    def begin_frame(self, colour):
        GL.glClearColor(*colour)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glUseProgram(self.program)
        GL.glBindVertexArray(self.vao)

        GL.glUniform2f(
            self.resolution_location,
            self.width,
            self.height,
        )

    def draw_rect(
        self, x, y, width, height, colour, angle=0.0
    ):
        GL.glUniform2f(
            self.centre_location,
            x + width / 2,
            y + height / 2,
        )

        GL.glUniform2f(
            self.size_location,
            width,
            height,
        )

        GL.glUniform1f(
            self.angle_location,
            math.radians(angle),
        )

        GL.glUniform4f(
            self.colour_location,
            *colour,
        )

        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

    def end_frame(self):
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def close(self):
        GL.glDeleteBuffers(1, [self.vbo])
        GL.glDeleteVertexArrays(1, [self.vao])
        GL.glDeleteProgram(self.program)