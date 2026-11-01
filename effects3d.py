"""Floating delivery beacon and batched low-poly particles."""

from dataclasses import dataclass
import math
import random

from OpenGL import GL
from renderer3d import Mesh3D, MeshBuilder


TEAL = (0.12, 0.76, 0.70, 1.0)
GOLD = (1.0, 0.69, 0.25, 1.0)


@dataclass
class Particle:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    life: float
    size: float
    colour: tuple
    age: float = 0.0


class Effects:
    LIMIT = 48

    def __init__(self, car, delivery):
        self.rng = random.Random(91)
        self.beacons = {}

        builder = MeshBuilder()
        builder.box(0, 0, 0, 1, 1, 1, TEAL)

        self.batch = Mesh3D(builder)
        self.batch.count = 0
        self.reset(car, delivery)

    def reset(self, car, delivery):
        self.particles: list[Particle] = []
        self.elapsed = 0.0
        self.condition = car.condition
        self.completed = delivery.completed_count
        self.state = delivery.state
        self.batch.count = 0

    def burst(self, x, y, z, colours, count):
        for _ in range(count):
            angle = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(20, 65)

            self.particles.append(
                Particle(
                    x, y, z,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    self.rng.uniform(45, 105),
                    self.rng.uniform(0.6, 1.1),
                    self.rng.uniform(1.0, 2.1),
                    self.rng.choice(colours),
                )
            )

        self.particles = self.particles[-self.LIMIT:]

    def observe(self, car, delivery):
        if car.condition < self.condition:
            self.burst(
                car.x, car.y, 10,
                (GOLD, (0.55, 0.61, 0.65, 1.0)),
                14,
            )

        if delivery.completed_count > self.completed:
            self.burst(
                car.x, car.y, 22,
                (TEAL, GOLD), 24,
            )

        elif (
            delivery.state == "dropoff"
            and self.state != "dropoff"
        ):
            self.burst(
                car.x, car.y, 30,
                (TEAL,), 10,
            )

        self.condition = car.condition
        self.completed = delivery.completed_count
        self.state = delivery.state

    def update(self, dt):
        self.elapsed += dt
        alive = []

        for particle in self.particles:
            particle.age += dt
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt

            particle.z += (
                particle.vz * dt - 85 * dt * dt
            )

            particle.vz -= 170 * dt

            if (
                particle.age < particle.life
                and particle.z > 0.5
            ):
                alive.append(particle)

        self.particles = alive

    def beacon(self, colour):
        if colour not in self.beacons:
            crate = MeshBuilder()
            beam = MeshBuilder()

            crate.box(
                -7, -6, 0, 14, 12, 12,
                (0.72, 0.47, 0.25, 1.0), 0.4,
            )

            crate.box(
                -1, -6.05, 0.05,
                2, 12.1, 12.15,
                colour, 1.0,
            )

            crate.box(
                -7.05, -1, 0.1,
                14.1, 2, 12.1,
                colour, 1.0,
            )

            tint = colour[:3] + (0.10,)

            beam.quad(
                (
                    (-3, 0, 0), (3, 0, 0),
                    (3, 0, 48), (-3, 0, 48),
                ),
                tint, 1.0,
            )

            beam.quad(
                (
                    (0, -3, 0), (0, 3, 0),
                    (0, 3, 48), (0, -3, 48),
                ),
                tint, 1.0,
            )

            self.beacons[colour] = (
                Mesh3D(crate), Mesh3D(beam)
            )

        return self.beacons[colour]

    def draw(self, renderer, camera, delivery):
        GL.glDepthMask(GL.GL_FALSE)

        try:
            if delivery.zone is not None:
                x, y, width, height = delivery.zone
                x += width / 2
                y += height / 2

                crate, beam = self.beacon(
                    delivery.marker_colour
                )

                renderer.draw(beam, x, y, 0.35)

                renderer.draw(
                    crate, x, y,
                    45 + math.sin(self.elapsed * 2) * 4,
                    self.elapsed * 35 % 360,
                )

            if not self.particles:
                return

            _, eye = camera.view_projection()

            ordered = sorted(
                self.particles,
                key=lambda p: (
                    (p.x - eye[0]) ** 2
                    + (-p.y - eye[1]) ** 2
                    + (p.z - eye[2]) ** 2
                ),
                reverse=True,
            )

            builder = MeshBuilder()

            for particle in ordered:
                remaining = (
                    1 - particle.age / particle.life
                )

                size = (
                    particle.size
                    * (0.35 + 0.65 * remaining)
                )

                tint = (
                    particle.colour[:3]
                    + (remaining * 0.9,)
                )

                builder.box(
                    particle.x - size,
                    particle.y - size,
                    particle.z - size,
                    size * 2,
                    size * 2,
                    size * 2,
                    tint,
                    1.0,
                )

            pixels = builder.vertices.tobytes()
            self.batch.count = len(builder.vertices) // 11

            GL.glBindBuffer(
                GL.GL_ARRAY_BUFFER,
                self.batch.vbo,
            )

            GL.glBufferData(
                GL.GL_ARRAY_BUFFER,
                len(pixels),
                pixels,
                GL.GL_STREAM_DRAW,
            )

            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
            renderer.draw(self.batch)

        finally:
            GL.glDepthMask(GL.GL_TRUE)

    def close(self):
        self.batch.close()

        for crate, beam in self.beacons.values():
            crate.close()
            beam.close()

        self.beacons.clear()