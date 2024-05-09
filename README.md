# ursina-particle-system

## TODO
- [x] `position[vec3]`: The initial speed of the particles. The greater the speed of the particles, the more spread out they will be. 
- [x] `velocity[vec3]`: The initial speed of the particles. The greater the speed of the particles, the more spread out they will be. 

- [x] `lifetime[float]`: If Looping isn’t checked, this determines how long the Particle will play. 
- [x] `delay[float]`: The delay in seconds before the particle system starts emitting.

- [x] `init_scale[vec2]`: The initial size of the particles.
- [x] `end_scale[vec2]`: The size the particles will fade to. 

- [x] `init_color[vec4]`: The initial color of the particles.
- [x] `end_color[vec4]`: The color the particles will fade to.

- [x] `Looping(bool)`: Determines if the Particle loops or plays only once. 
- [x] `gravity(vec3)`: The force of gravity on the particles.
- [x] `simulation_speed(float)`: Affects the speed of the simulation of the particles. 
- [x] `max_particles(int)`: The upper limit of how many particles can be alive at a once for the given Particle System. It will not emit any more particles after the limit has been reached. 
- [x] `culling(bool)`: Choose whether to render when the particle system origin is offscreen.