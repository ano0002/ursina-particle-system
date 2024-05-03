
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
out vec4 fragColor;

void main() {
    fragColor = texture(p3d_Texture0, texcoord) * p3d_ColorScale;
}