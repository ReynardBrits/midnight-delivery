import ctypes
import math

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from renderer3d import Renderer3D, VERTEX_SHADER


MAX_LIGHTS = 12
MAX_BLOCKERS = 16

NIGHT_SHADER = """
#version 330 core

in vec3 vPosition;
in vec3 vNormal;
in vec4 vColour;
in float vEmission;

uniform vec3 uEye;

uniform int uLightCount;
uniform vec3 uLightPosition[12];
uniform vec3 uLightColour[12];
uniform float uLightRadius[12];
uniform float uLightPower[12];

uniform bool uHeadlights;
uniform vec3 uHeadPosition[2];
uniform vec3 uHeadDirection;

uniform int uBlockCount;
uniform vec3 uBlockMin[16];
uniform vec3 uBlockMax[16];

out vec4 fragmentColour;

float safeComponent(float value)
{
    if (abs(value) < 0.00001)
        return value < 0.0 ? -0.00001 : 0.00001;

    return value;
}

bool blocked(vec3 origin, vec3 destination)
{
    vec3 ray = destination - origin;

    vec3 inverseRay = 1.0 / vec3(
        safeComponent(ray.x),
        safeComponent(ray.y),
        safeComponent(ray.z)
    );

    for (int i = 0; i < 16; ++i)
    {
        if (i >= uBlockCount) break;

        vec3 first = (uBlockMin[i] - origin) * inverseRay;
        vec3 second = (uBlockMax[i] - origin) * inverseRay;

        vec3 nearHit = min(first, second);
        vec3 farHit = max(first, second);

        float entry = max(
            max(nearHit.x, nearHit.y),
            nearHit.z
        );

        float exit = min(
            min(farHit.x, farHit.y),
            farHit.z
        );

        // Avoid treating the illuminated wall itself
        // as an obstruction.
        if (max(entry, 0.002) < min(exit, 0.992))
            return true;
    }

    return false;
}

void main()
{
    vec3 normal = normalize(vNormal);
    vec3 moon = normalize(vec3(-0.45, 0.35, 0.85));

    float moonDiffuse = max(dot(normal, moon), 0.0);

    vec3 illumination =
        vec3(0.20, 0.27, 0.42)
        + moonDiffuse * vec3(0.23, 0.27, 0.37);

    for (int i = 0; i < 12; ++i)
    {
        if (i >= uLightCount) break;

        vec3 toLight = uLightPosition[i] - vPosition;
        float distanceToLight = length(toLight);

        if (distanceToLight >= uLightRadius[i])
            continue;

        float falloff =
            1.0 - distanceToLight / uLightRadius[i];

        float diffuse = max(
            dot(
                normal,
                toLight / max(distanceToLight, 0.001)
            ),
            0.0
        );

        illumination +=
            uLightColour[i]
            * uLightPower[i]
            * falloff
            * falloff
            * diffuse;
    }

    if (uHeadlights)
    {
        for (int i = 0; i < 2; ++i)
        {
            vec3 fromLight = vPosition - uHeadPosition[i];
            float distanceToLight = length(fromLight);

            if (
                distanceToLight < 0.001
                || distanceToLight >= 340.0
            )
                continue;

            vec3 direction = fromLight / distanceToLight;

            float cone = smoothstep(
                0.9272,
                0.9903,
                dot(direction, uHeadDirection)
            );

            float diffuse = max(
                dot(normal, -direction),
                0.0
            );

            if (cone * diffuse < 0.001)
                continue;

            if (blocked(uHeadPosition[i], vPosition))
                continue;

            float falloff =
                1.0 - distanceToLight / 340.0;

            illumination +=
                vec3(1.0, 0.90, 0.67)
                * 9.0
                * cone
                * diffuse
                * falloff
                * falloff;
        }
    }

    vec3 colour = vColour.rgb * illumination;

    colour = mix(
        colour,
        vColour.rgb * 1.45,
        vEmission
    );

    // Compress bright areas smoothly.
    colour = vec3(1.0) - exp(
        -max(colour, vec3(0.0)) * 1.4
    );

    float fog = smoothstep(
        1700.0,
        4200.0,
        distance(uEye, vPosition)
    );

    colour = mix(
        colour,
        vec3(0.035, 0.055, 0.095),
        fog * 0.65
    );

    fragmentColour = vec4(colour, vColour.a);
}
"""


class NightRenderer(Renderer3D):
    """Add local lights and headlight obstruction."""

    def __init__(
        self, width, height, lights=(), blockers=()
    ):
        self.width = width
        self.height = height
        self.lights = tuple(lights)
        self.blockers = tuple(blockers)

        self.program = compileProgram(
            compileShader(
                VERTEX_SHADER,
                GL.GL_VERTEX_SHADER,
            ),
            compileShader(
                NIGHT_SHADER,
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
                "uLightCount",
                "uLightPosition[0]",
                "uLightColour[0]",
                "uLightRadius[0]",
                "uLightPower[0]",
                "uHeadlights",
                "uHeadPosition[0]",
                "uHeadDirection",
                "uBlockCount",
                "uBlockMin[0]",
                "uBlockMax[0]",
            )
        }

    def upload(self, name, values, components=3):
        if not values:
            return

        packed = (
            ctypes.c_float * len(values)
        )(*values)

        location = self.locations[name]

        if components == 3:
            GL.glUniform3fv(
                location,
                len(values) // 3,
                packed,
            )
        else:
            GL.glUniform1fv(
                location,
                len(values),
                packed,
            )

    def begin(
        self, camera, car_pose=None, headlights=True
    ):
        super().begin(camera)

        nearby = sorted(
            self.lights,
            key=lambda light: (
                (light[0][0] - camera.x) ** 2
                + (light[0][1] - camera.y) ** 2
            ),
        )[:MAX_LIGHTS]

        GL.glUniform1i(
            self.locations["uLightCount"],
            len(nearby),
        )

        self.upload(
            "uLightPosition[0]",
            [
                value
                for position, _, _, _ in nearby
                for value in (
                    position[0],
                    -position[1],
                    position[2],
                )
            ],
        )

        self.upload(
            "uLightColour[0]",
            [
                value
                for _, colour, _, _ in nearby
                for value in colour
            ],
        )

        self.upload(
            "uLightRadius[0]",
            [light[2] for light in nearby],
            1,
        )

        self.upload(
            "uLightPower[0]",
            [light[3] for light in nearby],
            1,
        )

        enabled = bool(
            headlights and car_pose is not None
        )

        GL.glUniform1i(
            self.locations["uHeadlights"],
            int(enabled),
        )

        GL.glUniform1i(
            self.locations["uBlockCount"],
            0,
        )

        if not enabled or car_pose is None:
            return

        x, y, z, angle = car_pose

        radians = math.radians(angle)
        sine = math.sin(radians)
        cosine = math.cos(radians)

        forward = (sine, cosine)
        right = (cosine, -sine)

        self.upload(
            "uHeadPosition[0]",
            [
                value
                for side in (-9.5, 9.5)
                for value in (
                    x + forward[0] * 28 + right[0] * side,
                    -y + forward[1] * 28 + right[1] * side,
                    z + 14,
                )
            ],
        )

        length = math.sqrt(1.0 + 0.1 ** 2)

        GL.glUniform3f(
            self.locations["uHeadDirection"],
            forward[0] / length,
            forward[1] / length,
            -0.1 / length,
        )

        candidates = []

        for (
            bx, by, width, depth, height
        ) in self.blockers:
            nearest_x = max(
                bx, min(x, bx + width)
            )

            nearest_y = max(
                by, min(y, by + depth)
            )

            distance = (
                (nearest_x - x) ** 2
                + (nearest_y - y) ** 2
            )

            if distance > 380 ** 2:
                continue

            dx = bx + width / 2 - x
            dy = by + depth / 2 - y

            along = dx * sine - dy * cosine
            across = dx * cosine + dy * sine
            radius = math.hypot(width, depth) / 2

            if (
                along + radius < 0
                or along - radius > 360
            ):
                continue

            if abs(across) > (
                max(0.0, along) * 0.45
                + radius + 25
            ):
                continue

            candidates.append(
                (
                    distance,
                    bx, by,
                    width, depth, height,
                )
            )

        chosen = sorted(candidates)[:MAX_BLOCKERS]

        GL.glUniform1i(
            self.locations["uBlockCount"],
            len(chosen),
        )

        self.upload(
            "uBlockMin[0]",
            [
                value
                for (
                    _, bx, by, width, depth, height
                ) in chosen
                for value in (
                    bx,
                    -(by + depth),
                    0.0,
                )
            ],
        )

        self.upload(
            "uBlockMax[0]",
            [
                value
                for (
                    _, bx, by, width, depth, height
                ) in chosen
                for value in (
                    bx + width,
                    -by,
                    height,
                )
            ],
        )