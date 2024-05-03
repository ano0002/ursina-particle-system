#version 140

uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

in vec3 position;
in vec4 rotation;
in vec3 scale;
in vec3 velocity;

uniform float elapsed_time;
uniform vec3 gravity;

out vec2 texcoords;

void main() {
    
    vec3 v = p3d_Vertex.xyz * scale;
    vec4 q = rotation;
    v = v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v);
    
    texcoords = p3d_MultiTexCoord0;

    vec3 adjusted_position = position+velocity*elapsed_time + 0.5*gravity*elapsed_time*elapsed_time;

    gl_Position = p3d_ModelViewProjectionMatrix * vec4(v + adjusted_position , 1.);
}