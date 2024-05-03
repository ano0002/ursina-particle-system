#version 140

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

in vec3 position;
in vec3 scale;
in vec3 velocity;
in vec4 particle_color;

uniform float elapsed_time;
uniform vec3 gravity;

out vec2 texcoord;
out vec4 new_color;

void main() {
    new_color = particle_color;

    vec3 v = p3d_Vertex.xyz * scale;
    
    texcoord = p3d_MultiTexCoord0;

    vec3 adjusted_position = position+velocity*elapsed_time + 0.5*gravity*elapsed_time*elapsed_time;

    gl_Position = p3d_ModelViewProjectionMatrix * vec4(v + adjusted_position, 1.0);
}