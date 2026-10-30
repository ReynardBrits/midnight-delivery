import ctypes
import math
from array import array

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader


BACKGROUND = (0.035, 0.055, 0.095, 1.0)

VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPosition;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec4 aColour;
layout (location = 3) in float aEmission;

uniform mat4 uViewProjection;
uniform vec3 uOffset;
uniform float uAngle;

out vec3 vPosition;
out vec3 vNormal;
out vec4 vColour;
out float vEmission;

void main()
{
    float c = cos(uAngle);
    float s = sin(uAngle);
    mat2 rotation = mat2(c, s, -s, c);

    vPosition = vec3(rotation * aPosition.xy, aPosition.z) + uOffset;
    vNormal = vec3(rotation * aNormal.xy, aNormal.z);

    // Game Y increases southwards; OpenGL uses a right-handed Z-up world.
    vPosition.y = -vPosition.y;
    vNormal.y = -vNormal.y;

    vColour = aColour;
    vEmission = aEmission;

    gl_Position = uViewProjection * vec4(vPosition, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
in vec3 vPosition;
in vec3 vNormal;
in vec4 vColour;
in float vEmission;

uniform vec3 uEye;
out vec4 fragmentColour;

void main()
{
    vec3 normal = normalize(vNormal);
    vec3 light = normalize(vec3(-0.45, -0.35, 0.85));

    float diffuse = max(dot(normal, light), 0.0);

    vec3 ambient = vec3(0.44, 0.51, 0.67);
    vec3 key = vec3(0.64, 0.59, 0.48);

    vec3 colour = vColour.rgb * (ambient + diffuse * key);
    colour = mix(colour, vColour.rgb, vEmission);

    float fog = smoothstep(
        1700.0, 4200.0, distance(uEye, vPosition)
    );

    colour = mix(
        colour,
        vec3(0.035, 0.055, 0.095),
        fog * 0.65
    );

    fragmentColour = vec4(colour, vColour.a);
}
"""


def normalise(vector):
    length = math.sqrt(
        sum(value * value for value in vector)
    )

    if length < 0.000001:
        return (0.0, 0.0, 1.0)

    return tuple(value / length for value in vector)


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


class Camera3D:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = float(x)
        self.y = float(y)
        self.yaw = 25.0
        self.span = 880.0

    def follow(self, x, y, dt):
        weight = 1.0 - math.exp(-8.0 * dt)
        self.x += (x - self.x) * weight
        self.y += (y - self.y) * weight

    def zoom(self, steps):
        self.span = max(
            500.0,
            min(1600.0, self.span * 0.9 ** steps),
        )

    def view_projection(self):
        angle = math.radians(self.yaw)

        eye = (
            self.x + math.sin(angle) * 1000.0,
            -self.y - math.cos(angle) * 1000.0,
            1300.0,
        )

        forward = normalise(
            (
                self.x - eye[0],
                -self.y - eye[1],
                -eye[2],
            )
        )

        right = normalise(
            cross(forward, (0.0, 0.0, 1.0))
        )

        up = cross(right, forward)

        view = (
            (*right, -dot(right, eye)),
            (*up, -dot(up, eye)),
            (
                -forward[0],
                -forward[1],
                -forward[2],
                dot(forward, eye),
            ),
            (0.0, 0.0, 0.0, 1.0),
        )

        half_width = self.span / 2
        half_height = (
            half_width * self.height / self.width
        )

        near, far = 1.0, 6000.0

        projection = (
            (1 / half_width, 0.0, 0.0, 0.0),
            (0.0, 1 / half_height, 0.0, 0.0),
            (
                0.0,
                0.0,
                -2 / (far - near),
                -(far + near) / (far - near),
            ),
            (0.0, 0.0, 0.0, 1.0),
        )

        matrix = [
            [
                sum(
                    projection[r][k] * view[k][c]
                    for k in range(4)
                )
                for c in range(4)
            ]
            for r in range(4)
        ]

        # OpenGL expects column-major matrix data.
        packed = (ctypes.c_float * 16)(
            *(
                matrix[row][column]
                for column in range(4)
                for row in range(4)
            )
        )

        return packed, eye


class MeshBuilder:
    def __init__(self):
        self.vertices = array("f")

    def triangle(
        self, a, b, c, colour, emission=0.0
    ):
        ab = tuple(b[i] - a[i] for i in range(3))
        ac = tuple(c[i] - a[i] for i in range(3))
        normal = normalise(cross(ab, ac))

        for position in (a, b, c):
            self.vertices.extend(
                (*position, *normal, *colour, emission)
            )

    def quad(self, points, colour, emission=0.0):
        a, b, c, d = points
        self.triangle(a, b, c, colour, emission)
        self.triangle(a, c, d, colour, emission)

    def plane(
        self, x, y, z, width, length,
        colour, emission=0.0,
    ):
        self.quad(
            (
                (x, y, z),
                (x + width, y, z),
                (x + width, y + length, z),
                (x, y + length, z),
            ),
            colour,
            emission,
        )

    def solid(self, points, colour, emission=0.0):
        for face in (
            (0, 3, 2, 1),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        ):
            self.quad(
                tuple(points[i] for i in face),
                colour,
                emission,
            )

    def box(
        self, x, y, z, width, length, height,
        colour, emission=0.0,
    ):
        self.loft(
            x, y, z, width, length, height,
            0, 0, colour, emission,
        )

    def loft(
        self, x, y, z, width, length, height,
        inset_x, inset_y, colour, emission=0.0,
    ):
        points = (
            (x, y, z),
            (x + width, y, z),
            (x + width, y + length, z),
            (x, y + length, z),
            (x + inset_x, y + inset_y, z + height),
            (
                x + width - inset_x,
                y + inset_y,
                z + height,
            ),
            (
                x + width - inset_x,
                y + length - inset_y,
                z + height,
            ),
            (
                x + inset_x,
                y + length - inset_y,
                z + height,
            ),
        )

        self.solid(points, colour, emission)

    def wheel(
        self, x, y, z, radius, width, colour
    ):
        segments = 12

        for index in range(segments):
            a = math.tau * index / segments
            b = math.tau * (index + 1) / segments

            ay = y + math.cos(a) * radius
            az = z + math.sin(a) * radius
            by = y + math.cos(b) * radius
            bz = z + math.sin(b) * radius

            self.quad(
                (
                    (x, ay, az),
                    (x, by, bz),
                    (x + width, by, bz),
                    (x + width, ay, az),
                ),
                colour,
            )

            self.triangle(
                (x, y, z),
                (x, by, bz),
                (x, ay, az),
                colour,
            )

            self.triangle(
                (x + width, y, z),
                (x + width, ay, az),
                (x + width, by, bz),
                colour,
            )

    def cone(
        self, x, y, z, radius, height, colour
    ):
        for index in range(8):
            a = math.tau * index / 8
            b = math.tau * (index + 1) / 8

            self.triangle(
                (
                    x + math.cos(a) * radius,
                    y + math.sin(a) * radius,
                    z,
                ),
                (
                    x + math.cos(b) * radius,
                    y + math.sin(b) * radius,
                    z,
                ),
                (x, y, z + height),
                colour,
            )


class Mesh3D:
    def __init__(self, builder):
        self.count = len(builder.vertices) // 11
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

        data = builder.vertices.tobytes()

        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            len(data),
            data,
            GL.GL_STATIC_DRAW,
        )

        for location, size, offset in (
            (0, 3, 0),
            (1, 3, 12),
            (2, 4, 24),
            (3, 1, 40),
        ):
            GL.glVertexAttribPointer(
                location,
                size,
                GL.GL_FLOAT,
                GL.GL_FALSE,
                44,
                ctypes.c_void_p(offset),
            )

            GL.glEnableVertexAttribArray(location)

        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def close(self):
        GL.glDeleteBuffers(1, [self.vbo])
        GL.glDeleteVertexArrays(1, [self.vao])


class Renderer3D:
    def __init__(self, width, height):
        self.width = width
        self.height = height

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

        self.locations = {
            name: GL.glGetUniformLocation(
                self.program, name
            )
            for name in (
                "uViewProjection",
                "uEye",
                "uOffset",
                "uAngle",
            )
        }

    def begin(self, camera):
        GL.glViewport(
            0, 0, self.width, self.height
        )

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glDepthMask(GL.GL_TRUE)

        GL.glDisable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_BLEND)

        GL.glBlendFunc(
            GL.GL_SRC_ALPHA,
            GL.GL_ONE_MINUS_SRC_ALPHA,
        )

        GL.glClearColor(*BACKGROUND)

        GL.glClear(
            int(GL.GL_COLOR_BUFFER_BIT)
            | int(GL.GL_DEPTH_BUFFER_BIT)
        )

        GL.glUseProgram(self.program)

        matrix, eye = camera.view_projection()

        GL.glUniformMatrix4fv(
            self.locations["uViewProjection"],
            1,
            GL.GL_FALSE,
            matrix,
        )

        GL.glUniform3f(
            self.locations["uEye"],
            *eye,
        )

    def draw(
        self, mesh, x=0.0, y=0.0,
        z=0.0, angle=0.0,
    ):
        GL.glUniform3f(
            self.locations["uOffset"],
            x, y, z,
        )

        GL.glUniform1f(
            self.locations["uAngle"],
            math.radians(angle),
        )

        GL.glBindVertexArray(mesh.vao)

        GL.glDrawArrays(
            GL.GL_TRIANGLES, 0, mesh.count
        )

        GL.glBindVertexArray(0)

    def close(self):
        GL.glDeleteProgram(self.program)