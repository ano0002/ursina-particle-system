from multiprocessing import parent_process
from ursina import *
from panda3d.core import (
    Geom,
    GeomVertexArrayFormat,
    GeomVertexFormat,
    GeomVertexWriter,
    OmniBoundingVolume
)
import random
from dataclasses import dataclass
from typing import List


window.vsync = False
app = Ursina()

particle_shader = Shader(
                name=f"particle_shader",
                language=Shader.GLSL,
                vertex=open("particle.vert", "r").read(),
                fragment=open("particle.frag", "r").read(),
            )

@dataclass
class Particle:
    position: Vec3
    velocity: Vec3

    lifetime: float
    delay: float

    init_scale: Vec2
    end_scale: Vec2

    init_color: Vec4
    end_color: Vec4


class ParticleManager(Entity):
    max_particles = 1_000_000
    i = 0
    
    def __init__(
        self,
        looping=False,
        simulation_speed=1,
        gravity=Vec3(0, -9.8, 0),
        particles=[],
        **kwargs,
    ):
        """Creates a new ParticleManager

        Args:
            looping (bool, optional): If the particles should loop. Defaults to False.
            simulation_speed (int, optional): The speed of the simulation. Defaults to 1.
            gravity (Vec3, optional): The gravity which will affect every particle in this manager. Defaults to Vec3(0,-9.8,0).
            particles (List[Particle], optional): Every starting particles. Defaults to [].
        """
        self.instance = ParticleManager.i
        super().__init__(
            model=Quad(segments=0),
            billboard=True,
            shader=particle_shader,
        )
        ParticleManager.i += 1
        self._bsphere = self.node().getBounds()
        self.elapsed_time = 0
        self.looping = looping
        self.simulation_speed = simulation_speed
        self.gravity = gravity
        self.particles = particles
        
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.geom_node = self.find("**/+GeomNode").node()

        if self.geom_node.getNumGeoms() == 0:
            raise Exception("No geometry found")

        if self.geom_node.getGeom(0).getVertexData().getNumRows() == 0:
            raise Exception("No vertex data found")

        if self.geom_node.getGeom(0).getVertexData().getNumRows() > 0:
            self.iformat = GeomVertexArrayFormat()
            self.iformat.setDivisor(1)
            self.iformat.addColumn(f"position", 3, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn(f"velocity", 3, Geom.NT_stdfloat, Geom.C_vector)

            self.iformat.addColumn(f"lifetime", 1, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn(f"delay", 1, Geom.NT_stdfloat, Geom.C_vector)

            self.iformat.addColumn(f"init_scale", 2, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn(f"end_scale", 2, Geom.NT_stdfloat, Geom.C_vector)

            self.iformat.addColumn(f"init_color", 4, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn(f"end_color", 4, Geom.NT_stdfloat, Geom.C_vector)

            self.vformat = GeomVertexFormat(
                self.geom_node.getGeom(0).getVertexData().getFormat()
            )
            self.vformat.addArray(self.iformat)
            self.vformat = GeomVertexFormat.registerFormat(self.vformat)

            self.vdata = self.geom_node.modifyGeom(0).modifyVertexData()
            self.vdata.setFormat(self.vformat)

            if self.vdata.getFormat() != self.vformat:
                raise Exception("Vertex data format mismatch")

            self.apply()
        else:
            raise Exception("No vertex data found")

    def update(self):
        self.elapsed_time += time.dt * self.simulation_speed
        self.set_shader_input("elapsed_time", self.elapsed_time)
        #print(mouse_emitter.world_position)

    def apply(self):
        to_generate = min(len(self.particles), ParticleManager.max_particles)

        self.vdata.setNumRows(to_generate)

        position_i = GeomVertexWriter(self.vdata, f"position")
        velocity_i = GeomVertexWriter(self.vdata, f"velocity")

        lifetime_i = GeomVertexWriter(self.vdata, f"lifetime")
        delay_i = GeomVertexWriter(self.vdata, f"delay")

        init_scale_i = GeomVertexWriter(self.vdata, f"init_scale")
        end_scale_i = GeomVertexWriter(self.vdata, f"end_scale")

        init_color_i = GeomVertexWriter(self.vdata, f"init_color")
        end_color_i = GeomVertexWriter(self.vdata, f"end_color")

        for i in range(to_generate):
            particle = self.particles[i]
            position_i.add_data3(*particle.position)
            velocity_i.add_data3(*particle.velocity)

            lifetime_i.add_data1(particle.lifetime)
            delay_i.add_data1(particle.delay)

            init_scale_i.add_data2(*particle.init_scale)
            end_scale_i.add_data2(*particle.end_scale)

            init_color_i.add_data4(*particle.init_color)
            end_color_i.add_data4(*particle.end_color)

        self.set_instance_count(to_generate)

        self.elapsed_time = 0

    @property
    def culling(self):
        return self._culling

    @culling.setter
    def culling(self, value: bool):
        if not value:
            self.node().setBounds(OmniBoundingVolume())
            self.node().setFinal(True)
            self._culling = False
        else:
            self.node().setBounds(self._bsphere)
            self.node().setFinal(False)
            self._culling = True

    @property
    def particles(self):
        return self._particles

    @particles.setter
    def particles(self, value: List[Particle]):
        self._particles = value
        self.apply()

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value: Vec3):
        self._gravity = value
        self.set_shader_input("gravity", value)

    @property
    def simulation_speed(self):
        return self._simulation_speed

    @simulation_speed.setter
    def simulation_speed(self, value: float):
        self._simulation_speed = value

    @property
    def looping(self):
        return self._looping

    @looping.setter
    def looping(self, value: bool):
        self._looping = value
        self.set_shader_input("looping", value)


def generate_particle():
    return Particle(
        position=Vec3(
            random.random() * 5 - 2.5, random.random() * 0.5, random.random() * 5 - 2.5
        ),
        velocity=Vec3(
            random.random() * 3 - 1.5,
            random.random() * 3 + 2,
            random.random() * 3 - 1.5,
        ),
        lifetime=random.random() * 5 + 3,
        delay=random.random() * 4,
        init_scale=Vec2(random.random() * 0.5),
        end_scale=Vec2(random.random() * 0.2),
        init_color=Vec4(random.random(), random.random(), random.random(), 0) * 0.2
        + color.orange,
        end_color=Vec4(Vec3(random.random()), 1),
    )


def generate_particles(n):
    return [generate_particle() for _ in range(n)]


def generate_mouse_particle():
    return Particle(
        position=Vec3(random.random(), random.random(), 0) * 0.01,
        velocity=Vec3(
            random.random() * 3 - 1.5,
            random.random() * 3 - 1.5,
            random.random() * 3 - 1.5,
        )
        / 2,
        lifetime=random.random() * 0.2,
        delay=random.random() * 0.05,
        init_scale=Vec2(random.random() * 0.005),
        end_scale=Vec2(random.random() * 0.02),
        init_color=color.white,
        end_color=color.random_color() * Vec4(Vec3(1), 0),
    )


def generate_mouse_particles(n):
    return [generate_mouse_particle() for _ in range(n)]




manager = ParticleManager(
    texture="particle",
    scale=1,
    particles=generate_particles(100_000),
    gravity=Vec3(0, 1, 0),
    position=Vec3(0, -3, 0),
    looping=True,
    culling=False,
)


mouse_emitter = ParticleManager(
    particles=generate_mouse_particles(100),
    scale=10,
    gravity=Vec3(0, 0, 0),
    position=mouse.position,
    looping=False,
    culling=False
)

def input(key):
    if key == "-":
        manager.simulation_speed -= 0.1
    if key == "+":
        manager.simulation_speed += 0.1
    if key == "k":
        camera.orthographic = not camera.orthographic
    if key == "space":
        mouse_emitter.position = mouse.position * camera.fov/4
        mouse_emitter.elapsed_time = 0



EditorCamera()

app.run()