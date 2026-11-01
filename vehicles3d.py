"""Cached vehicle meshes, cargo visuals and safe traffic activation."""

import math

from car import overlaps_building
from renderer3d import Mesh3D, MeshBuilder
from traffic import COLOURS, Traffic, rectangles_overlap


AMBER = (0.96, 0.57, 0.14, 1.0)
TEAL = (0.12, 0.76, 0.70, 1.0)
GLASS = (0.055, 0.13, 0.20, 1.0)
RUBBER = (0.035, 0.045, 0.06, 1.0)
METAL = (0.42, 0.50, 0.58, 1.0)

CARGO_KEYS = (
    ("STANDARD", 0),
    ("EXPRESS", 0),
    ("FRAGILE", 0),
    ("FRAGILE", 1),
    ("FRAGILE", 2),
)


def narrow(builder):
    """Fit NPC geometry to its existing collision width."""
    vertices = builder.vertices

    for index in range(0, len(vertices), 11):
        vertices[index] *= 0.9

        nx = vertices[index + 3] / 0.9
        ny = vertices[index + 4]
        nz = vertices[index + 5]
        length = math.sqrt(nx * nx + ny * ny + nz * nz)

        vertices[index + 3] = nx / length
        vertices[index + 4] = ny / length
        vertices[index + 5] = nz / length

    return builder


def body(colour=AMBER, courier=True, shadow=True):
    b = MeshBuilder()

    if shadow:
        b.plane(
            -24, -29, 0.2, 48, 62,
            (0.01, 0.015, 0.025, 0.4), 1.0,
        )

    for x in (-20, 14):
        for y in (-16, 17):
            b.wheel(x, y, 8, 8, 6, RUBBER)

            hub = x - 0.1 if x < 0 else x + 5.8
            b.wheel(hub, y, 8, 4, 0.3, METAL)

    b.loft(-16, -27, 9, 32, 54, 10, 1, 1, colour)
    b.box(-16, -27, 9, 32, 2, 4, RUBBER)
    b.box(-16, 25, 9, 32, 2, 4, RUBBER)
    b.loft(-14, -10, 19, 28, 29, 14, 3, 6, colour)

    b.quad(
        (
            (-12, -9.7, 20), (12, -9.7, 20),
            (10, -5, 31), (-10, -5, 31),
        ),
        GLASS,
    )

    b.quad(
        (
            (12, 18.7, 20), (-12, 18.7, 20),
            (-10, 14, 31), (10, 14, 31),
        ),
        GLASS,
    )

    for sign in (-1, 1):
        points = (
            (sign * 13.94, -8, 20),
            (sign * 13.94, 16, 20),
            (sign * 11.58, 11, 31),
            (sign * 11.58, -3, 31),
        )

        b.quad(
            points if sign > 0 else points[::-1],
            GLASS,
        )

        b.box(sign * 14 - 1, 7, 20, 2, 7, 2, METAL)
        b.box(sign * 18 - 2, -6, 20, 4, 5, 3, colour)

    if courier:
        b.box(-2, -25, 19.05, 4, 14, 0.3, TEAL)
        b.box(-11, -4, 33, 22, 18, 1.5, RUBBER)

        for x in (-11, 9):
            b.box(x, -4, 34.5, 2, 18, 1.5, METAL)

    return b if courier else narrow(b)


def lights(headlights, braking, reversing, npc=False):
    b = MeshBuilder()

    front = (
        (1.0, 0.91, 0.67, 1.0)
        if headlights
        else (0.15, 0.18, 0.22, 1.0)
    )

    rear = (
        (1.0, 0.16, 0.08, 1.0)
        if braking
        else (0.48, 0.055, 0.06, 1.0)
        if headlights
        else (0.14, 0.03, 0.04, 1.0)
    )

    glow = (
        1.0 if braking
        else 0.45 if headlights
        else 0.0
    )

    for x in (-12, 7):
        b.box(
            x, -27.3, 13, 5, 1.4, 3,
            front, float(headlights),
        )

        b.box(
            x, 26.1, 13, 5, 1.2, 3,
            rear, glow,
        )

    reverse = (
        (0.95, 0.98, 1.0, 1.0)
        if reversing
        else RUBBER
    )

    for x in (-5, 3):
        b.box(
            x, 26.1, 12, 2, 1.25, 2,
            reverse, 0.9 if reversing else 0.0,
        )

    return narrow(b) if npc else b


def parcel(kind, grade):
    b = MeshBuilder()

    height = 7 if grade == 2 else 10
    top = 35 + height

    cardboard = (
        (0.56, 0.36, 0.21, 1.0)
        if grade == 2
        else (0.72, 0.47, 0.25, 1.0)
    )

    label = {
        "STANDARD": TEAL,
        "EXPRESS": AMBER,
        "FRAGILE": (0.73, 0.60, 1.0, 1.0),
    }[kind]

    b.loft(
        -8, -2, 35,
        16, 14, height,
        grade, grade * 0.5,
        cardboard,
    )

    b.box(
        -1, -2, top + 0.05,
        2, 14, 0.2,
        (0.96, 0.82, 0.57, 1.0),
    )

    b.box(
        -7 + grade, 3, top + 0.1,
        14 - grade * 2, 4, 0.2,
        label,
    )

    if kind == "EXPRESS":
        for x in (-4, 3):
            b.plane(
                x, 0, top + 0.35,
                2, 9, RUBBER, 0.3,
            )

    elif kind == "FRAGILE":
        for x in (-4, 3):
            b.plane(
                x, 0, top + 0.35,
                1.3, 7, RUBBER, 0.3,
            )

    if grade:
        b.plane(2, 1, top + 0.4, 4, 2, RUBBER, 0.3)
        b.plane(1, 4, top + 0.4, 3, 1, RUBBER, 0.3)

    if grade == 2:
        b.plane(-6, 7, top + 0.4, 6, 2, RUBBER, 0.3)

    return b


def cargo_key(delivery):
    if delivery.state != "dropoff":
        return None

    kind = delivery.contract.kind
    grade = 0

    if kind == "FRAGILE":
        grade = (
            2 if delivery.cargo_condition <= 35
            else 1 if delivery.cargo_condition < 70
            else 0
        )

    return kind, grade


def interpolated_pose(vehicle, alpha):
    turn = (
        vehicle.angle - vehicle.previous_angle + 180
    ) % 360 - 180

    return (
        vehicle.previous_x
        + (vehicle.x - vehicle.previous_x) * alpha,
        vehicle.previous_y
        + (vehicle.y - vehicle.previous_y) * alpha,
        0.3,
        vehicle.previous_angle + turn * alpha,
    )


class Traffic3D(Traffic):
    def set_shift(self, shift_number, car=None):
        """Activate new vehicles in clear lane positions."""
        wanted = max(2, min(6, shift_number * 2))
        self.active_count = min(self.active_count, wanted)
        placed = self.active_vehicles

        for vehicle in self.vehicles[self.active_count:wanted]:
            for offset in range(
                0, int(vehicle.route.length), 64
            ):
                distance = (
                    vehicle.phase * vehicle.route.length + offset
                ) % vehicle.route.length

                pose = vehicle.route.sample(distance)

                bounds = vehicle.bounds_at(
                    *pose, padding=16
                )

                if car is not None and overlaps_building(
                    car.x, car.y, car.angle,
                    car.HALF_WIDTH, car.HALF_HEIGHT,
                    bounds,
                ):
                    continue

                if any(
                    rectangles_overlap(bounds, other.bounds)
                    for other in placed
                ):
                    continue

                vehicle.distance = distance
                vehicle.x, vehicle.y, vehicle.angle = pose
                vehicle.waiting = False
                vehicle.sync_render_state()

                placed.append(vehicle)
                self.active_count += 1
                break

            else:
                break


class VehicleModels:
    def __init__(self):
        self.meshes = []

        def upload(builder):
            mesh = Mesh3D(builder)
            self.meshes.append(mesh)
            return mesh

        self.player = upload(body())

        self.npcs = [
            upload(body(colour, courier=False))
            for colour in COLOURS
        ]

        self.lamps = {
            (headlights, braking, reversing): upload(
                lights(headlights, braking, reversing)
            )
            for headlights in (False, True)
            for braking in (False, True)
            for reversing in (False, True)
        }

        self.npc_lamps = {
            braking: upload(
                lights(True, braking, False, npc=True)
            )
            for braking in (False, True)
        }

        self.parcels = {
            key: upload(parcel(*key))
            for key in CARGO_KEYS
        }

        self.silhouettes: dict[
            tuple[str, int] | None, Mesh3D
        ] = {}

        for key in (None, *CARGO_KEYS):
            builder = body(shadow=False)

            builder.vertices.extend(
                lights(False, False, False).vertices
            )

            if key is not None:
                builder.vertices.extend(
                    parcel(*key).vertices
                )

            self.silhouettes[key] = upload(builder)

    def draw_player(
        self, renderer, car,
        delivery, pose, headlights,
    ):
        renderer.draw(self.player, *pose)

        renderer.draw(
            self.lamps[
                (headlights, car.braking, car.speed < -1)
            ],
            *pose,
        )

        key = cargo_key(delivery)

        if key is not None:
            renderer.draw(self.parcels[key], *pose)

    def draw_traffic(self, renderer, traffic, poses):
        for index, (vehicle, pose) in enumerate(
            zip(traffic.active_vehicles, poses)
        ):
            renderer.draw(self.npcs[index], *pose)

            renderer.draw(
                self.npc_lamps[vehicle.waiting],
                *pose,
            )

    def close(self):
        for mesh in reversed(self.meshes):
            mesh.close()

        self.meshes.clear()