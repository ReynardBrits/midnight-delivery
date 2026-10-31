"""Show a translucent car silhouette through objects blocking the camera."""

import math

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from renderer3d import VERTEX_SHADER


SILHOUETTE_SHADER = """
#version 330 core

uniform vec4 uTint;
out vec4 fragmentColour;

void main()
{
    fragmentColour = uTint;
}
"""


class CarVisibility:
    """Call after drawing the town and before drawing the normal car."""

    def __init__(self, enabled=True):
        self.enabled = enabled

        self.program = compileProgram(
            compileShader(
                VERTEX_SHADER,
                GL.GL_VERTEX_SHADER,
            ),
            compileShader(
                SILHOUETTE_SHADER,
                GL.GL_FRAGMENT_SHADER,
            ),
        )

        self.locations = {
            name: GL.glGetUniformLocation(
                self.program, name
            )
            for name in (
                "uViewProjection",
                "uOffset",
                "uAngle",
                "uTint",
            )
        }

    def draw(
        self, camera, mesh, scene_program,
        x, y, z, angle,
    ):
        if not self.enabled:
            return

        matrix, _ = camera.view_projection()

        GL.glUseProgram(self.program)

        GL.glUniformMatrix4fv(
            self.locations["uViewProjection"],
            1,
            GL.GL_FALSE,
            matrix,
        )

        GL.glUniform3f(
            self.locations["uOffset"],
            x, y, z,
        )

        GL.glUniform1f(
            self.locations["uAngle"],
            math.radians(angle),
        )

        GL.glUniform4f(
            self.locations["uTint"],
            0.16, 0.88, 0.78, 0.48,
        )

        try:
            GL.glBindVertexArray(mesh.vao)

            GL.glEnable(GL.GL_STENCIL_TEST)
            GL.glStencilMask(0xFF)
            GL.glClearStencil(0)

            GL.glClear(
                int(GL.GL_STENCIL_BUFFER_BIT)
            )

            # Mark car fragments behind the town's depth buffer.
            # Preserve scene depth for the normal car draw.
            GL.glDepthMask(GL.GL_FALSE)
            GL.glColorMask(False, False, False, False)

            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glDepthFunc(GL.GL_GREATER)

            GL.glStencilFunc(
                GL.GL_ALWAYS, 1, 0xFF
            )

            GL.glStencilOp(
                GL.GL_KEEP,
                GL.GL_KEEP,
                GL.GL_REPLACE,
            )

            GL.glDrawArrays(
                GL.GL_TRIANGLES, 0, mesh.count
            )

            # Fill each marked pixel once, preventing overlapping
            # car parts from building up opacity.
            GL.glColorMask(True, True, True, True)
            GL.glDisable(GL.GL_DEPTH_TEST)

            GL.glStencilFunc(
                GL.GL_EQUAL, 1, 0xFF
            )

            GL.glStencilOp(
                GL.GL_KEEP,
                GL.GL_KEEP,
                GL.GL_ZERO,
            )

            GL.glDrawArrays(
                GL.GL_TRIANGLES, 0, mesh.count
            )

        finally:
            GL.glColorMask(True, True, True, True)
            GL.glDepthMask(GL.GL_TRUE)
            GL.glDepthFunc(GL.GL_LEQUAL)
            GL.glEnable(GL.GL_DEPTH_TEST)

            GL.glDisable(GL.GL_STENCIL_TEST)
            GL.glStencilMask(0xFF)

            GL.glStencilFunc(
                GL.GL_ALWAYS, 0, 0xFF
            )

            GL.glStencilOp(
                GL.GL_KEEP,
                GL.GL_KEEP,
                GL.GL_KEEP,
            )

            GL.glBindVertexArray(0)
            GL.glUseProgram(scene_program)

    def close(self):
        GL.glDeleteProgram(self.program)