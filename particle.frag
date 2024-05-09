#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
flat in int discard_frag;
in vec4 new_color;
out vec4 fragColor;


void main() {
    if (discard_frag == 1) {
        discard;
    }
    fragColor = texture(p3d_Texture0, texcoord) * p3d_ColorScale * new_color;
}