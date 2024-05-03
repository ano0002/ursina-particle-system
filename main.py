from ursina import *
from panda3d.core import Geom, GeomVertexArrayFormat, GeomVertexFormat, GeomVertexWriter, GeomTriangles, GeomVertexData
import random
from dataclasses import dataclass

window.vsync = False
app = Ursina()

particle_shader=Shader(name='particle_shader', language=Shader.GLSL, vertex=open('particle.vert', 'r').read(),
                         fragment=open('particle.frag', 'r').read())

@dataclass
class Particle:
    position: Vec3
    scale: Vec3
    velocity: Vec3
    color: Vec4

class ParticleManager(Entity):
    max_particles = 100000

    def __init__(self,gravity=Vec3(0,-9.8,0),particles=[], **kwargs):
        super().__init__(model='quad',billboard=True, shader=particle_shader)
        
        self.elapsed_time = 0
        self.gravity = gravity    
        self.particles = particles

        for key,value in kwargs.items():
            setattr(self, key, value)

        self.geom_node = self.find("**/+GeomNode").node()

        if self.geom_node.getNumGeoms() == 0:
            raise Exception("No geometry found")

        if self.geom_node.getGeom(0).getVertexData().getNumRows() == 0:
            raise Exception("No vertex data found")

        if self.geom_node.getGeom(0).getVertexData().getNumRows() > 0:
            self.iformat = GeomVertexArrayFormat()
            self.iformat.setDivisor(1)
            self.iformat.addColumn("position", 3, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn("scale", 3, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn("velocity", 3, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn("particle_color", 4, Geom.NT_stdfloat, Geom.C_vector)

            self.vformat = GeomVertexFormat(self.geom_node.getGeom(0).getVertexData().getFormat())
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
        self.elapsed_time += time.dt
        self.set_shader_input('elapsed_time', self.elapsed_time)

    def apply(self):
        to_generate = min(len(self.particles), ParticleManager.max_particles)


        self.vdata.setNumRows(to_generate)

        position_i = GeomVertexWriter(self.vdata, 'position')
        scale_i = GeomVertexWriter(self.vdata, 'scale')
        velocity_i = GeomVertexWriter(self.vdata, 'velocity')
        color_i = GeomVertexWriter(self.vdata, 'particle_color')

        for i in range(to_generate):
            particle = self.particles[i]
            position_i.add_data3(*particle.position)
            scale_i.add_data3(*particle.scale)
            velocity_i.add_data3(*particle.velocity)
            color_i.add_data4(*particle.color)

        self.set_instance_count(to_generate)

        self.set_shader_input("gravity", self.gravity)

        self.elapsed_time = 0

def generate_particle():
    return Particle(
        position = Vec3(random.random()*5-2.5,random.random()*.5,random.random()*5-2.5),
        scale = Vec3(random.random()*0.5+0.5),
        velocity = Vec3(random.random()*5-2.5,random.random()*10,random.random()*5-2.5),
        color = Vec4(random.random(),random.random(),random.random(),0)*.2+color.orange
    )

def generate_particles(n):
    return [generate_particle() for _ in range(n)]

manager = ParticleManager(texture="particle",scale=1,particles=generate_particles(10000),gravity=Vec3(0,1,0),position=Vec3(0,-3,0))

EditorCamera()

app.run()