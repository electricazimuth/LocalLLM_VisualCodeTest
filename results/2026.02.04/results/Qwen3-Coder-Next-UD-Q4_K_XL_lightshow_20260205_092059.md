Here is a complete, single-file solution. It includes the WebGL setup, the vertex shader for the full-screen quad, and a complex fragment shader that implements ray marching, Signed Distance Functions with smooth blending, and psychedelic procedural coloring.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Psychedelic Ray Marching Metaballs</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; }
        canvas { display: block; width: 100vw; height: 100vh; }
        #ui {
            position: absolute; top: 10px; left: 10px; color: #aaa;
            font-family: monospace; font-size: 12px; pointer-events: none;
            background: rgba(0,0,0,0.5); padding: 5px; border-radius: 4px;
        }
    </style>
</head>
<body>
    <div id="ui">Ray Marching Metaballs | WebGL + SDF</div>
    <canvas id="glCanvas"></canvas>

    <!-- VERTEX SHADER -->
    <!-- Simple pass-through shader. We create a quad covering the screen (-1 to 1) 
         and pass the coordinates to the fragment shader for ray generation. -->
    <script id="vertex-shader" type="x-shader/x-vertex">
        attribute vec2 a_position;
        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
        }
    </script>

    <!-- FRAGMENT SHADER -->
    <!-- The main logic: Ray Marching, SDFs, Smooth Min, and Procedural Coloring -->
    <script id="fragment-shader" type="x-shader/x-fragment">
        #ifdef GL_ES
        precision highp float;
        #endif

        uniform vec2 u_resolution;
        uniform float u_time;

        // ----------------------------------------------------------
        // 1. UTILITY FUNCTIONS
        // ----------------------------------------------------------

        // 2D Rotation Matrix
        mat2 rot(float a) {
            float s = sin(a);
            float c = cos(a);
            return mat2(c, -s, s, c);
        }

        // Color Palette Function (Cosine based) - Creates nice gradients
        vec3 palette( float t ) {
            vec3 a = vec3(0.5, 0.5, 0.5);
            vec3 b = vec3(0.5, 0.5, 0.5);
            vec3 c = vec3(1.0, 1.0, 1.0);
            vec3 d = vec3(0.263, 0.416, 0.557); // Psychedelic Blue/Cyan/Crimson vibe
            return a + b*cos( 6.28318*(c*t+d) );
        }

        // ----------------------------------------------------------
        // 2. SDF OPERATORS (Signed Distance Functions)
        // ----------------------------------------------------------

        // Sphere SDF: Distance from point p to sphere center with radius r
        float sdSphere( vec3 p, float r ) {
            return length(p) - r;
        }

        // Smooth Minimum Function (Smooth Union)
        // k: the blending radius. Larger k = more distinct shapes, smaller k = more merging
        float smin( float a, float b, float k ) {
            float h = clamp( 0.5 + 0.5 * (b - a) / k, 0.0, 1.0 );
            // Polynomial smooth min (better than exponential for performance/stability)
            return mix( a, b, h ) - k * h * (1.0 - h);
        }

        // Scene SDF: Combines multiple metaballs
        float mapScene(vec3 p) {
            // Copy p to modify for animation
            vec3 pos = p;
            
            // Time factor for rotation/oscillation
            float t = u_time * 0.4;

            // Define Metaballs
            // We will have 3 main metaballs + 2 ambient ones for depth
            
            // Ball 1: Spinning around Y axis
            vec3 p1 = pos;
            p1.xz *= rot(t); 
            p1.y += sin(t * 0.5) * 1.5;
            float d1 = sdSphere(p1, 1.0 + 0.2*sin(t*2.0)); // Pulsating radius

            // Ball 2: Spinning opposite direction
            vec3 p2 = pos;
            p2.xy *= rot(-t * 0.8);
            p2.z += cos(t * 1.2) * 2.0;
            float d2 = sdSphere(p2, 0.9);

            // Ball 3: Complex spiral path
            vec3 p3 = pos;
            p3.x += sin(t * 1.5) * 2.5;
            p3.y += cos(t * 2.0) * 2.5;
            p3.z += sin(t * 0.5) * 2.0;
            // Rotate the point around Z to make it spiral
            p3.xy *= rot(t * 0.3);
            float d3 = sdSphere(p3, 0.8);

            // Ball 4 & 5: Ambient background noise
            vec3 p4 = pos;
            p4.x += cos(t * 0.7) * 3.5;
            p4.y += sin(t * 0.9) * 0.5;
            float d4 = sdSphere(p4, 0.6);

            vec3 p5 = pos;
            p5.y += cos(t * 1.3) * 3.5;
            p5.z += sin(t * 0.4) * 3.5;
            float d5 = sdSphere(p5, 0.7);

            // Combine all using Smooth Min
            // We chain smin: result = smin(smin(smin(d1,d2),d3),d4)
            // The 'k' parameter (0.7) controls how much they merge
            float res = smin(d1, d2, 0.7);
            res = smin(res, d3, 0.7);
            res = smin(res, d4, 0.6);
            res = smin(res, d5, 0.6);

            return res;
        }

        // ----------------------------------------------------------
        // 3. RAY MARCHING
        // ----------------------------------------------------------

        float raymarch(vec3 origin, vec3 dir) {
            float dO = 0.0; // Distance origin
            float dMax = 20.0; // Max distance
            float epsilon = 0.001; // Hit threshold

            // March!
            for(int i = 0; i < 60; i++) {
                vec3 p = origin + dir * dO;
                float dist = mapScene(p);
                
                if(dist < epsilon) {
                    return dO; // Hit! Return distance
                }
                
                if(dist > dMax) {
                    return -1.0; // Missed, return negative
                }
                
                dO += dist; // Move forward by the estimated distance
            }
            return -1.0;
        }

        // Calculate Normal using gradient approximation
        vec3 getNormal(vec3 p) {
            float d = mapScene(p);
            vec2 e = vec2(0.001, 0.0);
            vec3 n = d - vec3(
                mapScene(p - e.xyy),
                mapScene(p - e.yxy),
                mapScene(p - e.yyx)
            );
            return normalize(n);
        }

        // ----------------------------------------------------------
        // 4. SHADING & LIGHTING
        // ----------------------------------------------------------

        vec3 render(vec3 rayOrigin, vec3 rayDir) {
            float d = raymarch(rayOrigin, rayDir);

            // Background Color (Deep space black with a hint of color)
            vec3 finalColor = vec3(0.02, 0.01, 0.05); 

            if (d > 0.0) {
                vec3 hitPoint = rayOrigin + rayDir * d;
                vec3 normal = getNormal(hitPoint);

                // Psychedelic Coloring Logic
                // 1. Base color from palette based on position and time
                vec3 col = palette(length(hitPoint) * 0.5 + u_time * 0.2);
                
                // 2. Add interference patterns based on normal and time
                float noise = sin(hitPoint.x * 4.0 + u_time) * 
                              cos(hitPoint.y * 4.0 + u_time) * 
                              sin(hitPoint.z * 4.0 + u_time);
                
                col += noise * 0.3;

                // Lighting
                // Light 1: Main directional light
                vec3 lightDir = normalize(vec3(0.5, 1.0, 0.5));
                float diff = max(dot(normal, lightDir), 0.0);
                
                // Light 2: Rim light (Backlighting for halo effect)
                vec3 viewDir = normalize(rayOrigin - hitPoint); // Actually -rayDir
                float rim = 1.0 - max(dot(normal, viewDir), 0.0);
                rim = pow(rim, 3.0); // Sharpen the rim

                // Specular highlight
                vec3 reflectDir = reflect(-lightDir, normal);
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);

                // Combine lighting
                vec3 lighting = vec3(0.0);
                lighting += vec3(0.8, 0.8, 1.0) * diff;      // White/Greenish key light
                lighting += vec3(1.0, 0.2, 0.8) * rim * 0.8; // Purple Rim light
                lighting += vec3(1.0) * spec * 0.5;          // White specular

                finalColor = col * lighting;

                // Fog / Distance falloff (mix background color based on distance)
                finalColor = mix(vec3(0.0), finalColor, 1.0 - exp(-d * 0.15));
                
                // Add some "glow" saturation
                finalColor = pow(finalColor, vec3(1.2));
            }

            return finalColor;
        }

        void main() {
            // Normalize pixel coordinates (from 0 to 1)
            vec2 uv = gl_FragCoord.xy / u_resolution.xy;
            
            // Center coordinates (-0.5 to 0.5)
            uv = uv * 2.0 - 1.0;
            
            // Fix aspect ratio
            uv.x *= u_resolution.x / u_resolution.y;

            // Camera Setup
            vec3 ro = vec3(0.0, 0.0, -4.0); // Ray Origin (Camera position)
            vec3 rd = normalize(vec3(uv, 1.5)); // Ray Direction

            // Camera Movement (Orbit / Dolly zoom feel)
            // Slight tilt
            mat2 tilt = rot(sin(u_time * 0.1) * 0.1);
            ro.xy *= tilt;
            
            // Generate and Render
            vec3 color = render(ro, rd);

            // Post-processing: Simple Contrast Curve
            color = color * (1.5 - color);

            gl_FragColor = vec4(color, 1.0);
        }
    </script>

    <!-- JAVASCRIPT LOGIC -->
    <script>
        const canvas = document.getElementById('glCanvas');
        const gl = canvas.getContext('webgl');

        if (!gl) {
            alert('WebGL not supported');
            throw new Error('WebGL not supported');
        }

        // --- Compile Shader Helper ---
        function createShader(gl, type, source) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                console.error(gl.getShaderInfoLog(shader));
                gl.deleteShader(shader);
                return null;
            }
            return shader;
        }

        // --- Create Program ---
        const vertexShaderSource = document.getElementById('vertex-shader').text;
        const fragmentShaderSource = document.getElementById('fragment-shader').text;

        const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
        const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);

        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error(gl.getProgramInfoLog(program));
            throw new Error('Shader program link failed');
        }

        gl.useProgram(program);

        // --- Set up Geometry (Full Screen Quad) ---
        // Two triangles covering the NDC (Normalized Device Coordinate) space
        // (-1, -1) to (1, 1)
        const vertices = new Float32Array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
            -1.0,  1.0,
             1.0, -1.0,
             1.0,  1.0,
        ]);

        const positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

        const positionLocation = gl.getAttribLocation(program, 'a_position');
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

        // --- Uniform Locations ---
        const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
        const timeLocation = gl.getUniformLocation(program, 'u_time');

        // --- Resize Handling ---
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            gl.viewport(0, 0, canvas.width, canvas.height);
        }
        window.addEventListener('resize', resize);
        resize();

        // --- Animation Loop ---
        function render(time) {
            // Convert time to seconds
            const seconds = time * 0.001;

            // Update Uniforms
            gl.uniform2f(resolutionLocation, canvas.width, canvas.height);
            gl.uniform1f(timeLocation, seconds);

            // Draw
            gl.drawArrays(gl.TRIANGLES, 0, 6);

            requestAnimationFrame(render);
        }

        requestAnimationFrame(render);

    </script>
</body>
</html>
```

### Implementation Details

1.  **WebGL Setup**:
    *   The JavaScript initializes a standard WebGL context.
    *   It compiles a simple Vertex Shader (which acts as a pass-through for a full-screen quad) and a complex Fragment Shader (where the magic happens).
    *   A buffer containing two triangles is set up to cover the entire screen (-1 to 1 coordinate space).

2.  **Ray Marching Logic**:
    *   Inside the Fragment Shader, `raymarch` function iterates up to 60 times.
    *   It calculates the distance from the current ray point to the nearest surface using `mapScene`.
    *   It advances the ray by that distance (the "Ray March" algorithm).
    *   If the distance gets smaller than `epsilon` (0.001), it registers a "hit" and returns the total distance traveled.

3.  **SDF & Metaballs**:
    *   `sdSphere` defines the basic sphere SDF.
    *   `mapScene` creates 5 distinct spheres.
    *   **Smooth Minimum (`smin`)**: This is the core "Psychedelic" ingredient. Instead of using a standard `min()` function (which creates hard edges where objects touch), `smin` interpolates between the two objects. The parameter `k` (set to ~0.7) determines how "squishy" the merge is.
    *   **Animation**: The spheres' positions are manipulated using `sin` and `cos` of `u_time`, causing them to orbit, spin, and pulsate.

4.  **Shading & Coloring**:
    *   **Normal Calculation**: Since we don't have explicit triangle normals, we calculate the gradient of the SDF (`getNormal`) to find the surface orientation.
    *   **Procedural Palette**: The `palette` function uses cosine waves to generate smooth, shifting colors (Neon Cyan, Magenta, Electric Yellow) rather than hard RGB values.
    *   **Lighting**:
        *   **Diffuse**: Standard dot-product lighting.
        *   **Rim Light**: Calculates the angle between the view ray and the surface normal. This creates a glowing "halo" effect around the edges of the blobs, enhancing the volumetric feel.
    *   **Post-Processing**: A simple contrast curve `color * (1.5 - color)` is applied at the end to make the colors pop, and distance fog is used to fade objects into the deep background.

5.  **Performance**:
    *   The shader uses `highp` (high precision) for float calculations, which is essential for SDFs to prevent "stepping" artifacts.
    *   The loop count is capped at 60, which is generally safe for modern GPUs while maintaining high visual fidelity.

To run this, simply save the code block as an `.html` file (e.g., `metaballs.html`) and open it in any modern web browser. No external assets are required.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q4_K_XL.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Time: 69.34s -->
<!-- Fallback: False -->