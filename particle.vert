#version 140

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

in vec3 position;
in vec3 velocity;
in float lifetime;
in float delay;
in vec2 init_scale;
in vec2 end_scale;
in vec4 init_color;
in vec4 end_color;

uniform float elapsed_time;
uniform vec3 gravity;
uniform bool looping;

flat out int discard_frag;
out vec2 texcoord;
out vec4 new_color;

void main() {

    float adjusted_time = elapsed_time - delay;
    float life = adjusted_time / lifetime;

    if (life > 1.0) {
        if (looping) {
            life = fract(life);
            adjusted_time = mod(adjusted_time, lifetime);
        } else {
            discard_frag = 1;
            return;
        }
    }
    else if (life < 0.0){
        discard_frag = 1;
        return;
    }
    discard_frag = 0;

    vec3 new_scale = vec3(mix(init_scale, end_scale, life), 1.0);

    vec3 v = p3d_Vertex.xyz * new_scale;
    
    texcoord = p3d_MultiTexCoord0;

    new_color = mix(init_color, end_color, life);

    vec3 adjusted_position = position+velocity*adjusted_time + 0.5*gravity*adjusted_time*adjusted_time;

    gl_Position = p3d_ModelViewProjectionMatrix * vec4(v + adjusted_position, 1.0);
}