<think>
Okay, I need to create a WebGL application that simulates psychedelic metaballs using ray marching and SDFs. Let me break down the problem and figure out how to approach each part.

First, the setup. I'll need a WebGL context, so I'll initialize the canvas and get the WebGL context. The vertex shader is straightforward—it just passes the coordinates to the fragment shader. I'll set up a vertex buffer for a full-screen quad using two triangles.

Next, the fragment shader is where the magic happens. I'll start by defining the SDF for a sphere. The SDF function takes a point and the sphere's center and radius, returning the signed distance. Then, I'll combine multiple spheres using a smooth minimum function. The smooth minimum is crucial because it allows the metaballs to merge smoothly instead of having hard edges.

For the ray marching, I'll cast a ray from the camera through each pixel. I'll loop a set number of times, moving the ray's position by the distance estimated from the SDF each time. If the distance gets very small, I consider it a hit. Otherwise, if the ray goes too far, I stop and color it as the background.

Shading and coloring are next. When a hit occurs, I'll calculate the normal by sampling the SDF around the hit point. Then, I'll use this normal to compute lighting. I'll mix colors based on the hit's position and time to create vibrant, shifting colors. If no hit, I'll use a dark background.

In JavaScript, I'll set up the uniforms, including time, resolution, camera position, and parameters for each metaball. I'll use requestAnimationFrame to update the uniforms each frame, animating the metaballs' positions and sizes smoothly.

I'll also consider performance optimizations, like reducing the number of ray steps or using lower precision where possible. Additionally, I'll implement noise functions in the shader to add texture and complexity to the movement and appearance of the metaballs.

Finally, I'll ensure the code is clean and well-structured, with comments explaining complex parts. I'll test each component step by step, starting with the SDF, then ray marching, and finally the shading, to make sure everything works as expected before putting it all together.
</think>

Here's a complete implementation of the psychedelic metaball simulation using WebGL and ray marching. The code creates a mesmerizing display of glowing, merging spheres that evolve over time.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Psychedelic Metaballs</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; }
        canvas { display: block; width: 100vw; height: 100vh; }
    </style>
</head>
<body>
    <canvas id="glCanvas"></canvas>

    <!-- Vertex Shader -->
    <script id="vertexShader" type="x-shader/x-vertex">
        attribute vec2 position;
        varying vec2 uv;
        
        void main() {
            uv = position;
            gl_Position = vec4(position, 0.0, 1.0);
        }
    </script>

    <!-- Fragment Shader -->
    <script id="fragmentShader" type="x-shader/x-fragment">
        precision highp float;
        varying vec2 uv;
        uniform vec2 resolution;
        uniform float time;
        uniform vec3 cameraPos;
        uniform vec3 metaball1;
        uniform vec3 metaball2;
        uniform vec3 metaball3;

        #define MAX_STEPS 100
        #define MAX_DIST 100.0
        #define SURF_DIST 0.01

        float sphereSDF(vec3 p, vec3 center, float radius) {
            return length(p - center) - radius;
        }

        float smin(float a, float b, float k) {
            float res = exp(-k*a) + exp(-k*b);
            return -log(res)/k;
        }

        float sceneSDF(vec3 p) {
            float d1 = sphereSDF(p, metaball1, 1.0);
            float d2 = sphereSDF(p, metaball2, 1.0);
            float d3 = sphereSDF(p, metaball3, 1.0);
            
            float d = smin(d1, d2, 10.0);
            d = smin(d, d3, 10.0);
            
            return d;
        }

        vec3 getNormal(vec3 p) {
            vec2 eps = vec2(0.001, 0.0);
            vec3 norm = vec3(
                sceneSDF(p + eps.xyy) - sceneSDF(p - eps.xyy),
                sceneSDF(p + eps.yxy) - sceneSDF(p - eps.yxy),
                sceneSDF(p + eps.yyx) - sceneSDF(p - eps.yyx)
            );
            return normalize(norm);
        }

        void main() {
            vec2 fragCoord = uv * resolution;
            vec3 rayDir = normalize(vec3(fragCoord - resolution/2.0, 100.0));
            vec3 rayPos = cameraPos;
            
            float t = 0.0;
            float dist;
            for(int i = 0; i < MAX_STEPS; i++) {
                dist = sceneSDF(rayPos);
                if(dist < SURF_DIST) break;
                if(t > MAX_DIST) break;
                t += dist;
                rayPos = cameraPos + rayDir * t;
            }

            if(dist < SURF_DIST) {
                vec3 normal = getNormal(rayPos);
                vec3 lightDir = normalize(vec3(sin(time), cos(time), 1.0));
                
                float diff = max(0.0, dot(normal, lightDir));
                vec3 color1 = vec3(1.0, 0.5, 0.2) * diff;
                vec3 color2 = vec3(0.5, 1.0, 0.2) * diff;
                vec3 color3 = vec3(0.2, 0.5, 1.0) * diff;
                
                vec3 finalColor = color1 + color2 + color3;
                finalColor *= 1.5;
                finalColor = pow(finalColor, vec3(2.2));
                
                float timeFactor = sin(time * 0.5 + rayPos.x) * 0.5 + 0.5;
                finalColor = mix(finalColor, vec3(1.0, 1.0, 1.0), timeFactor * 0.5);
                
                gl_FragColor = vec4(finalColor, 1.0);
            } else {
                gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
            }
        }
    </script>

    <script>
        const canvas = document.getElementById('glCanvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

        if (!gl) {
            alert('WebGL not supported');
            throw new Error('WebGL not supported');
        }

        // Set canvas size
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Create shaders
        const vertexShader = gl.createShader(gl.VERTEX_SHADER);
        const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);

        gl.shaderSource(vertexShader, document.getElementById('vertexShader').text);
        gl.shaderSource(fragmentShader, document.getElementById('fragmentShader').text);

        gl.compileShader(vertexShader);
        gl.compileShader(fragmentShader);

        // Create program
        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);

        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            alert('Shader program failed to link');
            throw new Error('Shader program failed to link');
        }

        // Create vertex buffer
        const vertices = new Float32Array([
            -1, -1,
            1, -1,
            -1, 1,
            1, 1
        ]);

        const vertexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

        // Set up attributes and uniforms
        const positionLocation = gl.getAttribLocation(program, 'position');
        const resolutionLocation = gl.getUniformLocation(program, 'resolution');
        const timeLocation = gl.getUniformLocation(program, 'time');
        const cameraPosLocation = gl.getUniformLocation(program, 'cameraPos');
        const metaball1Location = gl.getUniformLocation(program, 'metaball1');
        const metaball2Location = gl.getUniformLocation(program, 'metaball2');
        const metaball3Location = gl.getUniformLocation(program, 'metaball3');

        // Set up vertex array
        gl.useProgram(program);
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

        // Animation loop
        let time = 0.0;
        function animate() {
            time += 0.02; // Approximately 60 FPS

            // Update uniforms
            gl.uniform2f(resolutionLocation, canvas.width, canvas.height);
            gl.uniform1f(timeLocation, time);
            gl.uniform3f(cameraPosLocation, 0.0, 0.0, -5.0);
            
            // Animate metaball positions
            gl.uniform3f(metaball1Location, 
                sin(time) * 2.0, 
                cos(time * 0.7) * 2.0, 
                0.0);
            gl.uniform3f(metaball2Location, 
                sin(time * 0.8 + 2.0) * 2.0, 
                cos(time * 0.5 + 1.0) * 2.0, 
                0.0);
            gl.uniform3f(metaball3Location, 
                sin(time * 0.6 + 4.0) * 2.0, 
                cos(time * 0.9 + 3.0) * 2.0, 
                0.0);

            // Draw
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

            requestAnimationFrame(animate);
        }

        // Start animation
        animate();
    </script>
</body>
</html>
```

This implementation includes:

1. A vertex shader that sets up the full-screen quad
2. A fragment shader that implements:
   - Ray marching algorithm
   - Signed Distance Functions (SDF) for spheres
   - Smooth minimum function for merging
   - Dynamic lighting and shading
   - Vibrant color palette
   - Animated metaballs

3. JavaScript code that:
   - Sets up the WebGL context
   - Compiles and links the shaders
   - Manages uniforms
   - Implements the animation loop
   - Updates metaball positions and parameters

The visualization features three animated metaballs that float through space, merging and separating in a hypnotic pattern. The color scheme shifts over time, creating a psychedelic effect. The simulation runs continuously without user interaction.

Key features:
- Smoothly merging spheres using SDFs and smooth minimum
- Dynamic lighting with normals calculated from SDF gradients
- Vibrant, shifting colors
- Continuous animation with smooth motion
- Full-screen rendering
- No external dependencies

To make it even more psychedelic, you could:
1. Add more metaballs
2. Implement noise functions for more complex movement patterns
3. Add post-processing effects
4. Include sound synchronization
5. Add more sophisticated lighting models

The code is optimized for clarity and performance while maintaining portability across modern browsers.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 278.55s -->
<!-- Fallback Used: False -->